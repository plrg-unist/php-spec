#!/usr/bin/env python3
"""Reached fixed defined CV lookups and the literal HALT quick check."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import halt_defined_cv_sources as cases
import halt_fixed_protocol as fixed
import halt_lookup_protocol as previous
import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('main-present-literal-contrast', 'child-present-main-absent', 'main-present-eval-absent')
PREFIX = previous.PREFIX + r'''
dec $test_defined_cv_front(pstate, nat, nat) : bool
def $test_defined_cv_front(S, n_unit, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.SELECTION = eps
  -- if $intrinsic_argument(S,pconfigcall.SITE,0) = ((NExprVariable (BYTES text_name) metadata_name,false,eps,porigin_arg,z_arg))
  -- if $dynamic_halt_call(pconfigcall)
def $test_defined_cv_front(S, n_unit, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.SELECTION = eps
  -- if $intrinsic_argument(S,pconfigcall.SITE,0) = ((NScalarString (BYTES text) metadata,false,eps,porigin_arg,z_arg))
  -- if $dynamic_halt_call(pconfigcall)
def $test_defined_cv_front(S, n_unit, n_mode) = false -- otherwise
dec $test_defined_cv_seek(pstate, nat, nat, nat) : pstate
def $test_defined_cv_seek(S, n_unit, n_mode, 0) = S
def $test_defined_cv_seek(S, n_unit, n_mode, n) = S
  -- if $(n > 0)
  -- if $test_defined_cv_front(S,n_unit,n_mode) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_defined_cv_seek(S, n_unit, n_mode, n) = $test_defined_cv_seek($drive_steps($test_running(S),1),n_unit,n_mode,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_defined_cv_front(S,n_unit,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, seed, unit, mode):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_defined_cv_seek(' + seed + ',' + str(unit) + ',' + str(mode) + ',2500)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$test_defined_cv_front(' + state + ',' + str(unit) + ',' + str(mode) + ')',
            state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
            '$config_invoke_valid(' + state + ',' + call + ')', *previous.public(state)]


def cv_front(state, seed, unit, sourcefile, offset):
    call = 'pconfigcall_' + state
    budget, resume = state + '_budget', state + '_resume'
    checks = reach(state, seed, unit, 0)
    checks += ['$exit_fixed(' + state + ',' + call + '.SITE) = (($ptascii("defined"),eps))',
               '$intrinsic_count(' + state + ',' + call + '.SITE) = (1)',
               '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((NExprVariable (BYTES text_name_' + state + ') metadata_name_' + state + ',false,eps,porigin_arg_' + state + ',z_arg_' + state + '))',
               call + '.SENT = [NAMED_SENT (KNOWN pvalue_query_' + state + ')]',
               '$string_bytes(pvalue_query_' + state + ') = ($ptascii("__COMPILER_HALT_OFFSET__"))',
               '$string_carrier_valid(' + state + ',pvalue_query_' + state + ')',
               '$dynamic_global_constant_known(' + state + ',' + call + '.SITE) = eps',
               '$dynamic_halt_cv_defined(' + state + ',' + call + ')',
               '~$dynamic_halt_literal_defined(' + state + ',' + call + ')',
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
               'pconfigcall_' + resume + ' = ' + call]
    return checks


def step(state, seed, value):
    checks = previous.step(state, seed, value)
    checks += [state + '.' + field + ' = ' + seed + '.' + field for field in
               ('INCLUDEDOPENED', 'FILESEQ', 'FILECONTEXTS', 'EVALCONTEXTS')]
    return checks


def eval_setup(directory, main, frontend, adapter):
    code = b'return defined($n) ? "1" : "0";'
    parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
        'profile': 'cli-raw-85', 'source': fixed.b64(code)})
    unit = fixed.checked(adapter, parsed)
    mainfile = fixed.term(os.fsencode(directory / 'main.php'))
    checks = ['S_wait = $php_run(' + main + ',2500,' +
              json.dumps(fixed.b64(os.fsencode(directory / 'main.php'))) + ')',
              'S_wait.COMPLETION = SOURCE_PENDING',
              'S_wait.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*',
              'pevalcontext.BYTES = ' + fixed.term(code),
              'S_seed = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + fixed.term(code) + ' ' + unit + ')',
              'S_seed.COMPLETION = NORMAL']
    return checks, 'pevalcontext.FILE', mainfile


def assertions(name, directory, frontend, adapter):
    source, child, expected = cases.CASES[name]
    assert (directory / 'main.php').read_bytes() == source
    assert child is None or (directory / 'child.php').read_bytes() == child
    assert (directory / 'native-stdout').read_bytes() == expected
    assert (directory / 'native-stderr').read_bytes() == b''
    main = fixed.checked(adapter, frontend.request({'op': 'parse', 'source': fixed.b64(source)}))
    mainfile = fixed.term(os.fsencode(directory / 'main.php'))
    if name == 'main-present-eval-absent':
        checks, evalfile, mainfile = eval_setup(directory, main, frontend, adapter)
        checks += cv_front('S_eval', 'S_seed', 1, evalfile, None)
        checks += ['$dynamic_halt_lookup(S_eval,' + mainfile + ',S_eval.DECLARATIONS) = HALT_OFFSET ' +
                   str(source.index(b'PAYLOAD'))]
        checks += step('S_eval_value', 'S_eval_resume', 'PBOOL false')
        checks += cv_front('S', 'S_eval_value', 0, mainfile, source.index(b'PAYLOAD'))
        checks += step('S_value', 'S_resume', 'PBOOL true')
        checks += previous.final('S_final', 'S_value', expected.decode())
        return checks
    setup_name = 'child-present-main-absent' if child is not None else name
    checks, unit, sourcefile = fixed.source_setup(setup_name, directory, main,
        directory / 'child.php' if child is not None else None, frontend, adapter)
    if child is not None:
        checks += cv_front('S_child', 'S_seed', 1, sourcefile, child.index(b'PAYLOAD'))
        checks += ['pdeclaration_prefix* = [PDENTER 0 eps S_child.REPORTING,PDEXIT 0 PCSCOMPLETE]',
                   'pdeclaration_enter = PDENTER 1 (pfilecontext.SITE) S_child.REPORTING',
                   'S_child.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter,PDEXIT 1 PCSCOMPLETE]',
                   'S_unknown = S_child[.DECLARATIONS = pdeclaration_prefix* ++ [pdeclaration_enter]]',
                   '$dynamic_halt_lookup(S_unknown,' + sourcefile + ',S_unknown.DECLARATIONS) = HALT_UNKNOWN',
                   '$dynamic_halt_valid(S_unknown,pconfigcall_S_child)',
                   '$dynamic_halt_receive(S_unknown,pconfigcall_S_child).COMPLETION = UNSUPPORTED "halt offset constant query"',
                   '$test_outputs(S_child.EVENTS) = $ptascii("I:")']
        checks += step('S_child_value', 'S_child_resume', 'PBOOL true')
        checks += cv_front('S', 'S_child_value', 0, mainfile, None)
        checks += ['$dynamic_halt_lookup(S,' + sourcefile + ',S.DECLARATIONS) = HALT_OFFSET ' +
                   str(child.index(b'PAYLOAD'))]
        checks += step('S_value', 'S_resume', 'PBOOL false')
        checks += previous.final('S_final', 'S_value', expected.decode())
        return checks
    checks += cv_front('S', 'S_seed', unit, sourcefile, source.index(b'PAYLOAD'))
    checks += step('S_value', 'S_resume', 'PBOOL true')
    checks += reach('S_literal', 'S_value', 0, 1)
    checks += ['$dynamic_halt_literal_defined(S_literal,pconfigcall_S_literal)',
               '~$dynamic_halt_cv_defined(S_literal,pconfigcall_S_literal)',
               '$call_sourcefile(S_literal.FILES,pconfigcall_S_literal.SITE) = ' + mainfile,
               '$dynamic_halt_lookup(S_literal,' + mainfile + ',S_literal.DECLARATIONS) = HALT_OFFSET ' +
                   str(source.index(b'PAYLOAD'))]
    checks += step('S_literal_value', 'S_literal', 'PBOOL false')
    checks += previous.final('S_final', 'S_literal_value', expected.decode())
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
