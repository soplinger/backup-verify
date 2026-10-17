"""Record and load a manifest of file sizes and SHA-256 hashes. Standard library only."""

import hashlib
import json
from pathlib import Path

CHUNK_SIZE = 1024 * 1024
MANIFEST_VERSION = 1


def sha256_file(path: Path) -> str:
    """Hash a file in chunks, so large files do not need to fit in memory."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(root: Path) -> dict:
    """Hash every regular file under root. Symlinks are skipped, so links cannot pull in outside files."""
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        files[rel] = {"size": path.stat().st_size, "sha256": sha256_file(path)}
    return {"version": MANIFEST_VERSION, "root_name": root.name, "files": files}


def save_manifest(manifest: dict, out: Path) -> None:
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("version") != MANIFEST_VERSION:
        raise ValueError(f"unsupported manifest version: {manifest.get('version')!r}")
    return manifest
