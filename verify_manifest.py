#!/usr/bin/env python3
"""Verify the released files against MANIFEST.json using only the standard library."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent

def main() -> int:
    try:
        manifest = json.loads((ROOT / 'MANIFEST.json').read_text(encoding='utf-8'))
        failures = []
        seen = set()
        for item in manifest['files']:
            relative = item['path']
            path = (ROOT / relative).resolve()
            if relative in seen or not path.is_relative_to(ROOT):
                failures.append({'path': relative, 'error': 'duplicate or unsafe path'})
                continue
            seen.add(relative)
            if not path.is_file():
                failures.append({'path': relative, 'error': 'missing file'})
                continue
            data = path.read_bytes()
            if len(data) != item['size_bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
                failures.append({'path': relative, 'error': 'size or SHA-256 mismatch'})
        print(json.dumps({'status': 'FAIL' if failures else 'PASS',
                          'files_checked': len(seen), 'failures': failures}, indent=2))
        return 1 if failures else 0
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(f'Manifest verification failed: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
