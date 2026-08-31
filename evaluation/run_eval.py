import json
import sys
import uuid
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent import Agent


def load_cases(path: str = "evaluation/visible-cases.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]


def check_expectations(response_text: str, expect: dict) -> list[str]:
    failures = []
    response_lower = response_text.lower()

    for phrase in expect.get("must_include", []):
        if phrase.lower() not in response_lower:
            failures.append(f"Missing expected phrase: '{phrase}'")

    for phrase in expect.get("must_not_include", []):
        if phrase.lower() in response_lower:
            failures.append(f"Contains forbidden phrase: '{phrase}'")

    for source in expect.get("required_sources", []):
        if source.lower() not in response_lower:
            failures.append(f"Missing required source citation: '{source}'")

    for source in expect.get("forbidden_sources_as_authority", []):
        if source.lower() in response_lower:
            failures.append(f"Cited forbidden/unauthoritative source: '{source}'")

    return failures


def run_case(agent: Agent, case: dict) -> dict:
    session_id = f"eval-{case['id']}-{uuid.uuid4().hex[:8]}"
    messages = case["messages"]
    expect = case.get("expect", {})

    result = {}
    for msg in messages:
        result = agent.handle_message_detailed(session_id, msg["content"])

    final_response = result.get("text", "")
    failures = check_expectations(final_response, expect)

    expected_tool = expect.get("tool")
    if expected_tool == "not_called":
        if result.get("tool_calls"):
            failures.append(f"Expected no tool call, but tools were called: {result['tool_calls']}")
    elif expected_tool == "order_lookup":
        called_lookup = any(tc["tool"] == "lookup_order" for tc in result.get("tool_calls", []))
        if not called_lookup:
            failures.append("Expected lookup_order tool to be called, but it was not.")

    expected_handoff = expect.get("handoff")
    if expected_handoff is not None:
        actual_handoff = result.get("handoff", False)
        if expected_handoff != actual_handoff:
            failures.append(f"Expected handoff={expected_handoff}, got handoff={actual_handoff}")

    return {
        "id": case["id"],
        "category": case["category"],
        "passed": len(failures) == 0,
        "failures": failures,
        "response": final_response,
    }


def main():
    agent = Agent()
    cases = load_cases()

    results = []
    for case in cases:
        print(f"Running: {case['id']} ({case['category']})...")
        result = run_case(agent, case)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"  -> {status}")
        if not result["passed"]:
            for f in result["failures"]:
                print(f"     - {f}")
        time.sleep(5)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    by_category: dict[str, list[dict]] = {}
    for r in results:
        by_category.setdefault(r["category"], []).append(r)

    for category, cat_results in sorted(by_category.items()):
        passed = sum(1 for r in cat_results if r["passed"])
        total = len(cat_results)
        print(f"{category}: {passed}/{total}")

    total_passed = sum(1 for r in results if r["passed"])
    total_cases = len(results)
    print(f"\nTOTAL: {total_passed}/{total_cases}")

    return results


if __name__ == "__main__":
    main()