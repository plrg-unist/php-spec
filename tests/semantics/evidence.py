#!/usr/bin/env python3
"""Negative checks for the shared source campaign's implementation identity."""
import copy
import json
import os
import subprocess
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
import validate


def check_inventory_paths():
    with tempfile.TemporaryDirectory(prefix='php-inventory-') as directory:
        root = Path(directory) / 'project'
        features = json.loads((ROOT / 'coverage/semantics/features.json').read_text())
        for entry in features['constructors'] + features['runtime_obligations']:
            for field in ('implementation', 'source_tests', 'helper_tests'):
                for name in entry.get(field, []):
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
        for name in ('scripts/check-semantic-inventory.py', 'spec/schema.json'):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        catalog = root / 'coverage/semantics/features.json'
        catalog.parent.mkdir(parents=True, exist_ok=True)
        def check(value):
            catalog.write_text(json.dumps(value))
            return subprocess.run([sys.executable, str(root / 'scripts/check-semantic-inventory.py')],
                                  capture_output=True, text=True, timeout=5)
        assert check(features).returncode == 0
        missing = copy.deepcopy(features)
        missing['constructors'][0]['implementation'] = ['missing.watsup']
        result = check(missing)
        assert result.returncode and 'missing or escaping implementation path' in result.stdout
        outside = Path(directory) / 'outside-evidence'
        outside.write_text('pass')
        (root / 'evidence-link').symlink_to(outside)
        escaping = copy.deepcopy(features)
        escaping['runtime_obligations'][0]['helper_tests'] = ['evidence-link']
        result = check(escaping)
        assert result.returncode and 'missing or escaping helper_tests path' in result.stdout
        unproved = copy.deepcopy(features)
        unproved['constructors'][0]['status'] = 'validated'
        unproved['constructors'][0]['source_tests'] = []
        result = check(unproved)
        assert result.returncode and 'missing source-level evidence' in result.stdout
        assert check(features).returncode == 0


def main():
    # A disposable project exercises the actual fingerprint function; no live
    # specification, binary or retained acceptance report is mutated.
    with tempfile.TemporaryDirectory(prefix='php-evidence-') as directory:
        root = Path(directory)
        fixed = ['Makefile', 'dune-project', '.tools/php/bin/php',
                 '.tools/php-file.so', '_build/default/adapter/main.exe',
                 'coverage/encoding-spellings.json']
        for name in fixed + ['spec/semantics/rules.watsup', 'tests/fixture.php']:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'original')
        original_root = validate.ROOT
        validate.ROOT = root
        try:
            before = validate.implementation_fingerprint()
            assert before == validate.implementation_fingerprint()
            source = root / 'spec/semantics/rules.watsup'
            stamp = source.stat()
            source.write_bytes(b'modified')  # Same size and restored mtime.
            os.utime(source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            assert before != validate.implementation_fingerprint(), 'stale source bytes accepted'
            source.write_bytes(b'original')
            assert before == validate.implementation_fingerprint()

            added = root / 'spec/semantics/new.watsup'
            added.write_bytes(b'original')
            assert before != validate.implementation_fingerprint(), 'added source path ignored'
            added.unlink()
            moved = source.with_name('renamed.watsup')
            source.rename(moved)
            assert before != validate.implementation_fingerprint(), 'renamed source path ignored'
            moved.rename(source)
            source.unlink()
            assert before != validate.implementation_fingerprint(), 'deleted source path ignored'
            source.write_bytes(b'original')

            binary = root / '.tools/php/bin/php'
            binary.write_bytes(b'modified')
            assert before != validate.implementation_fingerprint(), 'changed oracle binary ignored'
            binary.unlink()
            try:
                validate.implementation_fingerprint()
            except FileNotFoundError:
                pass
            else:
                raise AssertionError('missing pinned oracle accepted')
            binary.write_bytes(b'original')
            assert before == validate.implementation_fingerprint(), 'restored fixture differs'
        finally:
            validate.ROOT = original_root
    check_inventory_paths()
    print('6 stale-identity and 3 invalid-evidence checks rejected; restored identity matched')


if __name__ == '__main__':
    main()
