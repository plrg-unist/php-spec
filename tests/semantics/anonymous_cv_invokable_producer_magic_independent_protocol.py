#!/usr/bin/env python3
"""An actual CV object read freezes implicit __invoke before argument effects."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_invokable_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
READ = ('S.TODO = (CALL_DYNAMIC porigin_inner z_init z_call) :: ptask_read_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("receiver")) z_cv -- if S.CURRENT = eps '
        '-- if $magic_producer_candidate(S,ptask_read_tail*,porigin_inner)')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = METHOD_TARGET n_receiver_current porigin_method_current')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_result) -- if S.CURRENT = eps')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('producer', PRODUCER), ('result', RESULT), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvinvoke213_' + label + '_')
PREFIX += r'''
dec $cvinvoke213_outer_one(ptask) : pmagicmethodcall?
def $cvinvoke213_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $cvinvoke213_outer_one(ptask) = eps -- otherwise
dec $cvinvoke213_outer(ptask*) : pmagicmethodcall?
def $cvinvoke213_outer(eps) = eps
def $cvinvoke213_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvinvoke213_outer_one(ptask) = (pmagicmethodcall)
def $cvinvoke213_outer(ptask :: ptask_tail*) = $cvinvoke213_outer(ptask_tail*) -- if $cvinvoke213_outer_one(ptask) = eps
dec $cvinvoke213_bad_one(ptask) : ptask
def $cvinvoke213_bad_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 eps
def $cvinvoke213_bad_one(ptask) = ptask -- otherwise
dec $cvinvoke213_bad(ptask*) : ptask*
def $cvinvoke213_bad(eps) = eps
def $cvinvoke213_bad(ptask :: ptask_tail*) = $cvinvoke213_bad_one(ptask) :: $cvinvoke213_bad(ptask_tail*)
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S_read = S_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.').replace('(S,', '(S_read,'),
        'S_read.ORIGIN = (porigin_inner)',
        '$dynamic_task_valid(S_read,porigin_inner,z_init,z_call)',
        '$dynamic_fixed_name(S_read,porigin_inner) = eps',
        '$cvinvoke213_outer(ptask_read_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S_read,(pmagicmethodcall.SITE),1) = (porigin_inner)',
        '$origin_node(S_read.SOURCES,porigin_inner) = (expression_inner)',
        'expression_inner = NExprFuncCall (NExprVariable (BYTES text_cv) metadata_cv) (SEQUENCE phpType7_real*) metadata_invoke',
        'z_cv = $variable_line(BYTES text_cv,metadata_cv)',
        'z_init = $dynamic_init_line(S_read,porigin_inner)',
        'z_call = $runtime_line(S_read,eps,expression_inner)',
        '|phpType7_real*| = 2',
        '$magic_producer_cv_parts(S_read,porigin_inner,expression_inner) = ((porigin_inner,VARIABLE ($ptascii("receiver")) z_cv,$ptascii("__invoke"),phpType7_real*,phpType7_real*))',
        '$magic_producer_argument_site(S_read,porigin_inner) = (porigin_inner)',
        '$magic_producer_pending(S_read,S_read.TODO,porigin_inner) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1))',
        '$lookup(S_read.ENV,$ptascii("receiver")) = (n_receiver_cell)',
        '$lookup(S_read.ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        'n_receiver_cell <- S_read.REFCELLS',
        'S_read.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$magic_producer_cell(S_read,$ptascii("receiver")) = (n_receiver)',
        '$object_class_origin(S_read,n_receiver) = (porigin_class)',
        '$magic_producer_selected_source(S_read,porigin_inner,porigin_class) = (pmethoddesc)',
        '$effective_method(S_read,porigin_class,$ptascii("__invoke"),|S_read.CLASSES|) = (pmethoddesc)',
        '$object_invoke_method(S_read,n_receiver) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION',
        'pmethoddesc.OWNER =/= porigin_class',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$ptascii("__invoke"),phpType7_real*,z_init)',
        '$magic_method_copy_values(S_read,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1,[KNOWN (PINT 7)]) = eps',
        '$magic_method_copy_values(S_read,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1,[KNOWN (POBJECT pmagicmethodcall.OBJECT)]) = eps',
        '$factory182_output(S_read.EVENTS) = $ptascii("CTOR;INSTALL;")',
        'S_bad = S_read[.TODO = $cvinvoke213_bad(S_read.TODO)]',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_inner)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_inner) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$ptascii("__invoke"),phpType7_real*,z_init)',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        'pcalltarget = METHOD_TARGET n_receiver pfunction.ORIGIN',
        'S_selected.TODO = (FUNCTION_CACHE_INIT pcalltarget (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_inner) z_call)) :: ptask_selected_tail*',
        '$cvinvoke213_outer(ptask_selected_tail*) = (pmagicmethodcall_selected)',
        'pmagicproducerfact_selected = {SITE porigin_inner,CLASS porigin_class,METHOD pfunction.ORIGIN}',
        'pmagicmethodcall_selected = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact_selected]]',
        'S_selected.RESULT = KNOWN PNULL', 'S_selected.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(S_selected.TODO[0]) = [HOBJECT n_receiver]',
        '$task_nodes(MAGIC_METHOD_NAMED_SEND pmagicmethodcall_selected 1 ([KNOWN (PBOOL false)])) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_receiver) = 2',
        '$target_instance(pcalltarget) = eps',
        '$target_lexical_class(S_selected,pcalltarget) = (pmethoddesc.OWNER)',
        '$target_called_class(S_selected,pcalltarget) = (porigin_class)',
        '$call_selected_valid(S_selected,pcalltarget,(porigin_inner))',
        'S_ready = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_ready.COMPLETION = BUDGET',
        'S_ready.TODO = (CALL_ARGS pcalltarget phpType7_real* 0 eps (porigin_inner) z_call) :: ptask_selected_tail*',
        'S_direct = $drive_steps(S_read,2)', 'S_direct = S_ready',
        '$call_descriptors_valid(S_ready)', '$gc_state_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
        'S_producer_found = $cvinvoke213_producer_seek(S_ready[.COMPLETION = NORMAL],2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_receiver', 'n_receiver_current = n_receiver',
        'porigin_method_current = pfunction.ORIGIN',
        'pcallcontext_producer.INSTANCE = eps',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_receiver) = 2',
        'S_producer.FRAMES = pframe_producer :: pframe_producer_tail*',
        'S_outer = $constant_frame_scope(S_producer,pframe_producer,pframe_producer_tail*)',
        '$cvinvoke213_outer(pframe_producer.TODO) = (pmagicmethodcall_selected)',
        '$lookup(S_outer.ENV,$ptascii("receiver")) = eps',
        '$lookup(S_outer.ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        'S_producer.STORE[n_receiver_cell] = DEFINED PNULL',
        '$lookup(S_outer.ENV,$ptascii("late")) = (n_late_cell)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        '$objectprops_at(S_producer.OBJECTPROPS,n_receiver) = (ppropertyslot_receiver_items*)',
        '$property_slot_at(ppropertyslot_receiver_items*,$ptascii("text")) = (ppropertyslot_text)',
        'ppropertyslot_text.STATE = PROP_VALUE (DIRECT pvalue_string)',
        '$string_carrier_valid(S_producer,pvalue_string)',
        '$call_current_valid(S_producer)',
        'S_result_found = $cvinvoke213_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_receiver', 'pmagicmethodcall_result = pmagicmethodcall_selected',
        '~((HCELL n_saved_cell) <- S_result.ALLOCATIONS)',
        '$lookup(S_result.ENV,$ptascii("receiver")) = eps',
        '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)],[pmagicproducerfact_selected]) = ([PBOOL false,POBJECT n_receiver])',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)],eps) = eps',
        'S_sent = $drive_steps(S_result,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall_selected 2 ([KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)])) :: ptask_result_tail*',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_receiver) = 1',
        'S_child_found = $cvinvoke213_child_seek(S_sent[.COMPLETION = NORMAL],2048)', 'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        '$lookup(S_child.ENV,$ptascii("child")) = (n_child_cell)',
        'S_child.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_child.OBJECTPROPS,n_child) = (ppropertyslot_child_items*)',
        '$property_slot_at(ppropertyslot_child_items*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        'S_child.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT (POBJECT n_receiver))]',
        '$heap_owners($heap_graph(S_child),HOBJECT n_receiver) = 1',
        '$objectprops_at(S_child.OBJECTPROPS,n_receiver) = (ppropertyslot_receiver_items*)',
        '$factory182_output(S_child.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']).rsplit(b'CHILD;', 1)[0], filename),
        'S_done = $drive_steps(S_child,4096)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$magic_producer_facts_valid(S_done,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected])',
        '$call_descriptors_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
