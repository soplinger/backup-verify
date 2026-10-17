"""Compare a folder with a saved manifest."""

from dataclasses import dataclass, field
from pathlib import Path

from .manifest import build_manifest


@dataclass
class Report:
    ok: list = field(default_factory=list)
    changed: list = field(default_factory=list)
    missing: list = field(default_factory=list)
    new: list = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (self.changed or self.missing or self.new)


def verify(root: Path, manifest: dict) -> Report:
    """Rehash root and classify each file against the manifest. A file counts as changed if its size or hash differs."""
    expected = manifest["files"]
    current = build_manifest(root)["files"]
    report = Report()
    for rel in sorted(expected):
        if rel not in current:
            report.missing.append(rel)
        elif current[rel] == expected[rel]:
            report.ok.append(rel)
        else:
            report.changed.append(rel)
    report.new = sorted(set(current) - set(expected))
    return report
