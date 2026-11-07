"""Unit tests for the scorer, using synthetic traces. Run in CI without Codex:
    python3 -m unittest discover -s evals/codex -p 'test_*.py'
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import score  # noqa: E402


def cmd(command, code=0):
    return json.dumps({"type": "item.completed",
                       "item": {"type": "command_execution", "command": command, "exit_code": code}})


def msg(text):
    return json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": text}})


SKILL = "/home/u/.codex/skills/compose-expert"
CASE = {
    "expect_skill": True,
    "expect_refs_any": ["agsl-shaders.md"],
    "findings": ["api 33"],
}


class ScoreTests(unittest.TestCase):
    def ev(self, *lines):
        return score.parse_events(list(lines))

    def test_pass_when_skill_and_ref_read_by_command(self):
        e = self.ev(cmd(f"cat {SKILL}/SKILL.md"),
                    cmd(f"cat {SKILL}/references/agsl-shaders.md"),
                    msg("Needs API 33 gate."))
        ok, checks, obs = score.evaluate(CASE, e)
        self.assertTrue(ok, checks)
        self.assertEqual(obs["refs_read"], ["agsl-shaders.md"])

    def test_agent_prose_is_not_evidence(self):
        e = self.ev(cmd("rg -n shader ."),
                    msg("Needs API 33 gate.\nREFERENCES USED: compose-expert/references/agsl-shaders.md"))
        ok, checks, obs = score.evaluate(CASE, e)
        self.assertFalse(ok)
        self.assertFalse(checks["skill_invoked"])
        self.assertEqual(obs["refs_read"], [])

    def test_failed_command_does_not_count(self):
        e = self.ev(cmd(f"cat {SKILL}/SKILL.md", code=1), msg("API 33"))
        self.assertFalse(score.observe(e)["skill_used"])

    def test_wrong_reference_fails_expected_ref(self):
        e = self.ev(cmd(f"cat {SKILL}/SKILL.md"),
                    cmd(f"cat {SKILL}/references/animation.md"), msg("API 33"))
        ok, checks, _ = score.evaluate(CASE, e)
        self.assertFalse(ok)
        self.assertFalse(checks["expected_ref_read"])

    def test_missing_finding_fails(self):
        e = self.ev(cmd(f"cat {SKILL}/SKILL.md"),
                    cmd(f"cat {SKILL}/references/agsl-shaders.md"), msg("Looks fine."))
        ok, checks, _ = score.evaluate(CASE, e)
        self.assertFalse(ok)
        self.assertFalse(checks["finding_0"])

    def test_forbid_skill(self):
        case = {"forbid_skill": True, "findings": ["gradle"]}
        clean = self.ev(cmd("cat settings.gradle.kts"), msg("Gradle includes :shared"))
        dirty = self.ev(cmd(f"cat {SKILL}/SKILL.md"), msg("Gradle includes :shared"))
        self.assertTrue(score.evaluate(case, clean)[0])
        self.assertFalse(score.evaluate(case, dirty)[0])

    def test_reference_read_without_skill_md_still_counts_as_use(self):
        e = self.ev(cmd(f"cd {SKILL} && cat references/agsl-shaders.md"), msg("API 33"))
        self.assertTrue(score.observe(e)["skill_used"])

    def test_empty_answer_fails(self):
        e = self.ev(cmd(f"cat {SKILL}/SKILL.md"))
        ok, checks, _ = score.evaluate({"expect_skill": True}, e)
        self.assertFalse(ok)
        self.assertFalse(checks["answered"])

    def test_garbage_lines_are_ignored(self):
        e = score.parse_events(["Reading additional input from stdin...", "", "{bad json", msg("hi")])
        self.assertEqual(score.final_answer(e), "hi")


class InfraTests(unittest.TestCase):
    LIMIT = json.dumps({"type": "turn.failed", "error": {"message": "You've hit your usage limit."}})

    def test_turn_failed_is_infra(self):
        e = score.parse_events([self.LIMIT])
        self.assertIn("usage limit", score.infra_failure(e))
        self.assertTrue(score.is_limit(score.infra_failure(e)))

    def test_config_warning_item_is_not_infra(self):
        warn = json.dumps({"type": "item.completed", "item": {"type": "error", "message": "ignoring config"}})
        self.assertIsNone(score.infra_failure(score.parse_events([warn, msg("ok")])))

    def test_errored_runs_excluded_from_rate(self):
        case = {"mode": "explicit", "gate": True, "min_pass_rate": 1.0}
        ok = {"pass": True, "observed": {"skill_used": True}}
        err = {"error": "usage limit", "pass": None, "observed": {"skill_used": False}}
        s = score.summarize(case, [ok, ok, err])
        self.assertEqual((s["pass_rate"], s["valid_runs"], s["status"]), (1.0, 2, "INCOMPLETE"))

    def test_all_errored_is_inconclusive_not_zero(self):
        case = {"mode": "explicit", "gate": True, "min_pass_rate": 1.0}
        err = {"error": "usage limit", "pass": None, "observed": {"skill_used": False}}
        s = score.summarize(case, [err, err])
        self.assertIsNone(s["pass_rate"])
        self.assertEqual(s["status"], "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
