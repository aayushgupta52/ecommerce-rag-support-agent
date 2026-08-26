import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$", re.MULTILINE)

@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    source_file: str
    heading: str
    text: str
    metadata: dict = field(default_factory=dict)

    @property
    def citation(self) -> str:
        return f"{self.source_file} — {self.heading}"


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(raw)
    if not m:
        return {}, raw

    fm_text, body = m.group(1), m.group(2)
    meta = yaml.safe_load(fm_text) or {}
    return meta, body

def split_by_heading(body: str) -> list[tuple[str, str]]:
    matches = list(HEADING_RE.finditer(body))
    sections: list[tuple[str, str]] = []

    if not matches:
        stripped = body.strip()
        if stripped:
            sections.append(("(document body)", stripped))
        return sections

    doc_title = None
    first = matches[0]
    if first.group(1) == "#":
        doc_title = first.group(2).strip()

    h2_matches = [m for m in matches if m.group(1) == "##"]

    if not h2_matches:
        content = body[first.end():].strip()
        if content:
            sections.append((doc_title or "(document body)", content))
        return sections

    for i, m in enumerate(h2_matches):
        heading = m.group(2).strip()
        start = m.end()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(body)
        text = body[start:end].strip()
        if text:
            sections.append((heading, text))

    return sections


def load_documents(kb_dir: str | Path) -> list[Chunk]:
    kb_dir = Path(kb_dir)
    chunks: list[Chunk] = []

    for path in sorted(kb_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        sections = split_by_heading(body)

        doc_id = meta.get("document_id", path.stem)
        for idx, (heading, text) in enumerate(sections):
            chunk = Chunk(
                chunk_id=f"{doc_id}::{idx}",
                doc_id=doc_id,
                source_file=path.name,
                heading=heading,
                text=text,
                metadata=meta,
            )
            chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    chunks = load_documents("knowledge-base")
    for c in chunks:
        print(f"[{c.source_file}] status={c.metadata.get('status')} "
              f"authority={c.metadata.get('policy_authority')} :: {c.heading}")
    print(f"\nTotal chunks: {len(chunks)}")