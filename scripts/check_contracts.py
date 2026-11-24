#!/usr/bin/env python3
"""Check local document links, JSON syntax and the Conductor dependency graph."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import TypedDict, cast

ROOT = Path(__file__).resolve().parents[1]


class Milestone(TypedDict):
    id: str
    requires: list[str]
    status: str


class Dependencies(TypedDict):
    milestones: list[Milestone]


def validate_graph(milestones: list[Milestone]) -> None:
    graph = {item["id"]: item["requires"] for item in milestones}
    if len(graph) != len(milestones):
        raise ValueError("Duplicate milestone identifier")
    visited: set[str] = set()
    active: set[str] = set()

    def visit(name: str) -> None:
        if name not in graph:
            raise ValueError(f"Unknown prerequisite: {name}")
        if name in active:
            raise ValueError(f"Dependency cycle: {name}")
        if name not in visited:
            active.add(name)
            for dependency in graph[name]:
                visit(dependency)
            active.remove(name)
            visited.add(name)

    for name in graph:
        visit(name)


def main() -> None:
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        text=True,
    ).split("\0")
    for name in sorted(set(names)):
        path = ROOT / name
        if not name or not path.is_file() or path.is_symlink():
            continue
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
        if path.suffix == ".md":
            for link in re.findall(r"\[[^\]]*\]\(([^\s)]+)", path.read_text(encoding="utf-8")):
                target = link.split("#", 1)[0]
                if target and ":" not in target and not (path.parent / target).exists():
                    raise ValueError(f"Broken local link in {name}: {target}")
    dependencies = cast(
        Dependencies, json.loads((ROOT / "conductor/dependencies.json").read_text())
    )
    validate_graph(dependencies["milestones"])
    print(f"Local links, JSON and {len(dependencies['milestones'])} milestones passed")


if __name__ == "__main__":
    main()
