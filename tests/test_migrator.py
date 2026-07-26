from ubi9_agent.migrator import _fallback


def test_fallback_mapping():
    out, risks = _fallback(
        "FROM ubuntu:22.04\nRUN apt-get update && apt-get install -y build-essential libssl-dev\n",
        "ubi9",
        {
            "build-essential": ["gcc", "gcc-c++", "make"],
            "libssl-dev": ["openssl-devel"],
        },
    )
    assert "FROM ubi9" in out
    assert "gcc-c++" in out
    assert "openssl-devel" in out
    assert not risks
