#!/usr/bin/env python3
"""Actual scoped static targets, parameter copies and magic table owners."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_static_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_static_producer_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS)
        for row in json.loads(path.read_text())['cases']}
CASE = 'magic-static-user-pending-leaf'
UNPACK = 'magic-static-user-unpack-prefix-refused'
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_string_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_producer) metadata_string_producer) :: expression_echo_tail*)) metadata_echo_producer)) :: ptask_producer_tail* '
            '-- if $base64(text_producer) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_producer)')
NEW = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14_new phpType24_new ABSENT phpType44_new phpType42_new phpType23_new metadata_class_new) phpType6_new metadata_new)) :: ptask_new_tail* '
       '-- if S.CURRENT = (pcallcontext_new) -- if pcallcontext_new.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_new n_arguments pvalue_sent*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver phpType20_name (SEQUENCE phpType7*) metadata_site)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SHIFT)
for label, front in [('producer', PRODUCER), ('new', NEW), ('return', RETURN), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$static205_' + label + '_')
PREFIX += r'''
dec $static205_send_one(ptask) : (pcalltarget, porigin, int, nat)?
def $static205_send_one(CALL_SEND (SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) eps 1 ([KNOWN (POBJECT n_old)]) (porigin_site) z) = ((SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector,porigin_site,z,n_old))
def $static205_send_one(ptask) = eps -- otherwise
dec $static205_send(ptask*) : (pcalltarget, porigin, int, nat)?
def $static205_send(eps) = eps
def $static205_send(ptask :: ptask_tail*) = ((pcalltarget,porigin_site,z,n_old))
  -- if $static205_send_one(ptask) = ((pcalltarget,porigin_site,z,n_old))
def $static205_send(ptask :: ptask_tail*) = $static205_send(ptask_tail*)
  -- if $static205_send_one(ptask) = eps
dec $static205_outer_one(ptask) : pmagicmethodcall?
def $static205_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin? z) = (pmagicmethodcall)
def $static205_outer_one(ptask) = eps -- otherwise
dec $static205_outer(ptask*) : pmagicmethodcall?
def $static205_outer(eps) = eps
def $static205_outer(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $static205_outer_one(ptask) = (pmagicmethodcall)
def $static205_outer(ptask :: ptask_tail*) = $static205_outer(ptask_tail*)
  -- if $static205_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SHIFT,
        'S.FUNCTIONS = [pfunction_shift]', 'pcallcontext_shift.TARGET = pfunction_shift.ORIGIN',
        'S.FRAMES = [pframe]',
        '$static205_send(pframe.TODO) = ((pcalltarget_producer,porigin_producer_site,z_producer,n_old))',
        '$static205_outer(pframe.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.ARGUMENTS = [phpType7_producer,phpType7_later]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer_arg',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer_site)',
        '$origin_node(S.SOURCES,porigin_producer_site) = (expression_producer)',
        '$magic_method_static_call(expression_producer)',
        '$magic_method_static_producer(S,porigin_producer_site,expression_producer) = ((porigin_requested,pmethoddesc))',
        'pcalltarget_producer = SCOPED_TARGET porigin_requested pmethoddesc.FUNCTION.ORIGIN porigin_requested eps (KNOWN (PSTRING ptbytes_selector))',
        '$scoped_selector_class(S,KNOWN (PSTRING ptbytes_selector)) = (porigin_requested)',
        '$target_function(S,pcalltarget_producer) = (pmethoddesc.FUNCTION)',
        '$target_nodes(pcalltarget_producer) = eps', '$target_instance(pcalltarget_producer) = eps',
        '$target_receiver(S,pcalltarget_producer) = eps',
        '$target_lexical_class(S,pcalltarget_producer) = (pmethoddesc.OWNER)',
        '$target_called_class(S,pcalltarget_producer) = (porigin_requested)',
        'pmethoddesc.OWNER =/= porigin_requested',
        '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc_declaring)',
        '$class_at(S.CLASSES,porigin_requested) = (pclassdesc_called)',
        'pclassdesc_declaring.NAME = $ptascii("ProducerBase205")',
        'pclassdesc_called.NAME = $ptascii("ProducerChild205")',
        'pmethoddesc.STATIC', 'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '~$ppmethod_magic(pmethoddesc.NAME)',
        '$magic_method_argument_source(S,porigin_producer_site,0,expression_producer)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_user_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0) = eps',
        '$magic_method_array_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS) = eps',
        '~$magic_unpack_explicit_source(S,porigin_producer_site,expression_producer)',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S.STORE[n_argument_cell] = DEFINED (POBJECT n_replacement)', 'n_old =/= n_replacement',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_replacement) = 1',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$task_nodes(CALL_SEND pcalltarget_producer eps 1 ([KNOWN (POBJECT n_old)]) (porigin_producer_site) z_producer) = [HOBJECT n_old]',
        '$factory182_output(S.EVENTS) = eps',
        '$magic_method_copy_values(S,pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (POBJECT n_old)]) = ([POBJECT n_old])',
        '$magic_method_copy_values(S,pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (PINT 7)]) = ([PINT 7])',
        '$magic_method_copy_values(S[.CODE = eps],pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (POBJECT n_old)]) = eps',
        '$magic_method_copy_values(S[.CODE = eps],pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (PINT 7)]) = eps',
        '$magic_method_static_producer(S[.CLASSES = eps],porigin_producer_site,expression_producer) = eps',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_producer_found = $static205_producer_seek(S,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'pcallcontext_producer.TARGET = pcalltarget_producer',
        'pcallcontext_producer.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_producer.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_producer.CALLED_CLASS = (porigin_requested)',
        'pcallcontext_producer.RECEIVER = eps', 'pcallcontext_producer.INSTANCE = eps',
        'pcallcontext_producer.ARGC = 2', '$call_context_roots(S_producer.CURRENT) = eps',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
        '$lookup(S_producer.ENV,$ptascii("ignored")) = (n_ignored)',
        'n_saved =/= n_argument_cell',
        'S_producer.STORE[n_saved] = DEFINED (POBJECT n_old)',
        'S_producer.STORE[n_ignored] = DEFINED PNULL',
        '~(n_saved <- S_producer.REFCELLS)', '~(n_ignored <- S_producer.REFCELLS)',
        'S_producer.STORE[n_argument_cell] = DEFINED (POBJECT n_replacement)',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_replacement) = 1',
        '$factory182_output(S_producer.EVENTS) = $ptascii("SHIFT;")',
        '$call_current_valid(S_producer)', '$call_descriptors_valid(S_producer)',
        '$gc_state_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_new_found = $static205_new_seek(S_producer,2048)', 'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]', NEW.replace('S.', 'S_new.'),
        'pmagicmethodcall_new = pmagicmethodcall', 'pvalue_sent* = [POBJECT n_old,PNULL]',
        'S_new.STORE[n_argument_cell] = DEFINED PNULL',
        '~((HCELL n_saved) <- S_new.ALLOCATIONS)', '~((HCELL n_ignored) <- S_new.ALLOCATIONS)',
        '~((HOBJECT n_replacement) <- S_new.ALLOCATIONS)',
        '$lookup(S_new.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_new.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S_new.ARRAYS[n_arguments] = $magic_method_array(pvalue_sent*,0)',
        '$node_children(S_new,HARRAY n_arguments) = [HOBJECT n_old]',
        '$heap_owners($heap_graph(S_new),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_new),HARRAY n_arguments) = 1',
        '$factory182_output(S_new.EVENTS) = $ptascii("SHIFT;PRODUCER;ProducerBase205/ProducerChild205;NEW;HANDLER;")',
        '$call_current_valid(S_new)', '$call_descriptors_valid(S_new)',
        '$gc_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_return_found = $static205_return_seek(S_new,2048)', 'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)',
        'S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_return,HOBJECT n_child) = [HARRAY n_arguments]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_old) = 1',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_return.ALLOCATIONS)',
        '$factory182_output(S_return.EVENTS) = $ptascii("SHIFT;PRODUCER;ProducerBase205/ProducerChild205;NEW;HANDLER;OWNER;")',
        'S_split = $drive_steps(S_return,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROWS[CASE]['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_return,4098)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', '~((HOBJECT n_replacement) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $static205_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY,
        'S.ORIGIN = (porigin_site)', 'phpType7* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_static_producer(S,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
        'pmethoddesc.STATIC', 'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)', '$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps',
        '$lookup(S.ENV,$base64(text_pack)) = (n_pack_cell)',
        'S.STORE[n_pack_cell] = DEFINED (PARRAY n_pack)', '(HARRAY n_pack) <- S.ALLOCATIONS',
        'S.ARRAYS[n_pack] = $array_insert($array_empty(),KINT 0,DIRECT (PINT 9))',
        '~$magic_unpack_arguments(S,porigin_site,phpType7*)',
        '$factory182_output(S.EVENTS) = eps', 'S_done = $drive_steps(S,2048)',
        'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    clauses = unpack_boundary(fixture, filename) if case['source'] == ROWS[UNPACK]['source'] else ownership(fixture, filename)
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
            ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=(CASE, UNPACK))
    args = parser.parse_args()
    cases = {key: {'source': ROWS[key]['source']} for key in (CASE, UNPACK)
             if not args.case or key in args.case}
    protocol.run(cases, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
