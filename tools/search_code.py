import os
from pathlib import Path
from tools.common import IGNORED_DIRS, is_ignored_path, resolve_repo_path

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".c",
    ".h", ".hpp", ".cs", ".go", ".rs", ".php", ".rb", ".html",
    ".css", ".sql", ".json", ".yaml", ".yml", ".toml", ".md", ".txt",
    ".ipynb", ".sh", ".bat", ".ps1", ".xml", ".ini", ".cfg",
}
MAX_FILE_BYTES = 2_000_000
def search_code(
    repo_root: str,
    query: str,
    path: str = ".",
    mode: str = "text",
    max_results: int = 50,
) -> list[dict]:
    """Search source files for a case-insensitive text match and return exact line numbers."""
    if not query or not query.strip():
        raise ValueError("Error")
    if mode != "text":
        raise ValueError("Error")
    if not 1 <= max_results <= 200:
        raise ValueError("must be between 1 and 200.")

    root, target = resolve_repo_path(repo_root, path)
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not target.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    results = []
    query_folded = query.casefold()

    for current, dirs, files in os.walk(target, topdown=True, followlinks=False):
        current_path = Path(current)
        dirs[:] = [
            name for name in dirs
            if name not in IGNORED_DIRS
            and not (current_path / name).is_symlink()
            and not is_ignored_path((current_path / name).relative_to(root))
        ]

        for name in sorted(files):
            file_path = current_path / name
            if file_path.is_symlink() or is_ignored_path(file_path.relative_to(root)):
                continue
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            try:
                if file_path.stat().st_size > MAX_FILE_BYTES:
                    continue
                lines = file_path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue

            for line_number, line in enumerate(lines, start=1):
                if query_folded in line.casefold():
                    results.append({
                        "path": file_path.relative_to(root).as_posix(),
                        "line": line_number,
                        "text": line.strip(),
                    })
                    if len(results) >= max_results:
                        return results
    return results