You are analyzing a failed UBI9 container build. Use only evidence from the Dockerfile and build log.
Return JSON only with keys:
category, root_cause, evidence, risk, auto_fix_allowed, proposed_dockerfile, notes.
Set proposed_dockerfile to the complete corrected Dockerfile only when the fix is low risk. Otherwise return an empty string.
Never assume a tool is missing unless the log explicitly says it is not found.
