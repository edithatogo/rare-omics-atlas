"""Exercise the trusted-main cleanup against real squash history and Git leases."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


@unittest.skipUnless(sys.platform == "linux", "Cleanup runs on the Ubuntu Actions runner")
class PruneWorkflow(unittest.TestCase):
    def test_squash_and_ref_guards(self):
        for tool in ("git", "bash", "jq"):
            self.assertIsNotNone(shutil.which(tool), f"Linux workflow test requires {tool}")
        real_git = shutil.which("git")
        assert real_git is not None
        workflow = (
            Path(__file__).resolve().parents[2] / ".github/workflows/prune-merged-20261124.yml"
        )
        script = textwrap.dedent(workflow.read_text().split("        run: |\n", 1)[1])
        before, allowlist = script.split("done <<'APPROVED'\n", 1)
        _, after = allowlist.split("\nAPPROVED\n", 1)
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            work, remote, bin_dir = (root / name for name in ("work", "remote.git", "bin"))
            work.mkdir()
            bin_dir.mkdir()

            def git(*args):
                return subprocess.run(
                    [real_git, *args], cwd=work, env=env, check=True, capture_output=True, text=True
                ).stdout.strip()

            git("init", "--initial-branch=main")
            git("config", "user.name", "Cleanup fixture")
            git("config", "user.email", "cleanup@example.invalid")
            git("config", "commit.gpgsign", "false")
            (work / "sample").write_text("base\n")
            git("add", ".")
            git("commit", "-m", "Base")
            git("switch", "-c", "approved")
            (work / "sample").write_text("change\n")
            git("commit", "-am", "Source change")
            head = git("rev-parse", "HEAD")
            git("switch", "main")
            git("merge", "--squash", "approved")
            git("commit", "-m", "Squash source change")
            merged = git("rev-parse", "HEAD")
            self.assertEqual(git("merge-base", head, merged), git("rev-parse", head + "^"))
            self.assertNotEqual(head, merged)
            git("switch", "approved")
            (work / "sample").write_text("later work\n")
            git("commit", "-am", "Unmerged later work")
            advanced = git("rev-parse", "HEAD")
            git("switch", "main")
            git("init", "--bare", str(remote))
            git("remote", "add", "origin", str(remote))
            git("push", "origin", "main", "approved")

            repo = "edithatogo/rare-omics-atlas"
            pr = {
                "state": "closed",
                "merged": True,
                "merged_at": "2026-11-24T00:00:00Z",
                "merge_commit_sha": merged,
                "head": {"repo": {"full_name": repo}, "ref": "approved", "sha": head},
                "base": {"repo": {"full_name": repo}, "ref": "main"},
            }
            (bin_dir / "gh").write_text(
                "#!/usr/bin/env bash\nset -eu\n"
                f"if [ \"$*\" = 'api repos/{repo}/pulls/2' ]; then\n"
                "  printf '%s\\n' \"$TEST_PR\"\n"
                f"elif [ \"$*\" = 'api --paginate --slurp repos/{repo}/pulls?state=open&per_page=100' ]; then\n"
                "  printf '%s\\n' \"$TEST_OPEN\"\nelse exit 2; fi\n"
            )
            # Only the observation-to-deletion race is injected; Git enforces the real lease.
            (bin_dir / "git").write_text(
                f"#!{sys.executable}\n"
                + textwrap.dedent("""\
                    import os, subprocess, sys
                    from pathlib import Path
                    args = sys.argv[1:]
                    real = os.environ["TEST_GIT"]
                    marker = Path(os.environ["TEST_MARKER"])
                    if (os.environ["TEST_RACE"] == "1" and not marker.exists()
                            and args == ["ls-remote", "--heads", "origin", "refs/heads/approved"]):
                        result = subprocess.run([real, *args], check=True, capture_output=True, text=True)
                        subprocess.run([real, "--git-dir", os.environ["TEST_REMOTE"], "update-ref",
                                        "refs/heads/approved", os.environ["TEST_ADVANCED"]], check=True)
                        marker.touch()
                        sys.stdout.write(result.stdout)
                    else:
                        os.execv(real, [real, *args])
                    """)
            )
            for name in ("gh", "git"):
                (bin_dir / name).chmod(0o755)
            command = before + f"done <<'APPROVED'\n2 approved {head}\nAPPROVED\n" + after
            env.update(
                PATH=str(bin_dir) + os.pathsep + env["PATH"],
                GITHUB_REPOSITORY=repo,
                GITHUB_REF="refs/heads/main",
                GITHUB_SHA=merged,
                TEST_PR=json.dumps(pr),
                TEST_GIT=real_git,
                TEST_REMOTE=str(remote),
                TEST_ADVANCED=advanced,
                TEST_MARKER=str(root / "raced"),
            )
            for case in ("squash", "advanced", "open_head", "open_base", "race"):
                with self.subTest(case=case):
                    live = advanced if case == "advanced" else head
                    git("push", "--force", "origin", f"{live}:refs/heads/approved")
                    active = []
                    if case == "open_head":
                        active = [{"head": pr["head"], "base": pr["base"]}]
                    elif case == "open_base":
                        active = [{"head": {"ref": "other"}, "base": {"ref": "approved"}}]
                    env.update(
                        TEST_OPEN=json.dumps([active]), TEST_RACE="1" if case == "race" else "0"
                    )
                    result = subprocess.run(
                        ["bash", "-c", command], cwd=work, env=env, capture_output=True, text=True
                    )
                    actual = git("ls-remote", "--heads", "origin", "refs/heads/approved")
                    expected = "" if case == "squash" else advanced if case == "race" else live
                    self.assertEqual(actual.split()[0] if actual else "", expected, result.stderr)
                    if case == "race":
                        self.assertTrue((root / "raced").exists())
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
