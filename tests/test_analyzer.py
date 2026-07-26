from pathlib import Path

from ubi9_agent.analyzer import analyze


def test_analyze(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text(
        "FROM ubuntu:22.04\nRUN apt-get update && apt-get install -y curl\n"
    )
    result = analyze(tmp_path, "Dockerfile")
    assert result["selected_dockerfile"] == "Dockerfile"
    assert "apt-get" in result["package_managers"]
