from pathlib import Path

IGNORED_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build",
}

IGNORED_FILES = {
    ".env", ".env.local", ".env.production", "secrets.toml",
    "credentials.json", "id_rsa", "id_ed25519",
}

SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


def is_ignored_path(path: Path) -> bool:
    """Return True for secrets, hidden internals, and generated folders."""
    if any(part in IGNORED_DIRS for part in path.parts):
        return True

    name = path.name.lower()
    if name in IGNORED_FILES or name.startswith(".env"):
        return True
    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        return True
    if name.startswith(".") and name != ".gitignore":
        return True
    return False

def resolve_repo_path(repo_root: str, relative_path: str) -> tuple[Path, Path]:
    """Resolve a path while preventing traversal and symlink access."""
    root = Path(repo_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError("Repository directory does not exist.")

    requested = Path(relative_path or ".")
    raw_target = requested if requested.is_absolute() else root / requested

    try:
        relative_raw = raw_target.relative_to(root)
    except ValueError:
        raise ValueError("Path is outside the repository.") from None

    current = root
    for part in relative_raw.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symbolic links are not allowed.")

    target = raw_target.resolve()
    if not target.is_relative_to(root):
        raise ValueError("Path is outside the repository.")

    if is_ignored_path(target.relative_to(root)):
        raise ValueError("This path is excluded for safety.")

    return root, target
