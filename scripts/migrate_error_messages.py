import os
import re

def find_unstructured_exceptions(directory="src"):
    """
    Scans for unstructured 'raise Exception(...)' statements and suggests
    migration to the new standardized exception classes.
    """
    print(f"Scanning '{directory}' for unstructured exception messages to migrate...")
    # Regex to find simple `raise Exception("...")` statements
    exception_pattern = re.compile(r"raise\s+(Exception|ValueError|TypeError|RuntimeError)\(("|')(.+?)\2\)")

    found_issues = False
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            match = exception_pattern.search(line)
                            if match:
                                found_issues = True
                                error_type = match.group(1)
                                message = match.group(3)
                                print(f"\nFile: {file_path}, Line: {i}")
                                print(f"  - Found '{error_type}': \"{message}\"")
                                print(f"  - Consider migrating to a standardized exception from 'src.cli_multi_rapid.errors.exceptions'.")
                                # Simple suggestion logic
                                if "not found" in message.lower():
                                    print("  - Suggestion: `FileNotFoundError`")
                                elif "permission" in message.lower():
                                    print("  - Suggestion: `PermissionDeniedError`")
                                elif "config" in message.lower():
                                    print("  - Suggestion: `ConfigurationError`")
                                else:
                                    print("  - Suggestion: `GeneralError`")
                except Exception as e:
                    print(f"Could not read file {file_path}: {e}")

    if not found_issues:
        print("\nNo unstructured exception messages found.")

if __name__ == "__main__":
    find_unstructured_exceptions()
