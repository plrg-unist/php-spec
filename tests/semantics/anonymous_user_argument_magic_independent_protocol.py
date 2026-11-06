#!/usr/bin/env python3
"""Actual inner COPY sends and fresh producer params feed one real named table."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_user_argument_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
SEND = ('S.TODO = (CALL_SEND porigin_producer phpType7_send_tail* 0 eps (porigin_inner) z_inner) :: ptask_send_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("late")) z_variable '
        '-- if S.CURRENT = eps')
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_producer_marker) metadata_producer_string])) metadata_producer_echo)) :: ptask_producer_tail* '
            '-- if $base64(text_producer_marker) = $ptascii("PRODUCER;") '
            '-- if S.CURRENT = (pcallcontext_producer)')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) '
          '-- if S.CURRENT = (pcallcontext_return) '
          '-- if pcallcontext_return.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_return n_arguments n_named pvalue*')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") '
         '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SEND)
for label, front in [('producer', PRODUCER), ('return', RETURN), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$argument203_' + label + '_')
PREFIX += r'''
dec $argument203_outer_one(ptask) : pmagicmethodcall?
def $argument203_outer_one(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 0 eps) = (pmagicmethodcall)
def $argument203_outer_one(ptask) = eps -- otherwise
dec $argument203_outer(ptask*) : pmagicmethodcall?
def $argument203_outer(eps) = eps
def $argument203_outer(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $argument203_outer_one(ptask) = (pmagicmethodcall)
def $argument203_outer(ptask :: ptask_tail*) = $argument203_outer(ptask_tail*)
  -- if $argument203_outer_one(ptask) = eps
'''


def render(case, fixture, filename):
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.FUNCTIONS = [pfunction_shift,pfunction_producer]',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,4096)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SEND,
        'porigin_producer = pfunction_producer.ORIGIN',
        'pfunction_producer.SIGNATURE.PARAMETERS = [psparam_saved,psparam_marker]',
        'psparam_saved.NAME = $ptascii("saved")',
        'psparam_marker.NAME = $ptascii("marker")',
        r'psparam_saved.TYPE = eps /\ psparam_marker.TYPE = eps',
        r'~psparam_saved.BYREF /\ ~psparam_marker.BYREF',
        r'psparam_saved.REQUIRED /\ psparam_marker.REQUIRED',
        r'psparam_saved.DEFAULT = PSNONE /\ psparam_marker.DEFAULT = PSNONE',
        r'~psparam_saved.VARIADIC /\ ~psparam_marker.VARIADIC',
        'pfunction_producer.DEFAULTS = eps',
        '$argument203_outer(ptask_send_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_inner)',
        '$origin_node(S.SOURCES,porigin_inner) = (expression_inner)',
        'expression_inner = NExprFuncCall (NName (BYTES text_producer) metadata_producer_name) (SEQUENCE phpType7_inner*) metadata_producer_call',
        '|phpType7_inner*| = 2',
        'porigin_inner = PORIGIN n_unit pcpath_inner',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$code_name(pcode.NAMES,pcpath_inner) = ((preqbytes,eps))',
        '$call_target(S,preqbytes,eps) = (pfunction_producer)',
        '$call_selected_valid(S,porigin_producer,(porigin_inner))',
        '$call_task_valid(S,CALL_SEND porigin_producer phpType7_send_tail* 0 eps (porigin_inner) z_inner)',
        '$magic_method_required_producer(S,porigin_inner,expression_inner) = (pfunction_producer)',
        '$magic_method_argument_source(S,porigin_inner,0,expression_inner)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_copy_values(S[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (PINT 7)]) = eps',
        '$magic_method_value(S,POBJECT pmagicmethodcall.OBJECT)',
        '$magic_method_copy_values(S[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0,[KNOWN (POBJECT pmagicmethodcall.OBJECT)]) = eps',
        '$magic_method_array_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS) = eps',
        '~$magic_unpack_explicit_source(S,porigin_inner,expression_inner)',
        '$call_argument_origin(S,(porigin_inner),0) = (porigin_cv)',
        'phpType7_inner*[0] = NArg ABSENT expression_cv (BOOLEAN false) (BOOLEAN false) metadata_cv_arg',
        'expression_cv = NExprVariable (BYTES text_cv) metadata_cv',
        '$base64(text_cv) = $ptascii("late")',
        'z_variable = $variable_line(BYTES text_cv,metadata_cv)',
        '$lookup(S.ENV,$ptascii("late")) = (n_late_cell)',
        '$lookup(S.ENV,$ptascii("alias")) = (n_late_cell)',
        'n_late_cell <- S.REFCELLS',
        'S.STORE[n_late_cell] = DEFINED pvalue_string',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S.STRINGDATA = [$ptascii("REQUEST-OLD")]',
        '$string_carrier_valid(S,pvalue_string)',
        '$value_nodes(pvalue_string) = eps',
        '$lookup(S.ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED (POBJECT pmagicmethodcall.OBJECT)',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 2',
        '$factory182_output(S.EVENTS) = eps',
        '~$call_parameter_reference(S,porigin_producer,0)',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_sent = $drive_steps(S,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS porigin_producer phpType7_send_tail* 1 ([KNOWN pvalue_string]) (porigin_inner) z_inner) :: ptask_send_tail*',
        'S_sent.STORE[n_late_cell] = S.STORE[n_late_cell]',
        'S_sent.REFCELLS = S.REFCELLS',
        'S_sent.STRINGDATA = S.STRINGDATA',
        '$task_nodes(S_sent.TODO[0]) = eps',
        '~((HCELL n_late_cell) <- $task_nodes(S_sent.TODO[0]))',
        '$call_descriptors_valid(S_sent)', '$gc_state_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
        'S_producer_found = $argument203_producer_seek(S_sent[.COMPLETION = NORMAL],4096)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'pcallcontext_producer.TARGET = porigin_producer',
        'pcallcontext_producer.FUNCTION = porigin_producer',
        'pcallcontext_producer.CALLSITE = (porigin_inner)',
        'pcallcontext_producer.ARGC = 2',
        'pcallcontext_producer.PARAMS = [$ptascii("saved"),$ptascii("marker")]',
        r'pcallcontext_producer.EXTRA = eps /\ pcallcontext_producer.NAMED = eps',
        r'pcallcontext_producer.RECEIVER = eps /\ pcallcontext_producer.INSTANCE = eps',
        '$call_context_roots(S_producer.CURRENT) = eps',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)',
        '$lookup(S_producer.ENV,$ptascii("marker")) = (n_marker_cell)',
        r'n_saved_cell =/= n_late_cell /\ n_marker_cell =/= n_late_cell',
        '~(n_saved_cell <- S_producer.REFCELLS)',
        '~(n_marker_cell <- S_producer.REFCELLS)',
        'S_producer.STORE[n_saved_cell] = DEFINED pvalue_string',
        'S_producer.STORE[n_marker_cell] = DEFINED (PBOOL false)',
        'S_producer.STORE[n_late_cell] = DEFINED (PINT 99)',
        'S_producer.STORE[n_owner_cell] = DEFINED PNULL',
        'S_producer.STRINGDATA = S.STRINGDATA',
        '(HOBJECT pmagicmethodcall.OBJECT) <- $frames_roots(S_producer.FRAMES)',
        '$heap_owners($heap_graph(S_producer),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$factory182_output(S_producer.EVENTS) = $ptascii("SHIFT;")',
        '$call_current_valid(S_producer)', '$call_descriptors_valid(S_producer)',
        '$gc_state_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_return_found = $argument203_return_seek(S_producer,4096)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'pmagicmethodcall_return = pmagicmethodcall',
        'pcallcontext_return.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_return.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext_return.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pvalue* = [pvalue_string,PFLOAT 4609434218613702656]',
        '~((HCELL n_saved_cell) <- S_return.ALLOCATIONS)',
        '~((HCELL n_marker_cell) <- S_return.ALLOCATIONS)',
        'S_return.STORE[n_late_cell] = DEFINED (PINT 0)',
        '$magic_method_copy_source(S_return,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_collected_values(S_return,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_string,KNOWN (PFLOAT 4609434218613702656)]) = (pvalue*)',
        'S_return.STRINGDATA = S.STRINGDATA',
        'n_arguments = n_named',
        'S_return.FRAMES = pframe :: pframe_tail*',
        '$magic_named_frame(S_return,pcallcontext_return,pframe,pframe_tail*,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_buffer(S_return,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        'S_return.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT pvalue_string),ENTRY (KSTRING $ptascii("later")) (DIRECT (PFLOAT 4609434218613702656))]',
        '$node_children(S_return,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 3',
        '$object_body(S_return.OBJECTS[n_closure]) = REALCLOSURE pfunction_closure.ORIGIN ([DIRECT (PARRAY n_arguments),DIRECT (PSTRING $ptascii("MiSsInG"))]) eps',
        '$node_children(S_return,HOBJECT n_closure) = [HARRAY n_arguments]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_closure) = 1',
        '$closure_scope_at(S_return.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.LEXICAL = pclassdesc_base.ORIGIN',
        'pclosurescope.CALLED = pclassdesc_called.ORIGIN',
        'pclosurescope.RECEIVER = eps',
        '$task_nodes(MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue*) = [HARRAY n_named,HOBJECT pmagicmethodcall.OBJECT]',
        '$target_nodes(pcallcontext_return.TARGET) = eps',
        '$call_context_roots(S_return.CURRENT) = eps',
        '$heap_owners($heap_graph(S_return),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$factory182_output(S_return.EVENTS) = $ptascii("SHIFT;PRODUCER;MAGIC;")',
        '$call_current_valid(S_return)', '$call_descriptors_valid(S_return)',
        '$closure_state_valid(S_return)', '$gc_state_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_child_found = $argument203_child_seek(S_return,4096)',
        'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        'S_child.FRAMES = eps',
        '$lookup(S_child.ENV,$ptascii("alias")) = eps',
        '$lookup(S_child.ENV,$ptascii("late")) = eps',
        '~((HCELL n_late_cell) <- S_child.ALLOCATIONS)',
        '$lookup(S_child.ENV,$ptascii("factory")) = eps',
        '$lookup(S_child.ENV,$ptascii("child")) = (n_child_cell)',
        'S_child.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_child.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$objectprops_at(S_child.OBJECTPROPS,n_child) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_child,HOBJECT n_child) = [HARRAY n_arguments]',
        '$node_children(S_child,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_child),HOBJECT n_child) = 1',
        '$heap_owners($heap_graph(S_child),HARRAY n_arguments) = 1',
        'S_child.ARRAYS[n_arguments] = S_return.ARRAYS[n_arguments]',
        'S_child.STRINGDATA = S.STRINGDATA ++ [$ptascii("1.5")]',
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
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$closure_state_valid(S_done)',
        '$class_state_valid(S_done)', '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROW['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
