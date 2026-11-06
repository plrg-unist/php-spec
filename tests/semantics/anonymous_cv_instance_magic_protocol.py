#!/usr/bin/env python3
"""Actual plain receiver acquisition, descriptor facts and retained old payload."""
import argparse
import base64
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol
ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_instance_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_cv_instance_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-cv-instance-pending-leaf'
MISSING = 'magic-cv-instance-missing-receiver-warning-refused'
FUTURE = 'magic-cv-instance-family-instance'
LOOP = 'magic-cv-instance-repeated-site'
TYPED = 'magic-cv-instance-typed-parameter-ref-refused'
READ = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method_read) metadata_method_read) phpType7_inner* false false z_read) :: ptask_read_tail* '
        '-- if S.ORIGIN = (porigin_producer_site) -- if S.CURRENT = eps '
        '-- if $origin_node(S.SOURCES,porigin_producer_site) = (expression_producer) '
        '-- if expression_producer = NExprMethodCall (NExprVariable (BYTES text_receiver_read) metadata_receiver_read) (NIdentifier (BYTES text_method_read) metadata_method_read) (SEQUENCE phpType7_inner*) metadata_producer_read '
        '-- if $magic_producer_candidate(S,S.TODO,porigin_producer_site)')
TYPEDREAD = READ.replace('S.CURRENT = eps','S.CURRENT = (pcallcontext_typed)')
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_string_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_producer) metadata_string_producer) :: expression_echo_tail*)) metadata_echo_producer)) :: ptask_producer_tail* '
            '-- if $base64(text_producer) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_producer)')
NEW = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14_new phpType24_new ABSENT phpType44_new phpType42_new phpType23_new metadata_class_new) phpType6_new metadata_new)) :: ptask_new_tail* '
       '-- if S.CURRENT = (pcallcontext_new) -- if pcallcontext_new.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_new n_arguments pvalue_sent*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
LOOPA = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_loop_a) metadata_string_loop_a])) metadata_echo_loop_a)) :: ptask_loop_a_tail* '
         '-- if $base64(text_loop_a) = $ptascii("A;") -- if S.CURRENT = (pcallcontext_loop_a)')
LOOPB = LOOPA.replace('loop_a','loop_b').replace('"A;"','"B;"')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('typed', TYPEDREAD), ('shift', SHIFT), ('producer', PRODUCER), ('new', NEW), ('return', RETURN), ('loopa', LOOPA), ('loopb', LOOPB)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cv208_' + label + '_')
PREFIX += r'''
dec $cv208_outer_any_one(ptask) : pmagicmethodcall?
def $cv208_outer_any_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 poperand* (porigin) z) = (pmagicmethodcall)
def $cv208_outer_any_one(ptask) = eps -- otherwise
dec $cv208_outer_any(ptask*) : pmagicmethodcall?
def $cv208_outer_any(eps) = eps
def $cv208_outer_any(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cv208_outer_any_one(ptask) = (pmagicmethodcall)
def $cv208_outer_any(ptask :: ptask_tail*) = $cv208_outer_any(ptask_tail*) -- if $cv208_outer_any_one(ptask) = eps
dec $cv208_outer_one(ptask) : pmagicmethodcall?
def $cv208_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PINT 7)]) (porigin) z) = (pmagicmethodcall)
def $cv208_outer_one(ptask) = eps -- otherwise
dec $cv208_outer(ptask*) : pmagicmethodcall?
def $cv208_outer(eps) = eps
def $cv208_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cv208_outer_one(ptask) = (pmagicmethodcall)
def $cv208_outer(ptask :: ptask_tail*) = $cv208_outer(ptask_tail*) -- if $cv208_outer_one(ptask) = eps
dec $cv208_inner_one(ptask) : (nat, porigin, nat)?
def $cv208_inner_one(CALL_SEND (METHOD_TARGET n_receiver porigin_method) eps 1 ([KNOWN (POBJECT n_old)]) porigin? z) = ((n_receiver,porigin_method,n_old))
def $cv208_inner_one(ptask) = eps -- otherwise
dec $cv208_inner(ptask*) : (nat, porigin, nat)?
def $cv208_inner(eps) = eps
def $cv208_inner(ptask :: ptask_tail*) = ((n_receiver,porigin_method,n_old)) -- if $cv208_inner_one(ptask) = ((n_receiver,porigin_method,n_old))
def $cv208_inner(ptask :: ptask_tail*) = $cv208_inner(ptask_tail*) -- if $cv208_inner_one(ptask) = eps
'''

def owner(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_read_found = $factory182_seek(S_initial,2048)', 'S_read_found.COMPLETION = BUDGET',
        'S_read = S_read_found[.COMPLETION = NORMAL]', READ.replace('S.', 'S_read.').replace('candidate(S,', 'candidate(S_read,'),
        '$base64(text_receiver_read) = $ptascii("producer")',
        'S_read.RESULT = VARIABLE ($base64(text_receiver_read)) $variable_line(BYTES text_receiver_read,metadata_receiver_read)',
        'z_read = $runtime_line(S_read,eps,expression_producer)',
        '$cv208_outer(S_read.TODO) = (pmagicmethodcall_initial)',
        'pmagicmethodcall_initial.PRODUCERS = eps',
        'pmagicmethodcall_initial.ARGUMENTS = [phpType7_install,phpType7_producer]',
        '$call_argument_origin(S_read,(pmagicmethodcall_initial.SITE),1) = (porigin_producer_site)',
        '$magic_producer_pending(S_read,S_read.TODO,porigin_producer_site) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall_initial,1))',
        '$magic_producer_candidate(S_read,S_read.TODO,porigin_producer_site)',
        '$lookup(S_read.ENV,$ptascii("producer")) = (n_receiver_cell)',
        '~(n_receiver_cell <- S_read.REFCELLS)',
        'S_read.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$magic_producer_cell(S_read,$ptascii("producer")) = (n_receiver)',
        '$object_class_origin(S_read,n_receiver) = (porigin_class)',
        '$magic_producer_selected_source(S_read,porigin_producer_site,porigin_class) = (pmethoddesc)',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$base64(text_method_read),phpType7_inner*,z_read)',
        '$heap_owners($heap_graph(S_read),HOBJECT n_receiver) = 1',
        'S_bad = S_read[.TODO = (METHOD_PREP (NIdentifier (BYTES text_method_read) metadata_method_read) phpType7_inner* false false z_read) :: METHOD_RESULT :: (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_initial) eps 1 eps (pmagicmethodcall_initial.SITE) pmagicmethodcall_initial.LINE) :: METHOD_RESULT :: pmagicmethodcall_initial.TAIL]',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_producer_site)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_producer_site) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$base64(text_method_read),phpType7_inner*,z_read)',
        'S_bad_selected = $method_selected_metadata(S_bad,METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN,(porigin_producer_site))',
        'S_bad_selected.COMPLETION = UNSUPPORTED "magic method producer selection fact"',
        'S_bad_selected.TODO = S_bad.TODO',
        '$factory182_output(S_read.EVENTS) = $ptascii("INSTALL;")',
        '$call_descriptors_valid(S_read)', '$gc_state_valid(S_read)', '$heap_valid($heap_graph(S_read))',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        '$cv208_outer(S_selected.TODO) = (pmagicmethodcall)',
        'pmagicproducerfact = {SITE porigin_producer_site,CLASS porigin_class,METHOD pmethoddesc.FUNCTION.ORIGIN}',
        'pmagicmethodcall = pmagicmethodcall_initial[.PRODUCERS = [pmagicproducerfact]]',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,pmagicmethodcall.PRODUCERS)',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_receiver) = 2',
        'S_shift_found = $cv208_shift_seek(S_selected,2048)', 'S_shift_found.COMPLETION = BUDGET',
        'S = S_shift_found[.COMPLETION = NORMAL]', SHIFT,
        'S.FRAMES = [pframe]', '$cv208_outer(pframe.TODO) = (pmagicmethodcall)',
        '$cv208_inner(pframe.TODO) = ((n_receiver,porigin_method,n_old))',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
        '$target_nodes(METHOD_TARGET n_receiver porigin_method) = [HOBJECT n_receiver]',
        '$target_instance(METHOD_TARGET n_receiver porigin_method) = eps',
        '$target_receiver(S,METHOD_TARGET n_receiver porigin_method) = (n_receiver)',
        '$target_lexical_class(S,METHOD_TARGET n_receiver porigin_method) = (pmethoddesc.OWNER)',
        '$target_called_class(S,METHOD_TARGET n_receiver porigin_method) = (porigin_class)',
        'pmethoddesc.OWNER =/= porigin_class',
        '$lookup($global_table_view(S).ENV,$ptascii("payload")) = (n_payload_cell)',
        'S.STORE[n_payload_cell] = DEFINED (POBJECT n_new)',
        'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_replacement)', 'n_replacement =/= n_receiver',
        '~(n_receiver_cell <- S.REFCELLS)',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_new) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_replacement) = 1',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$task_nodes(CALL_SEND (METHOD_TARGET n_receiver porigin_method) eps 1 ([KNOWN (POBJECT n_old)]) (porigin_producer_site) z_read) = [HOBJECT n_receiver,HOBJECT n_old]',
        '$factory182_output(S.EVENTS) = $ptascii("INSTALL;")',
        '$object_class_origin(S,n_replacement) = (porigin_replacement)',
        '$magic_producer_selected_source(S,porigin_producer_site,porigin_replacement) = eps',
        '$magic_method_fact_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],pmagicmethodcall.PRODUCERS) = ([PINT 7,POBJECT n_old])',
        '$magic_method_fact_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],eps) = eps',
        '$magic_method_fact_values(S[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (PINT 7)],pmagicmethodcall.PRODUCERS) = eps',
        '$magic_method_fact_values(S[.CLASSES = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],pmagicmethodcall.PRODUCERS) = eps',
        '$magic_method_user_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0) = (pfunction_install)',
        '$magic_method_array_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS) = (pfunction_install)',
        '$magic_method_user_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1) = eps',
        '~$magic_unpack_explicit_source(S,porigin_producer_site,expression_producer)',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_producer_found = $cv208_producer_seek(S,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'pcallcontext_producer.TARGET = METHOD_TARGET n_receiver porigin_method',
        'pcallcontext_producer.RECEIVER = (n_receiver)', 'pcallcontext_producer.INSTANCE = eps',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
        '$lookup(S_producer.ENV,$ptascii("ignored")) = (n_ignored)',
        'S_producer.STORE[n_saved] = DEFINED (POBJECT n_old)',
        'S_producer.STORE[n_ignored] = DEFINED PNULL',
        '~(n_saved <- S_producer.REFCELLS)', '~(n_ignored <- S_producer.REFCELLS)',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_old) = 1',
        'S_new_found = $cv208_new_seek(S_producer,2048)', 'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]', NEW.replace('S.', 'S_new.'),
        'pmagicmethodcall_new = pmagicmethodcall', 'pvalue_sent* = [PINT 7,POBJECT n_old]',
        '~((HOBJECT n_receiver) <- S_new.ALLOCATIONS)',
        '~((HOBJECT n_replacement) <- S_new.ALLOCATIONS)', '~((HOBJECT n_new) <- S_new.ALLOCATIONS)',
        '~((HCELL n_saved) <- S_new.ALLOCATIONS)', '~((HCELL n_ignored) <- S_new.ALLOCATIONS)',
        'S_new.STORE[n_receiver_cell] = DEFINED PNULL',
        '$magic_method_fact_values(S_new,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],pmagicmethodcall.PRODUCERS) = ([PINT 7,POBJECT n_old])',
        '$lookup(S_new.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_new.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S_new.ARRAYS[n_arguments] = $magic_method_array(pvalue_sent*,0)',
        '$node_children(S_new,HARRAY n_arguments) = [HOBJECT n_old]',
        '$heap_owners($heap_graph(S_new),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_new),HARRAY n_arguments) = 1',
        '$factory182_output(S_new.EVENTS) = $ptascii("INSTALL;SHIFT;PRODUCER;ProducerBase208/ProducerChild208;PROVIDER;REPLACEMENT;NEW;HANDLER;")',
        '$call_descriptors_valid(S_new)', '$gc_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_return_found = $cv208_return_seek(S_new,2048)', 'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)',
        'S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot_items*)',
        '$property_slot_at(ppropertyslot_items*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_old) = 1',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_return.ALLOCATIONS)',
        'S_split = $drive_steps(S_return,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROWS[CASE]['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_return,4098)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def missing(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READ,
        '$base64(text_receiver_read) = $ptascii("producer")',
        '$magic_producer_candidate(S,S.TODO,porigin_producer_site)',
        '$magic_producer_pending(S,S.TODO,porigin_producer_site) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1))',
        'pmagicmethodcall.PRODUCERS = eps',
        '$error_handler_eligible(S,2)', '~$error_read_pending(S)',
        '$magic_producer_cell(S,$ptascii("producer")) = eps',
        '~$method_receiver_value_allowed(S,S.RESULT,$base64(text_method_read),phpType7_inner*,z_read)',
        '$factory182_output(S.EVENTS) = $ptascii("FIRST;")',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_step = $method_prepare(S,(NIdentifier (BYTES text_method_read) metadata_method_read),phpType7_inner*,false,false,z_read)',
        'S_step = S[.COMPLETION = UNSUPPORTED "magic method producer receiver read"]',
        'S_done = $drive_steps(S,1)',
        'S_done.COMPLETION = UNSUPPORTED "magic method producer receiver read"',
        '$factory182_output(S_done.EVENTS) = $ptascii("FIRST;")',
        'S_done.TODO = eps',
    ]


def typed(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $cv208_typed_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', TYPEDREAD,
        '$base64(text_receiver_read) = $ptascii("producer")',
        '$magic_producer_pending(S,S.TODO,porigin_producer_site) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1))',
        'pmagicmethodcall.PRODUCERS = eps',
        '$function_at($all_functions(S),pcallcontext_typed.FUNCTION) = (pfunction_typed)',
        'pfunction_typed.SIGNATURE.PARAMETERS = [psparam_receiver,psparam_owner]',
        'psparam_receiver.NAME = $ptascii("producer")', 'psparam_receiver.TYPE =/= eps', 'psparam_receiver.BYREF',
        '$lookup(S.ENV,psparam_receiver.NAME) = (n_receiver_cell)',
        'n_receiver_cell <- S.REFCELLS',
        'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$typed_object_exact(S,psparam_receiver.TYPE,POBJECT n_receiver)',
        '$magic_method_value(S,POBJECT n_receiver)',
        '$propref_at(S.PROPREFS,n_receiver_cell) = eps',
        '$reference_coercion_at(S.REFCOERCIONS,n_receiver_cell) = eps',
        '$parameter_backing_at(S.PARAMETERBACKINGS,n_receiver_cell) = eps',
        '$magic_producer_typed_formal(S,pfunction_typed.SIGNATURE.PARAMETERS,n_receiver_cell)',
        '~$magic_producer_untyped_cell(S,n_receiver_cell)',
        '$magic_producer_cell(S,$ptascii("producer")) = eps',
        'S_alias = S[.ENV = (BIND ($ptascii("alias")) n_receiver_cell) :: S.ENV]',
        '$magic_producer_cell(S_alias,$ptascii("alias")) = eps',
        '~$method_receiver_value_allowed(S,S.RESULT,$base64(text_method_read),phpType7_inner*,z_read)',
        '$factory182_output(S.EVENTS) = $ptascii("FIRST;")',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_step = $method_prepare(S,(NIdentifier (BYTES text_method_read) metadata_method_read),phpType7_inner*,false,false,z_read)',
        'S_step = S[.COMPLETION = UNSUPPORTED "magic method producer receiver read"]',
        'S.FRAMES = [pframe_typed]',
        'S_unwind = $drive_steps(S,1)',
        'S_unwind.COMPLETION = BUDGET',
        'S_unwind.TODO = [ERROR_UNWIND (UNSUPPORTED "magic method producer receiver read")]',
        'S_unwind.FRAMES = S.FRAMES',
        'S_done = $drive_steps(S_unwind[.COMPLETION = NORMAL],32)',
        'S_done.COMPLETION = UNSUPPORTED "magic method producer receiver read"',
        '$factory182_output(S_done.EVENTS) = $ptascii("FIRST;")', 'S_done.TODO = eps',
    ]


def future(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READ,
        '$magic_producer_pending(S,S.TODO,porigin_producer_site) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall,0))',
        'pmagicmethodcall.PRODUCERS = eps',
        'pmagicmethodcall.ARGUMENTS = [phpType7_first,phpType7_future]',
        '$magic_producer_cell(S,$base64(text_receiver_read)) = (n_receiver)',
        '$object_class_origin(S,n_receiver) = (porigin_class)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_future)',
        '$magic_producer_selected_source(S,porigin_future,porigin_class) = (pmethoddesc_future)',
        'pmagicproducerfact_future = {SITE porigin_future,CLASS porigin_class,METHOD pmethoddesc_future.FUNCTION.ORIGIN}',
        '$magic_producer_facts_valid(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_future])',
        '~$magic_producer_facts_limit(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact_future],1)',
        'pmagicmethodcall_future = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact_future]]',
        'S_bad = S[.TODO = (METHOD_PREP (NIdentifier (BYTES text_method_read) metadata_method_read) phpType7_inner* false false z_read) :: METHOD_RESULT :: (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_future) [phpType7_future] 0 eps (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: METHOD_RESULT :: pmagicmethodcall.TAIL]',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_producer_site)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_producer_site) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$base64(text_method_read),phpType7_inner*,z_read)',
        '$method_receiver_value_allowed(S,S.RESULT,$base64(text_method_read),phpType7_inner*,z_read)',
        '$factory182_output(S.EVENTS) = eps',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
    ]


def repeated(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_a_found = $cv208_loopa_seek(S_initial,2048)', 'S_a_found.COMPLETION = BUDGET',
        'S_a = S_a_found[.COMPLETION = NORMAL]', LOOPA.replace('S.','S_a.'),
        'S_a.FRAMES = [pframe_a]', '$cv208_outer_any(pframe_a.TODO) = (pmagicmethodcall_a)',
        'pcallcontext_loop_a.TARGET = METHOD_TARGET n_a porigin_method_a',
        'pcallcontext_loop_a.CALLSITE = (porigin_site)',
        '$object_class_origin(S_a,n_a) = (porigin_class_a)',
        'pmagicmethodcall_a.PRODUCERS = [pmagicproducerfact_a]',
        'pmagicproducerfact_a = {SITE porigin_site,CLASS porigin_class_a,METHOD porigin_method_a}',
        '$magic_producer_facts_valid(S_a,pmagicmethodcall_a.SITE,pmagicmethodcall_a.ARGUMENTS,pmagicmethodcall_a.PRODUCERS)',
        'S_b_found = $cv208_loopb_seek(S_a,4096)', 'S_b_found.COMPLETION = BUDGET',
        'S_b = S_b_found[.COMPLETION = NORMAL]', LOOPB.replace('S.','S_b.'),
        'S_b.FRAMES = [pframe_b]', '$cv208_outer_any(pframe_b.TODO) = (pmagicmethodcall_b)',
        'pcallcontext_loop_b.TARGET = METHOD_TARGET n_b porigin_method_b',
        'pcallcontext_loop_b.CALLSITE = (porigin_site)',
        '$object_class_origin(S_b,n_b) = (porigin_class_b)',
        'pmagicmethodcall_b.SITE = pmagicmethodcall_a.SITE',
        'pmagicmethodcall_b.ARGUMENTS = pmagicmethodcall_a.ARGUMENTS',
        'pmagicmethodcall_a.OWNER = 0', 'pmagicmethodcall_b.OWNER = 0',
        'pmagicmethodcall_b.OBJECT =/= pmagicmethodcall_a.OBJECT',
        'pmagicmethodcall_b.PRODUCERS = [pmagicproducerfact_b]',
        'pmagicproducerfact_b = {SITE porigin_site,CLASS porigin_class_b,METHOD porigin_method_b}',
        'porigin_class_a =/= porigin_class_b', 'porigin_method_a =/= porigin_method_b',
        'n_a =/= n_b', '~((HOBJECT n_a) <- S_b.ALLOCATIONS)',
        '$magic_producer_facts_valid(S_b,pmagicmethodcall_b.SITE,pmagicmethodcall_b.ARGUMENTS,pmagicmethodcall_b.PRODUCERS)',
        '$call_descriptors_valid(S_b)', '$gc_state_valid(S_b)', '$heap_valid($heap_graph(S_b))',
        'S_done = $drive_steps(S_b,4096)', r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROWS[LOOP]['stdout_template_base64']), filename),
        '~((HOBJECT n_b) <- S_done.ALLOCATIONS)', '$call_descriptors_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def render(case, fixture, filename):
    clauses = (missing(fixture,filename) if case['source']==ROWS[MISSING]['source'] else typed(fixture,filename) if case['source']==ROWS[TYPED]['source'] else future(fixture,filename) if case['source']==ROWS[FUTURE]['source'] else repeated(fixture,filename) if case['source']==ROWS[LOOP]['source'] else owner(fixture, filename))
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if '+c+'\n' for c in clauses), len(clauses)

def main():
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--sl',action='store_true');parser.add_argument('--case',action='append',choices=(CASE,MISSING,TYPED,FUTURE,LOOP))
    args = parser.parse_args()
    protocol.run({key:{'source':ROWS[key]['source']} for key in (CASE,MISSING,TYPED,FUTURE,LOOP) if not args.case or key in args.case},extra_inputs=(CATALOGUE,CONTROLS,Path(__file__)),fixture_renderer=render,runner_flags=('--sl',) if args.sl else ())
if __name__ == '__main__': main()
