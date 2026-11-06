#!/usr/bin/env python3
"""Ordinary invokable receiver release and exact new-call source boundaries."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_invokable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_invokable_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-invokable-pending-leaf'
UNPACK = 'magic-invokable-unpack-refused'
ANONYMOUS = 'magic-invokable-anonymous-new-refused'
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_producer) metadata_string_producer) :: expression_echo_tail*)) metadata_echo_producer)) :: ptask_producer_tail* '
            '-- if $base64(text_producer) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_producer)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) phpType7_remaining* 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.CURRENT = eps -- if S.RESULT = KNOWN (POBJECT n_sent)')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, PRODUCER)
for label, front in [('send', SEND), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$invoke212_' + label + '_')
PREFIX += r'''
dec $invoke212_outer_one(ptask) : pmagicmethodcall?
def $invoke212_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin? z) = (pmagicmethodcall)
def $invoke212_outer_one(ptask) = eps -- otherwise
dec $invoke212_outer(ptask*) : pmagicmethodcall?
def $invoke212_outer(eps) = eps
def $invoke212_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $invoke212_outer_one(ptask) = (pmagicmethodcall)
def $invoke212_outer(ptask :: ptask_tail*) = $invoke212_outer(ptask_tail*) -- if $invoke212_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    # Independent129 covers actual lookup/cache/argument order and returnThis.
    # Stop at this return-old SEND; existing generic table/child laws are reused.
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', PRODUCER,
        'pcallcontext_producer.TARGET = METHOD_TARGET n_receiver porigin_method',
        'pcallcontext_producer.INSTANCE = eps', 'pcallcontext_producer.RECEIVER = (n_receiver)',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        'S.FRAMES = [pframe]', '$invoke212_outer(pframe.TODO) = (pmagicmethodcall)',
        'pmagicmethodcall.PRODUCERS = eps',
        'pmagicmethodcall.ARGUMENTS = [phpType7_producer,phpType7_later]',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        '$magic_method_invokable_producer(S,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_method', 'pmethoddesc.OWNER =/= porigin_class',
        '$object_class_origin(S,n_receiver) = (porigin_class)',
        '$object_invoke_method(S,n_receiver) = (pmethoddesc)',
        'expression_producer = NExprFuncCall expression_new (SEQUENCE ([phpType7_arg0,phpType7_arg1])) metadata_invoke',
        '~$magic_method_plain_instance_source(S,pmethoddesc,[phpType7_arg0,phpType7_arg1])',
        '$lookup(S.ENV,$ptascii("saved")) = (n_saved_cell)', 'S.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        '$object_class_origin(S,n_old) = (porigin_old)', 'porigin_old =/= porigin_class',
        '$factory182_output(S.EVENTS) = $ptascii("SHIFT;")',
        'S_send_found = $invoke212_send_seek(S,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'pmagicmethodcall_send = pmagicmethodcall', 'n_sent = n_old', 'porigin_send = pmagicmethodcall.SITE',
        '~((HOBJECT n_receiver) <- S_send.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        '$magic_method_invokable_producer(S_send,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
        '$magic_method_collected_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS[0:1],[KNOWN (POBJECT n_old)]) = ([POBJECT n_old])',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;PRODUCER;ProducerBase212/ProducerChild212;PROVIDER;")',
        '$call_descriptors_valid(S_send)', '$gc_state_valid(S_send)', '$heap_valid($heap_graph(S_send))',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) ([phpType7_later]) 1 ([KNOWN (POBJECT n_old)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_sent_tail*',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1',
    ]


def boundary_start(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $invoke212_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY,
        'S.ORIGIN = (porigin_site)', 'phpType7_boundary* = [phpType7_producer,phpType7_later]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
    ]


def unpack_boundary(fixture, filename):
    return boundary_start(fixture, filename) + [
        'phpType7_later = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$magic_method_invokable_producer(S,porigin_producer,expression_producer) = ((porigin_class,pmethoddesc))',
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


def anonymous_boundary(fixture, filename):
    return boundary_start(fixture, filename) + [
        'expression_producer = NExprFuncCall (NExprNew (NStmtClass phpType14_anon phpType24_anon ABSENT phpType44_anon phpType42_anon phpType23_anon metadata_anon) phpType6_ctor metadata_new) (SEQUENCE phpType7_inner*) metadata_call',
        '$magic_method_invokable_call(expression_producer)',
        '$magic_method_invokable_producer(S,porigin_producer,expression_producer) = eps',
        '~$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
        '$magic_method_value(S,PINT 7)',
        '$lookup(S.ENV,$ptascii("owner")) = (n_owner_cell)', 'S.STORE[n_owner_cell] = DEFINED (POBJECT n_owner)',
        '$magic_method_value(S,POBJECT n_owner)',
        '$magic_method_collected_values(S,porigin_site,phpType7_boundary*[0:1],[KNOWN (PINT 7)]) = eps',
        '$magic_method_collected_values(S,porigin_site,phpType7_boundary*[0:1],[KNOWN (POBJECT n_owner)]) = eps',
        'S_done = $drive_steps(S,2048)', 'S_done.COMPLETION = UNSUPPORTED "magic method source or argument mode"',
        '$factory182_output(S_done.EVENTS) = eps',
    ]


def render(case, fixture, filename):
    source = case['source']
    clauses = unpack_boundary(fixture, filename) if source == ROWS[UNPACK]['source'] else anonymous_boundary(fixture, filename) if source == ROWS[ANONYMOUS]['source'] else ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=(CASE, UNPACK, ANONYMOUS))
    args = parser.parse_args()
    protocol.run({key: {'source': ROWS[key]['source']} for key in (CASE, UNPACK, ANONYMOUS) if not args.case or key in args.case}, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)), fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
