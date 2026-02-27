import os
import ast

SRC_ROOT = "..\src"


def list_imports_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(alias.name for alias in node.names)
            imports.append(f"from {module} import {names}")

    return imports


def scan_src_tree():
    print(f"\n==============================")
    print(f" IMPORTS BY FILE")
    print(f"==============================\n")

    for root, dirs, files in os.walk(SRC_ROOT):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, SRC_ROOT)

                imports = list_imports_in_file(full_path)

                print(f"\n--- {rel_path} ---")
                if imports:
                    for imp in imports:
                        print("  ", imp)
                else:
                    print("  (no imports)")


if __name__ == "__main__":
    scan_src_tree()
