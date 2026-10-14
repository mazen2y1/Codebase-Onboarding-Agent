from tools.common import resolve_repo_path

MAX_LINES = 500
MAX_FILE_BYTES = 2_000_000
def read_file(
    repo_root: str,
    path: str,
    start_line: int = 1,
    end_line: int | None = None,
) -> dict:
    """Read a repository text file or an inclusive range of 1-based line numbers."""
    root, target = resolve_repo_path(repo_root, path)

    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not target.is_file():
        raise IsADirectoryError(f"Not a file: {path}")
    if start_line < 1:
        raise ValueError("Error")
    if end_line is not None and end_line < start_line:
        raise ValueError("Error")
    if target.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Error")

    try:
        lines = target.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        raise ValueError("Error") from None

    total_lines = len(lines)
    if total_lines and start_line > total_lines:
        raise ValueError(f"Error")

    if total_lines == 0:
        actual_end = 0
        selected = []
    else:
        requested_end = total_lines if end_line is None else min(end_line, total_lines)
        actual_end = min(requested_end, start_line + MAX_LINES - 1)
        selected = lines[start_line - 1:actual_end]

    numbered = [f"{number}: {line}" for number, line in enumerate(selected, start=start_line)]
    return {
        "path": target.relative_to(root).as_posix(),
        "start_line": start_line,
        "end_line": actual_end,
        "total_lines": total_lines,
        "content": "\n".join(numbered),
    }
