"""Shared fixtures: load the hyphenated scripts as modules and build throwaway repositories."""

import contextlib
import importlib.util
import io
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def load_script(filename):
    spec = importlib.util.spec_from_file_location(filename.replace("-", "_")[:-3], SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FixtureRepo:
    """A temporary repository root with plugins, skills, agents and eval cases."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def cleanup(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def plugin(self, name):
        self.write(f"plugins/{name}/.claude-plugin/plugin.json", f'{{"name": "{name}"}}\n')

    def skill(self, plugin, name, description, extra=""):
        self.plugin(plugin)
        return self.write(
            f"plugins/{plugin}/skills/{name}/SKILL.md",
            f"---\nname: {name}\ndescription: {description}\n{extra}---\n\n# {name}\n",
        )

    def agent(self, plugin, name, description):
        self.plugin(plugin)
        return self.write(
            f"plugins/{plugin}/agents/{name}.md",
            f"---\nname: {name}\ndescription: {description}\n---\n\nBody.\n",
        )


def run_main(module, argv):
    """Run module.main(argv); return (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = module.main(argv)
    return code, out.getvalue(), err.getvalue()
