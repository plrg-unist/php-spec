#!/usr/bin/env python3
"""Reached namespace fallback calls for filename-local HALT offsets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import halt_fixed_protocol as fixed
import halt_lookup_protocol as previous
import halt_namespace_sources as cases
import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('ns-main-absent-trace', 'ns-main-present', 'ns-child-present-main-absent')
PREFIX = previous.PREFIX + r'''
dec $test_namespace_front(pstate, nat) : bool
def $test_namespace_front(S, n_unit) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.SELECTION = eps
  -- if $dynamic_halt_call(pconfigcall)
def $test_namespace_front(S, n_unit) = false -- otherwise
dec $test_namespace_seek(pstate, nat, nat) : pstate
def $test_namespace_seek(S, n_unit, 0) = S
def $test_namespace_seek(S, n_unit, n) = S
  -- if $(n > 0)
  -- if $test_namespace_front(S,n_unit) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_namespace_seek(S, n_unit, n) = $test_namespace_seek($drive_steps($test_running(S),1),n_unit,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_namespace_front(S,n_unit)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def front(state, seed, unit, sourcefile, offset):
    call = 'pconfigcall_' + state
    budget, resume = state + '_budget', state + '_resume'
    return [state + '_found = $test_namespace_seek(' + seed + ',' + str(unit) + ',2500)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$test_namespace_front(' + state + ',' + str(unit) + ')',
            state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
            '$config_invoke_valid(' + state + ',' + call + ')',
            '$exit_fixed(' + state + ',' + call + '.SITE) = ((preqbytes_' + state + ',preqbytes_fallback_' + state + '?))',
            'preqbytes_' + state + ' = ' + fixed.term(b'N\\constant'),
            'preqbytes_fallback_' + state + '? = ($ptascii("constant"))',
            '$intrinsic_named(preqbytes_' + state + ') = eps',
            '$call_target(' + state + ',preqbytes_' + state + ',preqbytes_fallback_' + state + '?) = eps',
            '$dynamic_halt_namespace_constant(' + state + ',' + call + ')',
            '~$dynamic_halt_fixed_constant(' + state + ',' + call + ')',
            '$dynamic_halt_valid(' + state + ',' + call + ')',
            '$call_sourcefile(' + state + '.FILES,' + call + '.SITE) = ' + sourcefile,
            '$dynamic_halt_lookup(' + state + ',' + sourcefile + ',' + state + '.DECLARATIONS) = ' +
                ('HALT_OFFSET ' + str(offset) if offset is not None else 'HALT_ABSENT'),
            '~$dynamic_halt_valid(' + state + ',' + call + '[.OWNER = (0)])',
            '~$dynamic_halt_valid(' + state + ',' + call + '[.NAMED = true])',
            '~$dynamic_halt_valid(' + state + ',' + call + '[.SENT = eps])',
            budget + ' = $drive_steps(' + state + ',0)',
            budget + ' = ' + state + '[.COMPLETION = BUDGET]',
            resume + ' = ' + budget + '[.COMPLETION = NORMAL]', resume + ' = ' + state,
            'pconfigcall_' + resume + ' = ' + call, *previous.public(state)]


def assertions(name, directory, frontend, adapter):
    source, child, expected = cases.CASES[name]
    assert (directory / 'main.php').read_bytes() == source
    assert child is None or (directory / 'child.php').read_bytes() == child
    assert (directory / 'native-stdout').read_bytes() == expected
    assert (directory / 'native-stderr').read_bytes() == b''
    main = fixed.checked(adapter, frontend.request({'op': 'parse', 'source': fixed.b64(source)}))
    setup_name = 'child-present-main-absent' if child is not None else name
    checks, unit, sourcefile = fixed.source_setup(setup_name, directory, main,
        directory / 'child.php' if child is not None else None, frontend, adapter)
    if child is not None:
        checks += front('S_child', 'S_seed', 1, sourcefile, 89)
        checks += ['pdeclaration_prefix* = [PDENTER 0 eps S_child.REPORTING,PDEXIT 0 PCSCOMPLETE]',
                   'pdeclaration_enter = PDENTER 1 (pfilecontext.SITE) S_child.REPORTING',
                   'S_child.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter,PDEXIT 1 PCSCOMPLETE]',
                   'S_unknown = S_child[.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter]]',
                   '$dynamic_halt_lookup(S_unknown,' + sourcefile + ',S_unknown.DECLARATIONS) = HALT_UNKNOWN',
                   '$dynamic_halt_valid(S_unknown,pconfigcall_S_child)',
                   '$dynamic_halt_receive(S_unknown,pconfigcall_S_child).COMPLETION = UNSUPPORTED "halt offset constant query"',
                   '$test_outputs(S_child.EVENTS) = $ptascii("I:")']
        checks += previous.step('S_child_value', 'S_child_resume', 'PINT 89')
        checks += ['S_child_value.' + field + ' = S_child_resume.' + field for field in
                   ('INCLUDEDOPENED', 'FILESEQ', 'FILECONTEXTS', 'EVALCONTEXTS')]
        mainfile = fixed.term(os.fsencode(directory / 'main.php'))
        checks += front('S', 'S_child_value', 0, mainfile, None)
        checks += ['$dynamic_halt_lookup(S,' + sourcefile + ',S.DECLARATIONS) = HALT_OFFSET 89',
                   '$test_outputs(S.EVENTS) = $ptascii("I:89|")']
        checks += fixed.error_checks('S', mainfile, expected)
    else:
        checks += front('S', 'S_seed', unit, sourcefile, 89 if name == 'ns-main-present' else None)
        if name == 'ns-main-present':
            checks += previous.step('S_value', 'S_resume', 'PINT 89')
            checks += ['S_value.' + field + ' = S_resume.' + field for field in
                       ('INCLUDEDOPENED', 'FILESEQ', 'FILECONTEXTS', 'EVALCONTEXTS')]
            checks += ['S_final = $drive_steps(S_value,10000)', 'S_final.COMPLETION = NORMAL',
                       'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = ' + fixed.term(expected),
                       *previous.public('S_final')]
        else:
            checks += fixed.error_checks('S', sourcefile, expected)
    return checks


def execute(name, checks, out):
    target = out / name
    target.mkdir()
    fixture = target / 'protocol.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
        ''.join('  -- if ' + check + '\n' for check in checks))
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(fixture)]
    result = subprocess.run(command, cwd=ROOT, env=types.ENV, capture_output=True, timeout=150)
    (target / 'stdout').write_bytes(result.stdout)
    (target / 'stderr').write_bytes(result.stderr)
    passed = result.returncode == 0 and result.stdout == b'true\n' and result.stderr == b''
    print(name, passed, len(checks), flush=True)
    return {'id': name, 'pass': passed, 'checks': len(checks), 'exit': result.returncode,
            'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
            'command': command, 'cwd': str(ROOT)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--case', choices=NAMES, action='append', default=[])
    args = parser.parse_args()
    selection = [name for name in NAMES if not args.case or name in args.case]
    sources, out = args.sources.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert json.loads((sources / 'native-report.json').read_text())['result'] == 'pass'
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records = []
    try:
        for name in selection:
            checks = assertions(name, sources / name, frontend, adapter)
            records.append(execute(name, checks, out))
            if not records[-1]['pass']:
                break
    finally:
        adapter.close()
        frontend.close()
    report = {'result': 'pass' if len(records) == len(selection) and all(row['pass'] for row in records) else 'fail',
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())),
              'module_manifest_sha256': hashlib.sha256((ROOT / 'spec/semantics/modules.json').read_bytes()).hexdigest(),
              'runner_sha256': hashlib.sha256((ROOT / 'tests/semantics/_build/default/numeric_runner.exe').read_bytes()).hexdigest(),
              'runtime_sha256': hashlib.sha256((ROOT / 'spec/semantics/400-dynamic-constants.watsup').read_bytes()).hexdigest(),
              'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
