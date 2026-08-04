#!/usr/bin/env python3
"""Atomic run-claim lockfile for the pipeline.

Subcommands:
  claim <lockpath> --run-id X [--ttl-hours 12]
      Atomically create the lockfile (O_CREAT|O_EXCL) holding JSON
      {"run_id": ..., "ts": <unix epoch>}. If a lock already exists and is
      fresh (younger than TTL), refuse with holder info (exit 1). If it is
      older than the TTL, steal it and print a STALE-STEAL warning.
      An unparseable existing lockfile is treated as stale (stolen with a
      warning) — a corrupt lock cannot prove a live holder.
  check <lockpath>
      Print lock state. Exit 0 if the path is claimable (free or stale),
      exit 1 if actively held.
  release <lockpath> --run-id X
      Delete the lock only if run_id matches the holder; refuse others
      (exit 1). Releasing an already-free lock succeeds (idempotent).

Every result prints one machine-readable line:
  LOCK <subcmd> OK|HELD|STALE|STALE-STEAL|REFUSED|FREE <detail>
"""

import argparse
import json
import os
import sys
import tempfile
import time


def report(subcmd, status, detail):
    print("LOCK %s %s %s" % (subcmd, status, detail))


def read_lock(lockpath):
    """Return (holder_dict_or_None, error_or_None) for an existing lockfile."""
    try:
        with open(lockpath, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
        if not isinstance(doc, dict):
            raise ValueError("lock content is not a JSON object")
        return doc, None
    except Exception as exc:
        return None, exc


def lock_age_seconds(lockpath, holder):
    """Age from the recorded ts; fall back to file mtime if ts is unusable."""
    ts = holder.get("ts") if holder else None
    if isinstance(ts, (int, float)):
        return time.time() - ts
    try:
        return time.time() - os.stat(lockpath).st_mtime
    except OSError:
        return float("inf")


def write_lock_exclusive(lockpath, payload):
    fd = os.open(lockpath, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
        fh.write("\n")


def overwrite_lock_atomic(lockpath, payload):
    """Replace a stale lock atomically (tempfile + os.replace)."""
    directory = os.path.dirname(os.path.abspath(lockpath)) or "."
    fd, tmppath = tempfile.mkstemp(prefix=".claim_lock.", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
            fh.write("\n")
        os.replace(tmppath, lockpath)
    except Exception:
        try:
            os.unlink(tmppath)
        except OSError:
            pass
        raise


def cmd_claim(args):
    payload = {"run_id": args.run_id, "ts": time.time()}
    ttl_seconds = args.ttl_hours * 3600.0
    try:
        write_lock_exclusive(args.lockpath, payload)
        report("claim", "OK", "%s claimed by run %s" % (args.lockpath, args.run_id))
        return 0
    except FileExistsError:
        pass
    except OSError as exc:
        report("claim", "REFUSED", "cannot create %s: %s" % (args.lockpath, exc))
        return 1

    holder, err = read_lock(args.lockpath)
    age = lock_age_seconds(args.lockpath, holder)
    if holder is not None and age <= ttl_seconds:
        report("claim", "HELD", "%s held by run %s (age %.0fs, ttl %.0fs)"
               % (args.lockpath, holder.get("run_id", "unknown"), age, ttl_seconds))
        return 1

    # Stale (or unparseable) lock: steal it, loudly.
    prior = holder.get("run_id", "unknown") if holder else "unparseable (%s)" % err
    try:
        overwrite_lock_atomic(args.lockpath, payload)
    except OSError as exc:
        report("claim", "REFUSED", "stale lock at %s could not be replaced: %s" % (args.lockpath, exc))
        return 1
    report("claim", "STALE-STEAL",
           "WARNING: %s previously held by run %s (age %.0fs > ttl %.0fs); stolen by run %s"
           % (args.lockpath, prior, age, ttl_seconds, args.run_id))
    return 0


def cmd_check(args):
    if not os.path.exists(args.lockpath):
        report("check", "FREE", "%s not held" % args.lockpath)
        return 0
    holder, err = read_lock(args.lockpath)
    age = lock_age_seconds(args.lockpath, holder)
    ttl_seconds = args.ttl_hours * 3600.0
    if holder is None:
        report("check", "STALE", "%s exists but is unparseable (%s)" % (args.lockpath, err))
        return 0
    if age > ttl_seconds:
        report("check", "STALE", "%s held by run %s but stale (age %.0fs > ttl %.0fs)"
               % (args.lockpath, holder.get("run_id", "unknown"), age, ttl_seconds))
        return 0
    report("check", "HELD", "%s held by run %s (age %.0fs)"
           % (args.lockpath, holder.get("run_id", "unknown"), age))
    return 1


def cmd_release(args):
    if not os.path.exists(args.lockpath):
        report("release", "OK", "%s already free" % args.lockpath)
        return 0
    holder, err = read_lock(args.lockpath)
    if holder is None:
        report("release", "REFUSED", "%s is unparseable (%s); refusing blind delete — reclaim via claim (stale-steal) instead"
               % (args.lockpath, err))
        return 1
    holder_id = holder.get("run_id")
    if holder_id != args.run_id:
        report("release", "REFUSED", "%s held by run %s, not run %s"
               % (args.lockpath, holder_id, args.run_id))
        return 1
    try:
        os.unlink(args.lockpath)
    except OSError as exc:
        report("release", "REFUSED", "cannot delete %s: %s" % (args.lockpath, exc))
        return 1
    report("release", "OK", "%s released by run %s" % (args.lockpath, args.run_id))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="claim_lock",
        description="Atomic run-claim lockfile. Exit: 0 success/claimable, 1 held/refused, 2 usage.",
    )
    sub = parser.add_subparsers(dest="subcmd", required=True)

    p = sub.add_parser("claim", help="atomically claim the lock (steals stale locks with a warning)")
    p.add_argument("lockpath")
    p.add_argument("--run-id", required=True)
    p.add_argument("--ttl-hours", type=float, default=12.0)
    p.set_defaults(func=cmd_claim)

    p = sub.add_parser("check", help="report lock state (exit 0 claimable, 1 held)")
    p.add_argument("lockpath")
    p.add_argument("--ttl-hours", type=float, default=12.0)
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("release", help="release the lock (holder only)")
    p.add_argument("lockpath")
    p.add_argument("--run-id", required=True)
    p.set_defaults(func=cmd_release)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
