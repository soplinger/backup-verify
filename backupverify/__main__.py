"""Command line: create a manifest, or verify a folder against one.

Exit codes: 0 clean, 1 differences found, 2 usage or input error.
"""

import sys
from pathlib import Path

from .manifest import build_manifest, load_manifest, save_manifest
from .verify import verify

USAGE = (
    "usage: python3 -m backupverify create <dir> <manifest.json>\n"
    "       python3 -m backupverify verify <dir> <manifest.json>"
)


def main(argv: list) -> int:
    if len(argv) != 4 or argv[1] not in ("create", "verify"):
        print(USAGE, file=sys.stderr)
        return 2
    command, root, manifest_path = argv[1], Path(argv[2]), Path(argv[3])
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    try:
        if command == "create":
            manifest = build_manifest(root)
            save_manifest(manifest, manifest_path)
            print(f"wrote {len(manifest['files'])} file(s) to {manifest_path}")
            return 0
        manifest = load_manifest(manifest_path)
        report = verify(root, manifest)
    except (OSError, ValueError) as e:
        print(f"{command} failed: {e}", file=sys.stderr)
        return 2
    print(
        f"ok: {len(report.ok)}  changed: {len(report.changed)}  "
        f"missing: {len(report.missing)}  new: {len(report.new)}"
    )
    for label, items in (("changed", report.changed), ("missing", report.missing), ("new", report.new)):
        for rel in items:
            print(f"{label}: {rel}")
    return 0 if report.clean else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
