#!/usr/bin/env python3
"""Closed-vocabulary probe runner for pipeline row verification.

Each probe checks one mechanical fact and prints exactly one machine-readable
result line:

    PROBE <subcmd> PASS|FAIL|USAGE|REFUSED <detail>

Exit codes: 0 pass, 1 fail, 2 usage error, 3 refused.

The `fixture` probe runs ONLY commands declared in the operator-ratified
grants file (.pipeline-grants.json, same discovery as the path guard:
$CLAUDE_PROJECT_DIR first, then cwd). Commands are argv arrays, never shell
strings, and are never taken from this script's arguments — an undeclared
fixture name is refused (exit 3), by design.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

GRANTS_FILENAME = ".pipeline-grants.json"

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_REFUSED = 3


def report(subcmd, status, detail):
    print("PROBE %s %s %s" % (subcmd, status, detail))


def probe_file_exists(args):
    path = args.path
    if os.path.isfile(path):
        st = os.stat(path)
        report("file_exists", "PASS", "%s size=%d mtime=%d" % (path, st.st_size, int(st.st_mtime)))
        return EXIT_PASS
    report("file_exists", "FAIL", "%s does not exist or is not a regular file" % path)
    return EXIT_FAIL


def probe_content_matches(args):
    path = args.path
    pattern = args.pattern
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    except OSError as exc:
        report("content_matches", "FAIL", "cannot read %s: %s" % (path, exc))
        return EXIT_FAIL
    if args.regex:
        try:
            matched = re.search(pattern, content) is not None
        except re.error as exc:
            report("content_matches", "USAGE", "invalid regex %r: %s" % (pattern, exc))
            return EXIT_USAGE
        kind = "regex"
    else:
        matched = pattern in content
        kind = "literal"
    if matched:
        report("content_matches", "PASS", "%s matches %s %r" % (path, kind, pattern))
        return EXIT_PASS
    report("content_matches", "FAIL", "%s does not match %s %r" % (path, kind, pattern))
    return EXIT_FAIL


def probe_commit_exists(args):
    repo = args.repo or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "cat-file", "-e", "%s^{commit}" % args.sha],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        report("commit_exists", "FAIL", "git executable not found")
        return EXIT_FAIL
    except (OSError, subprocess.TimeoutExpired) as exc:
        report("commit_exists", "FAIL", "git invocation failed in %s: %s" % (repo, exc))
        return EXIT_FAIL
    if result.returncode == 0:
        report("commit_exists", "PASS", "%s is a commit in %s" % (args.sha, repo))
        return EXIT_PASS
    stderr = (result.stderr or "").strip().splitlines()
    detail = stderr[0] if stderr else "git cat-file exit %d" % result.returncode
    report("commit_exists", "FAIL", "%s not found in %s (%s)" % (args.sha, repo, detail))
    return EXIT_FAIL


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Surface the 3xx itself instead of following it.


def probe_http_status(args):
    try:
        expected = int(args.expected_code)
    except ValueError:
        report("http_status", "USAGE", "expected_code %r is not an integer" % args.expected_code)
        return EXIT_USAGE
    handlers = [] if args.follow else [_NoRedirect()]
    opener = urllib.request.build_opener(*handlers)
    try:
        resp = opener.open(args.url, timeout=10)
        code = resp.getcode()
        resp.close()
    except urllib.error.HTTPError as exc:
        code = exc.code
    except (urllib.error.URLError, OSError) as exc:
        report("http_status", "FAIL", "%s unreachable: %s" % (args.url, exc))
        return EXIT_FAIL
    if code == expected:
        report("http_status", "PASS", "%s returned %d" % (args.url, code))
        return EXIT_PASS
    report("http_status", "FAIL", "%s returned %d, expected %d" % (args.url, code, expected))
    return EXIT_FAIL


def _find_grants_file():
    candidates = []
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        candidates.append(os.path.join(project_dir, GRANTS_FILENAME))
    candidates.append(os.path.join(os.getcwd(), GRANTS_FILENAME))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def probe_fixture(args):
    name = args.name
    grants_path = _find_grants_file()
    if grants_path is None:
        report("fixture", "REFUSED", "fixture not declared: no grants file found for %r" % name)
        return EXIT_REFUSED
    try:
        with open(grants_path, "r", encoding="utf-8") as fh:
            grants_doc = json.load(fh)
        fixtures = grants_doc.get("fixtures") or {}
        spec = fixtures.get(name)
    except Exception as exc:
        report("fixture", "REFUSED", "fixture not declared: grants file unreadable (%s)" % exc)
        return EXIT_REFUSED
    if spec is None:
        report("fixture", "REFUSED", "fixture not declared: %r absent from %s" % (name, grants_path))
        return EXIT_REFUSED
    cmd = spec.get("cmd") if isinstance(spec, dict) else None
    if (not isinstance(cmd, list) or not cmd
            or not all(isinstance(part, str) for part in cmd)):
        report("fixture", "REFUSED", "fixture %r malformed: cmd must be a non-empty argv array of strings" % name)
        return EXIT_REFUSED
    cwd = spec.get("cwd") or os.getcwd()
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        report("fixture", "FAIL", "%r could not run: %s" % (name, exc))
        return EXIT_FAIL
    if result.returncode == 0:
        report("fixture", "PASS", "%r exit 0" % name)
        return EXIT_PASS
    tail = (result.stderr or result.stdout or "").strip().splitlines()
    detail = tail[-1] if tail else "no output"
    report("fixture", "FAIL", "%r exit %d (%s)" % (name, result.returncode, detail))
    return EXIT_FAIL


def build_parser():
    parser = argparse.ArgumentParser(
        prog="probe_runner",
        description="Closed-vocabulary mechanical probes. Exit: 0 pass, 1 fail, 2 usage, 3 refused.",
    )
    sub = parser.add_subparsers(dest="subcmd", required=True)

    p = sub.add_parser("file_exists", help="file exists; prints size and mtime")
    p.add_argument("path")
    p.set_defaults(func=probe_file_exists)

    p = sub.add_parser("content_matches", help="file content contains pattern")
    p.add_argument("path")
    p.add_argument("pattern")
    p.add_argument("--regex", action="store_true", help="treat pattern as a regex (default: literal substring)")
    p.set_defaults(func=probe_content_matches)

    p = sub.add_parser("commit_exists", help="sha resolves to a commit in a git repo")
    p.add_argument("sha")
    p.add_argument("--repo", help="repo directory (default: cwd)")
    p.set_defaults(func=probe_commit_exists)

    p = sub.add_parser("http_status", help="URL returns the expected HTTP status (10s timeout)")
    p.add_argument("url")
    p.add_argument("expected_code")
    p.add_argument("--follow", action="store_true", help="follow redirects (default: report the 3xx itself)")
    p.set_defaults(func=probe_http_status)

    p = sub.add_parser("fixture", help="run an operator-ratified named test command from the grants file")
    p.add_argument("name")
    p.set_defaults(func=probe_fixture)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
