#!/usr/bin/env python3
"""Constructor parameters, ignored returns and authentic NEW-result owners."""
import argparse
import base64
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_constructor_magic_controls.json'
ROWS = {row['id']: row for path in (CATALOGUE, CONTROLS)
        for row in json.loads(path.read_text())['cases']}
CASE = 'magic-constructor-pending-leaf'
UNPACK = 'magic-constructor-zero-unpack-refused'
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_string_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
CTOR = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_ctor) metadata_string_ctor])) metadata_echo_ctor)) :: ptask_ctor_tail* '
        '-- if $base64(text_ctor) = $ptascii("CTOR;") -- if S.CURRENT = (pcallcontext_ctor)')
RESULT = ('S.TODO = (CTOR_RESULT n_result) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (PINT 7) -- if S.CURRENT = eps')
NEW = ('S.TODO = (EVAL (NExprNew (NStmtClass phpType14_new phpType24_new ABSENT phpType44_new phpType42_new phpType23_new metadata_class_new) phpType6_new metadata_new)) :: ptask_new_tail* '
       '-- if S.CURRENT = (pcallcontext_new) -- if pcallcontext_new.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_new n_arguments pvalue_sent*')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver phpType20_name (SEQUENCE phpType7*) metadata_site)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, SHIFT)
for label, front in [('ctor', CTOR), ('result', RESULT), ('new', NEW), ('return', RETURN), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$ctor204_' + label + '_')
PREFIX += r'''
dec $ctor204_send_one(ptask) : (nat, porigin, porigin, int, nat)?
def $ctor204_send_one(CALL_SEND (METHOD_TARGET n_packet porigin_ctor) eps 1 ([KNOWN (POBJECT n_old)]) (porigin_site) z) = ((n_packet,porigin_ctor,porigin_site,z,n_old))
def $ctor204_send_one(ptask) = eps -- otherwise
dec $ctor204_send(ptask*) : (nat, porigin, porigin, int, nat)?
def $ctor204_send(eps) = eps
def $ctor204_send(ptask :: ptask_tail*) = ((n_packet,porigin_ctor,porigin_site,z,n_old))
  -- if $ctor204_send_one(ptask) = ((n_packet,porigin_ctor,porigin_site,z,n_old))
def $ctor204_send(ptask :: ptask_tail*) = $ctor204_send(ptask_tail*)
  -- if $ctor204_send_one(ptask) = eps
dec $ctor204_outer_one(ptask) : pmagicmethodcall?
def $ctor204_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin? z) = (pmagicmethodcall)
def $ctor204_outer_one(ptask) = eps -- otherwise
dec $ctor204_outer(ptask*) : pmagicmethodcall?
def $ctor204_outer(eps) = eps
def $ctor204_outer(ptask :: ptask_tail*) = (pmagicmethodcall)
  -- if $ctor204_outer_one(ptask) = (pmagicmethodcall)
def $ctor204_outer(ptask :: ptask_tail*) = $ctor204_outer(ptask_tail*)
  -- if $ctor204_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', SHIFT,
        'S.FUNCTIONS = [pfunction_shift]',
        'pcallcontext_shift.TARGET = pfunction_shift.ORIGIN',
        'pcallcontext_shift.FUNCTION = pfunction_shift.ORIGIN',
        'S.FRAMES = [pframe]',
        '$ctor204_send(pframe.TODO) = ((n_packet,porigin_ctor,porigin_site,z_ctor,n_old))',
        '$ctor204_outer(pframe.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.ARGUMENTS = [phpType7_ctor,phpType7_later]',
        'phpType7_ctor = NArg ABSENT expression_ctor (BOOLEAN false) (BOOLEAN false) metadata_ctor_arg',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_site)',
        '$origin_node(S.SOURCES,porigin_site) = (expression_ctor)',
        '$magic_method_named_new(expression_ctor)',
        '$magic_method_constructor_producer(S,porigin_site,expression_ctor) = ((porigin_packet,pmethoddesc))',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_ctor',
        '$magic_method_argument_source(S,porigin_site,0,expression_ctor)',
        '$magic_method_no_constructor(S,porigin_site,expression_ctor) = eps',
        '~$magic_unpack_explicit_source(S,porigin_site,expression_ctor)',
        '$object_class_origin(S,n_packet) = (porigin_packet)',
        'S.OBJECTS[n_packet] = INSTANCE porigin_packet',
        '$node_children(S,HOBJECT n_packet) = eps',
        '$target_function(S,METHOD_TARGET n_packet porigin_ctor) = (pmethoddesc.FUNCTION)',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', '~pmethoddesc.STATIC', '~pmethoddesc.ABSTRACT',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = [psparam_saved,psparam_ignored]',
        'psparam_saved.NAME = $ptascii("saved")', 'psparam_ignored.NAME = $ptascii("ignored")',
        'psparam_saved.TYPE = eps', '~psparam_saved.BYREF', 'psparam_saved.REQUIRED',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S.STORE[n_argument_cell] = DEFINED (POBJECT n_replacement)', 'n_old =/= n_replacement',
        '$lookup($global_table_view(S).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_replacement) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_packet) = 2',
        '$heap_owners($heap_graph(S),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$task_nodes(CALL_SEND (METHOD_TARGET n_packet porigin_ctor) eps 1 ([KNOWN (POBJECT n_old)]) (porigin_site) z_ctor) = [HOBJECT n_packet,HOBJECT n_old]',
        '$task_nodes(CTOR_RESULT n_packet) = [HOBJECT n_packet]',
        '$factory182_output(S.EVENTS) = eps',
        '$origin_child((pfunction_shift.ORIGIN),[PCFIELD 5,PCINDEX 1,PCFIELD 0,PCFIELD 1]) = (porigin_legacy)',
        '$origin_node(S.SOURCES,porigin_legacy) = (expression_legacy)',
        '$magic_method_no_constructor(S,porigin_legacy,expression_legacy) = (porigin_replacement)',
        '$magic_method_argument_source(S,porigin_legacy,0,expression_legacy)',
        '$magic_unpack_explicit_source(S,porigin_legacy,expression_legacy)',
        '$object_class_origin(S,n_replacement) = (porigin_replacement)',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_ctor_found = $ctor204_ctor_seek(S,2048)', 'S_ctor_found.COMPLETION = BUDGET',
        'S_ctor = S_ctor_found[.COMPLETION = NORMAL]', CTOR.replace('S.', 'S_ctor.'),
        'pcallcontext_ctor.TARGET = METHOD_TARGET n_packet porigin_ctor',
        'pcallcontext_ctor.FUNCTION = porigin_ctor', 'pcallcontext_ctor.ARGC = 2',
        'pcallcontext_ctor.RECEIVER = (n_packet)',
        'pcallcontext_ctor.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_ctor.CALLED_CLASS = (porigin_packet)',
        '$lookup(S_ctor.ENV,$ptascii("saved")) = (n_saved)',
        '$lookup(S_ctor.ENV,$ptascii("ignored")) = (n_ignored)',
        'n_saved =/= n_argument_cell',
        'S_ctor.STORE[n_saved] = DEFINED (POBJECT n_old)',
        'S_ctor.STORE[n_ignored] = DEFINED PNULL',
        '~(n_saved <- S_ctor.REFCELLS)', '~(n_ignored <- S_ctor.REFCELLS)',
        '$objectprops_at(S_ctor.OBJECTPROPS,n_packet) = (ppropertyslot_ctor*)',
        '$property_slot_at(ppropertyslot_ctor*,$ptascii("saved")) = (ppropertyslot_saved)',
        'ppropertyslot_saved.STATE = PROP_VALUE (DIRECT (PINT 7))',
        '$factory182_output(S_ctor.EVENTS) = $ptascii("SHIFT;")',
        '$call_current_valid(S_ctor)', '$call_descriptors_valid(S_ctor)',
        '$gc_state_valid(S_ctor)', '$heap_valid($heap_graph(S_ctor))',
        'S_result_found = $ctor204_result_seek(S_ctor,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'n_result = n_packet', 'S_result.ORIGIN = (porigin_site)',
        '$ctor_result_valid(S_result,n_packet)',
        '~((HCELL n_saved) <- S_result.ALLOCATIONS)', '~((HCELL n_ignored) <- S_result.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_result.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_result),HOBJECT n_packet) = 1',
        '$factory182_output(S_result.EVENTS) = $ptascii("SHIFT;CTOR;OLD;")',
        'S_instance = $drive_steps(S_result,1)', 'S_instance.COMPLETION = BUDGET',
        'S_instance.RESULT = KNOWN (POBJECT n_packet)',
        'S_instance.TODO = ptask_result_tail*',
        '$heap_owners($heap_graph(S_instance),HOBJECT n_packet) = 1',
        '$magic_method_copy_values(S_instance,pmagicmethodcall.SITE,[phpType7_ctor],0,[KNOWN (POBJECT n_packet)]) = ([POBJECT n_packet])',
        '$magic_method_value(S_instance,PINT 7)',
        '$magic_method_copy_values(S_instance,pmagicmethodcall.SITE,[phpType7_ctor],0,[KNOWN (PINT 7)]) = eps',
        '$magic_method_value(S_instance,POBJECT n_replacement)',
        '$magic_method_copy_values(S_instance,pmagicmethodcall.SITE,[phpType7_ctor],0,[KNOWN (POBJECT n_replacement)]) = eps',
        '$magic_method_copy_values(S_instance[.CODE = eps],pmagicmethodcall.SITE,[phpType7_ctor],0,[KNOWN (POBJECT n_packet)]) = eps',
        '$magic_method_copy_values(S_instance[.CODE = eps],pmagicmethodcall.SITE,[phpType7_ctor],0,[KNOWN (PINT 7)]) = eps',
        '$magic_method_copy_values(S_instance[.CODE = eps],pmagicmethodcall.SITE,[phpType7_ctor],0,[KNOWN (POBJECT n_replacement)]) = eps',
        '$call_descriptors_valid(S_instance)', '$gc_state_valid(S_instance)', '$heap_valid($heap_graph(S_instance))',
        'S_new_found = $ctor204_new_seek(S_instance[.COMPLETION = NORMAL],2048)',
        'S_new_found.COMPLETION = BUDGET', 'S_new = S_new_found[.COMPLETION = NORMAL]', NEW.replace('S.', 'S_new.'),
        'pmagicmethodcall_new = pmagicmethodcall', 'pvalue_sent* = [POBJECT n_packet,PNULL]',
        'S_new.STORE[n_argument_cell] = DEFINED PNULL',
        '~((HOBJECT n_replacement) <- S_new.ALLOCATIONS)',
        '$lookup(S_new.ENV,$ptascii("arguments")) = (n_arguments_cell)',
        'S_new.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)',
        'S_new.ARRAYS[n_arguments] = $magic_method_array(pvalue_sent*,0)',
        '$node_children(S_new,HARRAY n_arguments) = [HOBJECT n_packet]',
        '$node_children(S_new,HOBJECT n_packet) = eps',
        '$heap_owners($heap_graph(S_new),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_new),HARRAY n_arguments) = 1',
        '$factory182_output(S_new.EVENTS) = $ptascii("SHIFT;CTOR;OLD;NEW;HANDLER;")',
        '$call_current_valid(S_new)', '$call_descriptors_valid(S_new)',
        '$gc_state_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_return_found = $ctor204_return_seek(S_new,2048)', 'S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_return.'),
        '$lookup(S_return.ENV,$ptascii("child")) = (n_child_cell)',
        'S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
        '$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot_child*)',
        '$property_slot_at(ppropertyslot_child*,$ptascii("saved")) = (ppropertyslot_child_saved)',
        'ppropertyslot_child_saved.STATE = PROP_VALUE (DIRECT (PARRAY n_arguments))',
        '$node_children(S_return,HOBJECT n_child) = [HARRAY n_arguments]',
        '$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1',
        '$heap_owners($heap_graph(S_return),HARRAY n_arguments) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_packet) = 1',
        '~((HOBJECT pmagicmethodcall.OBJECT) <- S_return.ALLOCATIONS)',
        '$factory182_output(S_return.EVENTS) = $ptascii("SHIFT;CTOR;OLD;NEW;HANDLER;OWNER;")',
        'S_split = $drive_steps(S_return,2)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL],4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$factory182_output(S_done.EVENTS) = ' + names.template(base64.b64decode(ROWS[CASE]['stdout_template_base64']), filename),
        'S_full = $drive_steps(S_return,4098)', 'S_full = S_done',
        '~((HOBJECT n_child) <- S_done.ALLOCATIONS)', '~((HARRAY n_arguments) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_packet) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', '~((HOBJECT n_replacement) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
        '$gc_state_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $ctor204_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY,
        'S.ORIGIN = (porigin_site)', 'phpType7* = [phpType7_ctor,phpType7_pack]',
        'phpType7_ctor = NArg ABSENT expression_ctor (BOOLEAN false) (BOOLEAN false) metadata_ctor',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_ctor)',
        'expression_ctor = NExprNew (NName (BYTES text_class) metadata_class) (SEQUENCE eps) metadata_new',
        '$magic_method_constructor_producer(S,porigin_ctor,expression_ctor) = ((porigin_class,pmethoddesc))',
        'pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS = eps',
        '$magic_method_argument_source(S,porigin_ctor,0,expression_ctor)',
        '$magic_method_no_constructor(S,porigin_ctor,expression_ctor) = eps',
        '~$magic_unpack_explicit_source(S,porigin_ctor,expression_ctor)',
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
