# UBI9 Migration Platform

This framework analyzes a repository, selects a source Dockerfile, creates a **separate** UBI9 Dockerfile, builds it for `linux/amd64`, performs smoke tests, analyzes failed build logs, applies only policy-approved low-risk fixes, produces Levels 1–3 evidence, and can open a pull request.

## Important behavior

- The source Dockerfile is preserved.
- The generated target defaults to `<source>.ubi9`.
- AI is used for migration reasoning and failure diagnosis.
- Deterministic package mappings and policy checks remain the safety boundary.
- High-risk changes are reported rather than automatically applied.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Local run

```bash
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-5"

ubi9-agent analyze --repo . --source docker/Dockerfile.cpu
ubi9-agent migrate --repo . --source docker/Dockerfile.cpu

docker build --platform linux/amd64   -f docker/Dockerfile.cpu.ubi9   -t my-app:ubi9 . 2>&1 | tee build.log

scripts/smoke_test.sh my-app:ubi9
ubi9-agent report --repo .
```

To test without an API key:

```bash
ubi9-agent migrate --repo . --source Dockerfile --no-ai
```

## GitHub configuration

Add repository secret:

- `OPENAI_API_KEY`

Add repository variable:

- `OPENAI_MODEL`

Optional for automated branch pushes and PR creation:

- `AGENT_PUSH_TOKEN`

For initial adoption, run only `ubi9-migrate-build.yml` and review the generated artifact manually. Enable `ubi9-failure-agent.yml` after branch protection, token permissions, and the policy file have been reviewed.

## Workflow

```text
Analyze repository
  -> generate Dockerfile.ubi9
  -> build linux/amd64 image
  -> smoke test
  -> report
  -> on failure: analyze logs
  -> apply only low-risk policy-approved fix
  -> open PR
```

## Current limitations

The deterministic fallback handles straightforward Debian package installation blocks. Complex shell scripts, external repositories, compiler toolchains, multi-architecture logic, and application source modifications require AI or human review. A successful image build does not by itself prove application correctness; add application-specific smoke tests to `config/ubi9-migration.yaml`.
