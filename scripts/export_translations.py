#!/usr/bin/env python
"""
Export i18n entries to CSV for translation.

Usage:
    python scripts/export_translations.py \
        --output translations_export.csv \
        --langs es fr de pt th vi id ms fil zh
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
I18N_DIR = BASE_DIR / "core" / "i18n" / "messages"


def parse_loose_yaml(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    values: Dict[str, str] = {}
    stack: List[tuple[int, str]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        list_adjust = 0
        if stripped.startswith("-"):
            stripped = stripped[1:].lstrip()
            list_adjust = 2
        if ":" not in stripped:
            i += 1
            continue
        key, rest = stripped.split(":", 1)
        key = key.strip()
        rest = rest.lstrip()
        indent += list_adjust
        while stack and stack[-1][0] >= indent:
            stack.pop()
        prefix = ".".join(item[1] for item in stack)
        full_key = f"{prefix}.{key}" if prefix else key

        if rest == "":
            stack.append((indent, key))
            i += 1
            continue
        if rest in {"|", "|-", ">", ">-"}:
            block_lines: List[str] = []
            block_indent = None
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip() and not block_lines:
                    i += 1
                    continue
                next_indent = len(nxt) - len(nxt.lstrip(" "))
                if nxt.strip() and nxt.lstrip().startswith("#") and next_indent >= indent + 1:
                    block_lines.append(nxt.strip())
                    i += 1
                    continue
                if next_indent <= indent and nxt.strip():
                    break
                if next_indent <= indent and not nxt.strip():
                    block_lines.append("")
                    i += 1
                    continue
                if block_indent is None:
                    block_indent = next_indent
                block_lines.append(nxt[block_indent:])
                i += 1
            value = "\n".join(block_lines).rstrip("\n")
            values[full_key] = value
            stack.append((indent, key))
            continue
        else:
            values[full_key] = rest
            stack.append((indent, key))
            i += 1
    return values


def gather_languages(args_langs: List[str]) -> List[str]:
    if args_langs:
        return args_langs
    langs: List[str] = []
    for path in sorted(I18N_DIR.glob("*.yml")):
        stem = path.stem
        if stem == "en":
            continue
        langs.append(stem)
    return langs


def main() -> None:
    parser = argparse.ArgumentParser(description="Export translations to CSV.")
    parser.add_argument("--output", default="translations_export.csv", help="CSV output path")
    parser.add_argument(
        "--langs",
        nargs="*",
        default=None,
        help="Languages to include (default: all available minus en)",
    )
    parser.add_argument(
        "--skip-missing",
        action="store_true",
        help="If set, rows missing in English will be skipped (default export all)",
    )
    args = parser.parse_args()

    langs = gather_languages(args.langs)
    if not langs:
        raise SystemExit("No language files found (except English).")

    en_map = parse_loose_yaml(I18N_DIR / "en.yml")

    language_maps: Dict[str, Dict[str, object]] = {}
    for lang in langs:
        language_maps[lang] = parse_loose_yaml(I18N_DIR / f"{lang}.yml")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    header = ["key", "en"] + langs
    rows_written = 0
    with output_path.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for key in sorted(en_map.keys()):
            en_value = en_map.get(key, "")
            if args.skip_missing and (en_value is None or en_value == ""):
                continue
            row = [key, en_value or ""]
            for lang in langs:
                value = language_maps.get(lang, {}).get(key, "")
                row.append(value or "")
            writer.writerow(row)
            rows_written += 1

    print(f"Exported {rows_written} keys to {output_path} for languages: {', '.join(langs)}")


if __name__ == "__main__":
    main()

