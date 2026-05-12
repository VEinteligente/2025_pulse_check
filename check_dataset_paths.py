#!/usr/bin/env python3
"""
Checks all file paths referenced in Dataset_shutdown_incidents_ISOC.csv
and reports which ones are missing from the repository.

Output columns (TSV):
  legacy_id | field | referenced_filename | directory_exists | available_files
"""

import csv
import re
import os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(REPO_ROOT, "Dataset_shutdown_incidents_ISOC.csv")

TEXT_FIELDS = [
    "data_analysis", "overview", "local_impact", "cause_documentation",
    "conversations", "experiences", "related_pulse_analysis",
    "related_events", "related_community_analysis", "related_news",
]


def extract_refs(text):
    """Return list of (folder, filename) tuples from text."""
    refs = []
    if not text:
        return refs

    repo_name = os.path.basename(REPO_ROOT)

    # HTML: src="/2025_pulse_check/{folder}/{filename}"
    for m in re.finditer(
        r'src=["\']/' + re.escape(repo_name) + r'/(\d+)/([^"\'>\s]+)["\']',
        text,
    ):
        refs.append((m.group(1), m.group(2)))

    # Markdown: ![alt]({folder}/{filename})
    for m in re.finditer(r'!\[.*?\]\((\d+)/([^)\s]+)\)', text):
        refs.append((m.group(1), m.group(2)))

    # Markdown with /repo_name/ prefix: ![alt](/repo_name/{folder}/{file})
    for m in re.finditer(
        r'!\[.*?\]\(/' + re.escape(repo_name) + r'/(\d+)/([^)\s]+)\)',
        text,
    ):
        refs.append((m.group(1), m.group(2)))

    return refs


def main():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    header = ["legacy_id", "field", "referenced_filename", "directory_exists", "available_files"]
    print("\t".join(header))

    seen = set()

    for row in rows:
        legacy_id = row["id"]
        for field in TEXT_FIELDS:
            val = row.get(field, "")
            refs = extract_refs(val)
            for folder, filename in refs:
                key = (legacy_id, field, folder, filename)
                if key in seen:
                    continue
                seen.add(key)

                folder_path = os.path.join(REPO_ROOT, folder)
                dir_exists = os.path.isdir(folder_path)

                if dir_exists:
                    available = sorted(
                        f for f in os.listdir(folder_path)
                        if os.path.isfile(os.path.join(folder_path, f))
                    )
                    available_str = ", ".join(available)
                else:
                    available_str = ""

                print("\t".join([
                    legacy_id,
                    field,
                    filename,
                    "TRUE" if dir_exists else "FALSE",
                    available_str,
                ]))


if __name__ == "__main__":
    main()
