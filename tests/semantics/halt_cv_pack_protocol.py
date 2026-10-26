#!/usr/bin/env python3
"""Reached ordinary-CV singleton-unpack HALT queries and their call certificates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import halt_fixed_protocol as fixed
import halt_lookup_protocol as previous
import halt_cv_pack_sources as cases
import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('cv-cow-positional', 'cv-key-rewrite-named', 'cv-absent-trace',
         'cv-repeated-site', 'cv-alias-leaf-control')
PREFIX = previous.PREFIX + r'''
dec $test_cv_pack_front(pstate, nat, bool) : bool
def $test_cv_pack_front(S, n_unit, b_named) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.SELECTION = eps
  -- if pconfigcall.NAMED = b_named
  -- if $dynamic_halt_cv_pack_constant(S,pconfigcall)
def $test_cv_pack_front(S, n_unit, b_named) = false -- otherwise
dec $test_cv_pack_seek(pstate, nat, bool, nat) : pstate
def $test_cv_pack_seek(S, n_unit, b_named, 0) = S
def $test_cv_pack_seek(S, n_unit, b_named, n) = S
  -- if $(n > 0)
  -- if $test_cv_pack_front(S,n_unit,b_named) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_cv_pack_seek(S, n_unit, b_named, n) = $test_cv_pack_seek($drive_steps($test_running(S),1),n_unit,b_named,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_cv_pack_front(S,n_unit,b_named)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_variable_pack_front(pstate) : bool
def $test_variable_pack_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.SELECTION = eps
  -- if $intrinsic_argument(S,pconfigcall.SITE,0) = ((NExprVariable (BYTES text) metadata,true,eps,porigin,z))
def $test_variable_pack_front(S) = false -- otherwise
dec $test_variable_pack_seek(pstate, nat) : pstate
def $test_variable_pack_seek(S, 0) = S
def $test_variable_pack_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_variable_pack_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_variable_pack_seek(S, n) = $test_variable_pack_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_variable_pack_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, seed, unit, named):
    call = 'pconfigcall_' + state
    mode = 'true' if named else 'false'
    return [state + '_found = $test_cv_pack_seek(' + seed + ',' + str(unit) + ',' + mode + ',2500)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$test_cv_pack_front(' + state + ',' + str(unit) + ',' + mode + ')',
            state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
            '$config_invoke_valid(' + state + ',' + call + ')', *previous.public(state)]


def front(state, seed, unit, named, sourcefile, offset):
    call = 'pconfigcall_' + state
    pack = 'pconfigpack_' + state
    item = 'pvalue_' + state
    array = 'n_array_' + state
    cv = 'n_cv_' + state
    key = 'KSTRING ' + fixed.term(b'name') if named else 'KINT 0'
    checks = reach(state, seed, unit, named)
    checks += ['$exit_fixed(' + state + ',' + call + '.SITE) = (($ptascii("constant"),eps))',
               call + '.OWNER = eps', call + '.PACKS = [' + pack + ']',
               call + '.INDEX = 1', pack + '.INDEX = 0',
               '$config_pack_source_valid(' + state + ',' + call + ',' + pack + ')',
               '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((NExprVariable (BYTES text_' + state + ') metadata_' + state + ',true,eps,porigin_arg_' + state + ',z_arg_' + state + '))',
               pack + '.SITE = porigin_arg_' + state,
               '$lookup(' + state + '.ENV,$base64(text_' + state + ')) = (' + cv + ')',
               state + '.STORE[' + cv + '] = DEFINED (PARRAY ' + array + ')',
               pack + '.ARRAY = ' + array,
               'HARRAY ' + array + ' <- ' + state + '.ALLOCATIONS',
               state + '.ARRAYS[' + array + '].ITEMS = [ENTRY (' + key + ') (DIRECT ' + item + ')]',
               pack + '.ITEMS = $config_pack_capture(' + state + ',' + state + '.ARRAYS[' + array + '].ITEMS)',
               call + '.SENT = [NAMED_SENT (KNOWN ' + item + ')]',
               '$string_bytes(' + item + ') = ($ptascii("__COMPILER_HALT_OFFSET__"))',
               '$string_plain(' + item + ') = ' + item + ' \\/ $string_carrier_valid(' + state + ',' + item + ')',
               '$dynamic_halt_cv_pack_constant(' + state + ',' + call + ')',
               '$dynamic_halt_valid(' + state + ',' + call + ')',
               '$call_sourcefile(' + state + '.FILES,' + call + '.SITE) = ' + sourcefile,
               '$dynamic_halt_lookup(' + state + ',' + sourcefile + ',' + state + '.DECLARATIONS) = ' +
               ('HALT_OFFSET ' + str(offset) if offset is not None else 'HALT_ABSENT')]
    checks += ['~$dynamic_halt_valid(' + state + ',' + call + '[.PACKS = eps])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.OWNER = (0)])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.LINE = $(' + call + '.LINE + 1)])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.PACKS = [' + pack + '[.SITE = ' + call + '.SITE]]])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.PACKS = [' + pack + '[.LINE = $(' + pack + '.LINE + 1)]]])',
               '~$dynamic_halt_cv_pack_constant(' + state + ',' + call + '[.PACKS = [' + pack + '[.ARRAY = $(' + array + ' + 1)]]])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.PACKS = [' + pack + '[.ITEMS = [ENTRY (' +
               ('KINT 0' if named else 'KSTRING ' + fixed.term(b'name')) + ') (DIRECT ' + item + ')]]]])',
               '~$dynamic_halt_valid(' + state + ',' + call + '[.PACKS = [' + pack + '[.ITEMS = [ENTRY (' + key + ') (DIRECT PNULL)]]]])',
               state + '_badcv = ' + state + '[.STORE = $set_cell(' + state + '.STORE,' + cv + ',DEFINED PNULL)]',
               '~$dynamic_halt_cv_pack_constant(' + state + '_badcv,' + call + ')',
               state + '_alias = ' + state + '[.ARRAYS[' + array + '].ITEMS = [ENTRY (' + key + ') (ALIAS ' + cv + ')]]',
               '~$dynamic_halt_cv_pack_constant(' + state + '_alias,' + call + ')']
    budget, resume = state + '_budget', state + '_resume'
    checks += [budget + ' = $drive_steps(' + state + ',0)',
               budget + ' = ' + state + '[.COMPLETION = BUDGET]',
               resume + ' = ' + budget + '[.COMPLETION = NORMAL]', resume + ' = ' + state,
               'pconfigcall_' + resume + ' = ' + call]
    return checks


def value_step(state, seed, offset):
    checks = previous.step(state, seed, 'PINT ' + str(offset))
    checks += [state + '.' + field + ' = ' + seed + '.' + field for field in
               ('INCLUDEDOPENED', 'FILESEQ', 'FILECONTEXTS', 'EVALCONTEXTS')]
    return checks


def assertions(name, directory, frontend, adapter):
    source, child, expected = cases.CASES[name]
    assert (directory / 'main.php').read_bytes() == source
    assert child is None
    assert (directory / 'native-stdout').read_bytes() == expected
    assert (directory / 'native-stderr').read_bytes() == b''
    main = fixed.checked(adapter, frontend.request({'op': 'parse', 'source': fixed.b64(source)}))
    mainfile = fixed.term(os.fsencode(directory / 'main.php'))
    checks = ['S_seed = $php_run(' + main + ',0,' + json.dumps(fixed.b64(os.fsencode(directory / 'main.php'))) + ')',
              'S_seed.COMPLETION = BUDGET']
    if name == 'cv-alias-leaf-control':
        checks += [
                  'S_found = $test_variable_pack_seek(S_seed,2500)',
                  'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
                  'S = S_found[.COMPLETION = NORMAL]', '$test_variable_pack_front(S)',
                  'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
                  '$config_invoke_valid(S,pconfigcall_S)',
                  '$exit_fixed(S,pconfigcall_S.SITE) = (($ptascii("constant"),eps))',
                  'pconfigcall_S.OWNER = eps /\\ pconfigcall_S.SELECTION = eps',
                  'pconfigcall_S.INDEX = 1',
                  'pconfigcall_S.PACKS = [pconfigpack_S]',
                  'pconfigpack_S.INDEX = 0',
                  '$config_pack_source_valid(S,pconfigcall_S,pconfigpack_S)',
                  '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((NExprVariable (BYTES text_alias) metadata_alias,true,eps,porigin_alias,z_alias))',
                  'pconfigpack_S.SITE = porigin_alias',
                  '$lookup(S.ENV,$base64(text_alias)) = (n_cv_alias)',
                  'S.STORE[n_cv_alias] = DEFINED (PARRAY n_array)',
                  'pconfigpack_S.ARRAY = n_array',
                  'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]',
                  'S.STORE[n_leaf] = DEFINED pvalue_leaf',
                  'pconfigpack_S.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
                  'pconfigpack_S.ITEMS = $config_pack_capture(S,S.ARRAYS[n_array].ITEMS)',
                  'pconfigcall_S.SENT = [NAMED_SENT (KNOWN pvalue_leaf)]',
                  '$string_bytes(pvalue_leaf) = ($ptascii("__COMPILER_HALT_OFFSET__"))',
                  '~$dynamic_halt_cv_pack_constant(S,pconfigcall_S)',
                  '~$dynamic_halt_valid(S,pconfigcall_S)',
                  '$dynamic_halt_receive(S,pconfigcall_S).COMPLETION = UNSUPPORTED "halt offset constant query"',
                  *previous.public('S')]
        return checks
    if name in ('cv-cow-positional', 'cv-key-rewrite-named'):
        offset = source.index(b'PAYLOAD')
        named = name == 'cv-key-rewrite-named'
        checks += front('S', 'S_seed', 0, named, mainfile, offset)
        checks += ['$lookup(S.ENV,$ptascii("s")) = (n_s_cell)',
                   'S.STORE[n_s_cell] = DEFINED (PARRAY n_s_array)',
                   'n_s_array =/= n_array_S',
                   'S.ARRAYS[n_s_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_s)]',
                   '$string_bytes(pvalue_s) = ' + fixed.term(b'__COMPILER_HALT_OFFSET__' if named else b'other')]
        if not named:
            checks += ['S.DECLARATIONS = [PDENTER 0 eps S.REPORTING,PDEXIT 0 PCSCOMPLETE]',
                       'S_unknown = S[.DECLARATIONS = [PDENTER 0 eps S.REPORTING]]',
                       '$dynamic_halt_lookup(S_unknown,' + mainfile + ',S_unknown.DECLARATIONS) = HALT_UNKNOWN',
                       '$dynamic_halt_valid(S_unknown,pconfigcall_S)',
                       '$dynamic_halt_receive(S_unknown,pconfigcall_S).COMPLETION = UNSUPPORTED "halt offset constant query"']
        checks += value_step('S_value', 'S_resume', offset)
        checks += previous.final('S_final', 'S_value', expected.decode())
    elif name == 'cv-repeated-site':
        offset = source.index(b'PAYLOAD')
        checks += front('S', 'S_seed', 0, False, mainfile, offset)
        checks += value_step('S_first_value', 'S_resume', offset)
        checks += front('S_named', 'S_first_value', 0, True, mainfile, offset)
        checks += ['pconfigcall_S.SITE = pconfigcall_S_named.SITE',
                   'n_array_S =/= n_array_S_named',
                   '$test_outputs(S_named.EVENTS) = ' + fixed.term(b'P:' + str(offset).encode() + b'|N:')]
        checks += value_step('S_second_value', 'S_named_resume', offset)
        checks += previous.final('S_final', 'S_second_value', expected.decode())
    else:
        assert name == 'cv-absent-trace'
        checks += front('S', 'S_seed', 0, False, mainfile, None)
        checks += fixed.error_checks('S', mainfile, expected)
    return checks


def execute(name, checks, out):
    target = out / name
    target.mkdir()
    (target / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
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
    tracked = [Path(__file__), ROOT / 'tests/semantics/halt_cv_pack_sources.py',
               sources / 'native-report.json', ROOT / 'spec/semantics/400-dynamic-constants.watsup',
               ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/profile.json',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               types.PHP, ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
               ROOT / '_build/default/adapter/main.exe']
    input_hashes = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in tracked}
    before = input_hashes()
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
              'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'inputs': before, 'stable_inputs': before == input_hashes(), 'records': records}
    if not report['stable_inputs']:
        report['result'] = 'fail'
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
