import json
import uuid
from typing import Any, Optional


def make_request(action: str, payload: Optional[dict] = None) -> str:
    return json.dumps({
        "id": str(uuid.uuid4()),
        "type": "request",
        "action": action,
        "payload": payload or {}
    }, ensure_ascii=False)


def parse_response(response_json: str) -> dict:
    return json.loads(response_json)


def make_event(event: str, data: dict) -> str:
    return json.dumps({
        "type": "event",
        "event": event,
        "data": data
    }, ensure_ascii=False)
