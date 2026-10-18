#!/usr/bin/env python3
"""Reached raw scalar flag reception, post-Warning snapshots and strict errors."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_array_scalar_flag_sources as sources

define, packet, common, std = prior.define, prior.packet, prior.common, prior.std
ROOT, text, term = prior.ROOT, prior.text, prior.term
PREFIX = define.PREFIX + r'''
dec $test_array_scalar_front(pstate, nat) : bool
def $test_array_scalar_front(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall
def $test_array_scalar_front(S,1) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_cell) metadata_variable) :: expression_tail*
  -- if $base64(text_cell) = $ptascii("cell")
def $test_array_scalar_front(S,n_phase) = false -- otherwise
dec $test_array_scalar_seek(pstate, nat, nat) : pstate
def $test_array_scalar_seek(S,n_phase,0) = S
def $test_array_scalar_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_scalar_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_scalar_seek(S,n_phase,n) = $test_array_scalar_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_scalar_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_scalar_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_scalar_front({state},{phase})', *common.public(state)]


def copied(state, before, cfg, label, number):
    edge, tag = text('edge'), text('tag')
    return [f'n_{label}_child = |{before}.ARRAYS|', f'n_{label}_root = $(n_{label}_child + 1)',
        f'parray_{label}_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT {number}))',
        f'parray_{label}_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_{label}_child))',
        f'{state}.ARRAYS = {before}.ARRAYS ++ [parray_{label}_child,parray_{label}_root]',
        f'$user_constant_at({state}.USERCONSTANTS,$ptascii("V76_{label.upper()}")) = (puserconstant_{label})',
        f'{state}.USERCONSTANTS = {before}.USERCONSTANTS ++ [puserconstant_{label}]',
        f'puserconstant_{label}.VALUE = PARRAY n_{label}_root',
        f'puserconstant_{label}.ORIGIN = {cfg}.SITE',
        f'puserconstant_{label}.CLASS = PVARRAY false ([(KSTRING {edge},PVARRAY false ([(KSTRING {tag},PVSCALAR)]))])',
        f'$heap_owners($heap_graph({state}),HARRAY n_{label}_root) = 1',
        f'$heap_owners($heap_graph({state}),HARRAY n_{label}_child) = 1']


def literal(initial, stdout):
    edge, tag = text('edge'), text('tag')
    values = [*initial, *define.reach('S_false', 'S_initial', 0, 'V76_FALSE'),
        'S_false.TODO = (CONFIG_INVOKE pconfigcall_false) :: ptask_false*',
        '$dynamic_scalar_define_flag_values(pconfigcall_false) = (($ptascii("V76_FALSE"),PARRAY n_input,pvalue_zero))',
        'pvalue_zero = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))',
        '$string_carrier_valid(S_false,pvalue_zero)',
        '$dynamic_scalar_define_flag_valid(S_false,pconfigcall_false)',
        '$dynamic_array_call_valid(S_false,pconfigcall_false)',
        '~$dynamic_scalar_define_flag_case_valid(S_false,pconfigcall_false)',
        '$lookup(S_false.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S_false.REFCELLS',
        '$lookup(S_false.ENV,$ptascii("input")) = (n_input_cell)',
        'S_false.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S_false.STORE[n_cell] = DEFINED (PARRAY n_seed)',
        f'S_false.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S_false.ARRAYS[n_input].NEXT = 91', 'S_false.USERCONSTANTS = eps',
        # The pure getter recognizes the shape; immutable flag facts still refuse it.
        'pconfigcall_wrong_literal = pconfigcall_false[.SENT = $named_slot_set(pconfigcall_false.SENT,2,KNOWN (PINT 0))]',
        '$dynamic_define_values(pconfigcall_wrong_literal) = $dynamic_define_values(pconfigcall_false)',
        '~$dynamic_scalar_define_flag_valid(S_false,pconfigcall_wrong_literal)',
        '~$dynamic_array_call_valid(S_false,pconfigcall_wrong_literal)',
        *common.step('S_fresh', 'S_false', 'PBOOL true'), *common.public('S_fresh'),
        'S_fresh.TODO = ptask_false*', 'S_fresh.EVENTS = S_false.EVENTS',
        *copied('S_fresh', 'S_false', 'pconfigcall_false', 'false', 7),
        'S_fresh.ARRAYS[n_input] = S_false.ARRAYS[n_input]',
        *define.reach('S_true', 'S_fresh', 0, 'V76_TRUE'),
        'S_true.TODO = (CONFIG_INVOKE pconfigcall_true) :: ptask_true*',
        '$dynamic_scalar_define_flag_values(pconfigcall_true) = (($ptascii("V76_TRUE"),PARRAY n_input,pvalue_float))',
        'pvalue_float = PFLOAT 4612811918334230528',
        '$dynamic_scalar_define_flag_valid(S_true,pconfigcall_true)',
        '$dynamic_scalar_define_flag_case_valid(S_true,pconfigcall_true)',
        '$dynamic_array_call_valid(S_true,pconfigcall_true)',
        '~$dynamic_constant_case_valid(S_true,pconfigcall_true)',
        '$lookup(S_true.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S_true.ENV,$ptascii("calls")) = (n_calls)',
        'S_true.STORE[n_flag] = DEFINED pvalue_float', 'S_true.STORE[n_calls] = DEFINED (PINT 0)',
        'S_true.STORE[n_cell] = DEFINED (PARRAY n_leaf11)',
        f'S_true.ARRAYS[n_leaf11].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 11))]',
        # Pure finite/carrier/source controls, never driven.
        '$dynamic_array_quiet_flag(PINT 0)', '$dynamic_array_quiet_flag(PFLOAT 9223372036854775808)',
        '~$dynamic_array_quiet_flag(PFLOAT 9218868437227405312)',
        '~$dynamic_array_quiet_flag(PFLOAT 9221120237041090560)',
        '$dynamic_array_quiet_flag(PSTRING ($ptascii("false")))',
        '$dynamic_constant_class(PSTRING ($ptascii("false"))) = eps',
        '~$dynamic_array_quiet_flag(PNULL)',
        'pconfigcall_int_zero = pconfigcall_true[.SENT = $named_slot_set(pconfigcall_true.SENT,2,KNOWN (PINT 0))]',
        '$dynamic_scalar_define_flag_valid(S_true,pconfigcall_int_zero)',
        '$dynamic_array_call_valid(S_true,pconfigcall_int_zero)',
        '~$dynamic_scalar_define_flag_case_valid(S_true,pconfigcall_int_zero)',
        'n_bad_string = |S_true.STRINGDATA|',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("false"))',
        'pconfigcall_bad = pconfigcall_true[.SENT = $named_slot_set(pconfigcall_true.SENT,2,KNOWN pvalue_bad)]',
        '~$dynamic_scalar_define_flag_valid(S_true,pconfigcall_bad)',
        '~$dynamic_array_call_valid(S_true,pconfigcall_bad)',
        'S_pause = $drive_steps(S_true,0)', 'S_pause = S_true[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S_true',
        *common.step('S_dispatch', 'S_resume'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_true*',
        'perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_true',
        'perrorcall.MESSAGE = $dynamic_constant_case_message()', '$error_call_valid(S_dispatch,perrorcall)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_input]',
        'S_dispatch.ARRAYS = S_true.ARRAYS', 'S_dispatch.ALLOCATIONS = S_true.ALLOCATIONS',
        'S_dispatch.STORE = S_true.STORE', 'S_dispatch.USERCONSTANTS = S_true.USERCONSTANTS',
        *reach('S_done', 'S_dispatch', 0),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
        'perrorcall_done.RESUME = perrorcall.RESUME', 'S_done.RESULT = KNOWN (PBOOL true)',
        'S_done.STORE[n_flag] = DEFINED pvalue_live_flag',
        '$string_bytes(pvalue_live_flag) = ($ptascii("0"))',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
        f'S_done.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 23))]',
        'S_done.STORE[n_input_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KSTRING {edge}) = (ALIAS n_cell)',
        '$entry_lookup(S_done.ARRAYS[n_caller].ITEMS,KINT 90) = (DIRECT (PINT 31))',
        'S_done.ARRAYS[n_input] = S_true.ARRAYS[n_input]',
        'S_done.USERCONSTANTS = S_true.USERCONSTANTS',
        '$dynamic_scalar_define_flag_case_valid(S_done,pconfigcall_true)',
        '~$destructor_operational(S_done)',
        *common.step('S_case', 'S_done'), *common.public('S_case'),
        'S_case.TODO = (DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_true) :: ptask_done*',
        'S_case.ARRAYS = S_done.ARRAYS',
        *common.step('S_row', 'S_case', 'PBOOL true'), *common.public('S_row'),
        'S_row.TODO = ptask_done*', *copied('S_row', 'S_case', 'pconfigcall_true', 'true', 23),
        '~(HARRAY n_input <- S_row.ALLOCATIONS)',
        *common.reach('S_query', 'S_row', 0, 'V76_TRUE'), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,$ptascii("V76_TRUE")) = (PARRAY n_true_root)',
        'n_query_owners = $heap_owners($heap_graph(S_query),HARRAY n_true_root)',
        *common.step('S_value', 'S_query', 'PARRAY n_true_root'),
        'S_value.ARRAYS = S_query.ARRAYS', 'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        '$heap_owners($heap_graph(S_value),HARRAY n_true_root) = $(n_query_owners + 1)',
        *reach('S_cow', 'S_value', 1),
        '$lookup(S_cow.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_cow.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_true_root',
        f'$entry_lookup(S_cow.ARRAYS[n_copy].ITEMS,KSTRING {edge}) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_true_child',
        f'S_cow.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 41))]',
        '$entry_lookup(S_cow.ARRAYS[n_copy].ITEMS,KINT 0) = (DIRECT (PINT 19))',
        'S_cow.ARRAYS[n_true_root] = parray_true_root', 'S_cow.ARRAYS[n_true_child] = parray_true_child',
        'S_cow.ARRAYS[n_false_root] = parray_false_root',
        '$user_constant_at(S_cow.USERCONSTANTS,$ptascii("V76_INT_ZERO")) = (puserconstant_int)',
        'puserconstant_int.VALUE = PARRAY n_int_root',
        f'S_cow.ARRAYS[n_int_root] = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 19))',
        *define.finish('S_cow', stdout),
        'S_final.USERCONSTANTS = [puserconstant_false,puserconstant_true,puserconstant_int]',
        '$heap_owners($heap_graph(S_final),HARRAY n_false_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_false_child) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_true_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_true_child) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_int_root) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy <- S_final.ALLOCATIONS)', '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)']
    return values


def strict(initial, stdout):
    values = [*initial, *define.reach('S', 'S_initial', 0, 'V76_STRICT_TYPE'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SITE = PORIGIN 1 pcpath_call',
        'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_scalar_define_flag_values(pconfigcall) = (($ptascii("V76_STRICT_TYPE"),PARRAY n_input,pvalue_flag))',
        'pvalue_flag = PFLOAT 4612811918334230528',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '~$dynamic_array_call_valid(S,pconfigcall)',
        '~$dynamic_scalar_define_flag_case_valid(S,pconfigcall)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)', '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)', '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.STORE[n_flag] = DEFINED (PINT 0)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_result] = DEFINED pvalue_result', '$string_bytes(pvalue_result) = ($ptascii("kept"))',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps',
        'S.USERCONSTANTS = eps', '$heap_owners($heap_graph(S),HARRAY n_input) = 3',
        'n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        *common.step('S_error', 'S'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, float given"))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_flag)',
        'n_trace = n_arrays', 'n_args = $(n_arrays + 1)', 'n_frame = $(n_arrays + 2)',
        'n_eval = $(n_arrays + 3)',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_eval))',
        '$trace_array_field(S_error,n_eval,$ptascii("function")) = PSTRING ($ptascii("eval"))',
        'parray_trace = S_error.ARRAYS[n_trace]', 'parray_args = S_error.ARRAYS[n_args]',
        'parray_frame = S_error.ARRAYS[n_frame]', 'parray_eval = S_error.ARRAYS[n_eval]',
        'S_error.ARRAYS = S.ARRAYS ++ [parray_trace,parray_args,parray_frame,parray_eval]',
        'S_error.STORE = S.STORE',
        'S_error.USERCONSTANTS = S.USERCONSTANTS', 'S_error.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_error),HARRAY n_input) = 3',
        *define.finish('S_error', stdout), 'S_final.USERCONSTANTS = eps',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)', '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)']
    return values


def prepare(out, originals):
    native = json.loads((originals / 'native-report.json').read_text())
    assert native['passed'] and native['inputs_stable']
    frontend = packet.Worker([str(packet.types.PHP), '-n', *packet.types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = packet.Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in sources.family.CASES:
            path = originals / name / 'main.php'
            row, = [r for r in native['records'] if r['id'] == name]
            assert sources.family.sha(path) == row['source_sha256'] and row['process']['exit'] == 0
            parsed = frontend.request({'op': 'parse', 'source': packet.b64(path.read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            initial = ['S_initial = $php_run(' + main + ',0,' + json.dumps(packet.b64(str(path).encode())) + ')', 'S_initial.COMPLETION = BUDGET']
            selected = any(n['node'] == 'Expr_Eval' for n in std.nodes(parsed['ast']))
            if selected:
                code, = [base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast'])
                    if n['node'] == 'Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'declare(strict_types=1); $result = $api')]
                unit = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval', 'profile': 'cli-raw-85', 'source': packet.b64(code)})
                assert unit['accepted']
                checked = adapter.request({'op': 'check', 'ast': unit['ast'], 'fixture': True})['fixture']
                response = 'SOURCE_ACCEPT 1 ' + term(code) + ' ' + checked
                initial = ['S_wait = $php_run(' + main + ',5000,' + json.dumps(packet.b64(str(path).encode())) + ')', 'S_wait.COMPLETION = SOURCE_PENDING',
                    *common.public('S_wait'), '$eval_response_valid(S_wait,' + response + ')', 'S_initial = $test_running($eval_resume(S_wait,' + response + '))']
            values = (strict if selected else literal)(initial, base64.b64decode(row['stdout']))
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + v + '\n' for v in values))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            frontend.close()


packet.sources, packet.prepare = sources, prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:
        sources.family.CASES = {args.case: sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if packet.main() else 1)
