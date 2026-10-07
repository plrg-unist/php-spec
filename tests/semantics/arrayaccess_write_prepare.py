"""Compile genuine writable ArrayAccess states; execution is a separate phase."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tests/semantics'))
from recorded_worker import Worker
from arrayaccess_write_cases import CASES as AUTHOR_SOURCES
from arrayaccess_write_review_cases import CASES as REVIEW_SOURCES
from arrayaccess_write_protocol import CASES, PREFIX
from error_handler_run import ROOT, ENV, describe, recorded, group

SOURCES = {name: (source, expected) for name, source, expected in AUTHOR_SOURCES + REVIEW_SOURCES}


def revision():
    def git(*args):
        return subprocess.run(['git', *args], cwd=ROOT, env=ENV, check=True,
                              stdout=subprocess.PIPE).stdout

    assert Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve() == ROOT
    diff = git('diff', '--binary', 'HEAD', '--')
    return {'head': git('rev-parse', 'HEAD').decode().strip(),
            'head_tree': git('rev-parse', 'HEAD^{tree}').decode().strip(),
            'status': git('status', '--porcelain').decode().strip(),
            'diff': {'sha256': hashlib.sha256(diff).hexdigest(), 'bytes': len(diff)}}


def main():
    assert Path.cwd() == ROOT
    head = revision()
    selected = set(sys.argv[1:]) or {case[0] for case in CASES}
    assert selected <= {case[0] for case in CASES}
    store = ROOT / '.tools/arrayaccess-write'
    store.mkdir(exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='prepared-', dir=store))
    print(out, flush=True)
    watched = {str(ROOT / name): describe(ROOT / name) for name in (
        'tests/semantics/arrayaccess_write_cases.py',
        'tests/semantics/arrayaccess_write_review_cases.py',
        'tests/semantics/arrayaccess_write_protocol.py',
        'tests/semantics/arrayaccess_write_prepare.py',
        'tests/semantics/error_handler_protocol.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/profile.json', 'spec/semantics/modules.json',
        'spec/semantics/30-storage.watsup', 'spec/semantics/39-ownership.watsup',
        'spec/semantics/242-dimension-write-continuations.watsup',
        'spec/semantics/249-coalesce-unset-key-continuations.watsup',
        'spec/semantics/255-nested-unset-append-continuations.watsup',
        'spec/semantics/276-container-write-continuations.watsup',
        'spec/semantics/284-arrayaccess-dimensions.watsup',
        'spec/semantics/292-arrayaccess-write-dimensions.watsup',
        '.tools/spectec/bin/p4spectec', '_build/default/adapter/main.exe',
        '.tools/php/bin/php', '.tools/php-file.so')}
    modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    rows, failure = [], None
    try:
        for name, source_id, stage, checks in CASES:
            if name not in selected:
                continue
            source, expected = SOURCES[source_id]
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')],
                directory / 'frontend')
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
            prefix = PREFIX
            if '$outputs(' in stage:
                declaration = 'dec $outputs(pevent*) : nat*\n'
                prefix = declaration + prefix.replace(declaration, '')
            fixture = directory / 'protocol.watsup'
            fixture.write_text(prefix.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in conditions))
            producer = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)],
                                directory / 'compiler', 120)
            al = directory / 'compiler.stdout'
            passed = (producer['exit'] == 0 and not producer['timeout']
                and not (directory / 'compiler.stderr').read_bytes()
                and b'\ndef $main : bool =\n' in al.read_bytes())
            rows.append({'id': name, 'source_id': source_id, 'source': str(path),
                'fixture': str(fixture), 'al': str(al), 'source_descriptor': describe(path),
                'fixture_descriptor': describe(fixture), 'al_descriptor': describe(al),
                'assertions': len(conditions), 'producer': producer, 'passed': passed})
            print(name, passed, len(conditions), flush=True)
            assert passed, name
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    stable = watched == {path: describe(path) for path in watched}
    current = revision()
    groups = {str(row['producer']['pgid']): group(row['producer']['pgid']) for row in rows}
    passed = (failure is None and stable and head == current and len(rows) == len(selected)
              and all(not members for members in groups.values()))
    (out / 'report.json').write_text(json.dumps({'passed': passed,
        'scope': 'Compiler preparation only; no native/model/state execution',
        'revision': head, 'revision_after': current, 'inputs': watched, 'records': rows,
        'jobs': 1, 'compiler_cap_seconds': 120,
        'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'],
                        'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
        'failure': failure, 'inputs_stable': stable, 'groups_after': groups}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
