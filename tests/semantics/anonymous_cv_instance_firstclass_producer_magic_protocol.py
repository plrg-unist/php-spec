#!/usr/bin/env python3
"""Actual CV capture, outer receipt and return-old receiver retirement."""
import argparse
import json
import re
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_instance_firstclass_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_cv_instance_firstclass_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-cv-instance-firstclass-pending-leaf'
UNPACK = 'magic-cv-instance-firstclass-unpack-refused'
READ = ('S.TODO = (METHOD_PREP (NIdentifier (BYTES text_method_read) metadata_method_read) phpType7_capture* false false z_read) :: ptask_read_tail* '
        '-- if S.CURRENT = eps -- if S.ORIGIN = (porigin_capture) '
        '-- if $origin_node(S.SOURCES,porigin_capture) = (expression_capture) '
        '-- if expression_capture = NExprMethodCall (NExprVariable (BYTES text_receiver_read) metadata_receiver_read) (NIdentifier (BYTES text_method_read) metadata_method_read) (SEQUENCE phpType7_capture*) metadata_capture '
        '-- if $magic_producer_argument_site(S,porigin_capture) = (porigin_producer) '
        '-- if porigin_producer =/= porigin_capture -- if $magic_producer_candidate(S,S.TODO,porigin_producer)')
PRODUCER = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_producer) metadata_string_producer) :: expression_echo_tail*)) metadata_echo_producer)) :: ptask_producer_tail* '
            '-- if $base64(text_producer) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_producer)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 1 ([KNOWN (PINT 7)]) (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.CURRENT = eps -- if S.RESULT = KNOWN (POBJECT n_sent)')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('producer', PRODUCER), ('send', SEND), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvfcc211_' + label + '_')
PREFIX += r'''
dec $cvfcc211_outer_one(ptask) : pmagicmethodcall?
def $cvfcc211_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PINT 7)]) porigin? z) = (pmagicmethodcall)
def $cvfcc211_outer_one(ptask) = eps -- otherwise
dec $cvfcc211_outer(ptask*) : pmagicmethodcall?
def $cvfcc211_outer(eps) = eps
def $cvfcc211_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $cvfcc211_outer_one(ptask) = (pmagicmethodcall)
def $cvfcc211_outer(ptask :: ptask_tail*) = $cvfcc211_outer(ptask_tail*) -- if $cvfcc211_outer_one(ptask) = eps
'''


def at(front, state):
    return re.sub(r'\bS\b', state, front)


def ownership(fixture, filename):
    # The unchanged210 table/child/full-tail laws are reused after this real SEND.
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_read_found = $factory182_seek(S_initial,2048)', 'S_read_found.COMPLETION = BUDGET',
        'S_read = S_read_found[.COMPLETION = NORMAL]', at(READ, 'S_read'),
        '$base64(text_receiver_read) = $ptascii("producer")',
        'S_read.RESULT = VARIABLE ($base64(text_receiver_read)) $variable_line(BYTES text_receiver_read,metadata_receiver_read)',
        'z_read = $runtime_line(S_read,eps,expression_capture)',
        '$cvfcc211_outer(S_read.TODO) = (pmagicmethodcall_initial)',
        'pmagicmethodcall_initial.PRODUCERS = eps',
        'pmagicmethodcall_initial.ARGUMENTS = [phpType7_install,phpType7_producer]',
        '$call_argument_origin(S_read,(pmagicmethodcall_initial.SITE),1) = (porigin_producer)',
        '$origin_child((porigin_producer),[PCFIELD 0]) = (porigin_capture)',
        '$origin_node(S_read.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_capture (SEQUENCE phpType7_args*) metadata_invocation',
        'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]',
        '$magic_producer_cv_parts(S_read,porigin_producer,expression_producer) = ((porigin_capture,S_read.RESULT,$base64(text_method_read),phpType7_capture*,phpType7_args*))',
        '$magic_method_firstclass_site(S_read,porigin_producer,expression_producer)',
        '$magic_producer_pending(S_read,S_read.TODO,porigin_producer) = ((MAGIC_METHOD_SEND_TARGET pmagicmethodcall_initial,1))',
        '$magic_producer_pending(S_read,S_read.TODO,porigin_capture) = eps',
        '$lookup(S_read.ENV,$ptascii("producer")) = (n_receiver_cell)',
        '~(n_receiver_cell <- S_read.REFCELLS)',
        'S_read.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$magic_producer_cell(S_read,$ptascii("producer")) = (n_receiver)',
        '$object_class_origin(S_read,n_receiver) = (porigin_class)',
        '$magic_producer_selected_source(S_read,porigin_producer,porigin_class) = (pmethoddesc)',
        '$method_receiver_value_allowed(S_read,S_read.RESULT,$base64(text_method_read),phpType7_capture*,z_read)',
        '$heap_owners($heap_graph(S_read),HOBJECT n_receiver) = 1',
        'S_bad = S_read[.TODO = (METHOD_PREP (NIdentifier (BYTES text_method_read) metadata_method_read) phpType7_capture* false false z_read) :: METHOD_RESULT :: (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_initial) eps 1 eps (pmagicmethodcall_initial.SITE) pmagicmethodcall_initial.LINE) :: METHOD_RESULT :: pmagicmethodcall_initial.TAIL]',
        '$magic_method_raw_valid(S_bad[.ORIGIN = (pmagicmethodcall_initial.SITE)],pmagicmethodcall_initial)',
        '$magic_producer_candidate(S_bad,S_bad.TODO,porigin_producer)',
        '$magic_producer_pending(S_bad,S_bad.TODO,porigin_producer) = eps',
        '~$method_receiver_value_allowed(S_bad,S_bad.RESULT,$base64(text_method_read),phpType7_capture*,z_read)',
        'S_bad_selected = $method_selected_metadata(S_bad,METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN,(porigin_capture))',
        'S_bad_selected.COMPLETION = UNSUPPORTED "magic method producer selection fact"',
        'S_bad_selected.TODO = S_bad.TODO',
        '$factory182_output(S_read.EVENTS) = $ptascii("INSTALL;")',
        'S_selected = $drive_steps(S_read,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (METHOD_CONVERT (METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN) porigin_capture z_read) :: ptask_selected_tail*',
        '$cvfcc211_outer(S_selected.TODO) = (pmagicmethodcall)',
        'pmagicproducerfact = {SITE porigin_producer,CLASS porigin_class,METHOD pmethoddesc.FUNCTION.ORIGIN}',
        'pmagicmethodcall = pmagicmethodcall_initial[.PRODUCERS = [pmagicproducerfact]]',
        '$magic_producer_fact_at(pmagicmethodcall.PRODUCERS,porigin_capture) = eps',
        '$magic_producer_facts_valid(S_selected,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,pmagicmethodcall.PRODUCERS)',
        '$heap_owners($heap_graph(S_selected),HOBJECT n_receiver) = 2',
        'n_wrapper = |S_selected.OBJECTS|',
        'S_captured = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_captured.COMPLETION = BUDGET',
        '$object_body(S_captured.OBJECTS[n_wrapper]) = METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN porigin_capture porigin_class pmethodcapture?',
        '$closure_scope_at(S_captured.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = pmethoddesc.OWNER', 'pclosurescope.CALLED = porigin_class',
        'pclosurescope.RECEIVER = (n_receiver)', '$node_children(S_captured,HOBJECT n_wrapper) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_captured),HOBJECT n_receiver) = 2',
        'S_producer_found = $cvfcc211_producer_seek(S_captured,2048)', 'S_producer_found.COMPLETION = BUDGET',
        'S_producer = S_producer_found[.COMPLETION = NORMAL]', at(PRODUCER, 'S_producer'),
        'pcallcontext_producer.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_producer.INSTANCE = (n_wrapper)',
        'pcallcontext_producer.RECEIVER = (n_receiver)', '$call_context_roots(S_producer.CURRENT) = [HOBJECT n_wrapper]',
        'S_producer.FRAMES = [pframe]', '$cvfcc211_outer(pframe.TODO) = (pmagicmethodcall)',
        '$lookup($global_table_view(S_producer).ENV,$ptascii("producer")) = eps',
        '$magic_producer_cell(S_producer,$ptascii("producer")) = eps',
        '$lookup(S_producer.ENV,$ptascii("saved")) = (n_saved)', 'S_producer.STORE[n_saved] = DEFINED (POBJECT n_old)',
        '$heap_owners($heap_graph(S_producer),HOBJECT n_receiver) = 1',
        '$magic_producer_selected_source(S_producer,porigin_producer,porigin_class) = (pmethoddesc)',
        '$factory182_output(S_producer.EVENTS) = $ptascii("INSTALL;SHIFT;REPLACEMENT;")',
        'S_send_found = $cvfcc211_send_seek(S_producer,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'pmagicmethodcall_send = pmagicmethodcall', 'n_sent = n_old', 'porigin_send = pmagicmethodcall.SITE',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_send.ALLOCATIONS)',
        '$lookup(S_send.ENV,$ptascii("producer")) = eps', '$magic_producer_cell(S_send,$ptascii("producer")) = eps',
        '$heap_owners($heap_graph(S_send),HOBJECT n_old) = 1',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],pmagicmethodcall.PRODUCERS) = ([PINT 7,POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7),KNOWN (POBJECT n_old)],eps) = eps',
        '$factory182_output(S_send.EVENTS) = $ptascii("INSTALL;SHIFT;REPLACEMENT;PRODUCER;ProducerBase211/ProducerChild211;PROVIDER;")',
        '$call_descriptors_valid(S_send)', '$closure_state_valid(S_send)', '$gc_state_valid(S_send)', '$heap_valid($heap_graph(S_send))',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 2 ([KNOWN (PINT 7),KNOWN (POBJECT n_old)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_sent_tail*',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_old) = 1',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $cvfcc211_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY,
        'S.ORIGIN = (porigin_site)', 'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
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
    clauses = unpack_boundary(fixture, filename) if case['source'] == ROWS[UNPACK]['source'] else ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + clause + '\n' for clause in clauses), len(clauses)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=(CASE, UNPACK))
    args = parser.parse_args()
    protocol.run({key: {'source': ROWS[key]['source']} for key in (CASE, UNPACK) if not args.case or key in args.case}, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)), fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
