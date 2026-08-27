from pydantic import BaseModel, Field, field_validator


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=12, max_length=256)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.count("@") != 1:
            raise ValueError("email must contain a single @ sign")
        local, domain = normalized.split("@", 1)
        if local == "" or domain == "" or "." not in domain:
            raise ValueError("email must include a local part and domain")
        return normalized


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=256)
    organization_name: str | None = Field(default=None, min_length=1, max_length=200)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized.count("@") != 1:
            raise ValueError("email must contain a single @ sign")
        local, domain = normalized.split("@", 1)
        if local == "" or domain == "" or "." not in domain:
            raise ValueError("email must include a local part and domain")
        return normalized


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    email: str
    organization_id: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
