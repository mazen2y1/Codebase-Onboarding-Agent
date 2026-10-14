import os
from pathlib import Path
from tools.common import IGNORED_DIRS, is_ignored_path, resolve_repo_path
MAX_ENTRIES = 2000

def list_files(
    repo_root: str,
    path: str = ".",
    recursive: bool = False,
) -> list[dict]:
    """List files and directories in a repository, excluding secrets and generated folders."""
    root, target = resolve_repo_path(repo_root, path)
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not target.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    results = []

    if not recursive:
        candidates = target.iterdir()
        for item in candidates:
            if item.is_symlink() or is_ignored_path(item.relative_to(root)):
                continue
            results.append({
                "path": item.relative_to(root).as_posix(),
                "type": "directory" if item.is_dir() else "file",
            })
            if len(results) >= MAX_ENTRIES:
                break
    else:
        for current, dirs, files in os.walk(target, topdown=True, followlinks=False):
            current_path = Path(current)
            dirs[:] = [
                name for name in dirs
                if name not in IGNORED_DIRS
                and not (current_path / name).is_symlink()
                and not is_ignored_path((current_path / name).relative_to(root))
            ]

            for name in sorted(dirs):
                item = current_path / name
                results.append({"path": item.relative_to(root).as_posix(), "type": "directory"})
                if len(results) >= MAX_ENTRIES:
                    break
            if len(results) >= MAX_ENTRIES:
                break

            for name in sorted(files):
                item = current_path / name
                if item.is_symlink() or is_ignored_path(item.relative_to(root)):
                    continue
                results.append({"path": item.relative_to(root).as_posix(), "type": "file"})
                if len(results) >= MAX_ENTRIES:
                    break
            if len(results) >= MAX_ENTRIES:
                break

    return sorted(results, key=lambda item: (item["type"] != "directory", item["path"]))
