import tempfile
import unittest
from pathlib import Path
from tools.list_files import list_files
from tools.read_file import read_file
from tools.search_code import search_code

class RepositoryToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "auth.py").write_text(
            "def login(user):\n    return user\n\nTOKEN = True\n",
            encoding="utf-8",
        )
        (self.root / ".env").write_text("SECRET=do-not-read", encoding="utf-8")
        (self.root / ".git").mkdir()
        (self.root / ".git" / "hidden.py").write_text("hidden", encoding="utf-8")
        (self.root / "empty.txt").write_text("", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_list_files_recursive_excludes_secrets_and_git(self):
        result = list_files(str(self.root), recursive=True)
        paths = {item["path"] for item in result}
        self.assertIn("src/auth.py", paths)
        self.assertNotIn(".env", paths)
        self.assertNotIn(".git/hidden.py", paths)

    def test_read_file_line_numbers(self):
        result = read_file(str(self.root), "src/auth.py", 2, 3)
        self.assertEqual(result["content"], "2:     return user\n3: ")

    def test_read_empty_file(self):
        result = read_file(str(self.root), "empty.txt")
        self.assertEqual(result["total_lines"], 0)
        self.assertEqual(result["content"], "")

    def test_search_returns_exact_line(self):
        result = search_code(str(self.root), "TOKEN")
        self.assertEqual(result[0]["path"], "src/auth.py")
        self.assertEqual(result[0]["line"], 4)

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            read_file(str(self.root), "../outside.txt")

    def test_secret_file_is_rejected(self):
        with self.assertRaises(ValueError):
            read_file(str(self.root), ".env")

if __name__ == "__main__":
    unittest.main()