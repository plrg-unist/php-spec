#!/usr/bin/env python3
"""A selected ref-CV receiver survives name removal through its real result owners."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_instance_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
EARLY = ('S.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall_early 0 eps) :: ptask_early_tail* '
         '-- if S.CURRENT = eps')
READ = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_read_method) metadata_read_method) phpType7_read* false false z_read) :: ptask_read_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("receiver")) z_receiver '
        '-- if S.CURRENT = eps')
SEND = ('S.TODO = (CALL_SEND pcalltarget_producer phpType7_send_tail* 0 eps (porigin_inner) z_inner) :: ptask_send_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("late")) z_variable '
        '-- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (RETURN_VALUE z_producer_return) :: ptask_producer_tail* '
            '-- if S.RESULT = KNOWN (POBJECT n_producer_return) '
            '-- if S.CURRENT = (pcallcontext_producer) '
            '-- if pcallcontext_producer.TARGET = METHOD_TARGET n_producer_current porigin_producer_current')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) '
          '-- if S.CURRENT = (pcallcontext_return) '
          '-- if pcallcontext_return.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_return n_arguments n_named pvalue*')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") '
         '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, EARLY)
for label, front in [('read', READ), ('send', SEND), ('producer', PRODUCER), ('return', RETURN), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cv208_' + label + '_')
PREFIX += r'''
dec $cv208_outer_one(ptask) : pmagicmethodcall?
def $cv208_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PBOOL false)])) = (pmagicmethodcall)
def $cv208_outer_one(ptask) = eps -- otherwise
dec $cv208_outer(ptask*) : pmagicmethodcall?
def $cv208_outer(eps) = eps
def $cv208_outer(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $cv208_outer_one(ptask) = (pmagicmethodcall)
def $cv208_outer(ptask :: ptask_tail*) = $cv208_outer(ptask_tail*)
  -- if $cv208_outer_one(ptask) = eps
dec $cv208_bad_sent(ptask*) : ptask*
def $cv208_bad_sent(eps) = eps
def $cv208_bad_sent((MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 poperand*) :: ptask_tail*) = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 eps) :: ptask_tail*
def $cv208_bad_sent(ptask :: ptask_tail*) = ptask :: $cv208_bad_sent(ptask_tail*) -- otherwise
'''


def render(case, fixture, filename):
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.FUNCTIONS = [pfunction_install,pfunction_shift]',
        'P.CLASSES = [pclassdesc_producer_base,pclassdesc_producer_called,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        '$method_named(pclassdesc_producer_base.METHODS,$ptascii("capture")) = (pmethoddesc_producer)',
        'pfunction_producer = pmethoddesc_producer.FUNCTION',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_early_found = $factory182_seek(S_initial,4096)',
        'S_early_found.COMPLETION = BUDGET',
        'S_early = S_early_found[.COMPLETION = NORMAL]', EARLY.replace('S.', 'S_early.'),
        'pmagicmethodcall_early.PRODUCERS = eps',
        '$lookup(S_early.ENV,$ptascii("receiver")) = (n_receiver_cell)',
        '$lookup(S_early.ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        'n_receiver_cell <- S_early.REFCELLS',
        'S_early.STORE[n_receiver_cell] = DEFINED PNULL',
        '$call_argument_origin(S_early,(pmagicmethodcall_early.SITE),1) = (porigin_producer_site)',
        '$origin_node(S_early.SOURCES,porigin_producer_site) = (expression_producer)',
        '$magic_producer_cv_source(S_early,porigin_producer_site,expression_producer)',
        '$magic_method_argument_source(S_early,porigin_producer_site,1,expression_producer)',
        '$magic_producer_cell(S_early,$ptascii("receiver")) = eps',
        '$magic_method_descriptor(S_early,pmagicmethodcall_early)',
        '$factory182_output(S_early.EVENTS) = eps',
        'S_read_found = $cv208_read_seek(S_early,4096)',
        'S_read_found.COMPLETION = BUDGET',
        'S_read = S_read_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.'),
        '$cv208_outer(ptask_read_tail*) = (pmagicmethodcall_read)',
        'pmagicmethodcall_read = pmagicmethodcall_early',
        'S_read.ORIGIN = (porigin_producer_site)',
        'expression_producer = NExprMethodCall (NExprVariable (BYTES text_receiver) metadata_receiver) (NIdentifier (BYTES text_read_method) metadata_read_method) (SEQUENCE phpType7_read*) metadata_producer',
        '$base64(text_receiver) = $ptascii("receiver")',
        'z_receiver = $variable_line(BYTES text_receiver,metadata_receiver)',
        'z_read = $runtime_line(S_read,eps,expression_producer)',
        '$base64(text_read_method) = $ptascii("capture")',
        '$lookup(S_read.ENV,$ptascii("receiver")) = (n_receiver_cell)',
        '$lookup(S_read.ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        'n_receiver_cell <- S_read.REFCELLS',
        'S_read.STORE[n_receiver_cell] = DEFINED (POBJECT n_producer)',
        '$magic_producer_cell(S_read,$ptascii("receiver")) = (n_producer)',
        'S_read.OBJECTS[n_producer] = INSTANCE pclassdesc_producer_called.ORIGIN',
        'pmethoddesc_producer.OWNER = pclassdesc_producer_base.ORIGIN',
        '$closure_source_class(S_read,porigin_producer_site) = eps',
        '$method_class_selected(S_read,pclassdesc_producer_called.ORIGIN,$ptascii("capture"),eps) = (pmethoddesc_producer)',
        '$method_selected_scope(S_read,n_producer,$ptascii("capture"),eps) = (pmethoddesc_producer)',
        '$magic_producer_selected_source(S_read,porigin_producer_site,pclassdesc_producer_called.ORIGIN) = (pmethoddesc_producer)',
        '$magic_producer_pending(S_read,S_read.TODO,porigin_producer_site) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall_read,1))',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$ptascii("capture"),phpType7_read*,z_read)',
        '~$magic_producer_read(S_read,porigin_producer_site,VARIABLE ($ptascii("receiver")) $(z_receiver + 1),$ptascii("capture"),phpType7_read*)',
        '~$magic_producer_read(S_read,porigin_producer_site,VARIABLE ($ptascii("other")) z_receiver,$ptascii("capture"),phpType7_read*)',
        '$magic_producer_cell(S_read[.STORE = $set_cell(S_read.STORE,n_receiver_cell,UNDEFINED)],$ptascii("receiver")) = eps',
        '$magic_producer_cell(S_read[.PROPREFS = [{CELL n_receiver_cell,SOURCES eps}]],$ptascii("receiver")) = eps',
        '$magic_producer_cell(S_read[.LITERALREFDEBTS = [n_receiver_cell]],$ptascii("receiver")) = eps',
        '$magic_producer_pending_task(S_read,MAGIC_METHOD_NAMED_SEND pmagicmethodcall_read 1 eps,porigin_producer_site) = eps',
        'S_bad_sent = S_read[.TODO = $cv208_bad_sent(S_read.TODO)]',
        '$magic_producer_candidate(S_bad_sent,S_bad_sent.TODO,porigin_producer_site)',
        '$magic_producer_pending(S_bad_sent,S_bad_sent.TODO,porigin_producer_site) = eps',
        '~$method_receiver_value_allowed(S_bad_sent,S_bad_sent.RESULT,$ptascii("capture"),phpType7_read*,z_read)',
        '$heap_owners($heap_graph(S_read),HOBJECT n_producer) = 1',
        '$factory182_output(S_read.EVENTS) = $ptascii("CTOR;INSTALL;")',
        '$call_descriptors_valid(S_read)', '$gc_state_valid(S_read)', '$heap_valid($heap_graph(S_read))',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        '$cv208_outer(S_selected.TODO) = (pmagicmethodcall_selected)',
        'pmagicproducerfact = {SITE porigin_producer_site,CLASS pclassdesc_producer_called.ORIGIN,METHOD pfunction_producer.ORIGIN}',
        'pmagicmethodcall_selected = pmagicmethodcall_read[.PRODUCERS = [pmagicproducerfact]]',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall_selected.SITE,pmagicmethodcall_selected.ARGUMENTS,[pmagicproducerfact])',
        '$task_nodes(MAGIC_METHOD_NAMED_SEND pmagicmethodcall_selected 1 ([KNOWN (PBOOL false)])) = $task_nodes(MAGIC_METHOD_NAMED_SEND pmagicmethodcall_read 1 ([KNOWN (PBOOL false)]))',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_producer) = 2',
        'S_selected.STORE[n_receiver_cell] = S_read.STORE[n_receiver_cell]',
        'S_selected.OBJECTS = S_read.OBJECTS',
        'S_selected.ALLOCATIONS = S_read.ALLOCATIONS',
        'S_selected.EVENTS = S_read.EVENTS',
        '$call_descriptors_valid(S_selected)', '$gc_state_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
        'S_found = $cv208_send_seek(S_selected[.COMPLETION = NORMAL],4096)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SEND,
        'porigin_inner = porigin_producer_site',
        'pcalltarget_producer = METHOD_TARGET n_producer pfunction_producer.ORIGIN',
        '$target_nodes(pcalltarget_producer) = [HOBJECT n_producer]',
        '$target_instance(pcalltarget_producer) = eps',
        '$target_receiver(S,pcalltarget_producer) = (n_producer)',
        '$target_function(S,pcalltarget_producer) = (pfunction_producer)',
        '$call_selected_valid(S,pcalltarget_producer,(porigin_inner))',
        '$call_task_valid(S,CALL_SEND pcalltarget_producer phpType7_send_tail* 0 eps (porigin_inner) z_inner)',
        '$cv208_outer(ptask_send_tail*) = (pmagicmethodcall_selected)',
        '$lookup(S.ENV,$ptascii("late")) = (n_late_cell)',
        '$lookup(S.ENV,$ptascii("alias")) = (n_late_cell)',
        'n_late_cell <- S.REFCELLS',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S.STORE[n_late_cell] = DEFINED pvalue_string',
        'S.STRINGDATA = [$ptascii("REQUEST-OLD")]',
        '$string_carrier_valid(S,pvalue_string)',
        '$value_nodes(pvalue_string) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_producer) = 2',
        '$lookup(S.ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED (POBJECT pmagicmethodcall_selected.OBJECT)',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall_selected.OBJECT) = 2',
        '~$call_parameter_reference(S,pcalltarget_producer,0)',
        'S_sent = $drive_steps(S,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS pcalltarget_producer phpType7_send_tail* 1 ([KNOWN pvalue_string]) (porigin_inner) z_inner) :: ptask_send_tail*',
        'S_sent.STORE[n_late_cell] = S.STORE[n_late_cell]',
        'S_sent.REFCELLS = S.REFCELLS',
        'S_sent.STRINGDATA = S.STRINGDATA',
        '$task_nodes(S_sent.TODO[0]) = [HOBJECT n_producer]',
        '~((HCELL n_late_cell) <- $task_nodes(S_sent.TODO[0]))',
        '$call_descriptors_valid(S_sent)', '$gc_state_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
        'S_producer_found = $cv208_producer_seek(S_sent[.COMPLETION = NORMAL],4096)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'pcallcontext_producer.TARGET = pcalltarget_producer',
        'n_producer_current = n_producer', 'n_producer_return = n_producer',
        'porigin_producer_current = pfunction_producer.ORIGIN',
        'pcallcontext_producer.LEXICAL_CLASS = (pclassdesc_producer_base.ORIGIN)',
        'pcallcontext_producer.CALLED_CLASS = (pclassdesc_producer_called.ORIGIN)',
        'pcallcontext_producer.CALLSITE = (porigin_inner)',
        'pcallcontext_producer.ARGC = 2',
        'pcallcontext_producer.PARAMS = [$ptascii("saved"),$ptascii("marker")]',
        r'pcallcontext_producer.RECEIVER = (n_producer) /\ pcallcontext_producer.INSTANCE = eps',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_producer]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_producer) = 2',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        '$lookup(S_producer.ENV,$ptascii("marker")) = (n_marker_cell)',
        r'n_saved_cell =/= n_late_cell /\ n_marker_cell =/= n_late_cell',
        r'~(n_saved_cell <- S_producer.REFCELLS) /\ ~(n_marker_cell <- S_producer.REFCELLS)',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        'S_producer.STORE[n_marker_cell] = DEFINED (PBOOL false)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_producer.STORE[n_owner_cell] = DEFINED PNULL',
        'S_producer.STORE[n_receiver_cell] = DEFINED PNULL',
        'S_producer.FRAMES = pframe_producer :: pframe_producer_tail*',
        'S_outer_view = $constant_frame_view(S_producer,pframe_producer,pframe_producer_tail*)',
        '$lookup(S_outer_view.ENV,$ptascii("receiver")) = eps',
        '$lookup(S_outer_view.ENV,$ptascii("receiverAlias")) = (n_receiver_cell)',
        '$cv208_outer(pframe_producer.TODO) = (pmagicmethodcall_selected)',
        '$magic_producer_cell(S_outer_view,$ptascii("receiver")) = eps',
        '$magic_producer_facts_valid(S_producer,pmagicmethodcall_selected.SITE,pmagicmethodcall_selected.ARGUMENTS,[pmagicproducerfact])',
        '$objectprops_at(S_producer.OBJECTPROPS,n_producer) = (ppropertyslot_producer_items*)',
        '$property_slot_at(ppropertyslot_producer_items*,$ptascii("text")) = (ppropertyslot_producer)',
        'ppropertyslot_producer.STATE = PROP_VALUE (DIRECT pvalue_string)',
        '$node_children(S_producer,HOBJECT n_producer) = eps',
        '$string_carrier_valid(S_producer,pvalue_string)',
        'S_producer.STRINGDATA[0] = $ptascii("REQUEST-OLD")',
        '$factory182_output(S_producer.EVENTS) = $ptascii("CTOR;INSTALL;SHIFT;PRODUCER:PeerProducerBase208:PeerProducerChild208;")',
        '$call_current_valid(S_producer)', '$call_descriptors_valid(S_producer)',
        '$gc_state_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_return_found = $cv208_return_seek(S_producer,4096)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'pmagicmethodcall_return = pmagicmethodcall_selected',
        'pcallcontext_return.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_return.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext_return.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pvalue* = [PBOOL false,POBJECT n_producer]',
        '~((HCELL n_saved_cell) <- S_return.ALLOCATIONS)',
        '~((HCELL n_marker_cell) <- S_return.ALLOCATIONS)',
        'S_return.STORE[n_late_cell] = DEFINED (PINT 0)',
        'S_return.STORE[n_receiver_cell] = DEFINED (PINT 0)',
        '$magic_producer_facts_valid(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,pmagicmethodcall_return.PRODUCERS)',
        '$magic_method_collected_values(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_producer)]) = eps',
        '$magic_method_fact_values(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_producer)],pmagicmethodcall_return.PRODUCERS) = (pvalue*)',
        '$magic_method_fact_values(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_producer)],eps) = eps',
        '~$magic_producer_facts_valid(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[pmagicproducerfact,pmagicproducerfact])',
        '~$magic_producer_facts_valid(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[pmagicproducerfact[.SITE = pmagicmethodcall_return.SITE]])',
        '~$magic_producer_facts_valid(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[pmagicproducerfact[.METHOD = pmethoddesc.FUNCTION.ORIGIN]])',
        '~$magic_producer_facts_limit(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[pmagicproducerfact],1)',
        '$magic_producer_facts_limit(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[pmagicproducerfact],2)',
        '$magic_method_fact_values(S_return[.CODE = eps],pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (PINT 7)],pmagicmethodcall_return.PRODUCERS) = eps',
        '$magic_method_array_producer(S_return,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS) = eps',
        '~$magic_unpack_explicit_source(S_return,porigin_producer_site,expression_producer)',
        '$string_carrier_valid(S_return,pvalue_string)',
        'S_return.STRINGDATA[0] = $ptascii("REQUEST-OLD")',
        'n_arguments = n_named',
        'S_return.FRAMES = pframe_return :: pframe_return_tail*',
        '$magic_named_frame(S_return,pcallcontext_return,pframe_return,pframe_return_tail*,pmagicmethodcall_return,n_arguments,n_named,pvalue*)',
        '$lookup(pframe_return.ENV,$ptascii("receiver")) = eps',
        '$magic_named_buffer(S_return,pmagicmethodcall_return,n_arguments,n_named,pvalue*)',
        'S_return.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PBOOL false)),ENTRY (KSTRING $ptascii("later")) (DIRECT (POBJECT n_producer))]',
        '$node_children(S_return,HARRAY n_arguments) = [HOBJECT n_producer]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_producer) = 1',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 3',
        '$object_body(S_return.OBJECTS[n_closure]) = REALCLOSURE pfunction_closure.ORIGIN ([DIRECT (PARRAY n_arguments),DIRECT (PSTRING $ptascii("MiSsInG"))]) eps',
        '$node_children(S_return,HOBJECT n_closure) = [HARRAY n_arguments]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_closure) = 1',
        '$closure_scope_at(S_return.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_base.ORIGIN',
        'pclosurescope.CALLED = pclassdesc_called.ORIGIN',
        'pclosurescope.RECEIVER = eps',
        '$task_nodes(MAGIC_METHOD_NAMED_RESULT pmagicmethodcall_return n_arguments n_named pvalue*) = [HARRAY n_named,HOBJECT pmagicmethodcall_return.OBJECT]',
        '$target_nodes(pcallcontext_return.TARGET) = eps',
        '$factory182_output(S_return.EVENTS) = $ptascii("CTOR;INSTALL;SHIFT;PRODUCER:PeerProducerBase208:PeerProducerChild208;MAGIC;")',
        '$call_descriptors_valid(S_return)', '$closure_state_valid(S_return)',
        '$class_state_valid(S_return)', '$gc_state_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_child_found = $cv208_child_seek(S_return,4096)',
        'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        '$lookup(S_child.ENV,$ptascii("receiver")) = eps',
        '$lookup(S_child.ENV,$ptascii("receiverAlias")) = eps',
        '~((HCELL n_receiver_cell) <- S_child.ALLOCATIONS)',
        '$lookup(S_child.ENV,$ptascii("late")) = eps',
        '$lookup(S_child.ENV,$ptascii("alias")) = eps',
        '~((HCELL n_late_cell) <- S_child.ALLOCATIONS)',
        '$lookup(S_child.ENV,$ptascii("factory")) = eps',
        '$lookup(S_child.ENV,$ptascii("child")) = (n_child_cell)',
        'S_child.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_child.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$objectprops_at(S_child.OBJECTPROPS,n_child) = (ppropertyslot_child_items*)',
        '$property_slot_at(ppropertyslot_child_items*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_child,HOBJECT n_child) = [HARRAY n_arguments]',
        '$node_children(S_child,HARRAY n_arguments) = [HOBJECT n_producer]',
        '$node_children(S_child,HOBJECT n_producer) = eps',
        '$heap_owners($heap_graph(S_child),HOBJECT n_producer) = 1',
        '$objectprops_at(S_child.OBJECTPROPS,n_producer) = (ppropertyslot_producer_items*)',
        '$heap_owners($heap_graph(S_child),HOBJECT n_child) = 1',
        '$heap_owners($heap_graph(S_child),HARRAY n_arguments) = 1',
        'S_child.ARRAYS[n_arguments] = S_return.ARRAYS[n_arguments]',
        '$string_carrier_valid(S_child,pvalue_string)',
        '~((HOBJECT n_closure) <- S_child.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall_return.OBJECT) <- S_child.ALLOCATIONS)',
        '$magic_producer_facts_valid(S_child,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,pmagicmethodcall_return.PRODUCERS)',
        '$factory182_output(S_child.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']).rsplit(b'CHILD;', 1)[0], filename),
        '$call_descriptors_valid(S_child)', '$closure_state_valid(S_child)',
        '$class_state_valid(S_child)', '$gc_state_valid(S_child)', '$heap_valid($heap_graph(S_child))',
        'S_split = $drive_steps(S_child,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROW['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_child,4098)', 'S_full = S_done',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall_return.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_producer) <- S_done.ALLOCATIONS)',
        '$magic_producer_selected_source(S_done,porigin_producer_site,pclassdesc_producer_called.ORIGIN) = (pmethoddesc_producer)',
        '$magic_producer_facts_valid(S_done,pmagicmethodcall_return.SITE,pmagicmethodcall_return.ARGUMENTS,pmagicmethodcall_return.PRODUCERS)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
