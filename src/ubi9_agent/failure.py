from __future__ import annotations

import json
from pathlib import Path

from .openai_client import AIClient
from .util import load_yaml, write_json


def analyze_failure(
    repo: str | Path,
    dockerfile: str,
    log_file: str,
    config_path: str,
    no_ai: bool = False,
) -> dict:
    repo = Path(repo).resolve()
    cfg = load_yaml(config_path)
    dockerfile_path = repo / dockerfile
    log = Path(log_file).read_text(errors="replace")[-60000:]
    current = dockerfile_path.read_text(errors="replace")
    result = None

    if not no_ai and cfg.get("ai", {}).get("enabled", True):
        try:
            prompt = (repo / "prompts" / "failure.md").read_text(encoding="utf-8")
            payload = f"Dockerfile:\n{current}\n\nBuild log:\n{log}"
            result = AIClient().json(prompt, payload)
        except Exception as exc:  # noqa: BLE001
            result = {
                "category": "unknown",
                "root_cause": "AI analysis unavailable",
                "evidence": str(exc),
                "risk": "high",
                "auto_fix_allowed": False,
                "proposed_dockerfile": "",
                "notes": "Manual review required",
            }

    if not result:
        result = {
            "category": "unknown",
            "root_cause": "No AI analysis requested",
            "evidence": log[-2000:],
            "risk": "high",
            "auto_fix_allowed": False,
            "proposed_dockerfile": "",
            "notes": "Manual review required",
        }

    allowed = set(cfg.get("policy", {}).get("auto_fix_categories", []))
    result["policy_allows_fix"] = bool(
        result.get("auto_fix_allowed")
        and result.get("category") in allowed
        and result.get("proposed_dockerfile")
    )
    write_json(repo / "reports" / "failure-analysis.json", result)
    return result


def apply_safe_fix(repo: str | Path, dockerfile: str, analysis_file: str) -> bool:
    repo = Path(repo).resolve()
    data = json.loads(Path(analysis_file).read_text(encoding="utf-8"))
    if not data.get("policy_allows_fix"):
        return False
    proposed = data.get("proposed_dockerfile", "")
    if not proposed.strip():
        return False
    (repo / dockerfile).write_text(proposed.rstrip() + "\n", encoding="utf-8")
    return True
