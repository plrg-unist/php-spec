#!/usr/bin/env python3
"""Keyword-New array FCC preserves real capture and wrapper ownership through SEND."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_invokable_producer_magic_protocol as direct
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_array_firstclass_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-array-firstclass-return-this'
CONVERT = ('S.TODO = (ARRAY_CONVERT pcalltarget_capture parrayselection_capture) :: ptask_convert_tail* '
           '-- if S.CURRENT = (pcallcontext_caller)')
BODY = direct.BODY.replace('INVOKE;', 'CAPTURE;')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PREFIX = direct.PREFIX.replace(direct.DYNAMIC, CONVERT).replace('INVOKE;', 'CAPTURE;')
PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, READY).replace('$factory182_', '$arrayfcc241_ready_')


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CONVERT,
        'pcalltarget_capture = METHOD_TARGET n_packet porigin_method',
        '$newinvoke236_outer(ptask_convert_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase241")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope241")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild241")) = (porigin_allocated)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)', 'porigin_scope =/= porigin_allocated',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_producer',
        'expression_capture = NExprFuncCall expression_callback (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_new (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
        'expression_method = NScalarString phpType33 metadata_literal',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        'porigin_capture = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        'parrayselection_capture.SITE = porigin_capture',
        'parrayselection_capture.REQUESTED = porigin_allocated',
        'parrayselection_capture.NAME = $ptascii("capture")',
        'pcpath_new = pcpath_producer ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0,PCINDEX 0,PCFIELD 1]',
        'porigin_new = PORIGIN n_unit pcpath_new',
        '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
        '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0,PCINDEX 1,PCFIELD 1])) = (expression_method)',
        '$magic_method_literal_value(S,PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0,PCINDEX 1,PCFIELD 1]),expression_method) = (pvalue_method)',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (parrayselection_capture.INIT)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = ((parrayselection_capture.LINE,b_capture))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_new) = (z_new)',
        '$magic_method_keyword_new_array_firstclass_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '~$magic_method_keyword_new_array_call(expression_producer)',
        '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
        '$magic_method_keyword_new_array_firstclass_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$method_class_selected(S,porigin_allocated,$ptascii("capture"),(porigin_scope)) = (pmethoddesc)',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC', r'~pmethoddesc.STATIC /\ ~pmethoddesc.ABSTRACT',
        '$magic_method_instance_source_body(S,pmethoddesc,phpType7_real*)',
        '$magic_method_fresh_method_source(S,porigin_allocated,porigin_capture,$ptascii("capture"),phpType7_real*) = (pmethoddesc)',
        '$magic_method_keyword_new_array_firstclass_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S,(pcallcontext_caller[.FUNCTION = porigin_method]),porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S,pmagicmethodcall.CALLER,porigin_new,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_new)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S[.CODE = [pcode[.EXPRESSIONS = $newinvoke236_without_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0])]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_firstclass_producer(S,porigin_producer,expression_producer) = eps',
        '~$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        '$array_convert_valid(S,pcalltarget_capture,parrayselection_capture)',
        '$target_receiver(S,pcalltarget_capture) = (n_packet)',
        '$target_lexical_class(S,pcalltarget_capture) = (porigin_base)',
        '$target_called_class(S,pcalltarget_capture) = (porigin_allocated)',
        '$task_nodes(S.TODO[0]) = [HOBJECT n_packet]',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS[n_wrapper] = ARRAYMETHODCLOSURE pcalltarget_capture parrayselection_capture pmethodcapture?',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [ARRAYMETHODCLOSURE pcalltarget_capture parrayselection_capture pmethodcapture?]',
        'pmethodcapture? = $method_capture_current(S,porigin_capture)',
        '$method_capture_certificate_valid(S_wrapped,porigin_capture,pmethodcapture?)',
        'S_wrapped.RESULT = KNOWN (POBJECT n_wrapper)', 'S_wrapped.BASE = BASE_VALUE (KNOWN PNULL)',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_base', 'pclosurescope.CALLED = porigin_allocated',
        'pclosurescope.RECEIVER = (n_packet)', 'pclosurescope.CREATION = eps',
        '$closure_scope_row_valid(S_wrapped,pclosurescope)',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_wrapper) = 1',
        'S_ready = $arrayfcc241_ready_seek(S_wrapped,2048)', 'S_ready.COMPLETION = BUDGET',
        direct.at(READY, 'S_ready'), 'n_wrapper_ready = n_wrapper',
        'phpType7_ready* = phpType7_real*', 'porigin_ready = porigin_producer',
        'pcallcontext_ready = pcallcontext_caller',
        'S_direct = $arrayfcc241_ready_seek(S,2048)', 'S_direct = S_ready',
        'pcalltarget = CLOSURE_TARGET n_wrapper',
        '$target_instance(pcalltarget) = (n_wrapper)',
        '$target_receiver(S_ready,pcalltarget) = (n_packet)',
        '$target_lexical_class(S_ready,pcalltarget) = (porigin_base)',
        '$target_called_class(S_ready,pcalltarget) = (porigin_allocated)',
        '$target_function(S_ready,pcalltarget) = (pmethoddesc.FUNCTION)',
        '$call_selected_valid(S_ready,pcalltarget,(porigin_producer))',
        '$task_nodes(S_ready.TODO[0]) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))',
        'S_shift_found = $newinvoke236_shift_seek(S_ready[.COMPLETION = NORMAL],2048)',
        'S_shift_found.COMPLETION = BUDGET',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]', direct.at(direct.SHIFT, 'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_keyword_new_array_firstclass_producer(S_shift,S_shift.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S_shift,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'S_body_found = $newinvoke236_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', direct.at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = pcalltarget',
        'pcallcontext_body.INSTANCE = (n_wrapper)', 'pcallcontext_body.RECEIVER = (n_packet)',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_body.CALLED_CLASS = (porigin_allocated)',
        '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1',
        '$magic_method_keyword_new_array_firstclass_producer(S_body,S_body.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_firstclass_producer(S_body,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)',
        'S_send_found = $newinvoke236_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', direct.at(direct.SEND, 'S_send'),
        'n_send = n_packet', 'pmagicmethodcall_send = pmagicmethodcall',
        'pcallcontext_send = pcallcontext_caller', 'porigin_send = pmagicmethodcall.SITE',
        'z_send = pmagicmethodcall.LINE', '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)', 'S_send.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_send),HOBJECT n_packet) = 1',
        '$heap_count(HOBJECT n_packet,$operand_nodes(S_send.RESULT)) = 1',
        '$heap_count(HOBJECT n_packet,$machine_base_roots(S_send)) = 0',
        '$heap_count(HOBJECT n_packet,$call_context_roots(S_send.CURRENT)) = 0',
        '$heap_count(HOBJECT n_packet,$frames_roots(S_send.FRAMES)) = 0',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = ([POBJECT n_packet])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = eps',
        '$factory182_output(S_send.EVENTS) = $ptascii("CTOR;SHIFT;CAPTURE;")',
        '$call_descriptors_valid(S_send)', '$heap_valid($heap_graph(S_send))',
        'S_sent = $drive_steps(S_send,1)', 'S_sent.COMPLETION = BUDGET',
        'S_sent.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (POBJECT n_packet)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: ptask_send_tail*',
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
    protocol.run({CASE: {'source': ROWS[CASE]['source']}}, extra_inputs=(CATALOGUE, Path(__file__), Path(direct.__file__), Path(names.__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
