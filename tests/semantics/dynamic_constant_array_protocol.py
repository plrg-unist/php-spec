#!/usr/bin/env python3
"""Reached define-array snapshots, rebuilt tables and literal constraints."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
STAGES = {'append': ('static-native-v42', 'append-copy', 'V42_NEXT'),
    'nested': ('static-native-v42-literal', 'nested-reference-literal', 'V42_REFS')}
b64 = lambda data: base64.b64encode(data).decode()
PREFIX = r'''
dec $test_output_item(pevent) : nat*
def $test_output_item(OUTPUT n*) = n*
def $test_output_item(pevent) = eps -- otherwise
dec $test_outputs(pevent*) : nat*
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output_item(pevent) ++ $test_outputs(pevent_tail*)
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_define_front(pstate) : bool
def $test_define_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
def $test_define_front(S) = false -- otherwise
dec $test_define_seek(pstate, nat) : pstate
def $test_define_seek(S, 0) = S
def $test_define_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_define_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_seek(S, n) = $test_define_seek($drive_steps($test_running(S), 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def bad_table(label, table, index='n_copy', state='S_row'):
    bad = 'S_' + label
    return [bad + ' = ' + state + '[.ARRAYS = $array_replace(' + state + '.ARRAYS,' + index + ',' + table + ')]',
        '$heap_valid($heap_graph(' + bad + '))',
        '$dynamic_array_value(' + bad + ',PARRAY n_copy,eps,false) = eps',
        '~$call_descriptors_valid(' + bad + ')']


def assertions(main, case, constant, stdout, stage):
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        'S_found = $test_define_seek(S_initial,1000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_define_front(S)',
        'S.FILEINCLUDEPATH = eps', 'S.USERCONSTANTS = eps',
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes_name,PARRAY n_input))',
        'preqbytes_name = $ptascii(' + json.dumps(constant) + ')',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'parray_input = S.ARRAYS[n_input]', 'n_before = |S.ARRAYS|', *public('S'),
        'S_after = $drive_steps(S,1)',
        r'S_after.COMPLETION = NORMAL \/ S_after.COMPLETION = BUDGET',
        'S_row = S_after[.COMPLETION = NORMAL]',
        'S_row.USERCONSTANTS = [puserconstant]',
        'puserconstant.ORIGIN = pconfigcall.SITE',
        'puserconstant.NAME = $user_constant_key(preqbytes_name)',
        'puserconstant.VALUE = PARRAY n_copy', 'n_copy =/= n_input',
        '$(n_copy >= n_before)', 'S_row.ARRAYS[0:n_before] = S.ARRAYS',
        'parray_copy = S_row.ARRAYS[n_copy]',
        'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
        'S_row.RESULT = KNOWN (PBOOL true)', 'S_row.EVENTS = S.EVENTS',
        '$source_constant_lookup(S_row,preqbytes_name) = (VALUE (PARRAY n_copy))',
        '$dynamic_array_value(S_row,PARRAY n_copy,eps,false) = ((S_row,PARRAY n_copy,puserconstant.CLASS))',
        '(HARRAY n_copy) <- $heap_graph(S_row).ROOTS', *public('S_row')]
    if stage == 'append':
        checks += ['parray_input.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
            'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_string) n_bytes*',
            'n_bytes* = $ptascii("v41")', '$string_carrier_valid(S_row,pvalue_leaf)',
            'parray_input.NEXT = 2', 'parray_input.SERIAL = 2',
            'parray_copy = $array_insert($array_empty(),KINT 0,DIRECT pvalue_leaf)',
            'parray_copy.NEXT = 1', 'parray_copy.SERIAL = 1',
            'puserconstant.CLASS = PVARRAY false ([(KINT 0,PVSTRING false)])']
        checks += bad_table('next', 'parray_copy[.NEXT = parray_input.NEXT]')
        checks += bad_table('serial', 'parray_copy[.POSITIONS = [POSITION (KINT 0) 1]][.SERIAL = parray_input.SERIAL]')
        checks += bad_table('carrier', 'parray_copy[.ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S_row.STRINGDATA|)) n_bytes*))]]')
        checks += ['S_structural = S_row[.ARRAYS = $array_replace(S_row.ARRAYS,n_copy,parray_copy[.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]])][.USERCONSTANTS = [puserconstant[.CLASS = PVARRAY false ([(KINT 0,PVSCALAR)])]]]',
            '$user_constants_valid(S_structural,S_structural.USERCONSTANTS)']
    else:
        left, nested, right = ['$ptascii(' + json.dumps(key) + ')' for key in ('left', 'nested', 'right')]
        checks += ['parray_input.ITEMS = [ENTRY (KSTRING ' + left + ') (ALIAS n_cell),ENTRY (KSTRING ' + nested + ') (DIRECT (PARRAY n_child_input))]',
            'S.ARRAYS[n_child_input].ITEMS = [ENTRY (KSTRING ' + right + ') (ALIAS n_cell)]',
            'S.STORE[n_cell] = DEFINED (PINT 17)', '(HCELL n_cell) <- S.ALLOCATIONS',
            'parray_copy.ITEMS = [ENTRY (KSTRING ' + left + ') (DIRECT (PINT 17)),ENTRY (KSTRING ' + nested + ') (DIRECT (PARRAY n_child_copy))]',
            'n_child_copy =/= n_child_input', 'n_child_copy =/= n_copy',
            'parray_child = S_row.ARRAYS[n_child_copy]',
            'parray_child = $array_insert($array_empty(),KSTRING ' + right + ',DIRECT (PINT 17))',
            'parray_copy = $array_insert($array_insert($array_empty(),KSTRING ' + left + ',DIRECT (PINT 17)),KSTRING ' + nested + ',DIRECT (PARRAY n_child_copy))',
            'pvalueclass_child = PVARRAY false ([(KSTRING ' + right + ',PVSCALAR)])',
            'puserconstant.CLASS = PVARRAY false ([(KSTRING ' + left + ',PVSCALAR),(KSTRING ' + nested + ',pvalueclass_child)])',
            '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps',
            'pconfigcall.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '~$dynamic_array_source(S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0],puserconstant.ORIGIN)',
            '~$call_descriptors_valid(S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0])']
        checks += bad_table('alias', 'parray_copy[.ITEMS = [ENTRY (KSTRING ' + left + ') (ALIAS n_cell),ENTRY (KSTRING ' + nested + ') (DIRECT (PARRAY n_child_copy))]]')
        checks += bad_table('child_alias', 'parray_child[.ITEMS = [ENTRY (KSTRING ' + right + ') (ALIAS n_cell)]]', index='n_child_copy')
        checks += ['S_cycle = S[.STORE = $set_cell(S.STORE,n_cell,DEFINED (PARRAY n_input))]',
            '$dynamic_array_value(S_cycle,PARRAY n_input,eps,true) = eps',
            'S_dag = S[.ARRAYS = $array_replace(S.ARRAYS,n_input,parray_input[.ITEMS = [ENTRY (KSTRING ' + left + ') (DIRECT (PARRAY n_child_input)),ENTRY (KSTRING ' + nested + ') (DIRECT (PARRAY n_child_input))]])]',
            '$dynamic_array_value(S_dag,PARRAY n_input,eps,true) = ((S_dag_copy,PARRAY n_dag,pvalueclass_dag))',
            'S_dag_copy.ARRAYS[n_dag].ITEMS = [ENTRY (KSTRING ' + left + ') (DIRECT (PARRAY n_dag_left)),ENTRY (KSTRING ' + nested + ') (DIRECT (PARRAY n_dag_right))]',
            'n_dag_left =/= n_dag_right', 'S_dag_copy.ARRAYS[n_dag_left] = S_dag_copy.ARRAYS[n_dag_right]']
    wrong_class = 'PVARRAY true ([(KINT 0,PVSTRING false)])' if stage == 'append' else \
        'PVARRAY true ([(KSTRING ' + left + ',PVSCALAR),(KSTRING ' + nested + ',pvalueclass_child)])'
    variants = ['[puserconstant[.ORIGIN = PORIGIN 0 eps]]',
        '[puserconstant[.NAME = $ptascii("V42_FORGED")]]',
        '[puserconstant[.VALUE = PARRAY n_input]]',
        '[puserconstant[.CLASS = ' + wrong_class + ']]',
        '[puserconstant[.READS = [{ORIGIN puserconstant.ORIGIN, VALUE (PINT 0), CLASS PVSCALAR, LOOKUP eps}]]]',
        '[puserconstant[.RECEIVES = [{OWNER 0, INDEX 0, FRONTIER (RECEIVE_METHOD puserconstant.ORIGIN puserconstant.ORIGIN puserconstant.ORIGIN 0), CAUSE {UNIT 0, CALLS eps, AUTOLOAD eps}}]]]',
        '[puserconstant,puserconstant]']
    if stage == 'append':
        variants += ['[puserconstant[.CLASS = PVARRAY false ([(KINT 0,PVSTRING true)])]]']
    checks += ['~$user_constants_valid(S_row[.USERCONSTANTS = ' + variant + '],' + variant + ')' for variant in variants]
    checks += ['~$call_descriptors_valid(S_row[.USERCONSTANTS = ' + variant + '])' for variant in variants]
    if stage == 'nested':
        checks += ['S_literal_found = $test_define_seek(S_row,1000)',
            r'S_literal_found.COMPLETION = NORMAL \/ S_literal_found.COMPLETION = BUDGET',
            'S_literal = S_literal_found[.COMPLETION = NORMAL]',
            'S_literal.TODO = (CONFIG_INVOKE pconfigcall_literal) :: ptask_literal*',
            '$dynamic_array_call_valid(S_literal,pconfigcall_literal)',
            '$dynamic_define_values(pconfigcall_literal) = (($ptascii("V42_LITERAL"),PARRAY n_literal_input))',
            '$dynamic_define_known(S_literal,pconfigcall_literal.SITE,1) = (PARRAY n_known)',
            'S_literal.USERCONSTANTS = [puserconstant]', *public('S_literal'),
            'S_literal_after = $drive_steps(S_literal,1)',
            r'S_literal_after.COMPLETION = NORMAL \/ S_literal_after.COMPLETION = BUDGET',
            'S_literal_row = S_literal_after[.COMPLETION = NORMAL]',
            'S_literal_row.USERCONSTANTS = [puserconstant,puserconstant_literal]',
            'puserconstant_literal.ORIGIN = pconfigcall_literal.SITE',
            'puserconstant_literal.VALUE = PARRAY n_literal',
            'n_literal =/= n_known', 'n_literal =/= n_literal_input',
            'parray_literal = S_literal_row.ARRAYS[n_literal]',
            'parray_literal = $array_insert($array_empty(),KSTRING ($ptascii("n")),DIRECT (PINT 17))',
            'puserconstant_literal.CLASS = PVARRAY false ([(KSTRING ($ptascii("n")),PVSCALAR)])',
            '$dynamic_array_known_matches(S_literal_row,PARRAY n_literal,(PARRAY n_known))', *public('S_literal_row'),
            'S_literal_bad = S_literal_row[.ARRAYS = $array_replace(S_literal_row.ARRAYS,n_literal,parray_literal[.ITEMS = [ENTRY (KSTRING ($ptascii("n"))) (DIRECT (PINT 18))]])]',
            '$heap_valid($heap_graph(S_literal_bad))',
            '$dynamic_array_value(S_literal_bad,PARRAY n_literal,eps,false) = ((S_literal_bad,PARRAY n_literal,puserconstant_literal.CLASS))',
            '~$dynamic_array_known_matches(S_literal_bad,PARRAY n_literal,(PARRAY n_known))',
            '~$call_descriptors_valid(S_literal_bad)',
            'S_continue = S_literal_row']
    else:
        checks += ['S_continue = S_row']
    checks += ['S_final = $drive_steps(S_continue,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FILEINCLUDEPATH = eps',
        '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(stdout) + ')',
        '$user_constant_at(S_final.USERCONSTANTS,preqbytes_name) = (puserconstant)', *public('S_final')]
    if stage == 'nested':
        checks += ['S_final.STORE[n_cell] = DEFINED (PINT 31)',
            'S_final.ARRAYS[n_copy] = parray_copy', 'S_final.ARRAYS[n_child_copy] = parray_child']
    else:
        checks += ['S_final.ARRAYS[n_copy] = parray_copy']
    return checks


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for stage in names:
            suite, case_name, constant = STAGES[stage]
            case = sources / suite / case_name
            native = json.loads((case.parent / 'report.json').read_text())
            row, = [item for item in native['records'] if item['id'] == case_name]
            assert native['result'] == 'native_observation' and native['stable_inputs']
            assert native['target'] == types.PROFILE and row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted'], parsed
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            checks = assertions(main, case, constant, row['stdout'], stage)
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names, out, sources = args.stage or list(STAGES), args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for name in names:
        suite, case, _ = STAGES[name]
        paths += [sources / suite / 'report.json', sources / suite / 'run.py', sources / suite / case / 'main.php']
        paths += [sources / suite / case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    assert not (out / (label + '-report.json')).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())), 'inputs': before,
        'implementation_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'records': [], 'agreement_credit': 0, 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
        else:
            mods = [str(ROOT / item) for item in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                target = out / name
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *mods,
                    str(target / 'protocol.watsup')], target / label, 90, ROOT)
                passed = runner.returncode == 0 and runner.stdout.strip() == b'true' and not runner.stderr
                report['records'].append({'id': name, 'pass': passed, 'runner_exit': runner.returncode,
                    'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]), flush=True)
                if not passed:
                    break
        report['result'] = 'pass' if args.phase == 'fixtures' or len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'], record['premises'] = False, 0
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['result'] == 'pass' else 1)


if __name__ == '__main__':
    main()
