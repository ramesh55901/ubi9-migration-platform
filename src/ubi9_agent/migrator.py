from __future__ import annotations

import re
from pathlib import Path

from .openai_client import AIClient
from .util import load_yaml, target_path, write_json


def _fallback(source_text: str, base: str, mappings: dict) -> tuple[str, list[str]]:
    risks: list[str] = []
    text = re.sub(
        r"^FROM\s+(?:ubuntu|debian)(?::\S+)?",
        f"FROM {base}",
        source_text,
        flags=re.M | re.I,
    )
    pattern = re.compile(
        r"apt-get\s+update\s*&&\s*apt-get\s+install\s+(?:-y\s+)?(?P<pkgs>[^;&\n\\]*(?:\\\n[^;&]*)*)",
        re.I,
    )

    def repl(match: re.Match[str]) -> str:
        raw = re.sub(r"\\\n", " ", match.group("pkgs"))
        packages = [p for p in re.split(r"\s+", raw.strip()) if p and not p.startswith("-")]
        output: list[str] = []
        for package in packages:
            mapped = mappings.get(package)
            if mapped:
                output.extend(mapped)
            else:
                output.append(package)
                risks.append(f"Unverified package mapping: {package}")
        return "dnf install -y " + " ".join(dict.fromkeys(output))

    text = pattern.sub(repl, text)
    text = text.replace("apt-get clean", "dnf clean all")
    text = text.replace("rm -rf /var/lib/apt/lists/*", "rm -rf /var/cache/dnf")
    return text, sorted(set(risks))


def migrate(repo: str | Path, source: str, config_path: str, no_ai: bool = False) -> dict:
    repo = Path(repo).resolve()
    src = (repo / source).resolve()
    cfg = load_yaml(config_path)
    mappings = load_yaml(repo / "knowledge" / "package_mappings.yaml").get("packages", {})
    destination = cfg.get("target", {}).get("dockerfile")
    dst = (repo / destination).resolve() if destination else target_path(src)
    if dst == src:
        raise ValueError("Target Dockerfile must differ from source Dockerfile")

    original = src.read_text(encoding="utf-8")
    base = cfg.get("target", {}).get(
        "base_image", "registry.access.redhat.com/ubi9/ubi:9.6"
    )
    result = None

    if not no_ai and cfg.get("ai", {}).get("enabled", True):
        try:
            prompt = (repo / "prompts" / "migrator.md").read_text(encoding="utf-8")
            payload = (
                f"Approved mappings:\n{mappings}\n"
                f"Target base: {base}\n"
                f"Source Dockerfile:\n{original}"
            )
            result = AIClient().json(prompt, payload)
        except Exception as exc:
            result = {
                "summary": "Deterministic fallback used because AI was unavailable.",
                "risks": [str(exc)],
                "dockerfile": "",
            }

    if not result or not result.get("dockerfile"):
        generated, risks = _fallback(original, base, mappings)
        result = {
            "summary": "Generated using deterministic UBI9 transformations.",
            "risks": (result or {}).get("risks", []) + risks,
            "dockerfile": generated,
        }

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(result["dockerfile"].rstrip() + "\n", encoding="utf-8")
    metadata = {
        "source": str(src.relative_to(repo)),
        "target": str(dst.relative_to(repo)),
        "summary": result.get("summary"),
        "risks": result.get("risks", []),
    }
    write_json(repo / "reports" / "migration.json", metadata)
    return metadata
