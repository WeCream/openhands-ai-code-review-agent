from src.diff_parser import parse_diff

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

for file_diff in result:
    print("文件:", file_diff.new_path)
    for line in file_diff.lines:
        print(
            line.kind,
            "旧行号:", line.old_line,
            "新行号:", line.new_line,
            "内容:", line.content,
        )
