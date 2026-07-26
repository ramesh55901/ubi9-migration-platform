#!/usr/bin/env bash
set -Eeuo pipefail
IMAGE="${1:?Usage: smoke_test.sh IMAGE}"
ARCH="$(docker image inspect "$IMAGE" --format '{{.Architecture}}')"
[[ "$ARCH" == "amd64" ]] || { echo "Expected amd64, got $ARCH"; exit 1; }
docker run --rm --entrypoint /bin/sh "$IMAGE" -c 'cat /etc/redhat-release && uname -m'
