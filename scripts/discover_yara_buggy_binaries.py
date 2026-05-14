"""Discover and build the failing-test binary for each yara case, then
write its in-container path into corpus.db.{buggy_binary_path,
buggy_binary_argv_json}.

The binaries persist in the bind-mounted workspace because we run inside
docker with the host workspace mounted at /work. After this script,
T1/T2/T3 prompts will reference the actual yara test binary instead of
falling back to `bash` (the trigger argv[0]).

Yara's autotools build emits the test binary at the project root
(`/work/test-atoms`), not under `tests/` — confirmed via `find` after
build. Earlier versions of this script wrote `tests/test-atoms` which
caused gdb to fail with "no such file" at runtime.
"""
import json
import re
import sqlite3
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "data" / "corpus.db"
IMAGE = "chatdbgpro/gdb-yara:latest"


def discover(bug_id: str, case_num: int, workspace: Path) -> str | None:
    """Build inside docker, run make check to identify failing test,
    locate the actual binary on disk, return its in-container path."""
    if not workspace.exists():
        print(f"[{bug_id}] workspace missing: {workspace}")
        return None
    # Use Windows-style absolute path for docker on Windows. Docker
    # Desktop's bash-style path translation only works for paths under
    # /mnt/c/, not for MINGW64's /c/... rewrite.
    ws_abs = str(workspace.resolve())
    inner = (
        f"cd /work; "
        f"echo 'return {case_num}' > tests/defects4cpp.lua; "
        f"make -j$(nproc) CFLAGS='-g -O0' 2>&1 | tail -3; "
        f"make -j1 check 2>&1 | grep -E '^(FAIL|PASS):' || true; "
        f"echo '=== test-suite.log ==='; "
        f"cat /work/test-suite.log 2>/dev/null | grep -E '^(FAIL|PASS):' || true; "
        f"echo '=== .trs results ==='; "
        f"for trs in /work/test-*.trs; do "
        f"  [ -f \"$trs\" ] && r=$(grep ':test-result:' \"$trs\" | head -1); "
        f"  echo \"$trs : $r\"; "
        f"done; "
        f"echo '=== test binaries on disk ==='; "
        f"find /work -maxdepth 3 -name 'test-*' -type f -executable "
        f"-not -name '*.c' -not -name '*.o' -not -name '*.log' "
        f"-not -name '*.trs' -not -name '*.sh' 2>/dev/null"
    )
    cmd = [
        "docker", "run", "--rm",
        "--platform", "linux/amd64",
        "-v", f"{ws_abs}:/work",
        "-w", "/work",
        IMAGE,
        "bash", "-c", inner,
    ]
    print(f"[{bug_id}] running make check (case={case_num})…")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    out = proc.stdout + "\n" + proc.stderr
    fail_match = re.search(r"^FAIL:\s+(\S+)", out, re.MULTILINE)
    if not fail_match:
        # Fallback: any .trs file with FAIL.
        trs_match = re.search(
            r"/work/(test-[^.]+)\.trs : :test-result:\s+FAIL", out
        )
        if trs_match:
            test_name = trs_match.group(1)
        else:
            print(f"[{bug_id}] no FAIL line in output:\n{out[-2000:]}")
            return None
    else:
        test_name = fail_match.group(1)
    # Find the actual binary among the listed paths after "=== test
    # binaries on disk ===". Match any path ending in /test_name.
    after_marker = out.split("=== test binaries on disk ===", 1)[-1]
    candidates = [
        line.strip() for line in after_marker.splitlines()
        if line.strip().endswith(f"/{test_name}")
    ]
    if not candidates:
        print(f"[{bug_id}] FAIL line said '{test_name}' but no matching "
              f"binary on disk after build. Output tail:\n{out[-1500:]}")
        return None
    # Prefer the shortest path (project root over libtool .libs).
    chosen = min(candidates, key=len)
    # Strip leading /work/ → relative to container cwd.
    rel = chosen.removeprefix("/work/")
    return rel


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT bug_id, trigger_argv_json, workspace_path "
        "FROM bugs WHERE project='yara' AND included_in_corpus=1 "
        "ORDER BY bug_index"
    ).fetchall()
    discovered: dict[str, str] = {}
    for bug_id, trig_json, ws_path in rows:
        trig = json.loads(trig_json)
        m = re.search(r"return\s+(\d+)", " ".join(trig))
        if not m:
            print(f"[{bug_id}] no case number in trigger: {trig}")
            continue
        case_num = int(m.group(1))
        path = discover(bug_id, case_num, Path(ws_path))
        if path:
            print(f"[{bug_id}] -> {path}")
            discovered[bug_id] = path
    print()
    print("=== applying to corpus.db ===")
    for bug_id, path in discovered.items():
        argv = [f"/work/{path}"]
        cur.execute(
            "UPDATE bugs SET buggy_binary_path=?, buggy_binary_argv_json=? "
            "WHERE bug_id=?",
            (path, json.dumps(argv), bug_id),
        )
    conn.commit()
    print(f"updated {len(discovered)} rows")
    print()
    print("=== verification ===")
    for row in rows:
        bug_id = row[0]
        v = cur.execute(
            "SELECT buggy_binary_path, buggy_binary_argv_json FROM bugs "
            "WHERE bug_id=?", (bug_id,)
        ).fetchone()
        print(f"  {bug_id}: path={v[0]}  argv={v[1]}")
    conn.close()


if __name__ == "__main__":
    main()
