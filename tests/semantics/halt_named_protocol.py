#!/usr/bin/env python3
"""Reached fixed named constant lookups of filename-local HALT registration."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import halt_named_sources as cases
import halt_fixed_protocol as fixed
import halt_lookup_protocol as previous
import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('named-absent-trace', 'named-main-present', 'named-child-present-main-absent')
PREFIX = previous.PREFIX + r'''
dec $test_named_halt_front(pstate, nat) : bool
def $test_named_halt_front(S, n_unit) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.SELECTION = eps /\ pconfigcall.NAMED
  -- if $intrinsic_argument(S,pconfigcall.SITE,0) = ((NScalarString (BYTES text) metadata,false,preqbytes_argname?,porigin_arg,z_arg))
  -- if preqbytes_argname? = ($ptascii("name"))
  -- if $dynamic_halt_call(pconfigcall)
def $test_named_halt_front(S, n_unit) = false -- otherwise
dec $test_named_halt_seek(pstate, nat, nat) : pstate
def $test_named_halt_seek(S, n_unit, 0) = S
def $test_named_halt_seek(S, n_unit, n) = S
  -- if $(n > 0)
  -- if $test_named_halt_front(S,n_unit) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_named_halt_seek(S, n_unit, n) = $test_named_halt_seek($drive_steps($test_running(S),1),n_unit,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_named_halt_front(S,n_unit)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, seed, unit):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_named_halt_seek(' + seed + ',' + str(unit) + ',2500)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$test_named_halt_front(' + state + ',' + str(unit) + ')',
            state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
            '$config_invoke_valid(' + state + ',' + call + ')', *previous.public(state)]


def named_front(state, seed, unit, sourcefile, offset):
    call = 'pconfigcall_' + state
    budget, resume = state + '_budget', state + '_resume'
    checks = reach(state, seed, unit)
    checks += ['$exit_fixed(' + state + ',' + call + '.SITE) = (($ptascii("constant"),eps))',
               '$intrinsic_count(' + state + ',' + call + '.SITE) = (1)',
               call + '.NAMED',
               '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((NScalarString (BYTES text_' + state + ') metadata_' + state + ',false,preqbytes_argname_' + state + '?,porigin_arg_' + state + ',z_arg_' + state + '))',
               'preqbytes_argname_' + state + '? = ($ptascii("name"))',
               '$base64(text_' + state + ') = $ptascii("__COMPILER_HALT_OFFSET__")',
               call + '.SENT = [NAMED_SENT (KNOWN pvalue_query_' + state + ')]',
               '$string_bytes(pvalue_query_' + state + ') = ($ptascii("__COMPILER_HALT_OFFSET__"))',
               '($string_plain(pvalue_query_' + state + ') = pvalue_query_' + state + ' \\/ $string_carrier_valid(' + state + ',pvalue_query_' + state + '))',
               '$dynamic_define_value_matches(pvalue_query_' + state + ',$dynamic_global_constant_known(' + state + ',' + call + '.SITE))',
               '$dynamic_halt_named_constant(' + state + ',' + call + ')',
               '~$dynamic_halt_fixed_constant(' + state + ',' + call + ')',
               '~$dynamic_halt_cv_constant(' + state + ',' + call + ')',
               '$dynamic_halt_valid(' + state + ',' + call + ')',
               '$call_sourcefile(' + state + '.FILES,' + call + '.SITE) = ' + sourcefile,
               '$dynamic_halt_lookup(' + state + ',' + sourcefile + ',' + state + '.DECLARATIONS) = ' +
                   ('HALT_OFFSET ' + str(offset) if offset is not None else 'HALT_ABSENT'),
               '~$dynamic_halt_valid(' + state + ',' + call + '[.OWNER = (0)])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.NAMED = false])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.SENT = eps])',
               budget + ' = $drive_steps(' + state + ',0)',
               budget + ' = ' + state + '[.COMPLETION = BUDGET]',
               resume + ' = ' + budget + '[.COMPLETION = NORMAL]', resume + ' = ' + state,
               'pconfigcall_' + resume + ' = ' + call]
    return checks


def positive_step(state, seed, value):
    checks = previous.step(state, seed, value)
    checks += [state + '.' + field + ' = ' + seed + '.' + field for field in
               ('INCLUDEDOPENED', 'FILESEQ', 'FILECONTEXTS', 'EVALCONTEXTS')]
    return checks


def assertions(name, directory, frontend, adapter):
    source, child, expected = cases.CASES[name]
    if expected is None:
        expected = cases.expected_trace()[0]
    assert (directory / 'main.php').read_bytes() == source
    assert child is None or (directory / 'child.php').read_bytes() == child
    assert (directory / 'native-stdout').read_bytes() == expected
    assert (directory / 'native-stderr').read_bytes() == b''
    main = fixed.checked(adapter, frontend.request({'op': 'parse', 'source': fixed.b64(source)}))
    child_path = directory / 'child.php' if child is not None else None
    checks, unit, sourcefile = fixed.source_setup('child-present-main-absent' if child is not None else name, directory, main, child_path, frontend, adapter)
    mainfile = fixed.term(os.fsencode(directory / 'main.php'))
    if child is not None:
        checks += named_front('S_child', 'S_seed', 1, sourcefile, child.index(b'PAYLOAD'))
        checks += ['pdeclaration_prefix* = [PDENTER 0 eps S_child.REPORTING,PDEXIT 0 PCSCOMPLETE]',
                   'pdeclaration_enter = PDENTER 1 (pfilecontext.SITE) S_child.REPORTING',
                   'S_child.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter,PDEXIT 1 PCSCOMPLETE]',
                   'S_unknown = S_child[.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter]]',
                   '$dynamic_halt_lookup(S_unknown,' + sourcefile + ',S_unknown.DECLARATIONS) = HALT_UNKNOWN',
                   '$dynamic_halt_valid(S_unknown,pconfigcall_S_child)',
                   '$dynamic_halt_receive(S_unknown,pconfigcall_S_child).COMPLETION = UNSUPPORTED "halt offset constant query"',
                   '$test_outputs(S_child.EVENTS) = $ptascii("I:")']
        checks += positive_step('S_child_value', 'S_child_resume', 'PINT ' + str(child.index(b'PAYLOAD')))
        checks += named_front('S', 'S_child_value', 0, mainfile, None)
        checks += ['$dynamic_halt_lookup(S,' + sourcefile + ',S.DECLARATIONS) = HALT_OFFSET ' + str(child.index(b'PAYLOAD')),
                   '$test_outputs(S.EVENTS) = ' + fixed.term(b'I:' + str(child.index(b'PAYLOAD')).encode() + b'|')]
        checks += fixed.error_checks('S', mainfile, expected)
    elif name == 'named-absent-trace':
        checks += named_front('S', 'S_seed', 0, mainfile, None)
        checks += fixed.error_checks('S', mainfile, expected)
    else:
        checks += named_front('S', 'S_seed', unit, sourcefile, source.index(b'PAYLOAD'))
        checks += positive_step('S_value', 'S_resume', 'PINT ' + str(source.index(b'PAYLOAD')))
        checks += previous.final('S_final', 'S_value', expected.decode())
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
