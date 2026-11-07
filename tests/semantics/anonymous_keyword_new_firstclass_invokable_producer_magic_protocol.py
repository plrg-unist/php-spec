#!/usr/bin/env python3
"""Implicit keyword-New FCC selection and real wrapper-to-result ownership."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_firstclass_method_producer_magic_protocol as methods
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_firstclass_invokable_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-fcc-invokable-return-this'
CAPTURE = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init z_capture) :: ptask_capture_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_packet) -- if S.CURRENT = (pcallcontext_caller)')
PREFIX = methods.PREFIX.replace(methods.CONVERT, CAPTURE).replace('"METHOD;"', '"INVOKE;"')
BODY = methods.BODY.replace('"METHOD;"', '"INVOKE;"')


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CAPTURE,
        '$newfcc235_outer(ptask_capture_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase237")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope237")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild237")) = (porigin_allocated)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)', 'porigin_scope =/= porigin_allocated',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall (NExprFuncCall expression_new (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture) (SEQUENCE phpType7_real*) metadata_producer',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        'porigin_capture = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        'porigin_new = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0])',
        'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
        '$magic_method_keyword_new_invokable_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_keyword_new_invokable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$effective_method(S,porigin_allocated,$ptascii("__invoke"),|S.CLASSES|) = (pmethoddesc)',
        '$object_invoke_method(S,n_packet) = (pmethoddesc)',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base',
        '$magic_method_instance_source_body(S,pmethoddesc,phpType7_real*)',
        '~$magic_method_instance_source_body(S,pmethoddesc,[NVariadicPlaceholder metadata_placeholder])',
        '$magic_method_firstclass_producer(S,porigin_producer,expression_producer) = eps',
        '$magic_method_invokable_producer(S,porigin_producer,expression_producer) = eps',
        '~$magic_method_invokable_call(expression_producer)',
        '$magic_method_keyword_new_invokable_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S,(pcallcontext_caller[.FUNCTION = porigin_method]),porigin_producer,expression_producer) = eps',
    ]
    for path in ('pcpath_producer', 'pcpath_producer ++ [PCFIELD 0]', 'pcpath_producer ++ [PCFIELD 0,PCFIELD 0]'):
        checks.append('$magic_method_keyword_new_invokable_producer(S[.CODE = [pcode[.EXPRESSIONS = $newfcc235_without_init(pcode.EXPRESSIONS,' + path + ')]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps')
    checks += [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
        'S_convert = S_one[.COMPLETION = NORMAL]',
        'S_convert.TODO = (METHOD_CONVERT (METHOD_TARGET n_packet porigin_method) porigin_capture z_capture) :: ptask_capture_tail*',
        '$method_capture_current(S_convert,porigin_capture) = eps',
        '$call_selected_valid(S_convert,METHOD_TARGET n_packet porigin_method,(porigin_capture))',
        '$heap_owners($heap_graph(S_convert),HOBJECT n_packet) = 1',
        'n_wrapper = |S_convert.OBJECTS|',
        'S_captured = $drive_steps(S_convert,1)', 'S_captured.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_captured',
        'S_captured.OBJECTS = S_convert.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_allocated eps]',
        'S_captured.RESULT = KNOWN (POBJECT n_wrapper)', 'S_captured.BASE = BASE_VALUE (KNOWN PNULL)',
        '$closure_scope_at(S_captured.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_base', 'pclosurescope.CALLED = porigin_allocated',
        'pclosurescope.RECEIVER = (n_packet)', 'pclosurescope.CREATION = eps',
        '$node_children(S_captured,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_captured),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_captured),HOBJECT n_wrapper) = 1',
        '$closure_state_valid(S_captured)', '$heap_valid($heap_graph(S_captured))',
        'S_shift_found = $newfcc235_shift_seek(S_captured[.COMPLETION = NORMAL],2048)',
        'S_shift_found.COMPLETION = BUDGET', 'S_shift = S_shift_found[.COMPLETION = NORMAL]', methods.at(methods.SHIFT, 'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_keyword_new_invokable_producer(S_shift,S_shift.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S_shift,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'S_body_found = $newfcc235_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', methods.at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper',
        'pcallcontext_body.INSTANCE = (n_wrapper)', 'pcallcontext_body.RECEIVER = (n_packet)',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_base)', 'pcallcontext_body.CALLED_CLASS = (porigin_allocated)',
        '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$node_children(S_body,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_body),HOBJECT n_wrapper) = 1',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)',
        'S_send_found = $newfcc235_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', methods.at(methods.SEND, 'S_send'),
        'n_send = n_packet', 'pmagicmethodcall_send = pmagicmethodcall',
        'pcallcontext_send = pcallcontext_caller',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)', '(HOBJECT n_packet) <- S_send.ALLOCATIONS',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_send),HOBJECT n_packet) = 1',
        '$heap_count(HOBJECT n_packet,$operand_nodes(S_send.RESULT)) = 1',
        '$heap_count(HOBJECT n_packet,$machine_base_roots(S_send)) = 0',
        '$heap_count(HOBJECT n_packet,$call_context_roots(S_send.CURRENT)) = 0',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = ([POBJECT n_packet])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = eps',
        '$factory182_output(S_send.EVENTS) = $ptascii("CTOR;SHIFT;INVOKE;")',
        '$call_descriptors_valid(S_send)', '$heap_valid($heap_graph(S_send))',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.RESULT = KNOWN PNULL', 'S_sent.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_sent),HOBJECT n_packet) = 1',
        '$heap_count(HOBJECT n_packet,$tasks_nodes(S_sent.TODO)) = 1',
        '$call_descriptors_valid(S_sent)', '$heap_valid($heap_graph(S_sent))',
    ]
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + condition + '\n' for condition in checks), len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    args = parser.parse_args()
    protocol.run({CASE: {'source': ROWS[CASE]['source']}},
                 extra_inputs=(CATALOGUE, Path(__file__), Path(methods.__file__), methods.CATALOGUE, Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
