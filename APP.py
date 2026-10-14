import io
import re
import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlparse
import requests
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
MAX_EXTRACTED_BYTES = 150 * 1024 * 1024
MAX_SINGLE_FILE_BYTES = 25 * 1024 * 1024

def _safe_archive_path(name: str) -> PurePosixPath | None:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts or (path.parts and ":" in path.parts[0]):
        return None
    if not path.parts:
        return None
    lowered = [part.lower() for part in path.parts]
    if any(part == ".git" or part == "node_modules" or part in {".venv", "venv", "__pycache__"} for part in lowered):
        return None
    filename = path.name.lower()
    if filename.startswith(".env") or filename in {"secrets.toml", "credentials.json", "id_rsa", "id_ed25519"}:
        return None
    if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
        return None
    return path

def _extract_zip_bytes(data: bytes, display_name: str) -> tuple[str, str]:
    if len(data) > MAX_ARCHIVE_BYTES:
        raise ValueError("too large")

    temp_dir = Path(tempfile.mkdtemp(prefix="codebase_repo_"))
    destination = temp_dir / "repository"
    destination.mkdir()
    total_size = 0

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            for member in members:
                safe_path = _safe_archive_path(member.filename)
                if safe_path is None or member.is_dir():
                    continue
                if member.file_size > MAX_SINGLE_FILE_BYTES:
                    continue
                total_size += member.file_size
                if total_size > MAX_EXTRACTED_BYTES:
                    raise ValueError("too large")

                output_path = (destination / Path(*safe_path.parts)).resolve()
                if not output_path.is_relative_to(destination.resolve()):
                    continue
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, output_path.open("wb") as target:
                    shutil.copyfileobj(source, target)

        children = list(destination.iterdir())
        repo_root = children[0] if len(children) == 1 and children[0].is_dir() else destination
        if not any(repo_root.iterdir()):
            raise ValueError("Error")
        return str(repo_root), display_name
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

def load_uploaded_zip(uploaded_file) -> tuple[str, str]:
    """Safely extract a Streamlit uploaded ZIP file."""
    return _extract_zip_bytes(uploaded_file.getvalue(), uploaded_file.name)


def load_github_repo(repo_url: str) -> tuple[str, str]:
    """Download a public GitHub repository ZIP without requiring git on the server."""
    parsed = urlparse(repo_url.strip())
    if parsed.scheme not in {"https", "http"} or parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Enter a public GitHub URL such as https://github.com/owner/repository.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ValueError("Error")
    owner, repo = parts[0], re.sub(r"\.git$", "", parts[1])
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner) or not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
        raise ValueError("Error")

    headers = {"User-Agent": "Codebase-Onboarding-Agent"}
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url, headers=headers, timeout=20)
    if response.status_code == 404:
        raise ValueError("Error")
    response.raise_for_status()
    info = response.json()
    branch = info.get("default_branch")
    if not branch:
        raise ValueError("Error")

    archive_url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{quote(branch, safe='')}"
    archive_response = requests.get(archive_url, headers=headers, timeout=60)
    archive_response.raise_for_status()
    if len(archive_response.content) > MAX_ARCHIVE_BYTES:
        raise ValueError("The repository ZIP is too large (maximum 100 MB).")
    return _extract_zip_bytes(archive_response.content, f"{owner}/{repo}")
