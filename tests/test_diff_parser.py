import unittest

from src.diff_parser import parse_diff


class TestParseDiff(unittest.TestCase):
    def test_added_and_removed_lines(self):
        sample = """diff --git a/example.py b/example.py
--- a/example.py
+++ b/example.py
@@ -1,3 +1,4 @@
 def greet():
-    print("Hello")
+    print("Hello, world")
+    return True
"""
        result = parse_diff(sample)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].new_path, "example.py")

        changes = result[0].lines
        self.assertEqual(len(changes), 4)
        self.assertEqual(changes[0].kind, "context")
        self.assertEqual(changes[0].new_line, 1)
        self.assertEqual(changes[1].kind, "removed")
        self.assertEqual(changes[1].old_line, 2)
        self.assertIsNone(changes[1].new_line)
        self.assertEqual(changes[2].kind, "added")
        self.assertEqual(changes[2].new_line, 2)
        self.assertIsNone(changes[2].old_line)
        self.assertEqual(changes[3].new_line, 3)

    def test_new_file(self):
        sample = """diff --git a/new.py b/new.py
--- /dev/null
+++ b/new.py
@@ -0,0 +1,2 @@
+print("hello")
+print("world")
"""
        result = parse_diff(sample)

        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0].old_path)
        self.assertEqual(result[0].new_path, "new.py")
        self.assertEqual(result[0].lines[0].new_line, 1)
        self.assertEqual(result[0].lines[1].new_line, 2)

    def test_empty_input(self):
        self.assertEqual(parse_diff(""), [])

    def test_multiple_files(self):
        sample = """diff --git a/a.py b/a.py
--- a/a.py
+++ b/a.py
@@ -1 +1 @@
-old()
+new()
diff --git a/b.py b/b.py
--- a/b.py
+++ b/b.py
@@ -1 +1 @@
-x = 1
+x = 2
"""
        result = parse_diff(sample)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].new_path, "a.py")
        self.assertEqual(result[1].new_path, "b.py")

    def test_deleted_file(self):
        sample = """diff --git a/old.py b/old.py
deleted file mode 100644
--- a/old.py
+++ /dev/null
@@ -1 +0,0 @@
-print("gone")
"""
        result = parse_diff(sample)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].old_path, "old.py")
        self.assertIsNone(result[0].new_path)
        self.assertEqual(result[0].lines[0].kind, "removed")

    def test_renamed_file_paths(self):
        sample = """diff --git a/old.py b/new.py
similarity index 100%
rename from old.py
rename to new.py
"""
        result = parse_diff(sample)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].old_path, "old.py")
        self.assertEqual(result[0].new_path, "new.py")

    def test_multiple_hunks(self):
        sample = """diff --git a/example.py b/example.py
--- a/example.py
+++ b/example.py
@@ -1,2 +1,2 @@
 first()
-old()
+new()
@@ -10,1 +10,1 @@
-old_last()
+new_last()
"""
        result = parse_diff(sample)

        self.assertEqual(len(result[0].lines), 5)
        self.assertEqual(result[0].lines[0].new_line, 1)
        self.assertEqual(result[0].lines[2].new_line, 2)
        self.assertEqual(result[0].lines[3].old_line, 10)
        self.assertEqual(result[0].lines[4].new_line, 10)

    def test_no_newline_marker(self):
        sample = """diff --git a/example.py b/example.py
--- a/example.py
+++ b/example.py
@@ -1 +1 @@
-old()
\\ No newline at end of file
+new()
\\ No newline at end of file
"""
        result = parse_diff(sample)

        self.assertEqual(len(result[0].lines), 2)
        self.assertEqual(result[0].lines[0].kind, "removed")
        self.assertEqual(result[0].lines[1].kind, "added")

    def test_context_line_numbers(self):
        sample = """diff --git a/example.py b/example.py
--- a/example.py
+++ b/example.py
@@ -5,3 +5,4 @@
 before()
-old()
+new()
+extra()
 after()
"""
        result = parse_diff(sample)
        lines = result[0].lines

        self.assertEqual(lines[0].old_line, 5)
        self.assertEqual(lines[0].new_line, 5)
        self.assertEqual(lines[-1].old_line, 7)
        self.assertEqual(lines[-1].new_line, 8)


if __name__ == "__main__":
    unittest.main()
