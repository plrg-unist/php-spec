#!/usr/bin/env python3
"""Named reference-CV snapshots outlive caller cells through a real Closure table."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_later_cv_magic_independent_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
CASE = ROW['id']
SEND = ('S.TODO = (MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PINT 7)])) :: ptask_send_tail* '
        '-- if S.CURRENT = eps')
RETURN = ('S.TODO = (RETURN_VALUE z_return) :: ptask_return_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_closure) '
          '-- if S.CURRENT = (pcallcontext) '
          '-- if pcallcontext.TARGET = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall_return n_arguments n_named pvalue*')
CHILD = ('S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_child) metadata_child])) metadata_unset)) :: ptask_child_tail* '
         '-- if $base64(text_child) = $ptascii("child") '
         '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SEND)
for label, front in [('return', RETURN), ('child', CHILD)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$later202_' + label + '_')


def render(case, fixture, filename):
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.CLOSURETEMPLATES = [pfunction_closure]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,4096)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SEND,
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pmagicmethodcall.ARGUMENTS = [phpType7_first,phpType7_later]',
        'phpType7_later = NArg phpType3_later expression_later (BOOLEAN false) (BOOLEAN false) metadata_later',
        'expression_later = NExprVariable (BYTES text_later) metadata_variable',
        '$base64(text_later) = $ptascii("late")',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),1) = (porigin_later)',
        'porigin_later = PORIGIN n_unit pcpath_later',
        '$origin_node(S.SOURCES,porigin_later) = (expression_later)',
        '$source_emission_cv(S,n_unit,pcpath_later,expression_later)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '~(pcpath_later <- $call_argument_paths(pcode.EXPRESSIONS))',
        '$magic_method_argument_source(S,porigin_later,1,expression_later)',
        '~$magic_method_argument_source(S,porigin_later,2,expression_later)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1)',
        'z_later = $runtime_line(S[.ORIGIN = (porigin_later)],eps,expression_later)',
        'S.RESULT = VARIABLE ($ptascii("late")) $variable_line(BYTES text_later,metadata_variable)',
        '$variable_line(BYTES text_later,metadata_variable) = 9',
        '$lookup(S.ENV,$ptascii("late")) = (n_late_cell)',
        '$lookup(S.ENV,$ptascii("alias")) = (n_late_cell)',
        'n_late_cell <- S.REFCELLS',
        '(HCELL n_late_cell) <- S.ALLOCATIONS',
        'S.STORE[n_late_cell] = DEFINED pvalue_string',
        'pvalue_string = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("REQUEST-OLD"))',
        'S.STRINGDATA = [$ptascii("REQUEST-OLD")]',
        '$string_carrier_valid(S,pvalue_string)',
        '$magic_method_primitive(S,pvalue_string)',
        '$value_nodes(pvalue_string) = eps',
        '$lookup(S.ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$task_nodes(MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PINT 7)])) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$factory182_output(S.EVENTS) = $ptascii("FIRST;")',
        '$magic_method_cv_pending(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall)',
        '$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(pmagicmethodcall.SITE),(porigin_later),z_later)',
        '~$call_send_value_allowed(S,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(pmagicmethodcall.SITE),(pmagicmethodcall.SITE),z_later)',
        'S_wrong_task = S[.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 1 ([KNOWN (PINT 7)])) :: ptask_send_tail*]',
        '~$call_send_value_allowed(S_wrong_task,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1,expression_later,(pmagicmethodcall.SITE),(porigin_later),z_later)',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_sent = $drive_steps(S,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 2 ([KNOWN (PINT 7),KNOWN pvalue_string])) :: ptask_send_tail*',
        'S_sent.STORE[n_late_cell] = S.STORE[n_late_cell]',
        'S_sent.REFCELLS = S.REFCELLS',
        'S_sent.STRINGDATA = S.STRINGDATA',
        'S_sent.RESULT = KNOWN PNULL',
        '~((HCELL n_late_cell) <- $task_nodes(S_sent.TODO[0]))',
        '$task_nodes(S_sent.TODO[0]) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$call_descriptors_valid(S_sent)', '$gc_state_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
        'S_return_found = $later202_return_seek(S_sent[.COMPLETION = NORMAL],4096)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'pmagicmethodcall_return = pmagicmethodcall',
        'pcallcontext.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext.RECEIVER = (pmagicmethodcall.OBJECT)',
        'pvalue* = [PINT 7,pvalue_string]',
        'S_return.STORE[n_late_cell] = DEFINED (PINT 99)',
        '$magic_method_copy_source(S_return,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1)',
        '$magic_method_collected_values(S_return,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN pvalue_string]) = (pvalue*)',
        'S_return.STRINGDATA = S.STRINGDATA',
        '$string_carrier_valid(S_return,pvalue_string)',
        'n_arguments = n_named',
        'S_return.FRAMES = pframe :: pframe_tail*',
        '$magic_named_frame(S_return,pcallcontext,pframe,pframe_tail*,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        '$magic_named_buffer(S_return,pmagicmethodcall,n_arguments,n_named,pvalue*)',
        'S_return.ARRAYS[n_arguments].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PINT 7)),ENTRY (KSTRING $ptascii("later")) (DIRECT pvalue_string)]',
        '$lookup(S_return.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_return.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
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
        '$target_nodes(pcallcontext.TARGET) = eps',
        '$call_context_roots(S_return.CURRENT) = eps',
        '$heap_owners($heap_graph(S_return),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$factory182_output(S_return.EVENTS) = $ptascii("FIRST;MAGIC;")',
        '$call_current_valid(S_return)', '$call_descriptors_valid(S_return)',
        '$closure_state_valid(S_return)', '$gc_state_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_child_found = $later202_child_seek(S_return,4096)',
        'S_child_found.COMPLETION = BUDGET',
        'S_child = S_child_found[.COMPLETION = NORMAL]', CHILD.replace('S.', 'S_child.'),
        'S_child.FRAMES = eps',
        '$lookup(S_child.ENV,$ptascii("alias")) = eps',
        '$lookup(S_child.ENV,$ptascii("late")) = (n_slot_cell)',
        '$lookup(S_child.ENV,$ptascii("slot")) = (n_slot_cell)',
        'n_slot_cell =/= n_late_cell',
        'S_child.STORE[n_slot_cell] = DEFINED PNULL',
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
        'S_child.STRINGDATA = S.STRINGDATA',
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
