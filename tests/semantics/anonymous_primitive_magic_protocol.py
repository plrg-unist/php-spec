#!/usr/bin/env python3
"""A primitive producer SEND retains its real receiver and packed table."""
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_primitive_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-primitive-producer-true-instance'
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_marker) metadata_string])) metadata_echo)) :: ptask_tail* '
         '-- if $base64(text_marker) = $ptascii("SHIFT;") '
         '-- if S.CURRENT = (pcallcontext)')
NEW = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_new_tail* '
       '-- if S.CURRENT = (pcallcontext_new) '
       '-- if pcallcontext_new.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_new n_arguments pvalue_sent*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_marker) metadata_string])) metadata_echo)) :: ptask_return_tail* '
          '-- if $base64(text_marker) = $ptascii("RETURN;") '
          '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SHIFT)
for label, front in [('new', NEW), ('return', RETURN)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$primitive200_' + label + '_')
PREFIX += r'''
dec $primitive200_send_one(ptask) : pmagicmethodcall?
def $primitive200_send_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PBOOL true)]) porigin? z) = (pmagicmethodcall)
def $primitive200_send_one(ptask) = eps -- otherwise
dec $primitive200_send(ptask*) : pmagicmethodcall?
def $primitive200_send(eps) = eps
def $primitive200_send(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $primitive200_send_one(ptask) = (pmagicmethodcall)
def $primitive200_send(ptask :: ptask_tail*) = $primitive200_send(ptask_tail*)
  -- if $primitive200_send_one(ptask) = eps
'''


def render(case, fixture, filename):
    row = ROWS[case['id']]
    checks = [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.FUNCTIONS = [pfunction_make,pfunction_shift]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SHIFT,
        'pcallcontext.FUNCTION = pfunction_shift.ORIGIN',
        'pcallcontext.TARGET = pfunction_shift.ORIGIN',
        'pcallcontext.ARGC = 0', 'pcallcontext.RECEIVER = eps',
        '$call_context_roots(S.CURRENT) = eps',
        'S.FRAMES = [pframe]',
        '$primitive200_send(pframe.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.CLASS = pclassdesc_called.ORIGIN',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'ptask_send = CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PBOOL true)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE',
        '$source_operand_suffix(pframe.TODO,ptask_send,METHOD_RESULT :: pmagicmethodcall.TAIL)',
        '$task_nodes(ptask_send) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$value_nodes(PBOOL true) = eps',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument)',
        'S.STORE[n_argument] = DEFINED (PINT 99)',
        '~((HCELL n_argument) <- $task_nodes(ptask_send))',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner)',
        'S.STORE[n_owner] = DEFINED PNULL',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_user_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0) = (pfunction_make)',
        '$magic_method_user_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1) = (pfunction_shift)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1)',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL true),KNOWN (PBOOL false)]) = ([PBOOL true,PBOOL false])',
        'pmagicmethodcall.ARGUMENTS = [phpType7_make,phpType7_shift]',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,[phpType7_shift,phpType7_make],[KNOWN (PBOOL true),KNOWN (PBOOL false)]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[REFERENCE n_argument,KNOWN (PBOOL false)]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL true)]) = eps',
        '$magic_method_user_producer(S[.FUNCTIONS = [pfunction_make[.SIGNATURE = pfunction_make.SIGNATURE[.BYREF = true]],pfunction_shift]],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0) = eps',
        '$magic_method_primitive(S,PNULL)', '$magic_method_primitive(S,PBOOL false)',
        '$magic_method_primitive(S,PFLOAT 9223372036854775808)',
        '~$magic_method_primitive(S,PFLOAT 18446744073709551616)',
        '~$magic_method_value(S,PNULL)', '~$magic_method_value(S,PBOOL true)',
        '~$magic_method_primitive(S,PSTRING $ptascii("unknown"))',
        '~$magic_method_primitive(S,PUNDEFINED)',
        '$factory182_output(S.EVENTS) = eps',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_new_found = $primitive200_new_seek(S,2048)',
        'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]', NEW.replace('S.', 'S_new.'),
        'pmagicmethodcall_new = pmagicmethodcall',
        'pvalue_sent* = [PBOOL true,PBOOL false]',
        'pcallcontext_new.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_new.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext_new.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext_new.RECEIVER = (pmagicmethodcall.OBJECT)',
        '$lookup(S_new.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_new.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S_new.ARRAYS[n_arguments] = $magic_method_array([PBOOL true,PBOOL false],0)',
        '$node_children(S_new,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_new),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S_new),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$target_nodes(pcallcontext_new.TARGET) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$call_context_roots(S_new.CURRENT) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$factory182_output(S_new.EVENTS) = $ptascii("SHIFT;")',
        '$call_current_valid(S_new)', '$call_descriptors_valid(S_new)',
        '$gc_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_return_found = $primitive200_return_seek(S_new,2048)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'S_return.FRAMES = eps',
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)',
        'S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$node_children(S_return,HOBJECT n_child) = eps',
        '$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1',
        '~((HARRAY n_arguments) <- S_return.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_return.ALLOCATIONS)',
        '$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,$ptascii("snapshot")) = (ppropertyslot_snapshot)',
        'ppropertyslot_snapshot.STATE = PROP_VALUE (DIRECT (PBOOL true))',
        '$property_slot_at(ppropertyslot*,$ptascii("later")) = (ppropertyslot_later)',
        'ppropertyslot_later.STATE = PROP_VALUE (DIRECT (PBOOL false))',
        '$factory182_output(S_return.EVENTS) = $ptascii("SHIFT;OWNER;")',
        'S_split = $drive_steps(S_return,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(row['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_return,2050)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    protocol.run({CASE: {'id': CASE, 'source': ROWS[CASE]['source']}},
                 (Path(__file__), CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
