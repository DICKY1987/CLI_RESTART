import os
import subprocess
import sys

def get_last_commit_date(file_path):
    """Gets the last commit date of a file using git."""
    try:
        cmd = ["git", "log", "-1", "--format=%ct", file_path]
        result = subprocess.check_output(cmd).strip()
        return int(result)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Return a very old timestamp if file not in git or git not found
        return 0

def check_doc_freshness(source_dir="src", docs_dir="docs"):
    """
    Checks if documentation is stale by comparing the last commit dates
    of source files and their corresponding documentation files.
    """
    stale_files = []
    print(f"Checking for stale documentation in '{docs_dir}' relative to '{source_dir}'...")

    for root, _, files in os.walk(source_dir):
        for file in files:
            if not file.endswith(".py"):
                continue

            source_file_path = os.path.join(root, file)
            # Assumes a flat docs structure where e.g. src/module/file.py -> docs/file.md
            doc_file_name = os.path.splitext(os.path.basename(file))[0] + ".md"
            doc_file_path = os.path.join(docs_dir, doc_file_name)

            if os.path.exists(doc_file_path):
                source_date = get_last_commit_date(source_file_path)
                doc_date = get_last_commit_date(doc_file_path)

                # If source is newer than docs, it's stale
                if source_date > doc_date:
                    stale_files.append((source_file_path, doc_file_path))

    if stale_files:
        print("\nStale documentation files found:")
        for src, doc in stale_files:
            print(f"  - Source '{src}' was updated more recently than its doc '{doc}'.")
        print("\nPlease update the documentation for these files.")
        sys.exit(1)
    else:
        print("\nAll documentation appears to be fresh.")
        sys.exit(0)

if __name__ == "__main__":
    check_doc_freshness()
