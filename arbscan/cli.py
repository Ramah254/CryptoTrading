"""Command line entry: ``python -m arbscan --snapshot data/snapshot_2026-10-03.json``."""
from __future__ import annotations

import argparse
import sys

from . import report
from .cycles import Snapshot
from .fees import Assumptions


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="arbscan", description=__doc__)
    ap.add_argument("--snapshot", required=True, help="path to a snapshot JSON")
    ap.add_argument("--sizes", type=float, nargs="+", default=[300, 1000, 3000], help="order sizes in USD")
    ap.add_argument("--mid", default="erapi", help="'erapi', 'wise' or a number (USD/KES mid-market)")
    ap.add_argument("--live", action="store_true",
                    help="refresh the snapshot from live endpoints first (needs network access to live.HOSTS)")
    ap.add_argument("--write-snapshot", help="write the (refreshed) snapshot JSON to this path")
    args = ap.parse_args(argv)

    snap = Snapshot.load(args.snapshot)
    banner = ""
    if args.live:
        from . import live
        data, errors = live.build_snapshot(snap.d)
        snap = Snapshot(data)
        if errors:
            banner = ("> **STALE DATA** - these live fetches failed and the previous values were kept:\n>\n"
                      + "\n".join(f"> - {e}" for e in errors) + "\n\n")
            sys.stderr.write(f"{len(errors)} live fetch(es) failed; see banner. Hosts needed: {', '.join(live.HOSTS)}\n")
    if args.write_snapshot:
        import json
        with open(args.write_snapshot, "w", encoding="utf-8") as fh:
            json.dump(snap.d, fh, indent=1)
    fx = snap.d["fx"]
    mid = {"erapi": fx["usdkes_mid_erapi"], "wise": fx["usdkes_mid_wise"]}.get(args.mid)
    if mid is None:
        mid = float(args.mid)
    A = Assumptions(mid_usdkes=mid, usdgbp=fx["usdgbp_erapi"])
    sys.stdout.write(banner + report.render(snap, A, args.sizes))
    return 0
