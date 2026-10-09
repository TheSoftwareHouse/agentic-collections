import json
import unittest

from helpers import FixtureRepo, load_script, run_main

lint = load_script("lint-descriptions.py")

SHARED = "Audits Terraform state against the live cloud account for drift, waste and missing tags"
OTHER = "Writes Playwright end-to-end tests with page objects and user-visible locators"


class ParseFrontmatter(unittest.TestCase):
    def setUp(self):
        self.repo = FixtureRepo()

    def tearDown(self):
        self.repo.cleanup()

    def parse(self, frontmatter):
        return lint.parse_frontmatter(self.repo.write("SKILL.md", f"---\n{frontmatter}\n---\nbody\n"))

    def test_plain_value_drops_trailing_comment(self):
        data, _ = self.parse("name: x\ndescription: Does a thing # internal note")
        self.assertEqual(data["description"], "Does a thing")

    def test_double_quoted_value_unescapes(self):
        data, _ = self.parse('description: "Says \\"hi\\" and: more"')
        self.assertEqual(data["description"], 'Says "hi" and: more')

    def test_single_quoted_value_unescapes(self):
        data, _ = self.parse("description: 'It''s fine'")
        self.assertEqual(data["description"], "It's fine")

    def test_description_line_points_at_the_key(self):
        _, line = self.parse("name: x\nmodel: sonnet\ndescription: here")
        self.assertEqual(line, 4)

    def test_rejects_block_scalar(self):
        with self.assertRaisesRegex(lint.ParseError, "block scalar"):
            self.parse("description: >\n  folded")

    def test_rejects_multi_line_plain_value(self):
        with self.assertRaisesRegex(lint.ParseError, "multi-line"):
            self.parse("description: starts here\n  and continues")

    def test_rejects_missing_frontmatter(self):
        path = self.repo.write("SKILL.md", "# no frontmatter\n")
        with self.assertRaisesRegex(lint.ParseError, "opening"):
            lint.parse_frontmatter(path)

    def test_rejects_unterminated_quote(self):
        with self.assertRaisesRegex(lint.ParseError, "unterminated"):
            self.parse('description: "never closed')


class Collect(unittest.TestCase):
    def setUp(self):
        self.repo = FixtureRepo()

    def tearDown(self):
        self.repo.cleanup()

    def test_skips_skills_the_model_cannot_invoke(self):
        self.repo.skill("tsh-a", "routed", SHARED)
        self.repo.skill("tsh-a", "manual", SHARED, extra="disable-model-invocation: true\n")
        components, errors = lint.collect(self.repo.root)
        self.assertEqual([c["id"] for c in components], ["tsh-a:routed"])
        self.assertEqual(errors, [])

    def test_agent_ids_carry_an_at_sign(self):
        self.repo.agent("tsh-a", "auditor", SHARED)
        components, _ = lint.collect(self.repo.root)
        self.assertEqual(components[0]["id"], "tsh-a:@auditor")

    def test_when_to_use_joins_the_routing_text(self):
        self.repo.skill("tsh-a", "x", "First part", extra="when_to_use: second part\n")
        components, _ = lint.collect(self.repo.root)
        self.assertEqual(components[0]["text"], "First part second part")

    def test_unparseable_component_is_an_error_not_a_skip(self):
        self.repo.plugin("tsh-a")
        self.repo.write("plugins/tsh-a/skills/broken/SKILL.md", "---\ndescription: |\n  x\n---\n")
        components, errors = lint.collect(self.repo.root)
        self.assertEqual(components, [])
        self.assertEqual(len(errors), 1)


class Main(unittest.TestCase):
    def setUp(self):
        self.repo = FixtureRepo()
        self.config = {"warn_above": 0.35, "fail_above": 0.5, "exclusive_bonus": 0.6,
                       "exclusive_groups": [], "allowed_pairs": []}
        self.repo.skill("tsh-z", "unrelated", OTHER)

    def tearDown(self):
        self.repo.cleanup()

    def run_lint(self):
        config = self.repo.write("lint.json", json.dumps(self.config))
        return run_main(lint, ["--root", str(self.repo.root), "--config", str(config), "--top", "50"])

    def test_identical_descriptions_in_two_plugins_fail(self):
        self.repo.skill("tsh-a", "one", SHARED)
        self.repo.skill("tsh-b", "two", SHARED)
        code, out, _ = self.run_lint()
        self.assertEqual(code, 1)
        self.assertIn("FAIL     tsh-a:one / tsh-b:two", out)

    def test_distinct_descriptions_pass(self):
        self.repo.skill("tsh-a", "one", SHARED)
        code, _, _ = self.run_lint()
        self.assertEqual(code, 0)

    def test_skill_and_agent_of_one_plugin_are_not_compared(self):
        self.repo.skill("tsh-a", "audit", SHARED)
        self.repo.agent("tsh-a", "auditor", SHARED)
        code, out, _ = self.run_lint()
        self.assertEqual(code, 0)
        self.assertNotIn("tsh-a:@auditor / tsh-a:audit", out)
        self.assertNotIn("tsh-a:audit / tsh-a:@auditor", out)

    def test_mutually_exclusive_plugins_get_the_bonus(self):
        self.repo.skill("tsh-a", "one", SHARED)
        self.repo.skill("tsh-b", "two", SHARED)
        self.config["exclusive_groups"] = [{"name": "clouds", "plugins": ["tsh-a", "tsh-b"]}]
        code, out, _ = self.run_lint()
        self.assertEqual(code, 0)
        self.assertIn("[exclusive]", out)

    def test_allowed_pair_never_fails(self):
        self.repo.skill("tsh-a", "one", SHARED)
        self.repo.skill("tsh-b", "two", SHARED)
        self.config["allowed_pairs"] = [{"a": "tsh-b:two", "b": "tsh-a:one", "reason": "proven"}]
        code, out, _ = self.run_lint()
        self.assertEqual(code, 0)
        self.assertIn("WARN     tsh-a:one / tsh-b:two [allowed]", out)

    def test_allowed_pair_naming_a_missing_component_fails(self):
        self.repo.skill("tsh-a", "one", SHARED)
        self.config["allowed_pairs"] = [{"a": "tsh-a:one", "b": "tsh-a:renamed", "reason": "stale"}]
        code, _, err = self.run_lint()
        self.assertEqual(code, 1)
        self.assertIn("unknown component tsh-a:renamed", err)


if __name__ == "__main__":
    unittest.main()
