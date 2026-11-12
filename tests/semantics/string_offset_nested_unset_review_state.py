#!/usr/bin/env python3
"""Independent reached-state checks of ordinary nested string unset errors."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import string_offset_nested_unset_cases as cases

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('nested-unset-leading-numeric-final-assignment', 'nested-unset-live-inner-cv')
HELPERS = r'''
dec $nested_unset_front(pstate) : bool
def $nested_unset_front(S) = true -- if S.TODO = UNSET_ARRAY :: ptask*
def $nested_unset_front(S) = false -- otherwise
dec $nested_unset_seek(pstate, nat) : pstate
def $nested_unset_seek(S, 0) = S
def $nested_unset_seek(S, n) = S
  -- if $(n > 0)
  -- if $nested_unset_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $nested_unset_seek(S, n) = $nested_unset_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$nested_unset_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def conditions(program, source, live):
    encoded = json.dumps(base64.b64encode(bytes(source)).decode())
    name, value = ('k', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("bad"))') if live else ('last', 'PINT 7')
    message = 'Cannot unset string offsets' if live else 'Cannot use string offset as an array'
    key = 'VARIABLE ($ptascii("k")) 3' if live else 'KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")))'
    output = ['Cannot unset string offsets', '|', 'bad', '|', 'ab'] if live else [message, '|', '3', '|', '7', '|', 'ab']
    events = '[' + ', '.join('OUTPUT ($ptascii(' + json.dumps(text) + '))' for text in output) + ']'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $nested_unset_seek(S_initial, 512)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        '$nested_unset_front(S)',
        'S.TODO = UNSET_ARRAY :: ptask_after*',
        'S.BASE = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ptbytes_s 3)) (' + key + ') 3) (KNOWN (' + value + ')) 3',
        'ptbytes_s = $ptascii("s")',
        r'S.REQUEST = eps /\ S.CURRENT = eps /\ S.EVENTS = eps',
        r'S.ERRORHANDLER.CALLBACK = eps /\ S.ERRORFATALTRACE = eps',
        'S.ORIGIN = (PORIGIN 0 pcpath)',
        'S.FILES = [SOURCEFILE 0 ($base64(' + encoded + '))]',
        '$lookup(S.ENV, ptbytes_s) = (n_s)',
        '$lookup(S.ENV, $ptascii(' + json.dumps(name) + ')) = (n_side)',
        'S.STORE[n_s] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("ab")))',
        'S.STORE[n_side] = DEFINED (' + value + ')',
        r'~(n_s <- S.REFCELLS) /\ ~(n_side <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_s) = 1',
        '$heap_owners($heap_graph(S), HCELL n_side) = 1',
        'PhpStep: S ~> S_raw',
        'S_raw = S[.TODO = ptask_after*][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_s][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "Error" ($ptascii(' + json.dumps(message) + ')) 3]',
        r'S_raw.STORE = S.STORE /\ S_raw.ARRAYS = S.ARRAYS /\ S_raw.STRINGDATA = S.STRINGDATA',
        r'S_raw.KEY = S.KEY /\ S_raw.HELD = S.HELD /\ S_raw.FRAMES = S.FRAMES',
        'S_raw.EVENTS = eps',
        '$heap_graph(S_raw) = $heap_graph(S[.TODO = ptask_after*][.BASE = BASE_VALUE (KNOWN PNULL)][.RESULT = KNOWN PNULL])',
        '$drive(S, 0) = S[.COMPLETION = BUDGET]',
        'S_public = $drive(S, 1)',
        'S_public.COMPLETION = BUDGET',
        'S_public.EVENTS = eps',
        'S_done = $drive_steps(S_public[.COMPLETION = NORMAL], 1000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0 /\ S_done.TODO = eps',
        r'S_done.FRAMES = eps /\ S_done.HELD = eps',
        r'S_done.STORE[n_s] = S.STORE[n_s] /\ S_done.STORE[n_side] = S.STORE[n_side]',
        'S_done.EVENTS = ' + events,
        r'S_done.POOLS = S.POOLS /\ S_done.CODE = S.CODE',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)',
        '$drive_steps(S, 1001) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.source_report.resolve()
    report = json.loads(report_path.read_bytes())
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert report['profile'] == profile
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    runtime_hashes = [value for path, value in report['inputs'].items()
                      if path == '.tools/php/bin/php' or path.endswith('/.tools/php/bin/php')]
    assert runtime_hashes == [digest(ROOT / '.tools/php/bin/php')]
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    blocks, watched = [], []
    try:
        for index, name in enumerate(NAMES):
            row = next(row for row in report['rows'] if row['id'] == name)
            native = row['native']
            assert native['exit'] == 0 and not native['timeout'] and native['interruption'] is None and native['group_after'] == []
            source = Path(native['argv'][-1])
            assert source.is_absolute() and source.read_bytes() == cases.CASES[name]
            assert digest(source) == row['source_sha256']
            expected = b'Cannot unset string offsets|bad|ab' if index else b'Cannot use string offset as an array|3|7|ab'
            assert source.with_name('native.stdout').read_bytes() == expected
            assert source.with_name('native.stderr').read_bytes() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(cases.CASES[name]).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            blocks.append(conditions(checked['fixture'], source, bool(index)))
            watched += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    finally:
        frontend.close()
        adapter.close()
    fixture = out / 'test.watsup'
    fixture.write_text(HELPERS + '\n' + '\n'.join('dec $nested_unset_review_' + str(index) + '() : bool\n'
        + 'def $nested_unset_review_' + str(index) + '() = true\n'
        + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
        for index, checks in enumerate(blocks))
        + '\ndec $main() : bool\ndef $main() = true\n  -- if $nested_unset_review_0()\n  -- if $nested_unset_review_1()\n')
    (out / 'assertions.json').write_text(json.dumps(dict(zip(NAMES, blocks)), indent=2) + '\n')
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched += [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json', runner,
                Path(__file__), Path(cases.__file__), report_path, fixture,
                ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
                ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
                ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    process = recorded([str(runner), *map(str, modules), str(fixture)], out / 'model', 180)
    passed = process['exit'] == 0 and not process['timeout'] and process['interruption'] is None and process['group_after'] == [] and (out / 'model.stdout').read_bytes() == b'true\n' and (out / 'model.stderr').read_bytes() == b''
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'AL',
        'selection': NAMES, 'conditions': sum(map(len, blocks)), 'raw_unset_steps': 2,
        'native_reused_from': str(report_path), 'inputs': before, 'process': process,
        'passed': passed, 'source_credit': 0}, indent=2) + '\n')
    print('nested-unset-review', sum(map(len, blocks)), passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
