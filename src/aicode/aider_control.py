import subprocess
import sys
from pathlib import Path

from aicode.aider_update_result import AiderUpdateResult
from aicode.util import extract_version_string

HERE = Path(__file__).parent
AIDER_INSTALL_PATH = HERE / "aider-install"

REQUIREMENTS = ["aider-chat[playwright]", "uv"]
ACTIVATE_SCRIPT = (
    '. .venv/bin/activate && "$@"'
    if sys.platform != "win32"
    else ".venv\\Scripts\\activate.bat && %*\n"
)


def aider_fetch_update_status() -> AiderUpdateResult:
    """Fetches the update string if it exists, else returns None if up to date"""
    cp = aider_run(
        ["aider", "--just-check-update"],
        capture_output=True,
        check=False,
        universal_newlines=True,
    )
    lines = cp.stdout.strip().split("\n")
    update_available = None
    current_version = None
    latest_version = None
    for line in lines:
        if "Update available" in line:
            update_available = True
        if "Current version" in line:
            current_version = extract_version_string(line)
        if "Latest version" in line:
            latest_version = extract_version_string(line)
    if update_available is None:
        # Old way means update available when cp.returncode == 1
        update_available = cp.returncode == 1
    out = AiderUpdateResult(
        has_update=update_available,
        latest_version=latest_version if latest_version else "Unknown",
        current_version=current_version if current_version else "Unknown",
    )
    return out


def aider_installed(path: Path | None = None) -> bool:
    path = path or AIDER_INSTALL_PATH
    return (path / "installed").exists()


def aider_run(
    cmd_list: list[str], path: Path | None = None, **process_args
) -> subprocess.CompletedProcess:
    path = path or AIDER_INSTALL_PATH
    """Runs the command using the isolated environment."""
    if not aider_installed(path):
        aider_install(path)
    activate_script_path = path / "activate_script"
    if sys.platform == "win32":
        activate_script_path = path / "activate_script.bat"
    full_cmd = [str(activate_script_path)] + cmd_list
    assert activate_script_path.exists(), f"{activate_script_path} does not exist"
    cmd = subprocess.list2cmdline(full_cmd)
    cp = subprocess.run(cmd, cwd=str(path), shell=True, **process_args)
    return cp


def aider_install(path: Path | None = None) -> None:
    """Uses isolated_environment to install aider."""
    path = path or AIDER_INSTALL_PATH
    if aider_installed(path):
        return
    # Print installing message
    print("Installing aider...")
    # Install aider using isolated_environment
    path.mkdir(exist_ok=True)
    subprocess.run(["uv", "venv"], cwd=str(path), check=True)
    requirements = path / "requirements.txt"
    requirements.write_text("\n".join(REQUIREMENTS))
    activate_script_path = path / "activate_script"
    if sys.platform == "win32":
        activate_script_path = path / "activate_script.bat"
    with open(activate_script_path, "w") as f:
        f.write(ACTIVATE_SCRIPT)
    if sys.platform != "win32":
        activate_script_path.chmod(
            activate_script_path.stat().st_mode | 0o111
        )  # Make executable

    subprocess.run(
        f"{activate_script_path} uv pip install -r requirements.txt",
        cwd=str(path),
        shell=True,
        check=True,
    )

    # add a file to indicate that the installation was successful
    (path / "installed").touch()


def aider_install_path() -> str | None:
    which = "which" if not sys.platform == "win32" else "where"
    if not aider_installed():
        return None
    cp = aider_run([which, "aider"], check=True, capture_output=True)
    return cp.stdout.strip()


def aider_upgrade() -> int:
    print("Upgrading aider...")

    if not aider_installed():
        aider_install()
        return 0
    cp = aider_run(["aider", "--upgrade"], check=True, path=AIDER_INSTALL_PATH)
    return cp.returncode
