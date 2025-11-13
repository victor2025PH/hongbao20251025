#!/usr/bin/env python
"""
Import translations from CSV back to YAML files.

Usage:
    python scripts/import_translations.py --input translations_export.csv
    python scripts/import_translations.py --input translations_export.csv --langs es fr
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
I18N_DIR = BASE_DIR / "core" / "i18n" / "messages"


def ensure_dict(path: Path) -> Dict[str, object]:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if text.strip():
            data = yaml.safe_load(text)
            if isinstance(data, dict):
                return data
    return {}


def set_nested(root: Dict[str, object], key_path: List[str], value: object) -> None:
    current = root
    for part in key_path[:-1]:
        node = current.get(part)
        if not isinstance(node, dict):
            node = {}
            current[part] = node
        current = node
    current[key_path[-1]] = value


def main() -> None:
    parser = argparse.ArgumentParser(description="Import translations from CSV.")
    parser.add_argument("--input", default="translations_export.csv", help="CSV file path")
    parser.add_argument(
        "--langs",
        nargs="*",
        default=None,
        help="Languages to import (default: all columns except key/en)",
    )
    parser.add_argument(
        "--overwrite-empty",
        action="store_true",
        help="If set，空字串也會覆蓋原值；預設跳過空值保留舊翻譯。",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input CSV not found: {input_path}")

    with input_path.open(encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames or "key" not in reader.fieldnames:
            raise SystemExit("CSV 需包含 'key' 欄位。")

        languages = args.langs or [
            name for name in reader.fieldnames if name not in {"key", "en"}
        ]
        if not languages:
            raise SystemExit("無語言欄位可導入。")

        lang_data: Dict[str, Dict[str, object]] = {}
        for lang in languages:
            lang_path = I18N_DIR / f"{lang}.yml"
            lang_data[lang] = ensure_dict(lang_path)

        updated_counts = {lang: 0 for lang in languages}

        for row in reader:
            key = row.get("key")
            if not key:
                continue
            key_parts = key.split(".")
            for lang in languages:
                value = row.get(lang, "")
                if value == "" and not args.overwrite_empty:
                    continue
                set_nested(lang_data[lang], key_parts, value)
                updated_counts[lang] += 1

    for lang, data in lang_data.items():
        lang_path = I18N_DIR / f"{lang}.yml"
        with lang_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=True,
            )
        print(f"Updated {lang_path} ({updated_counts[lang]} entries)")


if __name__ == "__main__":
    main()

