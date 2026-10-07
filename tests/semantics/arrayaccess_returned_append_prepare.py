"""Compile genuine returned-child append states; execution remains separate."""
from pathlib import Path
import base64
import json
import subprocess
import sys
import tempfile

from recorded_worker import Worker
from error_handler_run import ROOT, ENV, describe, recorded, group
from arrayaccess_returned_append_cases import CASES as AUTHOR_SOURCES, OBSERVED_STDOUT as AUTHOR_STDOUT
from arrayaccess_returned_append_review_cases import CASES as REVIEW_SOURCES, OBSERVED_STDOUT as REVIEW_STDOUT
from arrayaccess_returned_append_protocol import PREFIX, CASES as APPEND_CASES
from arrayaccess_returned_append_lifetime_cases import CASES as LIFETIME_SOURCES, OBSERVED_STDOUT as LIFETIME_STDOUT
from arrayaccess_returned_append_lifetime_protocol import CASES as LIFETIME_CASES

SOURCES = {row['id']: row['source'].encode() for row in AUTHOR_SOURCES + REVIEW_SOURCES + LIFETIME_SOURCES}
OBSERVED_STDOUT = AUTHOR_STDOUT | REVIEW_STDOUT | LIFETIME_STDOUT
CASES = APPEND_CASES + LIFETIME_CASES


def revision():
    return {key: subprocess.check_output(['git', *command], cwd=ROOT, env=ENV).decode().strip()
            for key, command in [('head', ['rev-parse', 'HEAD']), ('tree', ['rev-parse', 'HEAD^{tree}']),
                                 ('status', ['status', '--porcelain'])]}


def main():
    assert Path.cwd() == ROOT
    before = revision()
    selected = set(sys.argv[1:]) or {case[0] for case in CASES}
    assert selected <= {case[0] for case in CASES}
    store = ROOT / '.tools/arrayaccess-returned-append'
    store.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='prepared-', dir=store))
    print(out, flush=True)
    watched_names = [
        'tests/semantics/arrayaccess_returned_append_cases.py',
        'tests/semantics/arrayaccess_returned_append_review_cases.py',
        'tests/semantics/arrayaccess_returned_append_protocol.py',
        'tests/semantics/arrayaccess_returned_append_prepare.py',
        'tests/semantics/arrayaccess_returned_append_lifetime_cases.py',
        'tests/semantics/arrayaccess_returned_append_lifetime_protocol.py',
        'tests/semantics/error_handler_protocol.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/profile.json',
        'spec/semantics/modules.json',
        'spec/semantics/242-dimension-write-continuations.watsup',
        'spec/semantics/255-nested-unset-append-continuations.watsup',
        'spec/semantics/292-arrayaccess-write-dimensions.watsup',
        'spec/semantics/304-arrayaccess-append-dimensions.watsup',
        'spec/semantics/309-arrayaccess-returned-append.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        '.tools/spectec/bin/p4spectec']
    watched = {str(ROOT / name): describe(ROOT / name) for name in watched_names}
    modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    rows, failure = [], None
    try:
        for name, source_id, stage, checks in CASES:
            if name not in selected:
                continue
            source, expected = SOURCES[source_id], OBSERVED_STDOUT[source_id]
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
                    assert parsed['accepted'], parsed
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok'], checked
                finally:
                    adapter.close()
            finally:
                frontend.close()
            filename = json.dumps(base64.b64encode(str(path).encode()).decode())
            conditions = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + filename + ')',
                'S_initial.COMPLETION = BUDGET',
                'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
                r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
                'S = S_reached[.COMPLETION = NORMAL]', *checks,
                '$outputs(S_done.EVENTS) = [' + ','.join(map(str, expected)) + ']']
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in conditions))
            producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)], directory / 'compiler', 120)
            al = directory / 'compiler.stdout'
            emitted = al.read_bytes()
            markers = {marker: ('def $' + marker).encode() in emitted for marker in ('main', 'seek', 'access_finish_task', 'eager_written_task')}
            passed = (producer['exit'] == 0 and not producer['timeout'] and not producer['group_after']
                and not (directory / 'compiler.stderr').read_bytes() and all(markers.values()))
            rows.append({'id': name, 'source_id': source_id, 'source': str(path),
                'fixture': str(fixture), 'al': str(al), 'source_descriptor': describe(path),
                'fixture_descriptor': describe(fixture), 'al_descriptor': describe(al),
                'assertions': len(conditions), 'markers': markers, 'producer': producer, 'passed': passed})
            print(name, passed, len(conditions), flush=True)
            assert passed, name
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    stable = watched == {path: describe(path) for path in watched}
    after = revision()
    groups = {str(row['producer']['pgid']): group(row['producer']['pgid']) for row in rows}
    passed = (failure is None and stable and before == after and len(rows) == len(selected)
              and all(row['passed'] for row in rows) and all(not members for members in groups.values()))
    (out / 'report.json').write_text(json.dumps({'passed': passed,
        'scope': 'Compiler preparation only; no new source/state execution credit',
        'revision': before, 'revision_after': after, 'inputs': watched, 'records': rows,
        'failure': failure, 'inputs_stable': stable, 'groups_after': groups,
        'jobs': 1, 'compiler_cap_seconds': 120}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
