#!/usr/bin/env python3
"""Demo agent that turns a natural-language request into a real authorization check."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass

import httpx


SYSTEM_PROMPT = """You convert operator requests into strict JSON for an authorization API.
Return JSON only with the shape:
{"action":"...","resource":"...","context":{"amount":123,"currency":"USD"}}
Choose action names like refund.create or customer.delete.
"""


@dataclass(frozen=True)
class ParsedInstruction:
    action: str
    resource: str
    context: dict[str, str | int | float | bool]


def call_openai(request_text: str) -> ParsedInstruction:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for demo_agent.py")
    model = os.environ.get("TRUSTLAYER_LLM_MODEL", "gpt-4.1-mini")
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request_text},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    payload = json.loads(content)
    return ParsedInstruction(
        action=str(payload["action"]),
        resource=str(payload["resource"]),
        context=dict(payload.get("context", {})),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real TrustLayer authorization check from natural language.")
    parser.add_argument("request", help='Natural-language instruction, for example: "refund this $500 order"')
    parser.add_argument("--base-url", default=os.environ.get("TRUSTLAYER_API_URL", "http://localhost:8000"))
    parser.add_argument("--agent-id", default=os.environ.get("TRUSTLAYER_AGENT_ID"))
    parser.add_argument("--token", default=os.environ.get("TRUSTLAYER_ACCESS_TOKEN"))
    parser.add_argument("--api-key", default=os.environ.get("TRUSTLAYER_API_KEY"))
    args = parser.parse_args()

    if not args.agent_id:
        raise SystemExit("TRUSTLAYER_AGENT_ID or --agent-id is required")
    credential = args.token or args.api_key
    if not credential:
        raise SystemExit("Provide TRUSTLAYER_ACCESS_TOKEN, TRUSTLAYER_API_KEY, --token, or --api-key")

    parsed = call_openai(args.request)
    response = httpx.post(
        f"{args.base_url.rstrip('/')}/v1/authorization/check",
        headers={"Authorization": f"Bearer {credential}", "Content-Type": "application/json"},
        json={
            "agent_id": args.agent_id,
            "action": parsed.action,
            "resource": parsed.resource,
            "context": parsed.context,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    print(json.dumps({
        "parsed_instruction": parsed.__dict__,
        "decision": payload["decision"],
        "request_id": payload["request_id"],
        "policy_version": payload["policy_version"],
        "approval_request_id": payload.get("approval_request_id"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
