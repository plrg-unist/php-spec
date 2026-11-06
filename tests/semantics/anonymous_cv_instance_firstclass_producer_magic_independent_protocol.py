#!/usr/bin/env python3
"""An actual CV capture mints an outer-argument fact before its wrapper is born."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_instance_firstclass_producer_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
READ = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method) metadata_method) phpType7_capture* false b_base z_capture) :: ptask_read_tail* '
        '-- if $base64(text_method) = $ptascii("capture") -- if $ppfirstclass(phpType7_capture*) '
        '-- if S.RESULT = VARIABLE ($ptascii("receiver")) z_cv -- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_returned) -- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper_producer')
RESULT = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall_result 1 ([KNOWN (PBOOL false)])) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_result) -- if S.CURRENT = eps')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) -- if S.CURRENT = (pcallcontext_return) '
          '-- if pcallcontext_return.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_return n_arguments n_named pvalue*')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('producer', PRODUCER), ('result', RESULT), ('return', RETURN), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvfcc211_' + label + '_')
PREFIX += r'''
dec $cvfcc211_outer_one(ptask) : pmagicmethodcall?
def $cvfcc211_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $cvfcc211_outer_one(ptask) = eps -- otherwise
dec $cvfcc211_outer(ptask*) : pmagicmethodcall?
def $cvfcc211_outer(eps) = eps
def $cvfcc211_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvfcc211_outer_one(ptask) = (pmagicmethodcall)
def $cvfcc211_outer(ptask :: ptask_tail*) = $cvfcc211_outer(ptask_tail*) -- if $cvfcc211_outer_one(ptask) = eps
dec $cvfcc211_bad_one(ptask) : ptask
def $cvfcc211_bad_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 eps
def $cvfcc211_bad_one(ptask) = ptask -- otherwise
dec $cvfcc211_bad(ptask*) : ptask*
def $cvfcc211_bad(eps) = eps
def $cvfcc211_bad(ptask :: ptask_tail*) = $cvfcc211_bad_one(ptask) :: $cvfcc211_bad(ptask_tail*)
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S_read = S_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.'),
        'S_read.ORIGIN = (porigin_capture)',
        '$cvfcc211_outer(S_read.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S_read,(pmagicmethodcall.SITE),1) = (porigin_producer)',
        '$origin_child((porigin_producer),[PCFIELD 0]) = (porigin_capture)',
        '$origin_node(S_read.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_invoke',
        'expression_capture = NExprMethodCall expression_cv (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE phpType7_capture*) metadata_capture',
        'expression_cv = NExprVariable (BYTES text_cv) metadata_cv',
        'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]',
        '|phpType7_real*| = 2',
        '$origin_node(S_read.SOURCES,porigin_capture) = (expression_capture)',
        'z_cv = $variable_line(BYTES text_cv,metadata_cv)',
        'z_capture = $runtime_line(S_read,eps,expression_capture)',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        '$code_at(S_read.CODE,n_unit) = (pcode)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_init_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_init_capture)',
        '$dynamic_init_line(S_read,porigin_capture) = z_init_capture',
        '$magic_producer_cv_parts(S_read,porigin_producer,expression_producer) = ((porigin_capture,VARIABLE ($ptascii("receiver")) z_cv,$ptascii("capture"),phpType7_capture*,phpType7_real*))',
        '$magic_producer_argument_site(S_read,porigin_capture) = (porigin_producer)',
        '$magic_producer_index(S_read,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,porigin_producer,0) = (1)',
        '$magic_producer_index(S_read,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,porigin_capture,0) = eps',
        '$magic_producer_pending(S_read,S_read.TODO,porigin_producer) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1))',
        '$lookup(S_read.ENV,$ptascii("receiver")) = (n_receiver_cell)',
        '$lookup(S_read.ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        'n_receiver_cell <- S_read.REFCELLS',
        'S_read.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$magic_producer_cell(S_read,$ptascii("receiver")) = (n_receiver)',
        '$object_class_origin(S_read,n_receiver) = (porigin_class)',
        '$magic_producer_selected_source(S_read,porigin_producer,porigin_class) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION',
        'pmethoddesc.OWNER =/= porigin_class',
        '$closure_source_class(S_read,porigin_capture) = eps',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$ptascii("capture"),phpType7_capture*,z_capture)',
        '$heap_owners($heap_graph(S_read),HOBJECT n_receiver) = 1',
        '$factory182_output(S_read.EVENTS) = $ptascii("CTOR;INSTALL;")',
        'S_bad = S_read[.TODO = $cvfcc211_bad(S_read.TODO)]',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_producer)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_producer) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$ptascii("capture"),phpType7_capture*,z_capture)',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (METHOD_CONVERT (METHOD_TARGET n_receiver pfunction.ORIGIN) porigin_capture z_capture) :: ptask_selected_tail*',
        '$cvfcc211_outer(ptask_selected_tail*) = (pmagicmethodcall_selected)',
        'pmagicproducerfact_selected = {SITE porigin_producer,CLASS porigin_class,METHOD pfunction.ORIGIN}',
        'pmagicmethodcall_selected = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact_selected]]',
        '$magic_producer_fact_at(pmagicmethodcall_selected.PRODUCERS,porigin_capture) = eps',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected])',
        '~$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[{SITE porigin_capture,CLASS porigin_class,METHOD pfunction.ORIGIN}])',
        '~$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected],1)',
        '$magic_producer_facts_limit(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected],2)',
        '$target_lexical_class(S_selected,METHOD_TARGET n_receiver pfunction.ORIGIN) = (pmethoddesc.OWNER)',
        '$target_called_class(S_selected,METHOD_TARGET n_receiver pfunction.ORIGIN) = (porigin_class)',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_receiver) = 2',
        'n_wrapper = |S_selected.OBJECTS|',
        'S_wrapped = $drive_steps(S_selected[.COMPLETION = NORMAL],1)',
        'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S_read,2)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_selected.OBJECTS ++ [METHODCLOSURE pfunction.ORIGIN porigin_capture porigin_class eps]',
        'S_wrapped.RESULT = KNOWN (POBJECT n_wrapper)',
        'S_wrapped.TODO = ptask_selected_tail*',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope_wrapper)',
        'pclosurescope_wrapper.LEXICAL = pmethoddesc.OWNER',
        'pclosurescope_wrapper.CALLED = porigin_class',
        'pclosurescope_wrapper.RECEIVER = (n_receiver)',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_receiver) = 2',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_wrapper) = 1',
        '$call_descriptors_valid(S_wrapped)', '$closure_state_valid(S_wrapped)',
        '$gc_state_valid(S_wrapped)', '$heap_valid($heap_graph(S_wrapped))',
        'S_producer_found = $cvfcc211_producer_seek(S_wrapped[.COMPLETION = NORMAL],2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'n_returned = n_receiver', 'n_wrapper_producer = n_wrapper',
        'pcallcontext_producer.INSTANCE = (n_wrapper)',
        'pcallcontext_producer.RECEIVER = (n_receiver)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_receiver) = 2',
        'S_producer.FRAMES = pframe_producer :: pframe_producer_tail*',
        'S_outer = $constant_frame_scope(S_producer,pframe_producer,pframe_producer_tail*)',
        '$cvfcc211_outer(pframe_producer.TODO) = (pmagicmethodcall_selected)',
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
        '$factory182_output(S_producer.EVENTS) = $ptascii("CTOR;INSTALL;SHIFT;PRODUCER:PeerProducerBase211:PeerProducerChild211;")',
        '$call_current_valid(S_producer)', '$gc_state_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_result_found = $cvfcc211_result_seek(S_producer,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_receiver', 'pmagicmethodcall_result = pmagicmethodcall_selected',
        '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '~((HCELL n_saved_cell) <- S_result.ALLOCATIONS)',
        '$lookup(S_result.ENV,$ptascii("receiver")) = eps',
        'S_result.STORE[n_receiver_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
        '$task_nodes(S_result.TODO[0]) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)],[pmagicproducerfact_selected]) = ([PBOOL false,POBJECT n_receiver])',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)],eps) = eps',
        'S_sent = $drive_steps(S_result,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall_selected 2 ([KNOWN (PBOOL false),KNOWN (POBJECT n_receiver)])) :: ptask_result_tail*',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_receiver) = 1',
        'S_return_found = $cvfcc211_return_seek(S_sent[.COMPLETION = NORMAL],2048)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'pmagicmethodcall_return = pmagicmethodcall_selected',
        'pvalue* = [PBOOL false,POBJECT n_receiver]', 'n_arguments = n_named',
        'S_return.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT (POBJECT n_receiver))]',
        '$node_children(S_return,HARRAY n_arguments) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_receiver) = 1',
        '$node_children(S_return,HOBJECT n_closure) = [HARRAY n_arguments]',
        'S_child_found = $cvfcc211_child_seek(S_return,2048)', 'S_child_found.COMPLETION = BUDGET',
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
        '~((HOBJECT n_closure) <- S_child.ALLOCATIONS)',
        '$factory182_output(S_child.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']).rsplit(b'CHILD;', 1)[0], filename),
        'S_done = $drive_steps(S_child,4096)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$magic_producer_facts_valid(S_done,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_selected])',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
