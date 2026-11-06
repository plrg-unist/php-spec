#!/usr/bin/env python3
"""Required USER parameter copies through real magic table/child owners."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_user_argument_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_user_argument_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS)
        for row in json.loads(path.read_text())['cases']}
CASE = 'magic-required-user-pending-leaf'
UNPACK = 'magic-required-user-unpack-prefix-refused'
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_string_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_producer) metadata_string_producer])) metadata_echo_producer)) :: ptask_producer_tail* '
            '-- if $base64(text_producer) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_producer)')
NEW = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14_new phpType24_new ABSENT phpType44_new phpType42_new phpType23_new metadata_class_new) phpType6_new metadata_new)) :: ptask_new_tail* '
       '-- if S.CURRENT = (pcallcontext_new) -- if pcallcontext_new.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_new n_arguments pvalue_sent*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver phpType20_name (SEQUENCE phpType7*) metadata_site)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SHIFT)
for label, front in [('producer', PRODUCER), ('new', NEW), ('return', RETURN), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$required203_' + label + '_')
PREFIX += r'''
dec $required203_send_one(ptask) : (porigin, porigin, int, nat)?
def $required203_send_one(CALL_SEND porigin_producer eps 1 ([KNOWN (POBJECT n_old)]) (porigin_site) z) = ((porigin_producer,porigin_site,z,n_old))
def $required203_send_one(ptask) = eps -- otherwise
dec $required203_send(ptask*) : (porigin, porigin, int, nat)?
def $required203_send(eps) = eps
def $required203_send(ptask :: ptask_tail*) = ((porigin_producer,porigin_site,z,n_old))
  -- if $required203_send_one(ptask) = ((porigin_producer,porigin_site,z,n_old))
def $required203_send(ptask :: ptask_tail*) = $required203_send(ptask_tail*)
  -- if $required203_send_one(ptask) = eps
dec $required203_outer_one(ptask) : pmagicmethodcall?
def $required203_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin? z) = (pmagicmethodcall)
def $required203_outer_one(ptask) = eps -- otherwise
dec $required203_outer(ptask*) : pmagicmethodcall?
def $required203_outer(eps) = eps
def $required203_outer(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $required203_outer_one(ptask) = (pmagicmethodcall)
def $required203_outer(ptask :: ptask_tail*) = $required203_outer(ptask_tail*)
  -- if $required203_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    out = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SHIFT,
        'S.FUNCTIONS = [pfunction_producer,pfunction_shift]',
        'pcallcontext_shift.TARGET = pfunction_shift.ORIGIN',
        'pcallcontext_shift.FUNCTION = pfunction_shift.ORIGIN',
        'pcallcontext_shift.ARGC = 0', 'S.FRAMES = [pframe]',
        '$required203_send(pframe.TODO) = ((porigin_producer,porigin_producer_site,z_producer,n_old))',
        'porigin_producer = pfunction_producer.ORIGIN',
        '$required203_outer(pframe.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.NAME = $ptascii("MiSsInG")',
        'pmagicmethodcall.ARGUMENTS = [phpType7_producer,phpType7_later]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer_arg',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer_site)',
        '$origin_node(S.SOURCES,porigin_producer_site) = (expression_producer)',
        '$magic_method_argument_call(expression_producer)',
        '$magic_method_required_producer(S,porigin_producer_site,expression_producer) = (pfunction_producer)',
        '$magic_method_argument_source(S,porigin_producer_site,0,expression_producer)',
        '$magic_method_copy_source(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0)',
        '$magic_method_user_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0) = eps',
        '$magic_method_array_producer(S,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS) = eps',
        '~$magic_unpack_explicit_source(S,porigin_producer_site,expression_producer)',
        '$origin_node(S.SOURCES,pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11_producer (SEQUENCE phpType17*) phpType18_producer (SEQUENCE statement_producer*) metadata_function_producer)',
        'pfunction_producer.SIGNATURE.PARAMETERS = [psparam_saved,psparam_ignored]',
        '$magic_method_required_parameters(phpType17*,[psparam_saved,psparam_ignored])',
        'psparam_saved.NAME = $ptascii("saved")', 'psparam_ignored.NAME = $ptascii("ignored")',
        'psparam_saved.TYPE = eps', 'psparam_saved.REQUIRED', '~psparam_saved.BYREF',
        '~psparam_saved.VARIADIC', 'psparam_saved.DEFAULT = PSNONE',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_old =/= n_new',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$node_children(S,HOBJECT n_old) = eps', '$node_children(S,HOBJECT n_new) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_new) = 1',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$task_nodes(CALL_SEND porigin_producer eps 1 ([KNOWN (POBJECT n_old)]) (porigin_producer_site) z_producer) = [HOBJECT n_old]',
        '$factory182_output(S.EVENTS) = eps',
        '$magic_method_copy_values(S,pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (POBJECT n_old)]) = ([POBJECT n_old])',
        '$magic_method_copy_values(S,pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (PINT 7)]) = ([PINT 7])',
        '$magic_method_copy_values(S[.CODE = eps],pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (POBJECT n_old)]) = eps',
        '$magic_method_copy_values(S[.CODE = eps],pmagicmethodcall.SITE,[phpType7_producer],0,[KNOWN (PINT 7)]) = eps',
        'S_wrong = S[.FUNCTIONS = [pfunction_shift]]',
        '$magic_method_required_producer(S_wrong,porigin_producer_site,expression_producer) = eps',
        'S_ref = S[.FUNCTIONS = [pfunction_producer[.SIGNATURE = pfunction_producer.SIGNATURE[.BYREF = true]],pfunction_shift]]',
        '$magic_method_required_producer(S_ref,porigin_producer_site,expression_producer) = eps',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    for field, value in [('NAME', '$ptascii("wrong")'), ('BYREF', 'true'),
                         ('VARIADIC', 'true'), ('REQUIRED', 'false')]:
        out += ['~$magic_method_required_parameters(phpType17*,[psparam_saved[.' + field + ' = ' + value + '],psparam_ignored])']
    out += [
        '~$magic_method_required_parameters(phpType17*,[psparam_saved])',
        '~$magic_method_required_parameters(phpType17*,[psparam_saved[.DEFAULT = PSDEFAULT ABSENT "unused"],psparam_ignored])',
        'S_producer_found = $required203_producer_seek(S,2048)',
        'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'pcallcontext_producer.TARGET = porigin_producer',
        'pcallcontext_producer.FUNCTION = porigin_producer',
        'pcallcontext_producer.ARGC = 2', 'pcallcontext_producer.RECEIVER = eps',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)',
        '$lookup(S_producer.ENV,$ptascii("ignored")) = (n_ignored)',
        'n_saved =/= n_argument_cell', 'n_saved =/= n_ignored',
        'S_producer.STORE[n_saved] = DEFINED (POBJECT n_old)',
        'S_producer.STORE[n_ignored] = DEFINED PNULL',
        '~(n_saved <- S_producer.REFCELLS)', '~(n_ignored <- S_producer.REFCELLS)',
        'S_producer.STORE[n_argument_cell] = DEFINED (POBJECT n_new)',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_new) = 1',
        '$factory182_output(S_producer.EVENTS) = $ptascii("SHIFT;")',
        '$call_current_valid(S_producer)', '$call_descriptors_valid(S_producer)',
        '$gc_state_valid(S_producer)', '$heap_valid($heap_graph(S_producer))',
        'S_new_found = $required203_new_seek(S_producer,2048)', 'S_new_found.COMPLETION = BUDGET',
        'S_new = S_new_found[.COMPLETION = NORMAL]', NEW.replace('S.', 'S_new.'),
        'pmagicmethodcall_new = pmagicmethodcall',
        'pvalue_sent* = [POBJECT n_old,PFLOAT 4609434218613702656]',
        'S_new.STORE[n_argument_cell] = DEFINED PNULL',
        '~((HCELL n_saved) <- S_new.ALLOCATIONS)', '~((HCELL n_ignored) <- S_new.ALLOCATIONS)',
        '~((HOBJECT n_new) <- S_new.ALLOCATIONS)',
        '$lookup(S_new.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_new.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S_new.ARRAYS[n_arguments] = $magic_method_array(pvalue_sent*,0)',
        '$node_children(S_new,HARRAY n_arguments) = [HOBJECT n_old]',
        '$heap_owners($heap_graph(S_new),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_new),HARRAY n_arguments) = 1',
        '$factory182_output(S_new.EVENTS) = $ptascii("SHIFT;PRODUCER;NEW;HANDLER;")',
        '$call_current_valid(S_new)', '$call_descriptors_valid(S_new)',
        '$gc_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_return_found = $required203_return_seek(S_new,2048)', 'S_return_found.COMPLETION = BUDGET',
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
        '$factory182_output(S_return.EVENTS) = $ptascii("SHIFT;PRODUCER;NEW;HANDLER;OWNER;")',
        'S_split = $drive_steps(S_return,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROWS[CASE]['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_return,4098)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return out


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $required203_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY,
        'S.ORIGIN = (porigin_site)',
        'phpType7* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_required_producer(S,porigin_producer,expression_producer) = (pfunction_producer)',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)', '$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps',
        '$lookup(S.ENV,$base64(text_pack)) = (n_pack_cell)',
        'S.STORE[n_pack_cell] = DEFINED (PARRAY n_pack)',
        '(HARRAY n_pack) <- S.ALLOCATIONS',
        'S.ARRAYS[n_pack] = $array_insert($array_empty(),KINT 0,DIRECT (PINT 9))',
        '~$magic_unpack_arguments(S,porigin_site,phpType7*)',
        '$factory182_output(S.EVENTS) = eps',
        'S_done = $drive_steps(S,2048)',
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
