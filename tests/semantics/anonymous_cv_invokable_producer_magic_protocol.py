#!/usr/bin/env python3
"""Actual invokable CV read, required receipt and ordinary receiver release."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_invokable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_cv_invokable_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-cv-invokable-pending-leaf'
ZERO = 'magic-cv-invokable-family-static'
UNPACK = 'magic-cv-invokable-unpack-refused'
READ = ('S.TODO = (CALL_DYNAMIC porigin_producer z_init z_call) :: ptask_read_tail* '
        '-- if S.CURRENT = eps -- if S.RESULT = VARIABLE ($ptascii("producer")) z_cv '
        '-- if S.ORIGIN = (porigin_producer) -- if $magic_producer_candidate(S,S.TODO,porigin_producer)')
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_producer) metadata_string_producer) :: expression_echo_tail*)) metadata_echo_producer)) :: ptask_producer_tail* '
            '-- if $base64(text_producer) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_producer)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 1 ([KNOWN (PINT 7)]) (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.CURRENT = eps -- if S.RESULT = KNOWN (POBJECT n_sent)')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('producer', PRODUCER), ('send', SEND), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvinvoke213_' + label + '_')
PREFIX += r'''
dec $cvinvoke213_outer_one(ptask) : pmagicmethodcall?
def $cvinvoke213_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PINT 7)]) porigin? z) = (pmagicmethodcall)
def $cvinvoke213_outer_one(ptask) = eps -- otherwise
dec $cvinvoke213_outer(ptask*) : pmagicmethodcall?
def $cvinvoke213_outer(eps) = eps
def $cvinvoke213_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvinvoke213_outer_one(ptask) = (pmagicmethodcall)
def $cvinvoke213_outer(ptask :: ptask_tail*) = $cvinvoke213_outer(ptask_tail*) -- if $cvinvoke213_outer_one(ptask) = eps
dec $cvinvoke213_static_one(ptask) : pmagicstaticmethodcall?
def $cvinvoke213_static_one(CALL_SEND (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) eps 0 eps porigin? z) = (pmagicstaticmethodcall)
def $cvinvoke213_static_one(ptask) = eps -- otherwise
dec $cvinvoke213_static(ptask*) : pmagicstaticmethodcall?
def $cvinvoke213_static(eps) = eps
def $cvinvoke213_static(ptask :: ptask_tail*) = (pmagicstaticmethodcall) -- if $cvinvoke213_static_one(ptask) = (pmagicstaticmethodcall)
def $cvinvoke213_static(ptask :: ptask_tail*) = $cvinvoke213_static(ptask_tail*) -- if $cvinvoke213_static_one(ptask) = eps
'''


def read_start(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READ,
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall (NExprVariable (BYTES text_cv) metadata_cv) (SEQUENCE phpType7_inner*) metadata_call',
        'z_cv = $variable_line(BYTES text_cv,metadata_cv)',
        '$magic_producer_cv_parts(S,porigin_producer,expression_producer) = ((porigin_producer,S.RESULT,$ptascii("__invoke"),phpType7_inner*,phpType7_inner*))',
        '$lookup(S.ENV,$ptascii("producer")) = (n_receiver_cell)', 'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$object_class_origin(S,n_receiver) = (porigin_class)',
        '$magic_producer_selected_source(S,porigin_producer,porigin_class) = (pmethoddesc)',
        '$method_receiver_value_allowed(S,S.RESULT,$ptascii("__invoke"),phpType7_inner*,z_init)',
    ]


def ownership(fixture, filename):
    return read_start(fixture, filename) + [
        '$cvinvoke213_outer(S.TODO) = (pmagicmethodcall_initial)', 'pmagicmethodcall_initial.PRODUCERS = eps',
        '~(n_receiver_cell <- S.REFCELLS)',
        '$call_argument_origin(S,(pmagicmethodcall_initial.SITE),1) = (porigin_producer)',
        '$factory182_output(S.EVENTS) = $ptascii("INSTALL;")',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (FUNCTION_CACHE_INIT (METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN) (CALL_ARGS (METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN) phpType7_inner* 0 eps (porigin_producer) z_call)) :: ptask_selected_tail*',
        '$cvinvoke213_outer(S_selected.TODO) = (pmagicmethodcall)',
        'pmagicproducerfact = {SITE porigin_producer,CLASS porigin_class,METHOD pmethoddesc.FUNCTION.ORIGIN}',
        'pmagicmethodcall = pmagicmethodcall_initial[.PRODUCERS = [pmagicproducerfact]]',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_receiver) = 2',
        'S_producer_found = $cvinvoke213_producer_seek(S_selected,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', PRODUCER.replace('S.', 'S_producer.'),
        'pcallcontext_producer.TARGET = METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN',
        'pcallcontext_producer.INSTANCE = eps', 'pcallcontext_producer.RECEIVER = (n_receiver)',
        '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_receiver) = 1',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("producer")) = eps',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_producer.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_producer.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        '$factory182_output(S_producer.EVENTS) = $ptascii("INSTALL;SHIFT;REPLACEMENT;")',
        'S_send_found = $cvinvoke213_send_seek(S_producer,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'pmagicmethodcall_send = pmagicmethodcall', 'n_sent = n_old',
        '~((HOBJECT n_receiver) <- S_send.ALLOCATIONS)',
        '$lookup(S_send.ENV,$ptascii("producer")) = eps',
        '$magic_producer_selected_source(S_send,porigin_producer,porigin_class) = (pmethoddesc)',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],[pmagicproducerfact]) = ([PINT 7,POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],eps) = eps',
        '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        '$factory182_output(S_send.EVENTS) = $ptascii("INSTALL;SHIFT;REPLACEMENT;PRODUCER;ProducerBase213/ProducerChild213;PROVIDER;")',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 2 ([KNOWN (PINT 7),KNOWN (POBJECT n_old)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_sent_tail*',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1',
        '$call_descriptors_valid(S_sent)', '$gc_state_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
    ]


def zero_receipt(fixture, filename):
    return read_start(fixture, filename) + [
        'phpType7_inner* = eps', '$cvinvoke213_static(S.TODO) = (pmagicstaticmethodcall_initial)',
        'pmagicstaticmethodcall_initial.ARGUMENTS = [phpType7_producer]', 'pmagicstaticmethodcall_initial.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicstaticmethodcall_initial.SITE),0) = (porigin_producer)',
        '$lookup(S.ENV,$ptascii("alias")) = (n_receiver_cell)', 'n_receiver_cell <- S.REFCELLS',
        '$magic_method_value(S,PINT 7)', '$magic_method_value(S,POBJECT n_receiver)',
        '$magic_method_fact_values(S,pmagicstaticmethodcall_initial.SITE,[phpType7_producer],[KNOWN (PINT 7)],eps) = eps',
        '$magic_method_fact_values(S,pmagicstaticmethodcall_initial.SITE,[phpType7_producer],[KNOWN (POBJECT n_receiver)],eps) = eps',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (FUNCTION_CACHE_INIT (METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN) (CALL_ARGS (METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN) eps 0 eps (porigin_producer) z_call)) :: ptask_selected_tail*',
        '$cvinvoke213_static(S_selected.TODO) = (pmagicstaticmethodcall)',
        'pmagicproducerfact = {SITE porigin_producer,CLASS porigin_class,METHOD pmethoddesc.FUNCTION.ORIGIN}',
        'pmagicstaticmethodcall = pmagicstaticmethodcall_initial[.PRODUCERS = [pmagicproducerfact]]',
        '$magic_producer_facts_valid(S_selected,pmagicstaticmethodcall.SITE,[phpType7_producer],[pmagicproducerfact])',
        '$magic_method_fact_values(S_selected,pmagicstaticmethodcall.SITE,[phpType7_producer],[KNOWN (PINT 7)],[pmagicproducerfact]) = ([PINT 7])',
        '$magic_method_fact_values(S_selected,pmagicstaticmethodcall.SITE,[phpType7_producer],[KNOWN (POBJECT n_receiver)],[pmagicproducerfact]) = ([POBJECT n_receiver])',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_receiver) = 2',
        '$call_descriptors_valid(S_selected)', '$gc_state_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $cvinvoke213_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '~$magic_unpack_explicit_source(S,porigin_producer,expression_producer)',
        '$call_argument_origin(S,(porigin_site),1) = (PORIGIN n_unit pcpath_pack)',
        '$code_at(S.CODE,n_unit) = (pcode)', '$source_unit(S.SOURCES,n_unit) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_pack) =/= eps',
        '$lookup(S.ENV,$base64(text_pack)) = (n_pack_cell)', 'S.STORE[n_pack_cell] = DEFINED (PARRAY n_pack)',
        'S.ARRAYS[n_pack] = $array_insert($array_empty(),KINT 0,DIRECT (PINT 9))',
        '~$magic_unpack_arguments(S,porigin_site,phpType7_boundary*)',
        'S_done = $drive_steps(S,2048)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    source = case['source']
    clauses = unpack_boundary(fixture, filename) if source == ROWS[UNPACK]['source'] else zero_receipt(fixture, filename) if source == ROWS[ZERO]['source'] else ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=(CASE, ZERO, UNPACK))
    args = parser.parse_args()
    protocol.run({key: {'source': ROWS[key]['source']} for key in (CASE, ZERO, UNPACK) if not args.case or key in args.case}, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)), fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
