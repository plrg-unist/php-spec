#!/usr/bin/env python3
"""A fresh invokable selects its ordinary receiver target before arguments."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_invokable_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
DYNAMIC = ('S.TODO = (CALL_DYNAMIC porigin_inner z_init z_call) :: ptask_dynamic_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_receiver) -- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = METHOD_TARGET n_receiver_current porigin_method_current')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 0 eps) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_result) -- if S.CURRENT = eps')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) -- if S.CURRENT = (pcallcontext_return) '
          '-- if pcallcontext_return.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_return n_arguments n_named pvalue*')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, DYNAMIC)
for label, front in [('producer', PRODUCER), ('result', RESULT), ('return', RETURN), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$invoke212_' + label + '_')
PREFIX += r'''
dec $invoke212_outer_one(ptask) : pmagicmethodcall?
def $invoke212_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 0 eps) = (pmagicmethodcall)
def $invoke212_outer_one(ptask) = eps -- otherwise
dec $invoke212_outer(ptask*) : pmagicmethodcall?
def $invoke212_outer(eps) = eps
def $invoke212_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $invoke212_outer_one(ptask) = (pmagicmethodcall)
def $invoke212_outer(ptask :: ptask_tail*) = $invoke212_outer(ptask_tail*) -- if $invoke212_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S_dynamic = S_found[.COMPLETION = NORMAL]', DYNAMIC.replace('S.', 'S_dynamic.'),
        '$invoke212_outer(ptask_dynamic_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S_dynamic,(pmagicmethodcall.SITE),0) = (porigin_inner)',
        '$origin_node(S_dynamic.SOURCES,porigin_inner) = (expression_inner)',
        'expression_inner = NExprFuncCall expression_receiver (SEQUENCE phpType7_real*) metadata_invoke',
        'expression_receiver = NExprNew (NName (BYTES text_class) metadata_class) (SEQUENCE phpType7_ctor*) metadata_new',
        '$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_receiver)',
        '$magic_method_fresh_receiver(S_dynamic,porigin_receiver,expression_receiver) = (porigin_class)',
        '$object_class_origin(S_dynamic,n_receiver) = (porigin_class)',
        '$effective_method(S_dynamic,porigin_class,$ptascii("__invoke"),|S_dynamic.CLASSES|) = (pmethoddesc)',
        '$object_invoke_method(S_dynamic,n_receiver) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION',
        'pmethoddesc.OWNER =/= porigin_class',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        r'~pmethoddesc.STATIC /\ ~pmethoddesc.ABSTRACT',
        '|phpType7_real*| = 2',
        '$magic_method_argument_source(S_dynamic,porigin_inner,0,expression_inner)',
        '$magic_method_copy_source(S_dynamic,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_copy_values(S_dynamic[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS[0:1],0,[KNOWN (PINT 7)]) = eps',
        '$magic_method_copy_values(S_dynamic[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS[0:1],0,[KNOWN (POBJECT pmagicmethodcall.OBJECT)]) = eps',
        '$factory182_output(S_dynamic.EVENTS) = $ptascii("CTOR;")',
        '$lookup(S_dynamic.ENV,$ptascii("late")) = (n_late_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_dynamic.STORE[n_late_cell] = DEFINED pvalue_string',
        '$string_carrier_valid(S_dynamic,pvalue_string)',
        '$objectprops_at(S_dynamic.OBJECTPROPS,n_receiver) = (ppropertyslot_receiver_items*)',
        '$property_slot_at(ppropertyslot_receiver_items*,$ptascii("text")) = (ppropertyslot_text)',
        'ppropertyslot_text.STATE = PROP_VALUE (DIRECT pvalue_string)',
        'pcalltarget = METHOD_TARGET n_receiver pfunction.ORIGIN',
        'S_selected = $drive_steps(S_dynamic,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (FUNCTION_CACHE_INIT pcalltarget (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_inner) z_call)) :: ptask_dynamic_tail*',
        'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_selected.OBJECTS = S_dynamic.OBJECTS',
        '$target_instance(pcalltarget) = eps',
        '$target_receiver(S_selected,pcalltarget) = (n_receiver)',
        '$target_lexical_class(S_selected,pcalltarget) = (pmethoddesc.OWNER)',
        '$target_called_class(S_selected,pcalltarget) = (porigin_class)',
        '$call_selected_valid(S_selected,pcalltarget,(porigin_inner))',
        '$task_nodes(S_selected.TODO[0]) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_receiver) = 1',
        '$factory182_output(S_selected.EVENTS) = $ptascii("CTOR;")',
        'S_ready = $drive_steps(S_selected[.COMPLETION = NORMAL],1)',
        'S_ready.COMPLETION = BUDGET',
        'S_ready.TODO = (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_inner) z_call) :: ptask_dynamic_tail*',
        'S_direct = $drive_steps(S_dynamic,2)', 'S_direct = S_ready',
        '$call_descriptors_valid(S_ready)', '$gc_state_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
        'S_producer_found = $invoke212_producer_seek(S_ready[.COMPLETION = NORMAL],2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_receiver', 'n_receiver_current = n_receiver',
        'porigin_method_current = pfunction.ORIGIN',
        'pcallcontext_producer.INSTANCE = eps',
        'pcallcontext_producer.RECEIVER = (n_receiver)',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_producer.CALLED_CLASS = (porigin_class)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_receiver) = 2',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$objectprops_at(S_producer.OBJECTPROPS,n_receiver) = (ppropertyslot_receiver_items*)',
        '$factory182_output(S_producer.EVENTS) = $ptascii("CTOR;SHIFT;PRODUCER:PeerProducerBase212:PeerProducerChild212;")',
        '$call_current_valid(S_producer)', '$gc_state_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_result_found = $invoke212_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_receiver', 'pmagicmethodcall_result = pmagicmethodcall',
        'S_result.FRAMES = eps',
        '~((HCELL n_saved_cell) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
        '$magic_method_copy_source(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        'S_sent = $drive_steps(S_result,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 1 ([KNOWN (POBJECT n_receiver)])) :: ptask_result_tail*',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_receiver) = 1',
        'S_return_found = $invoke212_return_seek(S_sent[.COMPLETION = NORMAL],2048)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'pmagicmethodcall_return = pmagicmethodcall',
        'pvalue* = [POBJECT n_receiver,PFLOAT 4609434218613702656]', 'n_arguments = n_named',
        'S_return.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (POBJECT n_receiver)),ENTRY (KSTRING $ptascii("later")) (DIRECT (PFLOAT 4609434218613702656))]',
        '$node_children(S_return,HARRAY n_arguments) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_receiver) = 1',
        '$node_children(S_return,HOBJECT n_closure) = [HARRAY n_arguments]',
        'S_child_found = $invoke212_child_seek(S_return,2048)', 'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        '$lookup(S_child.ENV,$ptascii("child")) = (n_child_cell)',
        'S_child.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_child.OBJECTPROPS,n_child) = (ppropertyslot_child_items*)',
        '$property_slot_at(ppropertyslot_child_items*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        'S_child.ARRAYS[n_arguments] = S_return.ARRAYS[n_arguments]',
        '$node_children(S_child,HARRAY n_arguments) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_child),HOBJECT n_receiver) = 1',
        '$objectprops_at(S_child.OBJECTPROPS,n_receiver) = (ppropertyslot_receiver_items*)',
        '$string_carrier_valid(S_child,pvalue_string)',
        '$factory182_output(S_child.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']).rsplit(b'CHILD;', 1)[0], filename),
        'S_done = $drive_steps(S_child,4096)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$magic_method_copy_source(S_done,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
