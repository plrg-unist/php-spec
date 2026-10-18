#!/usr/bin/env python3
"""Independent captured object, property reference and throwing duplicate cleanup."""
import base64
import hashlib
import json
from pathlib import Path

import define_stdclass_protocol as protocol
import define_stdclass_review_sources as sources

packet, std, common = protocol.packet, protocol.std, protocol.common
ROOT, text, term = protocol.ROOT, protocol.text, protocol.term
TARGET = 'V65_REVIEW_DYN'
PREFIX = protocol.PREFIX + r'''
dec $test_std_define_review_throw(pstate) : bool
def $test_std_define_review_throw(S) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
  -- if preqbytes = $ptascii("V65_REVIEW_DYN")
def $test_std_define_review_throw(S) = false -- otherwise
dec $test_std_define_review_seek(pstate, nat) : pstate
def $test_std_define_review_seek(S,0) = S
def $test_std_define_review_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_std_define_review_throw(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_std_define_review_seek(S,n) = $test_std_define_review_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_std_define_review_throw(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def checks(initial, stdout):
    assert stdout == b'B|T|L|R|41|23|H|L|E|V65_STOP|L|53|23|A|'
    values = [*protocol.fresh(initial, TARGET, 'V65_REVIEW_LEFT'),
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (POBJECT n_object)),NAMED_SENT (KNOWN (PBOOL false))]',
        '$config_nodes(pconfigcall) = [HOBJECT n_object]',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V65_REVIEW_RIGHT")) = (puserconstant_right)',
        'puserconstant_right.VALUE = POBJECT n_right', 'n_right =/= n_object',
        'puserconstant_right.CLASS = PVSTDCLASS n_right porigin_right',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_right) = (pconstantstdobject_right)',
        '$global_std_completed(S,pconstantstdobject_right)',
        'S.CONSTANTSTDOBJECTS = [pconstantstdobject,pconstantstdobject_right]',
        '$lookup(S.ENV,$ptascii("payload")) = (n_payload)',
        'S.STORE[n_payload] = DEFINED (POBJECT n_right)',
        'S_row.STORE[n_payload] = DEFINED (POBJECT n_right)',
        'n_owners = 2', '$heap_owners($heap_graph(S_row),HOBJECT n_object) = 2',
        '$heap_owners($heap_graph(S_row),HOBJECT n_right) = 2',
        *protocol.property_value('S', 'n_object', 17, 'left_initial'),
        *protocol.property_value('S', 'n_right', 23, 'right_initial'),
        *protocol.reach('S_dup', 'S_row', 1, TARGET),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        'pconfigcall_dup.NAMED', 'pconfigcall_dup.SELECTION = (n_selection_dup)',
        'n_selection_dup =/= n_selection', 'pconfigcall_dup.SITE =/= pconfigcall.SITE',
        'pconfigcall_dup.SENT = [NAMED_SENT (KNOWN pvalue_name_dup),NAMED_SENT (KNOWN (POBJECT n_right))]',
        '$string_bytes(pvalue_name_dup) = (' + text(TARGET) + ')',
        '$config_nodes(pconfigcall_dup) = [HOBJECT n_right]',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS', 'n_constants = |S_dup.USERCONSTANTS|',
        'n_constants = 3', 'S_dup.CONSTANTSTDOBJECTS = S_row.CONSTANTSTDOBJECTS',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,n_constants)',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 3',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_object) = 2',
        '$property_slot_at($object_table_slots_at(S_dup,n_object),$ptascii("value")) = (ppropertyslot_ref)',
        'ppropertyslot_ref.STATE = PROP_VALUE (ALIAS n_property)',
        'n_property <- S_dup.REFCELLS', '(HCELL n_property) <- S_dup.ALLOCATIONS',
        'S_dup.STORE[n_property] = DEFINED (PINT 41)',
        '$heap_owners($heap_graph(S_dup),HCELL n_property) = 1',
        *protocol.property_value('S_dup', 'n_right', 23, 'right_dup'),
        # Pure invalid call projections are never driven.
        'pconfigcall_dup_true = pconfigcall_dup[.SENT = [NAMED_SENT (KNOWN pvalue_name_dup),NAMED_SENT (KNOWN (POBJECT n_right)),NAMED_SENT (KNOWN (PBOOL true))]]',
        '~$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup_true,n_constants)',
        '~$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,0)',
        '~$dynamic_define_source(S_dup[.SELECTEDCALLS = eps][.SELECTSEQ = 0],pconfigcall_dup.SITE)',
        *common.step('S_dispatch', 'S_dup'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dup*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup n_constants',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text(TARGET) + ')',
        '$error_call_valid(S_dispatch,perrorcall)',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HOBJECT n_right]',
        'S_dispatch.USERCONSTANTS = S_dup.USERCONSTANTS', 'S_dispatch.EVENTS = S_dup.EVENTS',
        *protocol.reach('S_entered', 'S_dispatch', 3, TARGET),
        'S_entered.CURRENT = (pcallcontext_entered)',
        '$error_context_call(S_entered,pcallcontext_entered) = (perrorcall_entered)',
        'perrorcall_entered.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup n_constants',
        '$task_nodes(perrorcall_entered.RESUME) = [HOBJECT n_right]',
        'S_entered.USERCONSTANTS = S_dup.USERCONSTANTS',
        '$heap_owners($heap_graph(S_entered),HOBJECT n_right) = 3',
        '$test_outputs(S_entered.EVENTS) = ' + term(b'B|T|L|R|41|23|'),
        # Reach the actual resumed caller with Exception search; no DUP result
        # task is inserted when the handler throws.
        'S_throw_found = $test_std_define_review_seek(S_entered,5000)',
        r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
        'S_throw = $test_running(S_throw_found)', '$test_std_define_review_throw(S_throw)',
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup n_constants',
        'S_throw.USERCONSTANTS = S_dup.USERCONSTANTS',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V65_STOP"))',
        'S_throw.STORE[n_property] = DEFINED (PINT 53)',
        '$property_slot_at($object_table_slots_at(S_throw,n_object),$ptascii("value")) = (ppropertyslot_ref)',
        *protocol.property_value('S_throw', 'n_right', 23, 'right_throw'),
        '$test_outputs(S_throw.EVENTS) = ' + term(b'B|T|L|R|41|23|H|L|'),
        '$task_nodes(ERROR_HANDLER_RESULT perrorcall_throw) = [HOBJECT n_right]',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("function"))) = (DIRECT pvalue_trace_function)',
        '$string_bytes(pvalue_trace_function) = ($ptascii("define"))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (POBJECT n_right))',
        'H_throw = $heap_graph(S_throw)',
        '$heap_edge_owners(HOBJECT n_right,H_throw.EDGES,[HARRAY n_trace_args]) = 1',
        'n_throw_owners = $heap_owners(H_throw,HOBJECT n_right)',
        'n_throw_owners = 4', *common.public('S_throw'), '$gc_state_valid(S_throw)',
        # Compare call cleanup after one genuine step. The driver may also
        # buffer an owner decrease in GC; that bookkeeping is checked separately.
        'S_discard = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_throw.RESUME),perrorcall_throw.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall_throw.RESUME) = S_expected',
        *common.step('S_after', 'S_throw'),
        'S_after[.GC = S_expected.GC] = S_expected', *common.public('S_after'), '$gc_state_valid(S_after)',
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_after.RESULT = KNOWN PNULL', 'S_after.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_after.EVENTS = S_throw.EVENTS', 'S_after.STORE[n_property] = DEFINED (PINT 53)',
        'H_after = $heap_graph(S_after)', 'H_after.NODES = H_throw.NODES', 'H_after.EDGES = H_throw.EDGES',
        '$heap_owners(H_after,HOBJECT n_right) = $(n_throw_owners - 1)',
        '$heap_edge_owners(HOBJECT n_right,H_after.EDGES,[HARRAY n_trace_args]) = 1',
        *protocol.finish('S_after', stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.CONSTANTSTDOBJECTS = S_row.CONSTANTSTDOBJECTS',
        'S_final.DESTRUCTION.REJECTED = eps',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 2',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~((HOBJECT n_error) <- S_final.ALLOCATIONS)',
        '~((HARRAY n_trace_args) <- S_final.ALLOCATIONS)',
        'S_final.STORE[n_property] = DEFINED (PINT 53)',
        '$property_slot_at($object_table_slots_at(S_final,n_object),$ptascii("value")) = (ppropertyslot_ref)',
        *protocol.property_value('S_final', 'n_right', 23, 'right_final')]
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
            row, = [r for r in native['records'] if r['id'] == name]
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
    raise SystemExit(0 if packet.main() else 1)
