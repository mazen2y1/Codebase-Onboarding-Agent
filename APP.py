import subprocess
import shutil
import os
import stat
from pathlib import Path


def clone_repo(repo_link):
    target_file = Path("REPODATA")

    def remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if target_file.exists():
        shutil.rmtree(target_file, onerror=remove_readonly)

    subprocess.run(
        ["git", "clone", repo_link, str(target_file)],
        check=True
    )

    return target_file