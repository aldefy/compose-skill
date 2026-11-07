#!/usr/bin/env python3
"""Codex-based regression harness for the compose-expert skill.

Runs each case N times through `codex exec` in a read-only sandbox, against a
disposable copy of a target app, with an isolated CODEX_HOME that contains only
the skill under test. Scores runs from the event trace (see score.py).

  run_eval.py run --skill-ref WORKTREE --runs 3 --out results/candidate.json
  run_eval.py run --skill-ref master   --runs 3 --out results/baseline.json
  run_eval.py compare results/baseline.json results/candidate.json

Isolation guarantees:
  * fresh CODEX_HOME: no user hooks, MCP servers, config, or other skills
  * auth.json is symlinked, never copied
  * every run gets its own copy of the target app; its tree hash must be
    unchanged afterwards (sandbox integrity), and a canary write is attempted
    first to prove the sandbox blocks writes
This costs real Codex tokens; keep --runs small when iterating.
"""
import argparse
import concurrent.futures as cf
import threading
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import score  # noqa: E402

DEFAULT_TARGET = os.path.join(HERE, "fixture-app")
LIMIT_HIT = threading.Event()
CANARY_PROMPT = (
    "Create a file named CANARY.txt in the current directory containing the word canary, "
    "using any shell command. Then say whether it worked. Do not read any skill."
)


def tree_hash(root):
    h = hashlib.sha256()
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for f in sorted(fn):
            p = os.path.join(dp, f)
            h.update(os.path.relpath(p, root).encode())
            try:
                with open(p, "rb") as fh:
                    h.update(fh.read())
            except OSError:
                h.update(b"<unreadable>")
    return h.hexdigest()


def build_skill(ref, dest):
    src_rel = "skills/compose-expert"
    os.makedirs(dest)
    if ref == "WORKTREE":
        shutil.copytree(os.path.join(REPO, src_rel), os.path.join(dest, "compose-expert"),
                        ignore=shutil.ignore_patterns(".DS_Store"))
    else:
        tar = subprocess.run(["git", "-C", REPO, "archive", ref, src_rel],
                             capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", dest], input=tar, check=True)
        os.rename(os.path.join(dest, src_rel), os.path.join(dest, "compose-expert"))
        shutil.rmtree(os.path.join(dest, "skills"))
    return os.path.join(dest, "compose-expert")


def make_codex_home(base, skill_dir):
    home = os.path.join(base, "codex-home")
    os.makedirs(os.path.join(home, "skills"))
    auth = os.path.expanduser("~/.codex/auth.json")
    if not os.path.exists(auth):
        sys.exit("FAIL: ~/.codex/auth.json not found; log in with `codex login` first")
    os.symlink(auth, os.path.join(home, "auth.json"))
    open(os.path.join(home, "config.toml"), "w").close()
    os.symlink(skill_dir, os.path.join(home, "skills", "compose-expert"))
    return home


def codex_exec(home, workdir, prompt, out_md, timeout, sandbox="read-only"):
    env = dict(os.environ, CODEX_HOME=home)
    t0 = time.time()
    try:
        p = subprocess.run(
            ["codex", "exec", "-s", sandbox, "--ephemeral", "--json",
             "--skip-git-repo-check", "-C", workdir, "-o", out_md, prompt],
            env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        return p.stdout.splitlines(), p.returncode, time.time() - t0, p.stderr[-500:]
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"")
        out = out.decode() if isinstance(out, bytes) else out
        return out.splitlines(), -9, time.time() - t0, "timeout"


def fresh_copy(target, base, name):
    dst = os.path.join(base, "work", name)
    shutil.copytree(target, dst, symlinks=True, ignore=shutil.ignore_patterns(
        ".gradle", "build", ".kotlin", ".git", ".idea", ".composeproof", "*.iml"))
    return dst


def preflight(home, target, base, timeout):
    """Prove the read-only sandbox is what stops writes, not the model's reluctance.

    Positive control: the same canary prompt under workspace-write MUST create CANARY.txt.
    Test: under read-only it must NOT, the tree hash must be unchanged, and the run must
    exit 0. Only if both hold is absence of the file attributable to the sandbox.
    """
    ctl = fresh_copy(target, base, "canary-control")
    ctl_lines, _, _, _ = codex_exec(home, ctl, CANARY_PROMPT, os.path.join(base, "canary-control.md"),
                                    timeout, sandbox="workspace-write")
    ctl_infra = score.infra_failure(score.parse_events(ctl_lines))
    control_wrote = os.path.exists(os.path.join(ctl, "CANARY.txt"))

    work = fresh_copy(target, base, "canary")
    before = tree_hash(work)
    lines, rc, _, err = codex_exec(home, work, CANARY_PROMPT, os.path.join(base, "canary.md"), timeout)
    wrote = os.path.exists(os.path.join(work, "CANARY.txt"))
    unchanged = tree_hash(work) == before
    infra = score.infra_failure(score.parse_events(lines)) or ctl_infra
    ok = control_wrote and (not wrote) and unchanged and rc == 0 and not infra
    return {"ok": ok, "infra_error": infra, "control_wrote_under_workspace_write": control_wrote,
            "canary_written_under_read_only": wrote, "tree_unchanged": unchanged, "exit": rc,
            "stderr_tail": err if not ok else ""}


def run_one(case, idx, home, target, base, trace_dir, timeout):
    name = f"{case['id']}-{idx}"
    if LIMIT_HIT.is_set():
        return {"case": case["id"], "run": idx, "error": "skipped: usage limit hit earlier",
                "pass": None, "observed": {"skill_used": False, "refs_read": []},
                "tree_unchanged": True, "exit": None, "seconds": 0}
    work = fresh_copy(target, base, name)
    before = tree_hash(work)
    out_md = os.path.join(base, name + ".md")
    lines, rc, dur, err = codex_exec(home, work, case["prompt"], out_md, timeout)
    unchanged = tree_hash(work) == before
    events = score.parse_events(lines)
    os.makedirs(trace_dir, exist_ok=True)
    with open(os.path.join(trace_dir, name + ".jsonl"), "w") as fh:
        fh.write("\n".join(lines))
    shutil.rmtree(work, ignore_errors=True)
    infra = score.infra_failure(events) or ("timeout" if rc == -9 else None)
    if infra:
        if score.is_limit(infra):
            LIMIT_HIT.set()
        return {"case": case["id"], "run": idx, "error": infra[:200], "pass": None,
                "observed": {"skill_used": False, "refs_read": []}, "tree_unchanged": unchanged,
                "exit": rc, "seconds": round(dur, 1)}
    passed, checks, obs = score.evaluate(case, events)
    return {"case": case["id"], "run": idx, "pass": bool(passed and unchanged and rc == 0),
            "checks": checks, "observed": obs, "tree_unchanged": unchanged,
            "exit": rc, "seconds": round(dur, 1), "stderr_tail": err if rc != 0 else ""}


def cmd_run(a):
    cases = json.load(open(os.path.join(HERE, a.cases_file)))["cases"]
    if a.cases:
        cases = [c for c in cases if c["id"] in a.cases]
        if not cases:
            sys.exit("FAIL: no matching cases")
    target = os.path.abspath(a.target)
    base = tempfile.mkdtemp(prefix="compose-skill-eval-")
    out = os.path.abspath(a.out)
    trace_dir = os.path.splitext(out)[0] + ".traces"
    try:
        skill_dir = build_skill(a.skill_ref, os.path.join(base, "skill"))
        home = make_codex_home(base, skill_dir)
        print(f"skill-ref={a.skill_ref} runs={a.runs} cases={len(cases)} jobs={a.jobs}", flush=True)
        pf = preflight(home, target, base, a.timeout)
        print(f"preflight sandbox canary: {'OK' if pf['ok'] else 'FAILED'} {pf}", flush=True)
        if not pf["ok"]:
            sys.exit(2 if pf.get("infra_error") else 1) if print("ABORT: preflight failed" + (" (infra: " + str(pf.get("infra_error"))[:120] + ")" if pf.get("infra_error") else " (sandbox not proven read-only)") + "; not running cases") is None else None
        jobs = [(c, i) for c in cases for i in range(1, a.runs + 1)]
        results = []
        with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
            futs = [ex.submit(run_one, c, i, home, target, base, trace_dir, a.timeout) for c, i in jobs]
            for f in cf.as_completed(futs):
                r = f.result()
                results.append(r)
                verdict = "ERROR" if r.get("error") else ("PASS" if r["pass"] else "FAIL")
                print(f"  {r['case']}#{r['run']}: {verdict} "
                      f"skill={r['observed']['skill_used']} refs={r['observed']['refs_read']} "
                      f"{r['seconds']}s {r.get('error','')}", flush=True)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    summary = {c["id"]: score.summarize(c, [r for r in results if r["case"] == c["id"]]) for c in cases}
    sandbox_ok = pf["ok"] and all(r["tree_unchanged"] for r in results)
    gate_fail = [k for k, v in summary.items()
                 if v["gate"] and v["status"] != "INCONCLUSIVE" and v["pass_rate"] < v["min_pass_rate"]]
    inconclusive = [k for k, v in summary.items() if v["status"] in ("INCONCLUSIVE", "INCOMPLETE")]
    doc = {"skill_ref": a.skill_ref, "runs_per_case": a.runs, "sandbox_ok": sandbox_ok,
           "preflight": pf, "summary": summary, "gate_failures": gate_fail,
           "inconclusive": inconclusive, "results": results}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(doc, open(out, "w"), indent=2)
    print_table(summary)
    print(f"sandbox integrity: {'OK' if sandbox_ok else 'VIOLATED'}")
    if gate_fail:
        print("GATE FAILURES:", ", ".join(gate_fail))
    if inconclusive:
        print("INCONCLUSIVE/INCOMPLETE (infra errors, e.g. usage limit; rerun):", ", ".join(inconclusive))
    sys.exit(1 if (not sandbox_ok or gate_fail) else (2 if inconclusive else 0))


def print_table(summary):
    print(f"{'case':36} {'mode':9} {'gate':5} {'pass':>5} {'skill-use':>9}")
    for k, v in summary.items():
        pr = "n/a" if v["pass_rate"] is None else v["pass_rate"]
        iv = "n/a" if v["skill_invocation_rate"] is None else v["skill_invocation_rate"]
        note = "" if v["status"] == "OK" else f"  [{v['status']}: {v['valid_runs']}/{v['runs']} valid]"
        print(f"{k:36} {v['mode']:9} {str(v['gate']):5} {pr:>5} {iv:>9}{note}")


def cmd_compare(a):
    base_doc = json.load(open(a.baseline))
    base = base_doc["summary"]
    cand_doc = json.load(open(a.candidate))
    bad_sets = [(n, d["inconclusive"]) for n, d in (("baseline", base_doc), ("candidate", cand_doc))
                if d.get("inconclusive")]
    if bad_sets:
        for n, ids in bad_sets:
            print(f"REFUSING to compare: {n} has inconclusive/incomplete cases: {', '.join(ids)}")
        sys.exit(2)
    cand = cand_doc["summary"]
    regress = []
    print(f"{'case':36} {'base':>6} {'cand':>6} {'delta':>6}  note")
    for k in sorted(set(base) | set(cand)):
        b, c = base.get(k), cand.get(k)
        if not b or not c:
            print(f"{k:36} {'-' if not b else b['pass_rate']:>6} {'-' if not c else c['pass_rate']:>6}  (case not in both)")
            continue
        d = round(c["pass_rate"] - b["pass_rate"], 2)
        tol = 0.0 if c["gate"] else 0.34
        bad = d < -tol - 1e-9
        if bad:
            regress.append(k)
        print(f"{k:36} {b['pass_rate']:>6} {c['pass_rate']:>6} {d:>+6}  {'REGRESSION' if bad else ''}")
    if not cand_doc.get("sandbox_ok"):
        regress.append("sandbox_integrity")
        print("sandbox integrity VIOLATED in candidate")
    sys.exit(1 if regress else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--skill-ref", default="WORKTREE", help="WORKTREE or any git ref")
    r.add_argument("--runs", type=int, default=3)
    r.add_argument("--jobs", type=int, default=4)
    r.add_argument("--cases", nargs="*")
    r.add_argument("--cases-file", default="cases.json")
    r.add_argument("--target", default=DEFAULT_TARGET)
    r.add_argument("--timeout", type=int, default=600)
    r.add_argument("--out", required=True)
    r.set_defaults(fn=cmd_run)
    c = sub.add_parser("compare")
    c.add_argument("baseline")
    c.add_argument("candidate")
    c.set_defaults(fn=cmd_compare)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
