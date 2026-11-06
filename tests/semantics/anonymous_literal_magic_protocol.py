#!/usr/bin/env python3
"""Compiled literal SEND ownership and the separate unpack-source boundary."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_literal_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_literal_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS)
        for row in json.loads(path.read_text())['cases']}
CASE = 'magic-literal-pending-instance'
UNPACK = 'magic-literal-prefix-unpack-refused'
LATER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_later) metadata_string_later])) metadata_echo_later)) :: ptask_later_tail* '
         '-- if $base64(text_later) = $ptascii("LATER;") '
         '-- if S.CURRENT = (pcallcontext_later)')
NEW = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_new_tail* '
       '-- if S.CURRENT = (pcallcontext_new) '
       '-- if pcallcontext_new.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_new n_arguments pvalue_sent*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") '
          '-- if S.CURRENT = eps')
UNPACK_FRONT = ('S.TODO = (EVAL (NExprMethodCall expression_receiver phpType20_name (SEQUENCE phpType7*) metadata_site)) :: ptask_boundary_tail* '
                '-- if $call_unpack_present(phpType7*) '
                '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, LATER)
for label, front in [('new', NEW), ('return', RETURN), ('boundary', UNPACK_FRONT)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$literal201_' + label + '_')
PREFIX += r'''
dec $literal201_send_one(ptask) : (pmagicmethodcall, pvalue)?
def $literal201_send_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN pvalue]) porigin? z) = ((pmagicmethodcall,pvalue))
def $literal201_send_one(ptask) = eps -- otherwise
dec $literal201_send(ptask*) : (pmagicmethodcall, pvalue)?
def $literal201_send(eps) = eps
def $literal201_send(ptask :: ptask_tail*) = ((pmagicmethodcall,pvalue))
  -- if $literal201_send_one(ptask) = ((pmagicmethodcall,pvalue))
def $literal201_send(ptask :: ptask_tail*) = $literal201_send(ptask_tail*)
  -- if $literal201_send_one(ptask) = eps
'''


def ownership(row, fixture, filename):
    return [
        'P = $ppstart(0,' + fixture + ',$base64(' + filename + '))',
        r'P.COMPLETION = PPCNORMAL /\ $ppimage_unit(P)',
        'P.CLASSES = [pclassdesc_child,pclassdesc_base,pclassdesc_called]',
        'P.FUNCTIONS = [pfunction_later]',
        '$method_named(pclassdesc_base.METHODS,$ptascii("__call")) = (pmethoddesc)',
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', LATER,
        'pcallcontext_later.FUNCTION = pfunction_later.ORIGIN',
        'pcallcontext_later.TARGET = pfunction_later.ORIGIN',
        'pcallcontext_later.ARGC = 0', 'pcallcontext_later.RECEIVER = eps',
        '$call_context_roots(S.CURRENT) = eps',
        'S.FRAMES = [pframe]',
        '$literal201_send(pframe.TODO) = ((pmagicmethodcall,pvalue_literal))',
        'pvalue_literal = PSTRING_CARRIER INTERNED_STRING $ptascii("PENDING")',
        'pmagicmethodcall.METHOD = pmethoddesc.FUNCTION.ORIGIN',
        'pmagicmethodcall.CLASS = pclassdesc_called.ORIGIN',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pmagicmethodcall.ARGUMENTS = [phpType7_literal,phpType7_later]',
        'phpType7_literal = NArg ABSENT expression_literal (BOOLEAN false) (BOOLEAN false) metadata_literal',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_literal)',
        '$origin_node(S.SOURCES,porigin_literal) = (expression_literal)',
        '$magic_method_literal_shape(expression_literal)',
        '$compiled_read(S,porigin_literal) = (PSTRING $ptascii("PENDING"))',
        '$compiled_effects(S,porigin_literal) = eps',
        '$compiled_string_value(S,porigin_literal,PSTRING $ptascii("PENDING")) = pvalue_literal',
        '$magic_method_literal_value(S,porigin_literal,expression_literal) = (pvalue_literal)',
        '~$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_user_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,1) = (pfunction_later)',
        'S.STRINGDATA = eps', '$value_nodes(pvalue_literal) = eps',
        'ptask_send = CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN pvalue_literal]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE',
        '$source_operand_suffix(pframe.TODO,ptask_send,METHOD_RESULT :: pmagicmethodcall.TAIL)',
        '$task_nodes(ptask_send) = [HOBJECT pmagicmethodcall.OBJECT]',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '~((HCELL n_owner_cell) <- $task_nodes(ptask_send))',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN pvalue_literal,KNOWN PNULL]) = ([pvalue_literal,PNULL])',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN PNULL]) = eps',
        '$magic_method_value(S,POBJECT pmagicmethodcall.OBJECT)',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT pmagicmethodcall.OBJECT),KNOWN PNULL]) = eps',
        '$magic_method_collected_values(S[.POOLS = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN PNULL]) = eps',
        '$magic_method_collected_values(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PSTRING $ptascii("PENDING")),KNOWN PNULL]) = eps',
        'S_spoof = S[.STRINGDATA = [$ptascii("PENDING")]]',
        '$string_carrier_valid(S_spoof,PSTRING_CARRIER (REQUEST_STRING 0) $ptascii("PENDING"))',
        '$magic_method_collected_values(S_spoof,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PSTRING_CARRIER (REQUEST_STRING 0) $ptascii("PENDING")),KNOWN PNULL]) = eps',
        '~$magic_method_value(S,pvalue_literal)',
        '$factory182_output(S.EVENTS) = eps',
        '$call_current_valid(S)', '$call_descriptors_valid(S)',
        '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_new_found = $literal201_new_seek(S,2048)',
        'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]', NEW.replace('S.', 'S_new.'),
        'pmagicmethodcall_new = pmagicmethodcall',
        'pvalue_sent* = [pvalue_literal,PNULL]',
        'pcallcontext_new.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_new.LEXICAL_CLASS = (pclassdesc_base.ORIGIN)',
        'pcallcontext_new.CALLED_CLASS = (pclassdesc_called.ORIGIN)',
        'pcallcontext_new.RECEIVER = (pmagicmethodcall.OBJECT)',
        '$lookup(S_new.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_new.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S_new.ARRAYS[n_arguments] = $magic_method_array([pvalue_literal,PNULL],0)',
        '$node_children(S_new,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_new),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S_new),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$call_context_roots(S_new.CURRENT) = [HOBJECT pmagicmethodcall.OBJECT]',
        'S_new.STRINGDATA = eps',
        '$factory182_output(S_new.EVENTS) = $ptascii("LATER;")',
        '$call_current_valid(S_new)', '$call_descriptors_valid(S_new)',
        '$gc_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_return_found = $literal201_return_seek(S_new,2048)',
        'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        'S_return.FRAMES = eps',
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)',
        'S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        'S_return.OBJECTS[n_child] = INSTANCE pclassdesc_child.ORIGIN',
        '$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_return,HOBJECT n_child) = [HARRAY n_arguments]',
        '$node_children(S_return,HARRAY n_arguments) = eps',
        '$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 1',
        'S_return.STRINGDATA = eps',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_return.ALLOCATIONS)',
        '$factory182_output(S_return.EVENTS) = $ptascii("LATER;OWNER;")',
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


def boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $literal201_boundary_seek(S_initial,2048)',
        'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', UNPACK_FRONT,
        'S.ORIGIN = (porigin_site)',
        '$origin_node(S.SOURCES,porigin_site) = (NExprMethodCall expression_receiver phpType20_name (SEQUENCE phpType7*) metadata_site)',
        'phpType7* = [phpType7_prefix,phpType7_pack]',
        'phpType7_prefix = NArg ABSENT expression_prefix (BOOLEAN false) (BOOLEAN false) metadata_prefix',
        'phpType7_pack = NArg ABSENT expression_pack (BOOLEAN false) (BOOLEAN true) metadata_pack',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_prefix)',
        '$magic_method_literal_value(S,porigin_prefix,expression_prefix) = (PBOOL true)',
        '$magic_method_argument_source(S,porigin_prefix,0,expression_prefix)',
        '~$magic_unpack_explicit_source(S,porigin_prefix,expression_prefix)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)',
        '$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps',
        '~$magic_unpack_source(S,porigin_site,phpType7*,0)',
        '~$magic_unpack_arguments(S,porigin_site,phpType7*)',
        '$factory182_output(S.EVENTS) = eps',
        '$class_state_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_done = $drive_steps(S,2048)',
        'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    checks = boundary(fixture, filename) if case['id'] == UNPACK else ownership(ROWS[case['id']], fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    selected = args.case or [CASE, UNPACK]
    protocol.run({name: {'id': name, 'source': ROWS[name]['source']} for name in selected},
                 (Path(__file__), CATALOGUE, CONTROLS, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',))
