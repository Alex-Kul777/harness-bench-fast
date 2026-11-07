#!/usr/bin/env python3
"""Parity tests for the bilingual fork layer (RU default + EN mirror).

Checks:
  1. Locale catalog keys are symmetric between ru and en.
  2. Every RU fork HTML page has an EN twin (and vice versa for shared chromes).
  3. RU/EN result pages carry the same number of data rows (structural parity).
  4. The RU/EN markdown auto-blocks carry the same number of rows.

Run:  python3 tests/test_fork_bilingual.py   (exit 0 = pass)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fork_i18n import CATALOG  # noqa: E402

FAILS: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        FAILS.append(msg)


def _row_count(path: Path) -> int:
    if not path.exists():
        return -1
    return len(re.findall(r"<tr", path.read_text(encoding="utf-8")))


def _md_block_rows(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    begin = text.find("<!-- FORK:RESULTS:BEGIN -->")
    end = text.find("<!-- FORK:RESULTS:END -->")
    if begin == -1 or end == -1:
        return -1
    body = text[begin:end]
    return sum(1 for ln in body.splitlines() if ln.strip().startswith("| ") and "---" not in ln)


# 1. catalog key symmetry
ru_keys = set(CATALOG["ru"])
en_keys = set(CATALOG["en"])
check(ru_keys == en_keys, f"catalog key mismatch: ru-only={ru_keys - en_keys} en-only={en_keys - ru_keys}")

# 2. html twins exist
for stem in ("fork", "fork-sample"):
    check((ROOT / "docs" / f"{stem}.html").exists(), f"missing docs/{stem}.html")
    check((ROOT / "docs" / f"{stem}.en.html").exists(), f"missing docs/{stem}.en.html")

# 3. structural parity of the two home pages
ru, en = _row_count(ROOT / "docs" / "fork.html"), _row_count(ROOT / "docs" / "fork.en.html")
check(ru > 0 and ru == en, f"fork.html/fork.en.html row count differ: ru={ru} en={en}")

# 4. markdown auto-block parity
mru = _md_block_rows(ROOT / "docs" / "fork-results.md")
men = _md_block_rows(ROOT / "docs" / "fork-results.en.md")
check(mru > 0 and mru == men, f"fork-results auto-block rows differ: ru={mru} en={men}")

# 5. EN mirror files exist
for f in ("FORK.en.md", "docs/fork-results.en.md"):
    check((ROOT / f).exists(), f"missing EN mirror {f}")

if FAILS:
    print("FAIL:")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print(f"ok: locale parity (fork rows ru={ru}=en, markdown rows={mru})")
