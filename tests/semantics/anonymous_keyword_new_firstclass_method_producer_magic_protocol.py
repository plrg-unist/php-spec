#!/usr/bin/env python3
"""Keyword-New FCC sites, saved caller scope, wrapper roots and real SEND."""
import argparse
import json
from pathlib import Path

import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_firstclass_method_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-fcc-return-this'
CONVERT = ('S.TODO = (METHOD_CONVERT (METHOD_TARGET n_packet porigin_method) porigin_capture z_capture) :: ptask_capture_tail* '
           '-- if S.CURRENT = (pcallcontext_caller) -- if S.ORIGIN = (porigin_capture)')
SHIFT = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_shift) metadata_shift])) metadata_echo_shift)) :: ptask_shift_tail* '
         '-- if $base64(text_shift) = $ptascii("SHIFT;") -- if S.CURRENT = (pcallcontext_shift)')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_body) metadata_body])) metadata_echo_body)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("METHOD;") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_send) -- if S.CURRENT = (pcallcontext_send)')
PREFIX = names.PREFIX.replace(names.FRONT, CONVERT)
for label, front in [('shift', SHIFT), ('body', BODY), ('send', SEND)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$newfcc235_' + label + '_')
PREFIX += r'''
dec $newfcc235_outer_one(ptask) : pmagicmethodcall?
def $newfcc235_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $newfcc235_outer_one(ptask) = eps -- otherwise
dec $newfcc235_outer(ptask*) : pmagicmethodcall?
def $newfcc235_outer(eps) = eps
def $newfcc235_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $newfcc235_outer_one(ptask) = (pmagicmethodcall)
def $newfcc235_outer(ptask :: ptask_tail*) = $newfcc235_outer(ptask_tail*) -- if $newfcc235_outer_one(ptask) = eps
dec $newfcc235_init_at(pcodeexpr, pcpath) : bool
def $newfcc235_init_at(CODECALL_INIT pcpath z, pcpath) = true
def $newfcc235_init_at(pcodeexpr, pcpath) = false -- otherwise
dec $newfcc235_without_init(pcodeexpr*, pcpath) : pcodeexpr*
def $newfcc235_without_init(eps, pcpath) = eps
def $newfcc235_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = $newfcc235_without_init(pcodeexpr_tail*, pcpath) -- if $newfcc235_init_at(pcodeexpr, pcpath)
def $newfcc235_without_init(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $newfcc235_without_init(pcodeexpr_tail*, pcpath) -- if ~$newfcc235_init_at(pcodeexpr, pcpath)
'''


def at(front, state):
    return front.replace('S.', state + '.')


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CONVERT,
        '$newfcc235_outer(ptask_capture_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase235")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope235")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild235")) = (porigin_allocated)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)', 'porigin_scope =/= porigin_allocated',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall (NExprMethodCall expression_receiver (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE ([(NVariadicPlaceholder metadata_placeholder)])) metadata_capture) (SEQUENCE phpType7_method*) metadata_producer',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        'porigin_capture = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        'porigin_receiver = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_receiver) = (expression_receiver)',
        '$ordinary_keyword_new_site(S,porigin_receiver)',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = (z_capture)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0,PCFIELD 0]) = (z_new)',
        '$magic_method_firstclass_site(S,porigin_producer,expression_producer)',
        '$magic_method_keyword_new_method_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_keyword_new_method_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'pmethoddesc.FUNCTION.ORIGIN = porigin_method', 'pmethoddesc.OWNER = porigin_base', '~pmethoddesc.STATIC',
        '$magic_method_firstclass_producer(S,porigin_producer,expression_producer) = eps',
        '$magic_method_instance_producer(S,porigin_producer,expression_producer) = eps',
        '~$magic_producer_cv_source(S,porigin_producer,expression_producer)',
        '~$magic_producer_candidate(S,S.TODO,porigin_producer)',
        '$magic_method_keyword_new_method_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S,(pcallcontext_caller[.FUNCTION = porigin_method]),porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S[.CODE = [pcode[.EXPRESSIONS = $newfcc235_without_init(pcode.EXPRESSIONS,pcpath_producer)]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S[.CODE = [pcode[.EXPRESSIONS = $newfcc235_without_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0])]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S[.CODE = [pcode[.EXPRESSIONS = $newfcc235_without_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0,PCFIELD 0])]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$call_task_valid(S,METHOD_CONVERT (METHOD_TARGET n_packet porigin_method) porigin_capture z_capture)',
        '$heap_owners($heap_graph(S),HOBJECT n_packet) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'n_wrapper = |S.OBJECTS|',
        'S_captured = $drive_steps(S,1)', 'S_captured.COMPLETION = BUDGET',
        'S_captured.RESULT = KNOWN (POBJECT n_wrapper)',
        'S_captured.BASE = BASE_VALUE (KNOWN PNULL)',
        '$object_body(S_captured.OBJECTS[n_wrapper]) = METHODCLOSURE porigin_method porigin_capture porigin_allocated pmethodcapture?',
        '$closure_scope_at(S_captured.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_base', 'pclosurescope.CALLED = porigin_allocated',
        'pclosurescope.RECEIVER = (n_packet)',
        '$node_children(S_captured,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_captured),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_captured),HOBJECT n_wrapper) = 1',
        '$call_descriptors_valid(S_captured)', '$closure_state_valid(S_captured)', '$heap_valid($heap_graph(S_captured))',
        'S_shift_found = $newfcc235_shift_seek(S_captured[.COMPLETION = NORMAL],2047)',
        'S_shift_found.COMPLETION = BUDGET',
        'S_shift_direct = $newfcc235_shift_seek(S,2048)', 'S_shift_direct = S_shift_found',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]', at(SHIFT, 'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        '$node_children(S_shift,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_keyword_new_method_producer(S_shift,S_shift.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S_shift,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        'S_body_found = $newfcc235_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', at(BODY, 'S_body'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper',
        'pcallcontext_body.INSTANCE = (n_wrapper)', 'pcallcontext_body.RECEIVER = (n_packet)',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_body.CALLED_CLASS = (porigin_allocated)',
        '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$node_children(S_body,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_body),HOBJECT n_wrapper) = 1',
        '$magic_method_keyword_new_method_producer(S_body,S_body.CURRENT,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_method_producer(S_body,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)',
        'S_send_found = $newfcc235_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', at(SEND, 'S_send'),
        'n_send = n_packet', 'pmagicmethodcall_send = pmagicmethodcall',
        'pcallcontext_send = pcallcontext_caller', 'porigin_send = pmagicmethodcall.SITE',
        'z_send = pmagicmethodcall.LINE',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)',
        '(HOBJECT n_packet) <- S_send.ALLOCATIONS',
        'S_send.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_send),HOBJECT n_packet) = 1',
        '$heap_count(HOBJECT n_packet,$operand_nodes(S_send.RESULT)) = 1',
        '$heap_count(HOBJECT n_packet,$machine_base_roots(S_send)) = 0',
        '$heap_count(HOBJECT n_packet,$call_context_roots(S_send.CURRENT)) = 0',
        '$heap_count(HOBJECT n_packet,$frames_roots(S_send.FRAMES)) = 0',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = ([POBJECT n_packet])',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_packet)],eps) = eps',
        '$factory182_output(S_send.EVENTS) = $ptascii("CTOR;SHIFT;METHOD;")',
        '$call_descriptors_valid(S_send)', '$closure_state_valid(S_send)', '$heap_valid($heap_graph(S_send))',
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
    protocol.run({CASE: {'source': ROWS[CASE]['source']}}, extra_inputs=(CATALOGUE, Path(__file__)),
                 fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
