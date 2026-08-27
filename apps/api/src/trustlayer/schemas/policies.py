from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from trustlayer.schemas.common import ScalarValue


DecisionType = str


class PolicyRuleCondition(BaseModel):
    action: str = Field(min_length=1, max_length=200)
    amount_lte: int | float | None = None
    amount_gt: int | float | None = None


class PolicyRule(BaseModel):
    if_: PolicyRuleCondition = Field(alias="if")
    then: str

    @field_validator("then")
    @classmethod
    def validate_then(cls, value: str) -> str:
        if value not in {"ALLOW", "DENY", "REQUIRE_APPROVAL"}:
            raise ValueError("then must be ALLOW, DENY, or REQUIRE_APPROVAL")
        return value


class CreatePolicyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    rules: list[PolicyRule]

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, value: list[PolicyRule]) -> list[PolicyRule]:
        if len(value) == 0:
            raise ValueError("rules must contain at least one rule")
        return value


class PolicyResponse(BaseModel):
    id: str
    name: str
    version: int
    is_active: bool
    rules: list[dict[str, dict[str, ScalarValue] | str]]
    created_at: datetime


class CreatePolicyResponse(BaseModel):
    id: str
    version: int
