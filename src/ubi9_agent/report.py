from __future__ import annotations

import json
from pathlib import Path


def generate(repo: str | Path) -> Path:
    repo = Path(repo).resolve()
    reports = repo / "reports"

    def read(name: str) -> dict:
        path = reports / name
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    analysis = read("analysis.json")
    migration = read("migration.json")
    failure = read("failure-analysis.json")
    lines = [
        "# UBI9 Migration Report",
        "",
        "## Level 1 — Repository analysis",
        f"- Selected Dockerfile: `{analysis.get('selected_dockerfile')}`",
        f"- Languages: {', '.join(analysis.get('languages', [])) or 'Not detected'}",
        f"- Source base images: {', '.join(analysis.get('base_images', [])) or 'Not detected'}",
        "",
        "## Level 2 — Dockerfile migration",
        f"- Generated: `{migration.get('target')}`",
        f"- Summary: {migration.get('summary', 'Not run')}",
    ]
    for risk in migration.get("risks", []):
        lines.append(f"- Risk: {risk}")
    lines.extend(
        [
            "",
            "## Level 3 — Build and remediation",
            f"- Failure category: {failure.get('category', 'No failure analysis')}",
            f"- Root cause: {failure.get('root_cause', 'N/A')}",
            f"- Automatic fix permitted: {failure.get('policy_allows_fix', False)}",
            "",
            "## Human review",
            "Review generated Dockerfile, image provenance, package repositories, license implications, and smoke-test coverage before merging.",
        ]
    )
    output = reports / "UBI9-MIGRATION-REPORT.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
