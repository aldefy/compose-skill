"""Pure scoring logic for Codex `--json` event traces. No I/O, no Codex dependency.

Skill use is counted ONLY from completed shell commands that exited 0 and whose
command text names the skill's files. The agent's own prose (including any
"REFERENCES USED" line) is never evidence.
"""
import json
import re

SKILL_MD = re.compile(r"compose-expert/SKILL\.md")
REF_FILE = re.compile(r"compose-expert/references/([A-Za-z0-9_\-]+\.md)")
# Reads that name a reference by relative path after a `cd` into the skill dir.
REF_ANY = re.compile(r"references/([A-Za-z0-9_\-]+\.md)")


def parse_events(lines):
    events = []
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    return events


def completed_commands(events):
    out = []
    for e in events:
        it = e.get("item") or {}
        if e.get("type") == "item.completed" and it.get("type") == "command_execution":
            out.append((it.get("command", ""), it.get("exit_code")))
    return out


def final_answer(events):
    last = ""
    for e in events:
        it = e.get("item") or {}
        if e.get("type") == "item.completed" and it.get("type") == "agent_message":
            last = it.get("text", "") or last
    return last


def observe(events):
    """Return what the run provably did."""
    skill_read = False
    refs = []
    for cmd, code in completed_commands(events):
        if code != 0:
            continue
        if SKILL_MD.search(cmd):
            skill_read = True
        names = REF_FILE.findall(cmd)
        if not names and "compose-expert" in cmd:
            names = REF_ANY.findall(cmd)
        for n in names:
            if n not in refs:
                refs.append(n)
    # A reference read without SKILL.md still proves skill use.
    skill_used = skill_read or bool(refs)
    return {"skill_used": skill_used, "skill_md_read": skill_read, "refs_read": refs}


def evaluate(case, events):
    """Score one run against a case. Returns (passed, checks, observed)."""
    obs = observe(events)
    answer = final_answer(events)
    checks = {}
    if case.get("expect_skill"):
        checks["skill_invoked"] = obs["skill_used"]
    if case.get("forbid_skill"):
        checks["skill_not_invoked"] = not obs["skill_used"]
    if case.get("expect_refs_any"):
        checks["expected_ref_read"] = any(r in obs["refs_read"] for r in case["expect_refs_any"])
    for i, rx in enumerate(case.get("findings", [])):
        checks[f"finding_{i}"] = bool(re.search(rx, answer, re.I | re.S))
    checks["answered"] = bool(answer.strip())
    return all(checks.values()), checks, obs


INFRA_HINTS = ("usage limit", "rate limit", "quota", "try again at", "unauthorized",
               "401", "429", "network", "timed out", "overloaded")


def infra_failure(events):
    """Return the failure message if the Codex turn itself failed (usage limit, auth,
    network). Such runs say nothing about the skill and must never count as test
    failures or passes. Only top-level turn.failed / error events count; config
    warnings arrive as item.completed items and are ignored."""
    for e in events:
        if e.get("type") in ("turn.failed", "error"):
            msg = e.get("message") or (e.get("error") or {}).get("message") or "turn failed"
            return str(msg)
    return None


def is_limit(message):
    m = (message or "").lower()
    return "usage limit" in m or "rate limit" in m or "quota" in m


def summarize(case, results):
    """Aggregate run results for one case. Errored runs are excluded from the rate."""
    valid = [r for r in results if not r.get("error")]
    errored = len(results) - len(valid)
    if not valid:
        rate = inv = None
        status = "INCONCLUSIVE"
    else:
        rate = round(sum(1 for r in valid if r["pass"]) / len(valid), 2)
        inv = round(sum(1 for r in valid if r["observed"]["skill_used"]) / len(valid), 2)
        status = "INCOMPLETE" if errored else "OK"
    return {"mode": case["mode"], "gate": case["gate"], "min_pass_rate": case["min_pass_rate"],
            "pass_rate": rate, "skill_invocation_rate": inv, "runs": len(results),
            "valid_runs": len(valid), "errored_runs": errored, "status": status}
