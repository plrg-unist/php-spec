#!/usr/bin/env python3
"""Independent abrupt copied-candidate release with original input trace roots."""
import base64
import hashlib
import json
from pathlib import Path

import define_stdclass_protocol as define
import define_stdclass_array_duplicate_review_sources as sources

packet, std, common = define.packet, define.std, define.common
ROOT, text, term = define.ROOT, define.text, define.term
TARGET = 'V67_REVIEW_TARGET'
PREFIX = define.PREFIX + r'''
dec $test_array_duplicate_peer_front(pstate, nat) : bool
def $test_array_duplicate_peer_front(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V67_REVIEW_TARGET"),pvalue))
def $test_array_duplicate_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V67_REVIEW_TARGET"),pvalue))
def $test_array_duplicate_peer_front(S,n_phase) = false -- otherwise
dec $test_array_duplicate_peer_seek(pstate, nat, nat) : pstate
def $test_array_duplicate_peer_seek(S,n_phase,0) = S
def $test_array_duplicate_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_duplicate_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_duplicate_peer_seek(S,n_phase,n) = $test_array_duplicate_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_duplicate_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_duplicate_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_duplicate_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|2|17|E|V67_STOP|define|R|17|41|19|31|kept|A|'
    head, nested, leaf = [text(key) for key in ('head', 'nested', 'leaf')]
    values = [*initial, *define.reach('S', 'S_initial', 1, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = ' + text(TARGET),
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$config_nodes(pconfigcall) = [HARRAY n_input]',
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right,puserconstant_old]',
        'puserconstant_old.NAME = preqbytes', 'puserconstant_old.VALUE = PINT 17',
        'puserconstant_old.CLASS = PVSCALAR',
        'puserconstant_left.NAME = $ptascii("V67_REVIEW_LEFT")',
        'puserconstant_left.VALUE = POBJECT n_left',
        'puserconstant_left.CLASS = PVSTDCLASS n_left porigin_left',
        'puserconstant_right.NAME = $ptascii("V67_REVIEW_RIGHT")',
        'puserconstant_right.VALUE = POBJECT n_right',
        'puserconstant_right.CLASS = PVSTDCLASS n_right porigin_right',
        'n_left =/= n_right',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_left) = (pconstantstdobject_left)',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_right) = (pconstantstdobject_right)',
        '$global_std_completed(S,pconstantstdobject_left)',
        '$global_std_completed(S,pconstantstdobject_right)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        'S.STORE[n_cell] = DEFINED (POBJECT n_left)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {head}) (ALIAS n_cell),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_input_child))]',
        f'S.ARRAYS[n_input_child].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps',
        'H_before = $heap_graph(S)',
        '$heap_edge_owners(HOBJECT n_left,H_before.EDGES,[HCELL n_cell]) = 1',
        '$heap_owners(H_before,HOBJECT n_left) = 2',
        '$heap_owners(H_before,HOBJECT n_right) = 1',
        '$heap_owners(H_before,HARRAY n_input) = 2',
        'n_constants = |S.USERCONSTANTS|', 'n_constants = 3',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        'n_before = |S.ARRAYS|', '$test_outputs(S.EVENTS) = ' + term(b'B|'),
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_copy pvalueclass_copy n_constants',
        '$error_call_valid(S_dispatch,perrorcall)', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(preqbytes)',
        'perrorcall.LINE = pconfigcall.LINE',
        'n_copy = $(n_before + 1)', 'n_child = n_before',
        'n_copy =/= n_input', 'n_child =/= n_input_child', 'n_child =/= n_copy',
        f'parray_child = $array_insert($array_empty(),KSTRING {leaf},DIRECT (POBJECT n_left))',
        f'parray_root = $array_insert($array_insert($array_empty(),KSTRING {head},DIRECT (POBJECT n_left)),KSTRING {nested},DIRECT (PARRAY n_child))',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        f'pvalueclass_child = PVARRAY false ([(KSTRING {leaf},PVSTDCLASS n_left porigin_left)])',
        f'pvalueclass_copy = PVARRAY false ([(KSTRING {head},PVSTDCLASS n_left porigin_left),(KSTRING {nested},pvalueclass_child)])',
        '$dynamic_array_value(S_dispatch,PARRAY n_copy,eps,false) = ((S_dispatch,PARRAY n_copy,pvalueclass_copy))',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_copy,pvalueclass_copy,n_constants)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_copy,HARRAY n_input]',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HARRAY n_copy,HARRAY n_input]',
        'S_dispatch.RESULT = KNOWN PNULL', 'S_dispatch.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.EVENTS = S.EVENTS',
        'H_dispatch = $heap_graph(S_dispatch)',
        '$heap_owners(H_dispatch,HARRAY n_copy) = 1',
        '$heap_owners(H_dispatch,HARRAY n_child) = 1',
        '$heap_owners(H_dispatch,HARRAY n_input) = 2',
        '$heap_owners(H_dispatch,HOBJECT n_left) = 4',
        '$heap_owners(H_dispatch,HOBJECT n_right) = 1',
        '$heap_edge_owners(HOBJECT n_left,H_dispatch.EDGES,[HARRAY n_copy,HARRAY n_child]) = 2']
    # Pure projections test authority only; none is driven.
    values += [
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_input,pvalueclass_copy,n_constants)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_copy,pvalueclass_copy,0)',
        'n_too_many = $(n_constants + 1)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_copy,pvalueclass_copy,n_too_many)',
        '~$dynamic_array_source(S_dispatch[.SELECTEDCALLS = eps][.SELECTSEQ = 0],pconfigcall.SITE)',
        'n_absent = |S_dispatch.ARRAYS|',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_absent,pvalueclass_copy,n_constants)',
        f'pvalueclass_bad = $pvclass_put(pvalueclass_copy,KSTRING {head},PVOBJECT)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_copy,pvalueclass_bad,n_constants)',
        'S_no_birth = S_dispatch[.CONSTANTSTDOBJECTS = eps]',
        '~$dynamic_array_duplicate_valid(S_no_birth,pconfigcall,n_copy,pvalueclass_copy,n_constants)',
        'S_incomplete = S_dispatch[.CONSTANTSTDOBJECTS = $global_std_record_put(S_dispatch.CONSTANTSTDOBJECTS,pconstantstdobject_left[.COMPLETE = false])]',
        '~$dynamic_array_duplicate_valid(S_incomplete,pconfigcall,n_copy,pvalueclass_copy,n_constants)',
        'S_dead = S_dispatch[.ALLOCATIONS = $destruction_node_delete(S_dispatch.ALLOCATIONS,HOBJECT n_left)]',
        '~$dynamic_array_duplicate_valid(S_dead,pconfigcall,n_copy,pvalueclass_copy,n_constants)',
        'S_empty = S_dispatch[.ARRAYS[n_copy].ITEMS = eps]',
        '~$dynamic_array_duplicate_valid(S_empty,pconfigcall,n_copy,PVARRAY false eps,n_constants)',
        '~$error_call_valid(S_dispatch,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_dispatch,perrorcall[.MESSAGE = $ptascii("wrong")])',
        *reach('S_entered', 'S_dispatch', 0),
        'S_entered.CURRENT = (pcallcontext_entered)',
        '$error_context_call(S_entered,pcallcontext_entered) = (perrorcall_entered)',
        'perrorcall_entered.RESUME = perrorcall.RESUME',
        '$heap_owners($heap_graph(S_entered),HARRAY n_copy) = 1',
        '$heap_owners($heap_graph(S_entered),HOBJECT n_left) = 4',
        *reach('S_throw', 'S_entered', 1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V67_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_side]',
        'puserconstant_side.VALUE = PINT 31', 'puserconstant_side.CLASS = PVSCALAR',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_copy,pvalueclass_copy,n_constants)',
        'S_throw.STORE[n_cell] = DEFINED (POBJECT n_right)',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_throw.ARRAYS[n_input_child] = S.ARRAYS[n_input_child]',
        'S_throw.ARRAYS[n_copy] = parray_root', 'S_throw.ARRAYS[n_child] = parray_child',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V67_STOP"))',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("function"))) = (DIRECT pvalue_function)',
        '$string_bytes(pvalue_function) = ($ptascii("define"))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$task_nodes(ERROR_HANDLER_RESULT perrorcall_throw) = [HARRAY n_copy,HARRAY n_input]',
        'H_throw = $heap_graph(S_throw)',
        '$heap_edge_owners(HARRAY n_input,H_throw.EDGES,[HARRAY n_trace_args]) = 1',
        '$heap_edge_owners(HARRAY n_copy,H_throw.EDGES,[HARRAY n_trace_args]) = 0',
        '$heap_edge_owners(HOBJECT n_left,H_throw.EDGES,[HARRAY n_copy,HARRAY n_child]) = 2',
        '$heap_edge_owners(HOBJECT n_right,H_throw.EDGES,[HCELL n_cell]) = 1',
        '$heap_owners(H_throw,HARRAY n_copy) = 1', '$heap_owners(H_throw,HARRAY n_input) = 3',
        '$heap_owners(H_throw,HOBJECT n_left) = 3', '$heap_owners(H_throw,HOBJECT n_right) = 2',
        *define.property_value('S_throw', 'n_left', 41, 'left_throw'),
        *define.property_value('S_throw', 'n_right', 19, 'right_throw'),
        '$test_outputs(S_throw.EVENTS) = ' + term(b'B|H|2|17|'), '$gc_state_valid(S_throw)',
        # One genuine handler discard retires only the private copied containers.
        'S_pause = $drive_steps(S_throw,0)', 'S_pause = S_throw[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S_throw',
        *common.step('S_after', 'S_resume'), *common.public('S_after'), '$gc_state_valid(S_after)',
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_after.RESULT = KNOWN PNULL', 'S_after.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_after.EVENTS = S_throw.EVENTS', 'S_after.CONSTANTSTDOBJECTS = S_throw.CONSTANTSTDOBJECTS',
        'S_after.STORE[n_cell] = DEFINED (POBJECT n_right)',
        '~((HARRAY n_copy) <- S_after.ALLOCATIONS)', '~((HARRAY n_child) <- S_after.ALLOCATIONS)',
        '(HARRAY n_input) <- S_after.ALLOCATIONS', '(HARRAY n_input_child) <- S_after.ALLOCATIONS',
        '(HOBJECT n_error) <- S_after.ALLOCATIONS',
        'H_after = $heap_graph(S_after)',
        '$heap_owners(H_after,HARRAY n_input) = 2',
        '$heap_edge_owners(HARRAY n_input,H_after.EDGES,[HARRAY n_trace_args]) = 1',
        '$heap_owners(H_after,HOBJECT n_left) = 1', '$heap_owners(H_after,HOBJECT n_right) = 2',
        *define.property_value('S_after', 'n_left', 41, 'left_after'),
        *define.finish('S_after', stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_final.CONSTANTSTDOBJECTS = S.CONSTANTSTDOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~((HARRAY n_input) <- S_final.ALLOCATIONS)', '~((HARRAY n_input_child) <- S_final.ALLOCATIONS)',
        '~((HARRAY n_trace) <- S_final.ALLOCATIONS)', '~((HARRAY n_trace_args) <- S_final.ALLOCATIONS)',
        '~((HOBJECT n_error) <- S_final.ALLOCATIONS)', '~((HCELL n_cell) <- S_final.ALLOCATIONS)',
        *define.property_value('S_final', 'n_left', 41, 'left_final'),
        *define.property_value('S_final', 'n_right', 19, 'right_final')]
    return values


def prepare(out, originals):
    native = json.loads((originals / 'native-report.json').read_text())
    assert native['passed'] and native['inputs_stable']
    frontend = packet.Worker([str(packet.types.PHP), '-n', *packet.types.FLAGS,
        '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = packet.Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in sources.family.CASES:
            path = originals / name / 'main.php'
            row, = [row for row in native['records'] if row['id'] == name]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['source_sha256']
            assert row['process']['exit'] == 0 and not base64.b64decode(row['stderr'])
            parsed = frontend.request({'op': 'parse', 'source': packet.b64(path.read_bytes())})
            assert parsed['accepted']
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            initial = ['S_initial = $php_run(' + main + ',0,' + json.dumps(packet.b64(str(path).encode())) + ')']
            values = checks(initial, base64.b64decode(row['stdout']))
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + value + '\n' for value in values))
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            frontend.close()


packet.sources, packet.prepare = sources, prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
