#!/usr/bin/env bash
# Smoke-test a locally loaded production image before it is pushed.
# Requires IMAGE (docker ref). Does not change deploy-hostinger.sh.
set -euo pipefail

IMAGE="${IMAGE:?set IMAGE to the locally loaded docker image ref}"
PORT="${SMOKE_PORT:-18080}"
NAME="${SMOKE_NAME:-vwf-smoke-$$}"
TIMEOUT="${SMOKE_TIMEOUT:-90}"

cleanup() {
    docker rm -f "$NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d --name "$NAME" \
    -e FLASK_SECRET=ci-smoke-flask-secret \
    -e JWT_SECRET=ci-smoke-jwt-secret \
    -e DATABASE_URI=sqlite:////tmp/smoke.db \
    -e APP_PROFILE=production \
    -p "127.0.0.1:${PORT}:5000" \
    "$IMAGE"

deadline=$((SECONDS + TIMEOUT))
ok=0
body=""
while ((SECONDS < deadline)); do
    if body="$(curl -sf "http://127.0.0.1:${PORT}/api/health" 2>/dev/null)"; then
        if printf '%s' "$body" | python3 -c \
            'import json,sys; d=json.load(sys.stdin); raise SystemExit(0 if d.get("status")=="ok" else 1)'; then
            ok=1
            break
        fi
    fi
    sleep 2
done

if [[ "$ok" -ne 1 ]]; then
    echo "error: container never became healthy (last body: ${body:-<empty>})" >&2
    docker logs "$NAME" >&2 || true
    exit 1
fi

code="$(curl -sf -o /dev/null -w '%{http_code}' "http://127.0.0.1:${PORT}/")"
if [[ "$code" != "200" ]]; then
    echo "error: GET / returned HTTP ${code}" >&2
    docker logs "$NAME" >&2 || true
    exit 1
fi

echo "smoke ok: /api/health status=ok and GET / returned 200"
