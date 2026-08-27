from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from trustlayer.agents.router import router as agents_router
from trustlayer.approvals.router import router as approvals_router
from trustlayer.audit.router import router as audit_router
from trustlayer.auth.router import router as auth_router
from trustlayer.authorization.router import router as authorization_router
from trustlayer.config import settings
from trustlayer.policies.router import router as policies_router


def create_app() -> FastAPI:
    app = FastAPI(title="TrustLayer API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Return a minimal process health response for local orchestration checks."""

        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(agents_router)
    app.include_router(policies_router)
    app.include_router(authorization_router)
    app.include_router(approvals_router)
    app.include_router(audit_router)
    return app


app = create_app()
