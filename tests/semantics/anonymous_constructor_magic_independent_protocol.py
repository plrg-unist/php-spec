#!/usr/bin/env python3
"""An inherited constructor's scalar return cannot replace its allocated instance."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
SEND = ('S.TODO = (CALL_SEND (METHOD_TARGET n_packet porigin_ctor) phpType7_send_tail* 0 eps (porigin_new) z_new) :: (CTOR_RESULT n_packet) :: ptask_send_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("late")) z_variable '
        '-- if S.CURRENT = eps')
CTOR_RETURN = ('S.TODO = (RETURN_VALUE z_ctor_return) :: ptask_ctor_return_tail* '
               '-- if S.RESULT = KNOWN (PBOOL false) '
               '-- if S.CURRENT = (pcallcontext_ctor) '
               '-- if pcallcontext_ctor.TARGET = METHOD_TARGET n_packet_return porigin_ctor_return')
CTOR_RESULT = ('S.TODO = (CTOR_RESULT n_packet_result) :: ptask_ctor_result_tail* '
               '-- if S.RESULT = KNOWN (PBOOL false) '
               '-- if S.CURRENT = eps')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) '
          '-- if S.CURRENT = (pcallcontext_return) '
          '-- if pcallcontext_return.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_return n_arguments n_named pvalue*')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") '
         '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SEND)
for label, front in [('ctor_return', CTOR_RETURN), ('ctor_result', CTOR_RESULT), ('return', RETURN), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$constructor204_' + label + '_')
PREFIX += r'''
dec $constructor204_outer_one(ptask) : pmagicmethodcall?
def $constructor204_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 0 eps) = (pmagicmethodcall)
def $constructor204_outer_one(ptask) = eps -- otherwise
dec $constructor204_outer(ptask*) : pmagicmethodcall?
def $constructor204_outer(eps) = eps
def $constructor204_outer(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $constructor204_outer_one(ptask) = (pmagicmethodcall)
def $constructor204_outer(ptask :: ptask_tail*) = $constructor204_outer(ptask_tail*)
  -- if $constructor204_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_packet_base,pclassdesc_packet_called,pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.FUNCTIONS = [pfunction_shift]',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        '$method_named(pclassdesc_packet_base.METHODS,$ptascii("__construct")) = (pmethoddesc_ctor)',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,4096)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SEND,
        'porigin_ctor = pmethoddesc_ctor.FUNCTION.ORIGIN',
        'pmethoddesc_ctor.OWNER = pclassdesc_packet_base.ORIGIN',
        'pmethoddesc_ctor.VISIBILITY = PROPERTY_PUBLIC',
        r'~pmethoddesc_ctor.STATIC /\ ~pmethoddesc_ctor.ABSTRACT',
        '$effective_method(S,pclassdesc_packet_called.ORIGIN,$ptascii("__construct"),|S.CLASSES|) = (pmethoddesc_ctor)',
        'S.OBJECTS[n_packet] = INSTANCE pclassdesc_packet_called.ORIGIN',
        '(HOBJECT n_packet) <- S.ALLOCATIONS',
        '$constructor204_outer(ptask_send_tail*) = (pmagicmethodcall)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_new)',
        '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
        'expression_new = NExprNew (NName (BYTES text_new) metadata_name_new) (SEQUENCE phpType7_new*) metadata_new',
        '|phpType7_new*| = 2',
        '$new_source_name(S,porigin_new) = (pclassdesc_packet_called.NAME)',
        '$magic_method_constructor_producer(S,porigin_new,expression_new) = ((pclassdesc_packet_called.ORIGIN,pmethoddesc_ctor))',
        '$magic_method_argument_source(S,porigin_new,0,expression_new)',
        '~$magic_unpack_explicit_source(S,porigin_new,expression_new)',
        '$call_selected_valid(S,METHOD_TARGET n_packet porigin_ctor,(porigin_new))',
        '$call_task_valid(S,CALL_SEND (METHOD_TARGET n_packet porigin_ctor) phpType7_send_tail* 0 eps (porigin_new) z_new)',
        '$call_task_valid(S,CTOR_RESULT n_packet)',
        '$magic_method_value(S,PINT 7)',
        '$magic_method_value(S,POBJECT pmagicmethodcall.OBJECT)',
        '$magic_method_copy_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (PINT 7)]) = eps',
        '$magic_method_copy_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (POBJECT pmagicmethodcall.OBJECT)]) = eps',
        '$magic_method_copy_values(S[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (POBJECT n_packet)]) = eps',
        '$call_argument_origin(S,(porigin_new),0) = (porigin_cv)',
        'phpType7_new*[0] = NArg ABSENT expression_cv (BOOLEAN false) (BOOLEAN false) metadata_cv_arg',
        'expression_cv = NExprVariable (BYTES text_cv) metadata_cv',
        '$base64(text_cv) = $ptascii("late")',
        'z_variable = $variable_line(BYTES text_cv,metadata_cv)',
        '$lookup(S.ENV,$ptascii("late")) = (n_late_cell)',
        '$lookup(S.ENV,$ptascii("alias")) = (n_late_cell)',
        'n_late_cell <- S.REFCELLS',
        'S.STORE[n_late_cell] = DEFINED pvalue_string',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S.STRINGDATA = [$ptascii("REQUEST-OLD")]',
        '$string_carrier_valid(S,pvalue_string)', '$value_nodes(pvalue_string) = eps',
        '$lookup(S.ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED (POBJECT pmagicmethodcall.OBJECT)',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_packet) = 2',
        '$task_nodes(S.TODO[0]) = [HOBJECT n_packet]',
        '$task_nodes(CTOR_RESULT n_packet) = [HOBJECT n_packet]',
        '$factory182_output(S.EVENTS) = eps',
        '~$call_parameter_reference(S,METHOD_TARGET n_packet porigin_ctor,0)',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_sent = $drive_steps(S,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (METHOD_TARGET n_packet porigin_ctor) phpType7_send_tail* 1 ([KNOWN pvalue_string]) (porigin_new) z_new) :: (CTOR_RESULT n_packet) :: ptask_send_tail*',
        'S_sent.STORE[n_late_cell] = S.STORE[n_late_cell]',
        'S_sent.STRINGDATA = S.STRINGDATA',
        '$task_nodes(S_sent.TODO[0]) = [HOBJECT n_packet]',
        '~((HCELL n_late_cell) <- $task_nodes(S_sent.TODO[0]))',
        'S_ctor_found = $constructor204_ctor_return_seek(S_sent[.COMPLETION = NORMAL],4096)',
        'S_ctor_found.COMPLETION = BUDGET',
        'S_ctor = S_ctor_found[.COMPLETION = NORMAL]', CTOR_RETURN.replace('S.', 'S_ctor.'),
        'n_packet_return = n_packet', 'porigin_ctor_return = porigin_ctor',
        'pcallcontext_ctor.FUNCTION = porigin_ctor',
        'pcallcontext_ctor.CALLSITE = (porigin_new)',
        'pcallcontext_ctor.ARGC = 2',
        'pcallcontext_ctor.LEXICAL_CLASS = (pclassdesc_packet_base.ORIGIN)',
        'pcallcontext_ctor.CALLED_CLASS = (pclassdesc_packet_called.ORIGIN)',
        'pcallcontext_ctor.RECEIVER = (n_packet)',
        '$call_context_roots(S_ctor.CURRENT) = [HOBJECT n_packet]',
        '$lookup(S_ctor.ENV,$ptascii("text")) = (n_text_cell)',
        '$lookup(S_ctor.ENV,$ptascii("marker")) = (n_marker_cell)',
        r'n_text_cell =/= n_late_cell /\ n_marker_cell =/= n_late_cell',
        r'~(n_text_cell <- S_ctor.REFCELLS) /\ ~(n_marker_cell <- S_ctor.REFCELLS)',
        'S_ctor.STORE[n_text_cell] = DEFINED pvalue_string',
        'S_ctor.STORE[n_marker_cell] = DEFINED (PINT 0)',
        'S_ctor.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_ctor.STORE[n_owner_cell] = DEFINED PNULL',
        '$objectprops_at(S_ctor.OBJECTPROPS,n_packet) = (ppropertyslot_packet*)',
        '$property_slot_at(ppropertyslot_packet*,$ptascii("text")) = (ppropertyslot_text)',
        'ppropertyslot_text.STATE = PROP_VALUE (DIRECT pvalue_string)',
        '$node_children(S_ctor,HOBJECT n_packet) = eps',
        '$magic_method_value(S_ctor,POBJECT n_packet)',
        '$heap_owners($heap_graph(S_ctor),HOBJECT n_packet) = 2',
        '$heap_owners($heap_graph(S_ctor),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$factory182_output(S_ctor.EVENTS) = $ptascii("SHIFT;CTOR;")',
        '$call_current_valid(S_ctor)', '$call_descriptors_valid(S_ctor)',
        '$gc_state_valid(S_ctor)', '$heap_valid($heap_graph(S_ctor))',
        'S_result_found = $constructor204_ctor_result_seek(S_ctor,4096)',
        'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', CTOR_RESULT.replace('S.', 'S_result.'),
        'n_packet_result = n_packet', 'S_result.FRAMES = eps',
        '~((HCELL n_text_cell) <- S_result.ALLOCATIONS)',
        '~((HCELL n_marker_cell) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_packet) = 1',
        '$call_task_valid(S_result,CTOR_RESULT n_packet)',
        '$objectprops_at(S_result.OBJECTPROPS,n_packet) = (ppropertyslot_packet*)',
        'S_result.STRINGDATA = S.STRINGDATA',
        'S_object = $drive_steps(S_result,1)', 'S_object.COMPLETION = BUDGET',
        'S_object.RESULT = KNOWN (POBJECT n_packet)',
        'S_object.TODO = ptask_ctor_result_tail*',
        '$heap_owners($heap_graph(S_object),HOBJECT n_packet) = 1',
        '$call_descriptors_valid(S_object)', '$gc_state_valid(S_object)', '$heap_valid($heap_graph(S_object))',
        'S_return_found = $constructor204_return_seek(S_object[.COMPLETION = NORMAL],4096)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'pmagicmethodcall_return = pmagicmethodcall',
        'pcallcontext_return.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_return.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext_return.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pvalue* = [POBJECT n_packet,PFLOAT 4609434218613702656]',
        'S_return.STORE[n_late_cell] = DEFINED (PINT 0)',
        '$magic_method_collected_values(S_return,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet),KNOWN (PFLOAT 4609434218613702656)]) = (pvalue*)',
        'n_arguments = n_named', 'S_return.FRAMES = pframe :: pframe_tail*',
        '$magic_named_frame(S_return,pcallcontext_return,pframe,pframe_tail*,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_buffer(S_return,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        'S_return.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (POBJECT n_packet)),ENTRY (KSTRING $ptascii("later")) (DIRECT (PFLOAT 4609434218613702656))]',
        '$node_children(S_return,HARRAY n_arguments) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 3',
        '$heap_owners($heap_graph(S_return),HOBJECT n_packet) = 1',
        '$object_body(S_return.OBJECTS[n_closure]) = REALCLOSURE pfunction_closure.ORIGIN ([DIRECT (PARRAY n_arguments),DIRECT (PSTRING $ptascii("MiSsInG"))]) eps',
        '$node_children(S_return,HOBJECT n_closure) = [HARRAY n_arguments]',
        '$closure_scope_at(S_return.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_base.ORIGIN',
        'pclosurescope.CALLED = pclassdesc_called.ORIGIN',
        'pclosurescope.RECEIVER = eps',
        '$target_nodes(pcallcontext_return.TARGET) = eps',
        '$call_context_roots(S_return.CURRENT) = eps',
        '$heap_owners($heap_graph(S_return),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$factory182_output(S_return.EVENTS) = $ptascii("SHIFT;CTOR;MAGIC;")',
        '$call_current_valid(S_return)', '$call_descriptors_valid(S_return)',
        '$closure_state_valid(S_return)', '$gc_state_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_child_found = $constructor204_child_seek(S_return,4096)',
        'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        'S_child.FRAMES = eps',
        r'$lookup(S_child.ENV,$ptascii("alias")) = eps /\ $lookup(S_child.ENV,$ptascii("late")) = eps',
        '~((HCELL n_late_cell) <- S_child.ALLOCATIONS)',
        '$lookup(S_child.ENV,$ptascii("factory")) = eps',
        '$lookup(S_child.ENV,$ptascii("child")) = (n_child_cell)',
        'S_child.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_child.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$objectprops_at(S_child.OBJECTPROPS,n_child) = (ppropertyslot_child*)',
        '$property_slot_at(ppropertyslot_child*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_child,HOBJECT n_child) = [HARRAY n_arguments]',
        '$node_children(S_child,HARRAY n_arguments) = [HOBJECT n_packet]',
        '$node_children(S_child,HOBJECT n_packet) = eps',
        '$heap_owners($heap_graph(S_child),HOBJECT n_child) = 1',
        '$heap_owners($heap_graph(S_child),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S_child),HOBJECT n_packet) = 1',
        'S_child.ARRAYS[n_arguments] = S_return.ARRAYS[n_arguments]',
        '$objectprops_at(S_child.OBJECTPROPS,n_packet) = (ppropertyslot_packet*)',
        '$string_carrier_valid(S_child,pvalue_string)',
        '~((HOBJECT n_closure) <- S_child.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_child.ALLOCATIONS)',
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
        '~((HOBJECT n_packet) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
