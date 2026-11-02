"""Tests for scripts/deploy-hostinger.sh masking, health, rollback, and timeouts."""

from __future__ import annotations

import os
import re
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "deploy-hostinger.sh"
DOCKER_PUBLISH = REPO_ROOT / ".github" / "workflows" / "docker-publish.yml"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

SECRET_VALUE = "s3cr3t-value-SHOULD-NOT-LEAK"
TOKEN_VALUE = "tok_SHOULD-NOT-LEAK"
KEY_VALUE = "key_SHOULD-NOT-LEAK"
PASSWORD_VALUE = "pw_SHOULD-NOT-LEAK"
URI_VALUE = "postgres://mask:uri@db/app"
URL_VALUE = "postgres://mask:url@db/app"
DSN_VALUE = "https://sentry.example/dsn-SHOULD-NOT-LEAK"
NORMAL_VALUE = "perfectly-visible-normal"
OLD_IMAGE = "ghcr.io/elizio/vanilla-webapp-framework:sha-oldimage"
NEW_SHA = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
NEW_IMAGE = f"ghcr.io/elizio/vanilla-webapp-framework:sha-{NEW_SHA}"
APP_URL = "https://dsfor.fun/vanilla-webapp-framework"

CURL_STUB = r'''#!/usr/bin/env bash
# Test-only curl stand-in. Never contacts the network.
set -euo pipefail
log="${CURL_STUB_LOG:?}"
out_file=""
write_fmt=""
method="GET"
data=""
url=""
connect_timeout=""
max_time=""

args=("$@")
i=0
while [ "$i" -lt "${#args[@]}" ]; do
  arg="${args[$i]}"
  case "$arg" in
    -o|--output)
      i=$((i + 1))
      out_file="${args[$i]}"
      ;;
    -w|--write-out)
      i=$((i + 1))
      write_fmt="${args[$i]}"
      ;;
    -X)
      i=$((i + 1))
      method="${args[$i]}"
      ;;
    -d|--data|--data-raw)
      i=$((i + 1))
      data="${args[$i]}"
      ;;
    -H|--header)
      i=$((i + 1))
      ;;
    --connect-timeout)
      i=$((i + 1))
      connect_timeout="${args[$i]}"
      ;;
    --max-time)
      i=$((i + 1))
      max_time="${args[$i]}"
      ;;
    -s|-S|-sS|-f|--fail|-sf|-sSf|-sfs) ;;
    http://*|https://*)
      url="$arg"
      ;;
  esac
  i=$((i + 1))
done

body=""
code="200"
if [ -z "$url" ]; then
  echo "curl-stub: missing url" >&2
  exit 1
fi

# Record every call so tests can assert deploy vs rollback and timeouts.
{
  printf 'method=%s url=%s connect_timeout=%s max_time=%s\n' \
    "$method" "$url" "$connect_timeout" "$max_time"
  if [ -n "$data" ]; then
    printf 'data=%s\n' "$data"
  fi
  printf '%s\n' '---'
} >> "$log"

if [[ "$url" == *"/docker/dsfor" && "$method" == "GET" ]]; then
  body="$(cat "${CURL_STUB_PROJECT:?}")"
elif [[ "$url" == *"/virtual-machines/1136636/docker" && "$method" == "POST" ]]; then
  body='{"id":"act-deploy-1"}'
  if [[ "$data" == *'"environment"'* && "$data" == *"sha-oldimage"* ]]; then
    printf 'rollback\n' >> "${CURL_STUB_ROLLBACK:?}"
    body='{"id":"act-rollback-1"}'
  fi
elif [[ "$url" == *"/actions/"* ]]; then
  body='{"state":"success"}'
elif [[ "$url" == *"/api/health"* ]]; then
  if [ "${CURL_STUB_HEALTH_MODE:-match}" = "timeout" ]; then
    if [ -n "$out_file" ]; then
      : > "$out_file"
    fi
    if [ -n "$write_fmt" ]; then
      printf '000'
    fi
    echo "curl: (28) Operation timed out after 30000 milliseconds" >&2
    exit 28
  elif [ "${CURL_STUB_HEALTH_MODE:-match}" = "mismatch" ]; then
    body='{"status":"ok","version":"not-the-expected-sha"}'
  else
    body="$(printf '{"status":"ok","version":"%s"}' "${GITHUB_SHA:?}")"
  fi
elif [[ "$url" == "${APP_URL}/" || "$url" == "${APP_URL}" ]]; then
  body="ok"
else
  echo "curl-stub: unexpected url $url" >&2
  code="404"
  body='{"error":"unexpected"}'
fi

if [ -n "$out_file" ]; then
  printf '%s' "$body" > "$out_file"
else
  printf '%s' "$body"
fi

if [ -n "$write_fmt" ]; then
  # The deploy script only asks for %{http_code}.
  printf '%s' "$code"
fi

if [ "$code" != "200" ] && [ "$code" != "201" ]; then
  exit 22
fi
exit 0
'''

SLEEP_STUB = '''#!/usr/bin/env bash
# Instant sleep so the 36-attempt health loop is testable.
exit 0
'''


def _project_payload(image_var: str = "VWF_IMAGE") -> str:
    """Return a Hostinger GET-project JSON body with mixed secret keys."""
    environment = "\n".join(
        [
            f"{image_var}={OLD_IMAGE}",
            f'FLASK_SECRET="{SECRET_VALUE}"',
            f"HOSTINGER_LIKE_TOKEN={TOKEN_VALUE}",
            f"API_KEY={KEY_VALUE}",
            f"DB_PASSWORD={PASSWORD_VALUE}",
            f"DATABASE_URI={URI_VALUE}",
            f"DATABASE_URL={URL_VALUE}",
            f"SENTRY_DSN={DSN_VALUE}",
            f"NORMAL_FLAG={NORMAL_VALUE}",
            "EMPTY_SECRET=",
        ]
    )
    return subprocess.check_output(
        [
            "jq",
            "-n",
            "--arg",
            "content",
            "services: {}\n",
            "--arg",
            "env",
            environment,
            '{"content":$content,"environment":$env}',
        ],
        text=True,
    )


def _write_executable(path: Path, contents: str) -> None:
    """Write *contents* to *path* and mark the file executable."""
    path.write_text(contents)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def _base_env(
    tmp_path: Path, health_mode: str, image_var: str = "VWF_IMAGE"
) -> dict[str, str]:
    """Build the environment the deploy script expects in CI."""
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    _write_executable(stub_dir / "curl", CURL_STUB)
    _write_executable(stub_dir / "sleep", SLEEP_STUB)

    project_file = tmp_path / "project.json"
    project_file.write_text(_project_payload(image_var=image_var))
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{stub_dir}{os.pathsep}{env.get('PATH', '')}",
            "HOSTINGER_API_TOKEN": "test-hostinger-token",
            "VM_ID": "1136636",
            "PROJECT_NAME": "dsfor",
            "NEW_IMAGE": NEW_IMAGE,
            "APP_URL": APP_URL,
            "GITHUB_SHA": NEW_SHA,
            "RUNNER_TEMP": str(tmp_path / "runner"),
            "CURL_STUB_LOG": str(tmp_path / "curl.log"),
            "CURL_STUB_PROJECT": str(project_file),
            "CURL_STUB_ROLLBACK": str(tmp_path / "rollback.log"),
            "CURL_STUB_HEALTH_MODE": health_mode,
        }
    )
    (tmp_path / "runner").mkdir()
    return env


def _run_script(
    tmp_path: Path,
    health_mode: str = "match",
    *,
    image_var: str = "VWF_IMAGE",
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run the deploy script with a stubbed curl and sleep."""
    env = _base_env(tmp_path, health_mode, image_var=image_var)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _source_emit_masks(env_text: str) -> str:
    """Source the deploy script and run emit_masks on *env_text*."""
    result = subprocess.run(
        ["bash", "-c", 'source "$SCRIPT" && emit_masks "$ENV_TEXT"'],
        cwd=str(REPO_ROOT),
        env={**os.environ, "SCRIPT": str(SCRIPT), "ENV_TEXT": env_text},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_deploy_script_exists() -> None:
    """The Hostinger deploy job is a repo script, not inline workflow bash."""
    assert SCRIPT.is_file()


def test_no_set_x_or_echo_secret_patterns() -> None:
    """A reverted `echo` of a secret or `set -x` must fail this test."""
    text = SCRIPT.read_text()
    assert "set -x" not in text
    assert "set -o xtrace" not in text
    assert "set +x" not in text
    leaking = re.compile(
        r"echo\s+.*\$(?:\{)?(?:"
        r"HOSTINGER_API_TOKEN|SECRET|TOKEN|PASSWORD|"
        r"JWT_SECRET|FLASK_SECRET|DATABASE_URI)",
        re.IGNORECASE,
    )
    assert leaking.search(text) is None


def test_emit_masks_covers_secret_like_keys_including_url_and_dsn() -> None:
    """emit_masks adds ::add-mask:: for SECRET, TOKEN, KEY, PASSWORD, URI, URL, DSN."""
    env_text = "\n".join(
        [
            f'TEST_SECRET="{SECRET_VALUE}"',
            f"TEST_TOKEN={TOKEN_VALUE}",
            f"TEST_API_KEY={KEY_VALUE}",
            f"TEST_PASSWORD={PASSWORD_VALUE}",
            f"TEST_DATABASE_URI={URI_VALUE}",
            f"TEST_DATABASE_URL={URL_VALUE}",
            f'TEST_DSN="{DSN_VALUE}"',
            f"NORMAL_VAR={NORMAL_VALUE}",
            "COMMENTED_SECRET=ignored",
        ]
    )
    # The commented line is a real assignment here; add a true comment too.
    env_text = "# IGNORE_SECRET=not-masked\n" + env_text.replace(
        "COMMENTED_SECRET=ignored", "# COMMENTED_SECRET=ignored"
    )

    output = _source_emit_masks(env_text)
    masks = [
        line.split("::add-mask::", 1)[1]
        for line in output.splitlines()
        if line.startswith("::add-mask::")
    ]

    assert f'"{SECRET_VALUE}"' in masks
    assert SECRET_VALUE in masks
    assert TOKEN_VALUE in masks
    assert KEY_VALUE in masks
    assert PASSWORD_VALUE in masks
    assert URI_VALUE in masks
    assert URL_VALUE in masks
    assert f'"{DSN_VALUE}"' in masks
    assert DSN_VALUE in masks
    assert NORMAL_VALUE not in masks
    assert "ignored" not in masks
    assert "not-masked" not in masks


def test_emit_masks_is_selective_for_non_secret_keys() -> None:
    """Keys that do not look like secrets stay unmasked."""
    env_text = "\n".join(
        [
            f"NORMAL_VAR={NORMAL_VALUE}",
            "APP_PROFILE=production",
            "PORT=5000",
            "VWF_IMAGE=ghcr.io/example/app:tag",
            "EMPTY_SECRET=",
        ]
    )
    output = _source_emit_masks(env_text)
    assert "::add-mask::" not in output
    assert NORMAL_VALUE not in output
    assert "production" not in output
    assert "5000" not in output
    assert "ghcr.io/example/app:tag" not in output


def test_image_var_defaults_to_vwf_image(tmp_path: Path) -> None:
    """Unset IMAGE_VAR retags VWF_IMAGE so existing Hostinger deploys stay unchanged."""
    result = _run_script(tmp_path, health_mode="match")
    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    log = (tmp_path / "curl.log").read_text()
    assert f"VWF_IMAGE={NEW_IMAGE}" in log
    leaked = _secret_leaks(combined)
    assert leaked == [], leaked


def test_image_var_override_retags_custom_key(tmp_path: Path) -> None:
    """IMAGE_VAR selects which project env key the script rewrites."""
    result = _run_script(
        tmp_path,
        health_mode="match",
        image_var="GB_IMAGE",
        extra_env={"IMAGE_VAR": "GB_IMAGE"},
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    log = (tmp_path / "curl.log").read_text()
    assert f"GB_IMAGE={NEW_IMAGE}" in log
    assert "VWF_IMAGE=" not in log
    leaked = _secret_leaks(combined)
    assert leaked == [], leaked


def test_image_var_rejects_unsafe_identifier(tmp_path: Path) -> None:
    """IMAGE_VAR must be a safe shell identifier before any Hostinger call."""
    env = _base_env(tmp_path, "match")
    env["IMAGE_VAR"] = "VWF_IMAGE;rm"
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 1, combined
    assert "IMAGE_VAR" in combined
    assert not (tmp_path / "curl.log").exists()
    leaked = _secret_leaks(combined)
    assert leaked == [], leaked


def test_health_match_does_not_rollback(tmp_path: Path) -> None:
    """A health version equal to github.sha completes without a rollback POST."""
    result = _run_script(tmp_path, health_mode="match")
    combined = result.stdout + result.stderr
    assert result.returncode == 0, combined
    assert "Deployment completed successfully" in result.stdout
    assert "Health check passed" in result.stdout
    assert "Rolling back to previous image" not in combined
    assert not (tmp_path / "rollback.log").exists()

    leaked = _secret_leaks(combined)
    assert leaked == [], leaked
    _assert_logged_curl_timeouts((tmp_path / "curl.log").read_text())


def test_health_mismatch_triggers_rollback(tmp_path: Path) -> None:
    """A version mismatch exhausts the health loop and POSTs the old environment."""
    result = _run_script(tmp_path, health_mode="mismatch")
    combined = result.stdout + result.stderr
    assert result.returncode == 1, combined
    assert "Health check failed" in combined
    assert "Rolling back to previous image" in combined
    assert (tmp_path / "rollback.log").exists()

    log = (tmp_path / "curl.log").read_text()
    assert "/virtual-machines/1136636/docker/dsfor" in log
    assert log.count("method=POST url=") >= 2
    assert OLD_IMAGE in log
    assert NEW_IMAGE in log

    leaked = _secret_leaks(combined)
    assert leaked == [], leaked
    _assert_logged_curl_timeouts((tmp_path / "curl.log").read_text())


def test_missing_token_fails_without_calling_hostinger(tmp_path: Path) -> None:
    """An empty HOSTINGER_API_TOKEN exits before any Hostinger URL is touched."""
    env = _base_env(tmp_path, "match")
    env["HOSTINGER_API_TOKEN"] = ""
    result = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "HOSTINGER_API_TOKEN" in result.stdout + result.stderr
    assert not (tmp_path / "curl.log").exists()


def test_workflow_calls_script_with_same_inputs() -> None:
    """The deploy job checks out github.sha and calls the script, not inline bash."""
    text = DOCKER_PUBLISH.read_text()
    assert "scripts/deploy-hostinger.sh" in text
    assert "VM_ID: 1136636" in text
    assert "PROJECT_NAME: dsfor" in text
    image_line = (
        "NEW_IMAGE: ghcr.io/elizio/vanilla-webapp-framework:sha-${{ github.sha }}"
    )
    assert image_line in text
    assert "APP_URL: https://dsfor.fun/vanilla-webapp-framework" in text
    assert "HOSTINGER_API_TOKEN: ${{ secrets.HOSTINGER_API_TOKEN }}" in text
    assert "ref: ${{ github.sha }}" in text
    # No leftover multi-line Hostinger bash in the workflow.
    assert "emit_masks()" not in text
    assert "poll_action()" not in text
    assert "developers.hostinger.com" not in text


def test_actions_are_sha_pinned() -> None:
    """Every external uses: pin is a full 40-char SHA; local ./ workflows are exempt."""
    unpinned: list[str] = []
    for path in sorted(WORKFLOWS_DIR.glob("*.yml")):
        for line_no, line in enumerate(path.read_text().splitlines(), start=1):
            stripped = line.lstrip()
            if not stripped.startswith("uses:") and not stripped.startswith("- uses:"):
                continue
            if re.search(r"uses:\s+\./", line):
                continue
            if not re.search(r"@[0-9a-f]{40}\b", line):
                unpinned.append(f"{path.name}:{line_no}:{line.strip()}")
    assert unpinned == []


def test_build_and_push_smokes_loaded_image_before_push() -> None:
    """build-and-push loads the image, smokes it, then pushes only off PRs.

    The deploy job is unchanged: it still waits on ``build-and-push`` and
    still calls ``scripts/deploy-hostinger.sh``.
    """
    text = DOCKER_PUBLISH.read_text()
    build_block = text.split("build-and-push:")[1].split("\n  deploy:")[0]
    deploy_block = text.split("\n  deploy:")[1]
    assert "load: true" in build_block
    assert "make smoke" in build_block
    smoke_at = build_block.index("make smoke")
    assert "docker push" in build_block[smoke_at:]
    assert "github.event_name != 'pull_request'" in build_block
    assert "push: false" in build_block or "push: 'false'" in build_block
    assert "FLASK_SECRET" in Path(REPO_ROOT / "scripts" / "smoke-image.sh").read_text()
    assert "scripts/deploy-hostinger.sh" in deploy_block
    assert "make smoke" not in deploy_block


def test_packages_write_only_on_build_and_push() -> None:
    """packages: write is limited to the build-and-push job."""
    text = DOCKER_PUBLISH.read_text()
    assert re.search(r"^permissions:\n  contents: read\n", text, re.MULTILINE)
    assert not re.search(
        r"^permissions:\n  contents: read\n  packages: write", text, re.MULTILINE
    )
    build_block = text.split("build-and-push:")[1].split("\n  deploy:")[0]
    assert "packages: write" in build_block
    deploy_block = text.split("\n  deploy:")[1]
    assert "packages: write" not in deploy_block
    ci_block = text.split("\n  ci:")[1].split("build-and-push:")[0]
    assert "contents: read" in ci_block
    assert "packages: write" not in ci_block
    assert "packages: write" not in CI_WORKFLOW.read_text()


def _curl_invocations(script: str) -> list[str]:
    """Return each ``curl`` command, joining bash line continuations.

    Matches the ``curl`` command word only (not helper names like
    ``curl_timed``). Comment-only tails are stripped.
    """
    invocations: list[str] = []
    current: list[str] = []
    continuing = False
    for raw in script.splitlines():
        code = raw.split("#", 1)[0].rstrip()
        if continuing:
            current.append(code.rstrip("\\").strip())
            continuing = code.endswith("\\")
            if not continuing:
                invocations.append(" ".join(part for part in current if part))
                current = []
            continue
        if re.search(r"(?:^|[`$;(]|\s)curl(?:\s|$)", code):
            current = [code.rstrip("\\").strip()]
            if code.endswith("\\"):
                continuing = True
            else:
                invocations.append(current[0])
                current = []
    assert not continuing, "unterminated curl line continuation"
    return invocations


def _assert_logged_curl_timeouts(log: str) -> None:
    """Assert every stubbed curl call received connect and max-time flags."""
    calls = [
        line
        for line in log.splitlines()
        if line.startswith("method=") and "url=" in line
    ]
    assert calls, "expected at least one stubbed curl call"
    for line in calls:
        match = re.search(
            r"connect_timeout=(\S*) max_time=(\S*)",
            line,
        )
        assert match, f"missing timeout fields: {line}"
        connect, max_time = match.group(1), match.group(2)
        assert connect == "10", f"connect-timeout: {line}"
        assert max_time.isdigit() and int(max_time) >= 30, f"max-time: {line}"


def test_every_curl_in_script_has_timeout_flags() -> None:
    """Every curl in the deploy script carries connect and max-time flags."""
    invocations = _curl_invocations(SCRIPT.read_text())
    assert invocations, "expected at least one curl invocation"
    missing = [
        inv
        for inv in invocations
        if "--connect-timeout" not in inv or "--max-time" not in inv
    ]
    assert missing == [], missing


def test_health_timeout_retries_then_rolls_back(tmp_path: Path) -> None:
    """A health-check curl timeout is 'not healthy yet', then rollback runs.

    Under ``set -e``, a timed-out curl (exit 28) must not abort the 36x5s
    loop; otherwise rollback never runs.
    """
    result = _run_script(tmp_path, health_mode="timeout")
    combined = result.stdout + result.stderr
    assert result.returncode == 1, combined
    assert "Health check failed" in combined
    assert "Rolling back to previous image" in combined
    assert (tmp_path / "rollback.log").exists()

    log = (tmp_path / "curl.log").read_text()
    health_calls = log.count("/api/health")
    assert health_calls >= 36, f"health loop aborted early ({health_calls} calls)"
    _assert_logged_curl_timeouts(log)

    leaked = _secret_leaks(combined)
    assert leaked == [], leaked


def test_deploy_job_only_has_timeout_minutes() -> None:
    """Only the deploy job is capped at 15 minutes."""
    text = DOCKER_PUBLISH.read_text()
    ci_block = text.split("\n  ci:")[1].split("build-and-push:")[0]
    build_block = text.split("build-and-push:")[1].split("\n  deploy:")[0]
    deploy_block = text.split("\n  deploy:")[1]
    assert "timeout-minutes" not in ci_block
    assert "timeout-minutes" not in build_block
    assert re.search(r"^    timeout-minutes: 15\s*$", deploy_block, re.MULTILINE)


def _secret_leaks(combined: str) -> list[str]:
    """Return secret values that appear outside ::add-mask:: lines."""
    leaked: list[str] = []
    secrets = (
        SECRET_VALUE,
        TOKEN_VALUE,
        KEY_VALUE,
        PASSWORD_VALUE,
        URI_VALUE,
        URL_VALUE,
        DSN_VALUE,
    )
    for line in combined.splitlines():
        if "::add-mask::" in line:
            continue
        for secret in secrets:
            if secret in line:
                leaked.append(line)
                break
    return leaked
