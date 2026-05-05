"""
Fetches Google Scholar stats for a given author ID and writes them
to scholar-stats.json. Run by GitHub Actions on a schedule.

Author ID for Dr. Hirak Mazumdar: abk9F98AAAAJ
"""

from datetime import datetime, timezone
import json
import sys

from scholarly import scholarly

USER_ID = "abk9F98AAAAJ"
OUTPUT_FILE = "scholar-stats.json"


def fetch_stats(user_id: str) -> dict:
    print(f"[scholar-sync] Looking up author {user_id} ...")
    author = scholarly.search_author_id(user_id)
    author = scholarly.fill(author, sections=["indices", "counts"])

    cites_per_year = author.get("cites_per_year", {}) or {}
    years_sorted = sorted(int(y) for y in cites_per_year.keys())

    stats = {
        "citations":      int(author.get("citedby", 0) or 0),
        "citationsSince": int(author.get("citedby5y", 0) or 0),
        "hIndex":         int(author.get("hindex", 0) or 0),
        "hIndexSince":    int(author.get("hindex5y", 0) or 0),
        "i10Index":       int(author.get("i10index", 0) or 0),
        "i10IndexSince":  int(author.get("i10index5y", 0) or 0),
        "citeYears":      years_sorted,
        "citeVals":       [int(cites_per_year[y]) for y in years_sorted],
        "updatedAt":      datetime.now(timezone.utc).isoformat(),
        "source":         "scholarly",
    }

    if not stats["citations"]:
        raise RuntimeError("Citation count came back as zero — likely a bot block.")

    return stats


def main() -> int:
    try:
        stats = fetch_stats(USER_ID)
    except Exception as exc:
        print(f"[scholar-sync] ERROR: {exc}", file=sys.stderr)
        return 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        f.write("\n")

    print(f"[scholar-sync] Wrote {OUTPUT_FILE}:")
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
