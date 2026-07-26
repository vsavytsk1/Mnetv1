#!/usr/bin/env python3
# ============================================================================
#  install_prepush_guard.py -- CURSE 31 counter-hex, installed as a git hook
# ----------------------------------------------------------------------------
#  Installs a pre-push hook into THIS repo's .git/hooks/ that REFUSES any push
#  containing a file >= 100 MB (GitHub's hard wall). The push passes through
#  this logic first, every time -- so it can never silently wedge again.
#
#      py -3 builder/install_prepush_guard.py          # install into this repo
#
#  Pure stdlib. ASCII source. LF newlines. Re-run any time; it overwrites.
# ============================================================================
import os
import sys
import stat
import subprocess

LIMIT_MB = 100

# The hook body. It scans the commits being pushed (the range git hands it on
# stdin) for any blob >= 100 MB and blocks the push if it finds one.
HOOK = r'''#!/usr/bin/env python3
# pre-push guard -- CURSE 31 (The Hundred-Meg Wall). Auto-installed. Do not edit here;
# edit builder/install_prepush_guard.py and re-run it instead.
import sys, subprocess

LIMIT = 100 * 1024 * 1024  # 100 MB, GitHub's hard wall (private repos too)

def blobs_in_range(rng):
    # list (size, path) for every blob reachable in the push range
    try:
        objs = subprocess.check_output(["git", "rev-list", "--objects"] + rng,
                                       text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return []
    lines = [l for l in objs.splitlines() if " " in l]
    if not lines:
        return []
    check = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objecttype) %(objectsize) %(rest)"],
        input="\n".join(l.split(" ", 1)[0] + " " + l.split(" ", 1)[1] for l in lines),
        text=True, capture_output=True)
    out = []
    for row in check.stdout.splitlines():
        p = row.split(" ", 2)
        if len(p) == 3 and p[0] == "blob":
            try:
                size = int(p[1])
            except ValueError:
                continue
            if size >= LIMIT:
                out.append((size, p[2]))
    return out

def main():
    offenders = []
    seen = set()
    for line in sys.stdin:
        parts = line.split()
        if len(parts) < 4:
            continue
        local_sha, remote_sha = parts[1], parts[3]
        if local_sha == "0" * 40:
            continue  # branch deletion
        if remote_sha == "0" * 40:
            rng = [local_sha, "--not", "--remotes"]  # new branch: all not-yet-remote
        else:
            rng = [remote_sha + ".." + local_sha]
        for size, path in blobs_in_range(rng):
            key = (size, path)
            if key not in seen:
                seen.add(key)
                offenders.append(key)
    if offenders:
        sys.stderr.write("\n  PUSH BLOCKED -- CURSE 31 (The Hundred-Meg Wall)\n")
        sys.stderr.write("  GitHub hard-rejects any file >= 100 MB (private repos too).\n")
        sys.stderr.write("  These blobs in your push are too big:\n\n")
        for size, path in sorted(offenders, reverse=True):
            sys.stderr.write("    %7.1f MB  %s\n" % (size / 1024 / 1024, path))
        sys.stderr.write("\n  FIX: gitignore the big generated copy, git rm --cached it,\n")
        sys.stderr.write("  and regenerate it locally. Store the math; render on demand.\n")
        sys.stderr.write("  See GIT_INCIDENT_001.md. Pay thea Heleni in compute.\n\n")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
'''


def repo_git_dir():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--git-dir"],
                                      text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        sys.exit("ERROR: not inside a git repository.")
    return out


def main():
    git_dir = repo_git_dir()
    hooks = os.path.join(git_dir, "hooks")
    os.makedirs(hooks, exist_ok=True)
    hook_path = os.path.join(hooks, "pre-push")
    with open(hook_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HOOK)
    # make executable (matters on POSIX; harmless on Windows)
    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print("installed pre-push guard (>= %d MB blocked) -> %s" % (LIMIT_MB, hook_path))


if __name__ == "__main__":
    main()
