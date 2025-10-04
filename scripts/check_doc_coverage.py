import ast
import os


def check_doc_coverage(directory="src"):
    """
    Analyzes Python files in a directory to check for docstring coverage.
    Reports coverage for modules, classes, and functions.
    """
    total_nodes = 0
    nodes_with_docstrings = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                total_nodes += 1  # Count module
                file_path = os.path.join(root, file)
                with open(file_path, encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=file)
                        if ast.get_docstring(tree):
                            nodes_with_docstrings += 1
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                total_nodes += 1
                                if ast.get_docstring(node):
                                    nodes_with_docstrings += 1
                    except SyntaxError as e:
                        print(f"Error parsing {file_path}: {e}")

    if total_nodes == 0:
        print("No Python files found to analyze.")
        return

    coverage = (nodes_with_docstrings / total_nodes) * 100
    print(f"Documentation Coverage: {coverage:.2f}% ({nodes_with_docstrings}/{total_nodes} documented nodes)")

if __name__ == "__main__":
    check_doc_coverage()
