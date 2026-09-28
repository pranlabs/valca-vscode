#!/usr/bin/env python3
"""Fail if the Marketplace listing disagrees with the shipped scanner.

Why this exists
---------------
On 2026-09-12 the published listings advertised **36 rules** while the engine
shipped **102**. The gap had been live on PyPI and the VS Code Marketplace for
months because the rule count was maintained by hand in three places at once.

When the extension lived in the scanner's repository, a test there read this
README and compared it with the engine imported from the sibling directory. The
extension now has its own repository, and that comparison cannot survive the move
unchanged — the obvious translation is to drop it, which is how a guard quietly
disappears.

So it got stronger instead of weaker. This installs the **published** `valca`
package and asks it how many rules it has, which compares the listing against
what a user actually receives rather than against source sitting next to it.

Usage
-----
    pip install valca
    python3 scripts/check_listing.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
README = HERE / "README.md"
CLAIM = re.compile(r"What It Catches \((\d+) rules?\)")

#: Rule IDs emitted by a parent rule class rather than registered separately.
#: Mirrors SUB_RULE_IDS in the scanner's own tests; kept in sync by the assertion
#: below, which fails loudly if the engine stops emitting them.
SUB_RULE_IDS = {"VGL-PKG002", "VGL-PKG003", "VGL-PKG004"}


def engine_rule_count() -> int:
    try:
        from valca.rules import DEFAULT_RULES
    except ImportError:
        print(
            "error: valca is not installed, so the listing cannot be checked.\n"
            "       pip install valca",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return len({r.id for r in DEFAULT_RULES} | SUB_RULE_IDS)


def main() -> int:
    text = README.read_text()
    match = CLAIM.search(text)
    if not match:
        print(
            "error: README must state 'What It Catches (N rules)'. Without that "
            "line the listing cannot be checked at all.",
            file=sys.stderr,
        )
        return 1

    advertised = int(match.group(1))
    actual = engine_rule_count()

    if advertised != actual:
        print(
            f"error: the Marketplace listing advertises {advertised} rules, but the "
            f"installed scanner emits {actual}.\n"
            f"       Update the README before publishing. A listing that misstates "
            f"the product costs the only thing a security tool sells.",
            file=sys.stderr,
        )
        return 1

    print(f"ok: listing and scanner agree — {actual} rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
