# backup-verify

Record a manifest of a folder (SHA-256 and size for every file), then later check the folder against it.
Reports changed, missing, and new files. Standard library only.

    python3 -m backupverify create /path/to/data data.manifest.json
    python3 -m backupverify verify /path/to/data data.manifest.json

Exit codes: 0 clean, 1 differences found, 2 usage or input error.
Symlinks are skipped, so links cannot pull in files from outside the folder.

Run the tests: `python3 -m unittest -q tests.test_verify`
