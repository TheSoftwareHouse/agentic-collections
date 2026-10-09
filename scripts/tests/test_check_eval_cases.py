import unittest

from helpers import FixtureRepo, load_script, run_main

check = load_script("check-eval-cases.py")

README = """# Checking skill routing

## Known failures

| Case | Observed | Fix lives in |
| :-- | :-- | :-- |
{rows}
"""


def grader(name, skill, negative):
    lines = [
        f"  - name: {name}",
        "    type: tool_used",
        "    tool: Skill",
        f"    input_match: '\"skill\"\\s*:\\s*\"(?:[\\w-]+:)?{skill}\"'",
    ]
    lines += ["    min: 0", "    max: 0"] if negative else ["    arm: with-only"]
    return "\n".join(lines)


def case_yaml(name, fire="audit", sibling="build", tags="[routing]", max_turns=1,
              allowed="[Skill]", plugins='["../../../plugins/tsh-a"]', extra=""):
    graders = []
    if fire:
        graders.append(grader("fired", fire, negative=False))
    if sibling:
        graders.append(grader("sibling-not-fired", sibling, negative=True))
    return f"""schema_version: "1.1"
name: {name}
description: An audit request must route to audit.
# a comment between keys
tags: {tags}
plugins: {plugins}
runs: 1
{extra}execution:
  prompt: |
    Audit the checkout page.

    Report every violation.
  max_turns: {max_turns}
  allowed_tools: {allowed}
graders:
{chr(10).join(graders)}
"""


class ParseCase(unittest.TestCase):
    def test_block_scalar_keeps_blank_lines_and_drops_indent(self):
        data, _ = check.parse_case(case_yaml("x"))
        self.assertEqual(data["execution"]["prompt"], "Audit the checkout page.\n\nReport every violation.\n")

    def test_flow_list_with_quoted_commas(self):
        data, _ = check.parse_case('plugins: ["a, b", \'c\', d]\n')
        self.assertEqual(data["plugins"], ["a, b", "c", "d"])

    def test_list_of_mappings_and_line_numbers(self):
        data, lines = check.parse_case(case_yaml("x"))
        self.assertEqual(data["graders"][1]["max"], 0)
        self.assertEqual(lines["graders.1.input_match"], 24)

    def test_rejects_unsupported_constructs(self):
        with self.assertRaises(check.ParseError):
            check.parse_case("execution: {prompt: hi}\n")
        with self.assertRaises(check.ParseError):
            check.parse_case("execution:\n  nested:\n    deeper: 1\n")


class Check(unittest.TestCase):
    def setUp(self):
        self.repo = FixtureRepo()
        self.repo.skill("tsh-a", "audit", "Audits pages")
        self.repo.skill("tsh-a", "build", "Builds components")
        self.repo.skill("tsh-a", "manual", "Entry point", extra="disable-model-invocation: true\n")
        self.readme([])

    def tearDown(self):
        self.repo.cleanup()

    def readme(self, quarantined):
        rows = "\n".join(f"| `{name}` | flaky | tsh-a |" for name in quarantined)
        self.repo.write("evals/README.md", README.format(rows=rows))

    def case(self, name, **kwargs):
        self.repo.write(f"evals/routing/{name}/case.yaml", case_yaml(name, **kwargs))

    def run_check(self, *extra):
        return run_main(check, ["--root", str(self.repo.root), *extra])

    def assert_fails_with(self, message):
        code, _, err = self.run_check()
        self.assertEqual(code, 1, err)
        self.assertIn(message, err)

    def test_valid_case_passes_and_counts_coverage(self):
        self.case("audit-not-build")
        code, out, err = self.run_check("--coverage")
        self.assertEqual(code, 0, err)
        self.assertIn("1 of 2 model-invocable skills", out)
        self.assertIn("no must-fire case: tsh-a:build", out)

    def test_misspelled_must_not_fire_skill_fails(self):
        self.case("audit-not-build", sibling="biuld")
        self.assert_fails_with("names skill 'biuld', which none of the case's plugins ships")

    def test_skill_from_a_plugin_the_case_does_not_load_fails(self):
        self.repo.skill("tsh-b", "elsewhere", "Lives in another plugin")
        self.case("audit-not-build", sibling="elsewhere")
        self.assert_fails_with("names skill 'elsewhere'")

    def test_skill_the_model_cannot_invoke_fails(self):
        self.case("audit-not-build", sibling="manual")
        self.assert_fails_with("disable-model-invocation: true")

    def test_name_must_match_directory(self):
        self.repo.write("evals/routing/renamed/case.yaml", case_yaml("original"))
        self.assert_fails_with("does not match directory 'renamed'")

    def test_more_than_one_turn_fails(self):
        self.case("x", max_turns=3)
        self.assert_fails_with("max_turns must be 1")

    def test_extra_tools_fail(self):
        self.case("x", allowed="[Skill, Bash]")
        self.assert_fails_with("allowed_tools must be [Skill]")

    def test_scaffold_script_fails(self):
        self.case("x", extra="scaffold_script: setup.sh\n")
        self.assert_fails_with("must not declare scaffold_script")

    def test_case_without_a_must_not_fire_grader_fails(self):
        self.case("x", sibling=None)
        self.assert_fails_with("no must-not-fire grader")

    def test_unresolved_plugin_path_fails(self):
        self.case("x", plugins='["../../../plugins/tsh-missing"]')
        self.assert_fails_with("does not resolve to a plugin")

    def test_case_needs_exactly_one_status_tag(self):
        self.case("x", tags="[routing, known-failure]")
        self.assert_fails_with("exactly one of 'routing' or 'known-failure'")

    def test_quarantined_case_must_be_listed(self):
        self.case("x", tags="[known-failure]")
        self.assert_fails_with("missing from the Known failures table")

    def test_listed_case_must_be_quarantined(self):
        self.case("x")
        self.readme(["x"])
        self.assert_fails_with("lists 'x', which is not a known-failure case")

    def test_listed_quarantined_case_passes_but_earns_no_coverage(self):
        self.case("x", tags="[known-failure]")
        self.readme(["x"])
        code, out, err = self.run_check()
        self.assertEqual(code, 0, err)
        self.assertIn("1 quarantined; 0 of 2", out)

    def test_directory_without_case_file_fails(self):
        (self.repo.root / "evals/routing/empty").mkdir(parents=True)
        self.assert_fails_with("directory has no case.yaml")


if __name__ == "__main__":
    unittest.main()
