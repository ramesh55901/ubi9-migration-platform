from __future__ import annotations
import re
from pathlib import Path
from .util import write_json

IGNORE={".git","node_modules","vendor",".venv","venv","dist","build"}

def find_dockerfiles(repo: Path) -> list[Path]:
    files=[]
    for p in repo.rglob("*"):
        if any(part in IGNORE for part in p.parts): continue
        if p.is_file() and (p.name == "Dockerfile" or p.name.startswith("Dockerfile.")) and not p.name.endswith(".ubi9"):
            files.append(p)
    return sorted(files)

def analyze(repo: str | Path, source: str | None = None) -> dict:
    repo=Path(repo).resolve()
    dockerfiles=find_dockerfiles(repo)
    selected=(repo/source).resolve() if source else (dockerfiles[0] if len(dockerfiles)==1 else None)
    text=selected.read_text(errors="replace") if selected else ""
    from_images=re.findall(r"^FROM\s+(?:--platform=\S+\s+)?(\S+)", text, flags=re.M|re.I)
    managers=[]
    for token in ("apt-get","apt ","apk ","yum ","dnf ","microdnf"):
        if token in text: managers.append(token.strip())
    languages=[]
    indicators={"python":["requirements.txt","pyproject.toml","setup.py"],"go":["go.mod"],"node":["package.json"],"rust":["Cargo.toml"],"java":["pom.xml","build.gradle"]}
    for lang,names in indicators.items():
        if any((repo/n).exists() for n in names): languages.append(lang)
    result={
      "repository": str(repo),
      "dockerfiles": [str(p.relative_to(repo)) for p in dockerfiles],
      "selected_dockerfile": str(selected.relative_to(repo)) if selected else None,
      "base_images": from_images,
      "package_managers": sorted(set(managers)),
      "languages": languages,
      "build_stages": len(from_images),
      "requires_selection": selected is None,
    }
    write_json(repo/"reports"/"analysis.json", result)
    return result
