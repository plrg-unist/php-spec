#!/usr/bin/env python3
"""Source-derived ordinary string-constant publication fronts."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

import const_string_sources as sources
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
sha = sources.family.sha

PREFIX = r'''
dec $test_string_bind_front(pstate, preqbytes) : bool
def $test_string_bind_front(S, preqbytes) = true
  -- if S.TODO = (CONSTANT_BIND porigin) :: ptask_tail*
  -- if $constant_declaration(S,porigin) = ((preqbytes,z))
def $test_string_bind_front(S,preqbytes) = false -- otherwise
dec $test_string_bind_seek(pstate, preqbytes, nat) : pstate
def $test_string_bind_seek(S,preqbytes,0) = S
def $test_string_bind_seek(S,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_string_bind_front(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_string_bind_seek(S,preqbytes,n) = $test_string_bind_seek($drive_steps(S[.COMPLETION = NORMAL],1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_string_bind_front(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def fingerprint():
    return dict(sources.family.fingerprint(), **{name: sha(ROOT / name) for name in (
        'tests/semantics/const_string_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/static_types.py', 'tests/semantics/_build/default/numeric_runner.exe')})


def initial(program, path):
    return '$php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')'


def decision(program, path):
    return PREFIX + r'''
dec $main() : (pvalue, pvalueclass, bool, bool, bool, bool, pcompletion)
def $main() = (pvalue,pvalueclass,$constant_value_class_valid(S,pvalue,pvalueclass),$global_constant_transfer_valid(S,porigin,pvalueclass,S.USERCONSTANTS),$call_descriptors_valid(S),$constant_facts_valid(S,porigin,pconstantcontext.FACTS),S_found.COMPLETION)
  -- if S_initial = ''' + initial(program, path) + r'''
  -- if S_found = $test_string_bind_seek(S_initial,$ptascii("ConstString22\\Literal"),256)
  -- if S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
  -- if S = S_found[.COMPLETION = NORMAL]
  -- if $test_string_bind_front(S,$ptascii("ConstString22\\Literal"))
  -- if S.TODO = (CONSTANT_BIND porigin) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if pvalueclass = $constant_received_class(S,porigin)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'decision'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    report_path = out / (args.phase + '-report.json')
    assert not report_path.exists()
    native = json.loads((args.sources / 'native-report.json').read_bytes())
    assert native['passed'] and native['inputs_stable'] and native['head_stable']
    path = args.sources.resolve() / 'literal-folded-and-alias/main.php'
    assert path.read_bytes() == sources.family.CASES['literal-folded-and-alias']
    native_row, = [row for row in native['records'] if row['id'] == 'literal-folded-and-alias']
    assert native_row['source_sha256'] == sha(path)
    watched = [path, args.sources.resolve() / 'native-report.json']
    inputs = lambda: dict(fingerprint(), **{str(p): sha(p) for p in watched})
    before = inputs()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'phase': args.phase, 'revision': head, 'inputs': before,
        'native_report_sha256': sha(args.sources / 'native-report.json'),
        'source': str(path), 'source_sha256': sha(path), 'passed': False}
    fixture = out / 'decision.watsup'
    try:
        if args.phase == 'prepare':
            frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
                    assert parsed['accepted']
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    (out / 'checked.json').write_text(json.dumps(checked) + '\n')
                    fixture.write_text(decision(checked['fixture'], path))
                finally:
                    adapter.close()
            finally:
                frontend.close()
        else:
            preparation = json.loads((out / 'prepare-report.json').read_bytes())
            assert preparation['passed'] and preparation['inputs'] == before
            assert preparation['fixture_sha256'] == sha(fixture)
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())
            command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT / name) for name in modules], str(fixture)]
            report['process'] = recorder.recorded(command, out / 'decision', 60)
            assert report['process']['exit'] == 0 and not report['process']['timeout']
            assert not report['process']['group_after']
            assert preparation['fixture_sha256'] == sha(fixture)
            assert (out / 'decision.stderr').read_bytes() == b''
            report['stdout'] = (out / 'decision.stdout').read_text()
        report['fixture_sha256'] = sha(fixture)
        report['passed'] = True
    finally:
        report['inputs_stable'] = before == inputs()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']
    print(report_path, flush=True)


if __name__ == '__main__':
    main()
