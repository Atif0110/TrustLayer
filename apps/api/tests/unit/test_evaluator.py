from trustlayer.policy_engine.evaluator import evaluate

RULES = [
    {"if": {"action": "refund.create", "amount_lte": 100}, "then": "ALLOW"},
    {"if": {"action": "refund.create", "amount_gt": 100}, "then": "REQUIRE_APPROVAL"},
    {"if": {"action": "customer.delete"}, "then": "DENY"},
]


def test_decisions_and_default_deny() -> None:
    assert evaluate(RULES, "refund.create", {"amount": 50})[0] == "ALLOW"
    assert evaluate(RULES, "refund.create", {"amount": 500})[0] == "REQUIRE_APPROVAL"
    assert evaluate(RULES, "customer.delete", {})[0] == "DENY"
    assert evaluate(RULES, "unknown", {})[0] == "DENY"


def test_non_numeric_amount_fails_closed() -> None:
    assert evaluate(RULES, "refund.create", {"amount": "500"})[0] == "DENY"
