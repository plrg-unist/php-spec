#!/usr/bin/env python3
"""Restore callbacks preserve active and saved argument frames during a property write."""
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

SOURCE = '<?php class R{function __toString(){echo "R",func_num_args();ini_set("include_path","inner\\0tail");return "include_path";}} class P{function __toString(){echo "P";ini_restore(new R);echo ini_set("include_path","after");return "s\\0typed";}} class H{public static string $p="old";} function store($v){echo "B";H::$p=$v;echo func_num_args();} ini_set("include_path","seed\\0old");store(new P);echo "|",H::$p;'


def snapshot():
    modules = json.loads((cross.ROOT / 'spec/semantics/modules.json').read_text())
    paths = [*modules, 'spec/semantics/modules.json', 'tests/semantics/profile.json',
             'tests/semantics/typed_static_restore.py',
             'tests/semantics/typed_static_ini_prefix_protocol.py',
             'tests/semantics/typed_static_invoke_set_protocol.py',
             '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe']
    return {'source': cross.snapshot(None),
            'sha256': {name: cross.invoke.sha(cross.ROOT / name) for name in paths}}


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot()
    out = Path(tempfile.mkdtemp(prefix='typed-static-restore-source-', dir=cross.ROOT / '.tools'))
    path = out / 'main.php'; path.write_text(SOURCE)
    report = {'passed': False, 'completed': False, 'before': before,
              'profile': cross.invoke.types.PROFILE, 'source_sha256': cross.invoke.sha(path),
              'expected_stdout': 'BPR0.:1|s\x00typed', 'expected_exit_status': 0}
    print(out, flush=True)
    try:
        report['outcome'] = cross.source({'abrupt': False, 'expected_stdout': 'BPR0.:1|s\x00typed',
                                         'expected_exit_status': 0}, out, path)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = snapshot()
        report['passed'] = report['passed'] and report['before'] == report['after']
        report['raw_files'] = {str(p.relative_to(cross.ROOT)): {'sha256': cross.invoke.sha(p),
            'bytes': p.stat().st_size, 'mode': oct(p.stat().st_mode & 0o7777)}
            for p in sorted(out.rglob('*')) if p.is_file()}
        receipt = out / 'report.json'; receipt.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        print(receipt, cross.invoke.sha(receipt), 'pass', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
