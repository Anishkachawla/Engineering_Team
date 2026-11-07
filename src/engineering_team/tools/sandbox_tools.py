from crewai.tools import tool
from pathlib import Path
import shutil
import subprocess
import re


SANDBOX_DIR = Path(__file__).parents[3] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


def reset_sandbox() -> None:
    """Wipe the sandbox and re-initialize it as a fresh uv project with gradio."""
    if SANDBOX_DIR.exists():
        shutil.rmtree(SANDBOX_DIR, ignore_errors=True)
    SANDBOX_DIR.mkdir(parents=True)

    subprocess.run(["uv", "init", "--bare", "--python", "3.13"], cwd=SANDBOX_DIR, check=True)
    subprocess.run(["uv", "add", "gradio"], cwd=SANDBOX_DIR, check=True)

@tool("List Sandbox Files")
def list_sandbox_files() -> str:
    """
    List the filenames currently in the sandbox directory.

    Returns:
        A newline-separated list of filenames, or a message if the
        sandbox is empty.
    """
    names = sorted(p.name for p in SANDBOX_DIR.iterdir())
    return "\n".join(names) if names else "The sandbox is empty."


@tool("Read Sandbox File")
def read_sandbox_file(filename: str) -> str:
    """
    Read and return the text contents of a file in the sandbox directory.

    Args:
        filename: The name of the file to read (e.g. "solution.py").
    Returns:
        The file's contents, or a message if the file does not exist.
    """
    path = SANDBOX_DIR / filename
    if not path.is_file():
        return f"No such file in the sandbox: {filename}"
    return path.read_text()


@tool("Write Sandbox File")
def write_sandbox_file(filename: str, content: str) -> str:
    """
    Write text to a file in the sandbox directory, replacing any existing
    file with the same name.

    Args:
        filename: The name of the file to write (e.g. "solution.py").
        content: The text content to write.
    Returns:
        A confirmation message.
    """
    path = SANDBOX_DIR / filename
    path.write_text(content)
    return f"Wrote {len(content)} characters to {filename}."


@tool("Run Sandbox Python File")
def run_sandbox_python(filename: str) -> str:
    """
    Execute a Python file from the sandbox directory inside an ephemeral
    Docker container, with the sandbox mounted as the working directory,
    using a uv run to run the code in the uv project,
    and return whatever the script printed to stdout.

    Args:
        filename: The name of the Python file to run (e.g. "solution.py").
    Returns:
        The text printed to stdout by the executed script.
    """
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{SANDBOX_DIR}:/workspace",
            "-w", "/workspace",
            "ghcr.io/astral-sh/uv:python3.13-bookworm-slim",
            "uv", "run", filename,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result.stdout

sandbox_tools = [list_sandbox_files, read_sandbox_file, write_sandbox_file, run_sandbox_python]


def _never_cache(*_args, **_kwargs) -> bool:
    return False


# Sandbox state changes between calls (files appear/change/run), so caching tool
# results would feed agents stale data. Opt out of CrewAI's default tool caching.
for _t in sandbox_tools:
    _t.cache_function = _never_cache



def _safe_sandbox_file(filename: str) -> Path:
    """Resolve a filename and ensure it stays inside the sandbox."""
    if not filename or Path(filename).name != filename:
        raise ValueError("Only filenames in the sandbox root are allowed.")

    root = SANDBOX_DIR.resolve()
    path = (root / filename).resolve()

    if path.parent != root:
        raise ValueError("Path must remain inside the sandbox root.")

    return path


@tool("Read Sandbox File Safely")
def read_sandbox_file_safely(filename: str) -> str:
    """Read a file that is located directly inside the sandbox."""
    path = _safe_sandbox_file(filename)

    if not path.is_file():
        return f"No such sandbox file: {filename}"

    return path.read_text(encoding="utf-8")


@tool("Write Test File")
def write_test_file(filename: str, content: str) -> str:
    """Write only Python unit-test files in the sandbox root."""
    path = _safe_sandbox_file(filename)

    if not re.fullmatch(r"test_[A-Za-z0-9_]+\.py", filename):
        raise ValueError(
            "The test engineer may write only files named test_*.py."
        )

    # Prevent overwriting symlinks or non-regular files.
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise ValueError("Refusing to overwrite a non-regular test file.")

    path.write_text(content, encoding="utf-8")
    return f"Wrote test file {filename} ({len(content)} characters)."


@tool("Run Backend Unit Tests")
def run_backend_unit_tests() -> str:
    """Run unittest discovery in a restricted, read-only container."""
    command = [
        "docker", "run", "--rm",
        "--network", "none",
        "--read-only",
        "--memory", "512m",
        "--cpus", "1",
        "--pids-limit", "64",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m",
        "-e", "PYTHONDONTWRITEBYTECODE=1",
        "-v", f"{SANDBOX_DIR.resolve()}:/workspace:ro",
        "-w", "/workspace",
        "ghcr.io/astral-sh/uv:python3.13-bookworm-slim",
        "python", "-B", "-m", "unittest", "discover", "-v",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "TEST_STATUS: FAIL\nReason: Unit tests exceeded 120 seconds."
    except OSError as exc:
        return f"TEST_STATUS: FAIL\nReason: Could not start Docker: {exc}"

    output = (
        f"Exit code: {result.returncode}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    if result.returncode != 0:
        return f"TEST_STATUS: FAIL\n{output}"

    return f"TEST_STATUS: PASS\n{output}"


test_agent_tools = [
    list_sandbox_files,
    read_sandbox_file_safely,
    write_test_file,
    run_backend_unit_tests,
]



MAX_VALIDATION_ATTEMPTS = 2
VALIDATION_TIMEOUT_SECONDS = 300


def _run_final_check(label: str, args: list[str]) -> dict:
    """Run a validation command with bounded execution retries."""
    attempts = []

    for attempt in range(1, MAX_VALIDATION_ATTEMPTS + 1):
        command = [
            "docker", "run", "--rm",
            "-v", f"{SANDBOX_DIR.resolve()}:/workspace",
            "-w", "/workspace",
            "ghcr.io/astral-sh/uv:python3.13-bookworm-slim",
            "uv", "run", *args,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=VALIDATION_TIMEOUT_SECONDS,
                check=False,
            )

            passed = result.returncode == 0
            details = (
                f"Exit code: {result.returncode}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

        except subprocess.TimeoutExpired as exc:
            passed = False
            details = (
                f"Timed out after {VALIDATION_TIMEOUT_SECONDS} seconds.\n"
                f"Partial stdout: {exc.stdout or ''}\n"
                f"Partial stderr: {exc.stderr or ''}"
            )

        except OSError as exc:
            passed = False
            details = f"Could not start Docker: {exc}"

        attempts.append({
            "attempt": attempt,
            "passed": passed,
            "details": details,
        })

        if passed:
            break

    return {
        "name": label,
        "passed": attempts[-1]["passed"],
        "attempts": attempts,
    }


def run_final_integration_validation() -> dict:
    """Run final UI and backend checks and write a failure report."""
    report_path = SANDBOX_DIR / "integration_summary.md"
    checks = []

    required_files = ["app.py", "_validate.py"]
    missing = [
        filename
        for filename in required_files
        if not (SANDBOX_DIR / filename).is_file()
    ]

    test_files = sorted(SANDBOX_DIR.glob("test_*.py"))

    if not test_files:
        missing.append("at least one test_*.py file")

    if missing:
        checks.append({
            "name": "Required files",
            "passed": False,
            "attempts": [{
                "attempt": 1,
                "passed": False,
                "details": "Missing: " + ", ".join(missing),
            }],
        })
    else:
        checks.append({
            "name": "Required files",
            "passed": True,
            "attempts": [{
                "attempt": 1,
                "passed": True,
                "details": "Required files and test files exist.",
            }],
        })

        # Only execute application checks when their required files exist.
        checks.append(_run_final_check(
            "Backend unit tests",
            ["python", "-m", "unittest", "discover", "-v"],
        ))

        checks.append(_run_final_check(
            "Gradio UI construction",
            ["python", "_validate.py"],
        ))

    passed = all(check["passed"] for check in checks)

    lines = [
        "# Final Integration Validation",
        "",
        f"**Overall status:** {'PASS' if passed else 'FAIL'}",
        f"**Maximum attempts per command:** {MAX_VALIDATION_ATTEMPTS}",
        "",
    ]

    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        lines.extend([
            f"## {check['name']}: {status}",
            "",
        ])

        for attempt in check["attempts"]:
            lines.extend([
                f"### Attempt {attempt['attempt']}",
                "",
                "```text",
                attempt["details"].rstrip(),
                "```",
                "",
            ])

        if not check["passed"]:
            lines.extend([
                "**Failure:** Validation did not pass within the "
                "allowed attempts.",
                "",
            ])

    lines.extend([
        "## Final decision",
        "",
        (
            "All required checks passed."
            if passed
            else
            "Integration validation failed. Do not mark this build "
            "successful. Review the failed checks and logs above, "
            "fix the underlying issue, and rerun the workflow."
        ),
        "",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "passed": passed,
        "summary_file": str(report_path),
        "checks": checks,
    }
