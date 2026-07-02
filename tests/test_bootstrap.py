from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from insta_creator_bootstrap.core import (
    BootstrapValidationError,
    bootstrap_project,
    validate_bootstrap_environment,
    validate_project_spec,
)


class BootstrapTests(unittest.TestCase):
    def test_validate_project_spec_accepts_template_shape(self) -> None:
        spec = """# Brand Spec: Example

## Project name
Example

## Target platform
Instagram

## Brand voice
...

## Visual rules
...

## CTA conventions
...

## Growth strategy
...

## Approval behavior
Approval channel: main channel
...

## Prohibited angles
...

## Asset constraints
...
"""
        validate_project_spec(spec)

    def test_validate_project_spec_rejects_missing_sections(self) -> None:
        spec = """# Brand Spec: Example

## Project name
Example

## Target platform
Instagram
"""
        with self.assertRaises(BootstrapValidationError):
            validate_project_spec(spec)

    def test_bootstrap_project_creates_expected_scaffold(self) -> None:
        with TemporaryDirectory() as tmp:
            result = bootstrap_project(tmp, project_name="Demo Project")
            target = Path(tmp)
            expected = [
                target / "README.md",
                target / "docs" / "project-spec.md",
                target / "content" / "posts" / ".gitkeep",
            ]
            self.assertFalse(result.dry_run)
            self.assertGreaterEqual(len(result.actions), len(expected))
            for path in expected:
                self.assertTrue(path.exists(), f"missing {path}")
            validate_bootstrap_environment(tmp)

    def test_bootstrap_project_dry_run_does_not_write(self) -> None:
        with TemporaryDirectory() as tmp:
            result = bootstrap_project(tmp, project_name="Dry Run Project", dry_run=True)
            self.assertTrue(result.dry_run)
            self.assertEqual(result.written, ())
            self.assertFalse((Path(tmp) / "README.md").exists())

    def test_cli_apply_and_validate(self) -> None:
        with TemporaryDirectory() as tmp:
            apply = subprocess.run(
                [sys.executable, "-m", "insta_creator_bootstrap", "apply", "--target", tmp, "--project-name", "Cli Project"],
                cwd=str(Path(__file__).resolve().parents[1]),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(apply.returncode, 0, apply.stdout + apply.stderr)
            validate = subprocess.run(
                [sys.executable, "-m", "insta_creator_bootstrap", "validate", "--target", tmp],
                cwd=str(Path(__file__).resolve().parents[1]),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)


if __name__ == "__main__":
    unittest.main()
