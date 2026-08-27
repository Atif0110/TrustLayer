from collections.abc import Mapping

from trustlayer.policy_engine.rules import matches_condition

DECISIONS = {"ALLOW", "DENY", "REQUIRE_APPROVAL"}


def evaluate(rules: list[dict[str, object]], action: str, context: Mapping[str, object]) -> tuple[str, str]:
    """Return the first matching decision, failing closed when no rule applies."""
    for rule in rules:
        condition = rule.get("if")
        decision = rule.get("then")
        if not isinstance(condition, dict) or decision not in DECISIONS:
            continue
        if matches_condition(condition, action=action, context=context):
            return str(decision), "matched policy rule"
    return "DENY", "no policy rule matched"
