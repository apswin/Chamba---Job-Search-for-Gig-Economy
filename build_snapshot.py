"""Pull a snapshot of real SF hourly listings into the query cache.

Run this once before demoing:  .venv/bin/python build_snapshot.py

Why it exists: Adzuna's free tier throttles without warning and starts serving
HTML error pages for every request. Once these queries are cached, the bot
answers instantly and never touches the network during a demo — while still
showing genuinely real, genuinely recent listings.

Deliberately slow. Do not remove the pauses.
"""

from __future__ import annotations

import collections
import time

from dotenv import load_dotenv

load_dotenv()

import jobs as jobsearch  # noqa: E402

# The search terms our intake actually produces, for the roles in our ICP.
TERMS = [
    "line cook",
    "prep cook",
    "dishwasher",
    "server restaurant",
    "warehouse associate",
    "janitorial custodian",
    "retail associate",
    "food service worker",
    "delivery driver",
    "housekeeping hotel",
]

WHERES = ["San Francisco", "Oakland"]


def main() -> None:
    total = 0
    channels: collections.Counter = collections.Counter()
    freshness: collections.Counter = collections.Counter()

    for where in WHERES:
        for term in TERMS:
            found = jobsearch.search(term, where, 25)
            total += len(found)
            channels.update(j.channel for j in found)
            for j in found:
                bucket = (
                    "today" if j.days_ago == 0
                    else "this week" if j.days_ago <= 7
                    else "this month"
                )
                freshness[bucket] += 1
            print(f"  {where:16} {term:22} {len(found):3} listings")
            time.sleep(1)

    print()
    print(f"  cached {total} listings across {len(TERMS) * len(WHERES)} queries")
    print(f"  channels : {dict(channels)}")
    print(f"  freshness: {dict(freshness)}")
    print()
    print("  The bot will now answer from cache. Re-run this to refresh.")


if __name__ == "__main__":
    main()
