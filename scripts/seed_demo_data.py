"""Seed realistic demo data through the local Cognos AI API.

This script is intentionally API-based instead of direct database-based.
It exercises the same backend routes the dashboard uses and keeps demo setup
close to the real product flow.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import date, datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4


DEFAULT_API_BASE = "http://localhost:8000"
DEFAULT_TOKEN = "local-dev-platform-admin-token"
DEFAULT_DEMO_PASSWORD = "Demo12345!"


class ApiClient:
    def __init__(self, api_base: str, token: str) -> None:
        self.api_base = api_base.rstrip("/")
        self.token = token

    def get(self, path: str) -> Any:
        return self._request("GET", path)

    def post(self, path: str, payload: dict[str, Any]) -> Any:
        return self._request("POST", path, payload)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        url = f"{self.api_base}{path}"
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Content-Type": "application/json",
                "X-Platform-Admin-Token": self.token,
            },
        )

        try:
            with urlopen(request, timeout=20) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else None
        except HTTPError as exc:
            detail = exc.read().decode("utf-8")
            raise RuntimeError(f"{method} {url} failed: {exc.code} {detail}") from exc
        except URLError as exc:
            raise RuntimeError(
                f"Could not reach {url}. Is the local backend running?"
            ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed Cognos AI demo data.")
    parser.add_argument("--api-base", default=os.getenv("COGNOS_API_BASE", DEFAULT_API_BASE))
    parser.add_argument(
        "--token",
        default=os.getenv("PLATFORM_ADMIN_TOKEN", DEFAULT_TOKEN),
        help="Platform admin token for local setup APIs.",
    )
    parser.add_argument(
        "--company-name",
        default=None,
        help="Optional demo company name. A unique suffix is added when omitted.",
    )
    args = parser.parse_args()

    client = ApiClient(api_base=args.api_base, token=args.token)
    suffix = uuid4().hex[:8]
    company_name = args.company_name or f"Cognos Demo Construction {suffix}"

    print(f"Seeding demo data into {args.api_base}...")
    assert_backend_is_healthy(client)

    company = client.post(
        "/companies",
        {
            "name": company_name,
            "status": "active",
            "ai_key_mode": "platform_managed",
            "ai_subscription_enabled": True,
        },
    )

    users = seed_users(client, company["id"], suffix)
    project = seed_project(client, company["id"], suffix)
    seed_project_assignments(client, company["id"], project["id"], users)
    progress_entries = seed_progress_entries(client, company["id"], project["id"], users)
    manpower_entries = seed_manpower_entries(client, company["id"], project["id"], users)
    material_entries = seed_material_transactions(client, company["id"], project["id"], users)
    stock_balances = seed_stock_balances(client, company["id"], project["id"])
    media_files = seed_media_files(
        client,
        company["id"],
        project["id"],
        users,
        progress_entries,
        material_entries,
    )

    print("\nDemo data created.")
    print(f"Company: {company['name']} ({company['id']})")
    print(f"Project: {project['name']} ({project['code']})")
    print(f"Users: {len(users)}")
    print(f"Progress entries: {len(progress_entries)}")
    print(f"Manpower entries: {len(manpower_entries)}")
    print(f"Material transactions: {len(material_entries)}")
    print(f"Stock balances: {len(stock_balances)}")
    print(f"Media files: {len(media_files)}")
    print("\nDemo login:")
    print(f"Email: {users['owner']['email']}")
    print(f"Password: {DEFAULT_DEMO_PASSWORD}")
    print("\nOpen the dashboard:")
    print("http://localhost:3000")
    return 0


def assert_backend_is_healthy(client: ApiClient) -> None:
    health = client.get("/health")
    if health.get("status") != "healthy":
        raise RuntimeError(f"Backend is not healthy: {health}")


def seed_users(client: ApiClient, company_id: str, suffix: str) -> dict[str, Any]:
    random_digits = random.randint(100000, 999999)
    user_payloads = {
        "owner": {
            "name": "Demo Owner",
            "phone": f"+919100{random_digits}",
            "email": f"owner-{suffix}@example.com",
            "password": DEFAULT_DEMO_PASSWORD,
            "role": "owner",
        },
        "project_manager": {
            "name": "Demo Project Manager",
            "phone": f"+919101{random_digits}",
            "email": f"pm-{suffix}@example.com",
            "password": DEFAULT_DEMO_PASSWORD,
            "role": "project_manager",
        },
        "site_engineer": {
            "name": "Demo Site Engineer",
            "phone": f"+919102{random_digits}",
            "email": f"engineer-{suffix}@example.com",
            "password": DEFAULT_DEMO_PASSWORD,
            "role": "site_engineer",
        },
        "storekeeper": {
            "name": "Demo Storekeeper",
            "phone": f"+919103{random_digits}",
            "email": f"store-{suffix}@example.com",
            "password": DEFAULT_DEMO_PASSWORD,
            "role": "storekeeper",
        },
    }

    return {
        key: client.post(f"/companies/{company_id}/users", payload)
        for key, payload in user_payloads.items()
    }


def seed_project(client: ApiClient, company_id: str, suffix: str) -> dict[str, Any]:
    today = date.today()
    return client.post(
        f"/companies/{company_id}/projects",
        {
            "name": "Green Residency Demo",
            "code": f"GRD-{suffix.upper()}",
            "location": "Pune",
            "status": "active",
            "start_date": (today - timedelta(days=45)).isoformat(),
            "end_date": (today + timedelta(days=180)).isoformat(),
            "timezone": "Asia/Kolkata",
        },
    )


def seed_project_assignments(
    client: ApiClient,
    company_id: str,
    project_id: str,
    users: dict[str, Any],
) -> None:
    assignments = [
        ("owner", "owner", True, True, True, True),
        ("project_manager", "project_manager", True, True, True, True),
        ("site_engineer", "site_engineer", True, True, False, True),
        ("storekeeper", "storekeeper", False, False, True, True),
    ]
    for user_key, role, progress, manpower, materials, dashboard in assignments:
        client.post(
            f"/companies/{company_id}/projects/{project_id}/users",
            {
                "user_id": users[user_key]["id"],
                "role_on_project": role,
                "can_enter_progress": progress,
                "can_enter_manpower": manpower,
                "can_enter_materials": materials,
                "can_view_dashboard": dashboard,
            },
        )


def seed_progress_entries(
    client: ApiClient,
    company_id: str,
    project_id: str,
    users: dict[str, Any],
) -> list[dict[str, Any]]:
    today = date.today()
    entries = [
        ("Plastering", "Tower A Floor 2", 50, "sqm", today, "Aaj Tower A Floor 2 me 50 sqm plaster complete hua"),
        ("Plastering", "Tower A Floor 3", 35, "sqm", today, "Tower A Floor 3 plaster 35 sqm done"),
        ("Brickwork", "Block B Floor 1", 900, "nos", today - timedelta(days=1), "Block B Floor 1 brickwork 900 nos complete"),
        ("Waterproofing", "Basement 1", 120, "sqm", today - timedelta(days=1), "Basement waterproofing 120 sqm complete"),
        ("Tiling", "Clubhouse", 25, "sqm", today - timedelta(days=2), "Clubhouse tiling 25 sqm done"),
    ]
    return [
        client.post(
            f"/companies/{company_id}/projects/{project_id}/reporting/progress-entries",
            {
                "entered_by": users["site_engineer"]["id"],
                "activity_name": activity,
                "location_text": location,
                "quantity": quantity,
                "unit_symbol": unit,
                "work_date": work_date.isoformat(),
                "status": "confirmed",
                "original_text": original_text,
            },
        )
        for activity, location, quantity, unit, work_date, original_text in entries
    ]


def seed_manpower_entries(
    client: ApiClient,
    company_id: str,
    project_id: str,
    users: dict[str, Any],
) -> list[dict[str, Any]]:
    today = date.today()
    entries = [
        ("mason", 14, "Tower A", today),
        ("helper", 18, "Tower A", today),
        ("electrician", 4, "Block B", today),
        ("plumber", 3, "Basement 1", today),
        ("painter", 6, "Clubhouse", today - timedelta(days=1)),
    ]
    return [
        client.post(
            f"/companies/{company_id}/projects/{project_id}/reporting/manpower-entries",
            {
                "entered_by": users["site_engineer"]["id"],
                "trade_name": trade,
                "worker_count": count,
                "location_text": location,
                "work_date": work_date.isoformat(),
                "status": "confirmed",
                "original_text": f"{count} {trade} at {location}",
            },
        )
        for trade, count, location, work_date in entries
    ]


def seed_material_transactions(
    client: ApiClient,
    company_id: str,
    project_id: str,
    users: dict[str, Any],
) -> list[dict[str, Any]]:
    today = date.today()
    entries = [
        ("received", "cement", 120, "bags", "Tower A", today, "attached"),
        ("issued", "cement", 75, "bags", "Tower A", today, "not_attached"),
        ("received", "steel", 5, "tons", "Store Yard", today - timedelta(days=1), "attached"),
        ("issued", "steel", 6, "tons", "Basement 1", today, "not_attached"),
        ("received", "bricks", 6000, "nos", "Block B", today - timedelta(days=2), "attached"),
        ("issued", "bricks", 1000, "nos", "Block B", today - timedelta(days=1), "not_attached"),
    ]
    return [
        client.post(
            f"/companies/{company_id}/projects/{project_id}/reporting/material-transactions",
            {
                "entered_by": users["storekeeper"]["id"],
                "transaction_type": transaction_type,
                "material_name": material,
                "quantity": quantity,
                "unit_symbol": unit,
                "location_text": location,
                "transaction_date": transaction_date.isoformat(),
                "proof_status": proof_status,
                "status": "confirmed",
                "original_text": f"{quantity} {material} {unit} {transaction_type} at {location}",
            },
        )
        for transaction_type, material, quantity, unit, location, transaction_date, proof_status in entries
    ]


def seed_stock_balances(
    client: ApiClient,
    company_id: str,
    project_id: str,
) -> list[dict[str, Any]]:
    entries = [
        ("cement", "bags", 120, 75, 45, 60),
        ("steel", "tons", 5, 6, -1, 1),
        ("bricks", "nos", 6000, 1000, 5000, 1000),
    ]
    return [
        client.post(
            f"/companies/{company_id}/projects/{project_id}/reporting/material-stock-balances",
            {
                "material_name": material,
                "unit_symbol": unit,
                "total_received": total_received,
                "total_issued": total_issued,
                "current_balance": current_balance,
                "low_stock_threshold": threshold,
            },
        )
        for material, unit, total_received, total_issued, current_balance, threshold in entries
    ]


def seed_media_files(
    client: ApiClient,
    company_id: str,
    project_id: str,
    users: dict[str, Any],
    progress_entries: list[dict[str, Any]],
    material_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    captured_at = datetime.now(timezone.utc).isoformat()
    entries = [
        (
            "progress_entry",
            progress_entries[0]["id"],
            "image",
            "https://example.com/demo/tower-a-plaster.jpg",
            "tower-a-plaster.jpg",
            "Tower A plaster progress photo",
            users["site_engineer"]["id"],
        ),
        (
            "material_transaction",
            material_entries[0]["id"],
            "image",
            "https://example.com/demo/cement-delivery.jpg",
            "cement-delivery.jpg",
            "Cement delivery proof",
            users["storekeeper"]["id"],
        ),
    ]
    return [
        client.post(
            f"/companies/{company_id}/projects/{project_id}/reporting/media-files",
            {
                "uploaded_by": uploaded_by,
                "linked_entity_type": entity_type,
                "linked_entity_id": entity_id,
                "media_type": media_type,
                "storage_url": storage_url,
                "file_name": file_name,
                "caption": caption,
                "processing_status": "stored",
                "captured_at": captured_at,
            },
        )
        for entity_type, entity_id, media_type, storage_url, file_name, caption, uploaded_by in entries
    ]


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
