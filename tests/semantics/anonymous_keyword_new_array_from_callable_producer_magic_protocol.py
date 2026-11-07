#!/usr/bin/env python3
"""Keyword-New method arrays transfer the receiver before real invocation args."""
import argparse
import json
from pathlib import Path

import anonymous_keyword_new_firstclass_invokable_producer_magic_protocol as fcc
import anonymous_keyword_new_firstclass_method_producer_magic_protocol as methods
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_new_array_from_callable_producer_magic_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())['cases']}
CASE = 'magic-keyword-new-array-from-callable-return-this'
FACTORY = ('S.TODO = (API_CALLABLE_RESULT papiquery 0) :: ptask_factory_tail* '
           '-- if papiquery.SOURCE = CONFIG_INVOKE pconfigcall '
           '-- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE -- if S.CURRENT = (pcallcontext_caller)')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
PREFIX = fcc.PREFIX.replace(fcc.CAPTURE, FACTORY).replace('"INVOKE;"','"CAPTURE;"')
BODY = fcc.BODY.replace('"INVOKE;"','"CAPTURE;"')
PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, READY).replace('$factory182_', '$kwfrom239_ready_')
PREFIX += r'''
dec $kwfrom239_expr_at(pcodeexpr, pcpath) : bool
def $kwfrom239_expr_at(CODEEXPR pcpath z b, pcpath) = true
def $kwfrom239_expr_at(pcodeexpr, pcpath) = false -- otherwise
dec $kwfrom239_without_expr(pcodeexpr*, pcpath) : pcodeexpr*
def $kwfrom239_without_expr(eps, pcpath) = eps
def $kwfrom239_without_expr(pcodeexpr :: pcodeexpr_tail*, pcpath) = $kwfrom239_without_expr(pcodeexpr_tail*, pcpath) -- if $kwfrom239_expr_at(pcodeexpr, pcpath)
def $kwfrom239_without_expr(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $kwfrom239_without_expr(pcodeexpr_tail*, pcpath) -- if ~$kwfrom239_expr_at(pcodeexpr, pcpath)
'''


def render(case, fixture, filename):
    checks = [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')',
        r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FACTORY,
        '$newfcc235_outer(ptask_factory_tail*) = (pmagicmethodcall)',
        'pmagicmethodcall.CALLER = (pcallcontext_caller)', 'pmagicmethodcall.PRODUCERS = eps',
        '$class_named(S.CLASSNAMES,$ptascii("packetbase239")) = (porigin_base)',
        '$class_named(S.CLASSNAMES,$ptascii("packetscope239")) = (porigin_scope)',
        '$class_named(S.CLASSNAMES,$ptascii("packetchild239")) = (porigin_allocated)',
        'pcallcontext_caller.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_caller.CALLED_CLASS = (porigin_allocated)', 'porigin_scope =/= porigin_allocated',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]',
        'papiquery.VALUE = PARRAY n_callback',
        'S.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_packet)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        'papiquery.INPUT = POBJECT n_packet',
        'papiquery.CLASS.REQUESTED = porigin_allocated', 'papiquery.CLASS.RECEIVER = (n_packet)',
        'papiquery.SCOPE = pcallcontext_caller.LEXICAL_CLASS',
        '$object_class_origin(S,n_packet) = (porigin_allocated)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_producer)',
        '$origin_node(S.SOURCES,porigin_producer) = (expression_producer)',
        'expression_producer = NExprFuncCall expression_factory (SEQUENCE phpType7_real*) metadata_producer',
        'expression_factory = NExprStaticCall phpType19_factory phpType20_factory (SEQUENCE ([NArg ABSENT expression_callback (BOOLEAN false) (BOOLEAN false) metadata_arg])) metadata_factory',
        'expression_callback = NExprArray (SEQUENCE ([(NArrayItem ABSENT expression_new (BOOLEAN false) (BOOLEAN false) metadata_receiver),(NArrayItem ABSENT expression_method (BOOLEAN false) (BOOLEAN false) metadata_method)])) metadata_array',
        'expression_method = NScalarString phpType33 metadata_name',
        'expression_new = NExprNew name_new (SEQUENCE phpType7_ctor*) metadata_new',
        '|phpType7_ctor*| = 1', '|phpType7_real*| = 2',
        'porigin_producer = PORIGIN n_unit pcpath_producer',
        'porigin_factory = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0])',
        'porigin_callback = PORIGIN n_unit (pcpath_producer ++ [PCFIELD 0,PCFIELD 2,PCINDEX 0,PCFIELD 1])',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 0,PCFIELD 1]) = (porigin_new)',
        'porigin_new = PORIGIN n_unit pcpath_new',
        '$origin_child((porigin_callback),[PCFIELD 0,PCINDEX 1,PCFIELD 1]) = (porigin_literal)',
        '$magic_method_literal_value(S,porigin_literal,expression_method) = (pvalue_method)',
        '$string_bytes(pvalue_method) = ($ptascii("capture"))',
        'pconfigcall.SITE = porigin_factory', '$from_site(S,porigin_factory)',
        '$ordinary_keyword_new_site(S,porigin_new)',
        '$code_at(S.CODE,n_unit) = (pcode)', 'S.CODE = [pcode]',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer) = (z_outer)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = ((z_factory,false))',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0]) = eps',
        '$magic_method_from_callable_parts(S,porigin_producer,expression_producer) = ((porigin_callback,expression_callback,phpType7_real*))',
        '$magic_method_keyword_new_array_from_callable_call(expression_producer)',
        '$magic_method_context_call(expression_producer)',
        '$magic_method_keyword_new_array_from_callable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = ((porigin_allocated,pmethoddesc))',
        '$scope_method(S,porigin_allocated,$ptascii("capture"),true,pcallcontext_caller.LEXICAL_CLASS) = (pmethoddesc)',
        '$api_selected_method(S,papiquery,$ptascii("capture")) = (pmethoddesc)',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN', 'pmethoddesc.OWNER = porigin_base',
        '$magic_method_plain_instance_source(S,pmethoddesc,phpType7_real*)',
        '$magic_method_from_callable_producer(S,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_invokable_producer(S,pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_from_callable_producer(S,eps,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_from_callable_producer(S[.SOURCES = eps],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_from_callable_producer(S,(pcallcontext_caller[.FUNCTION = porigin_method]),porigin_producer,expression_producer) = eps',
        '$magic_method_keyword_new_array_from_callable_producer(S[.CODE = [pcode[.EXPRESSIONS = $kwfrom239_without_expr(pcode.EXPRESSIONS,pcpath_producer ++ [PCFIELD 0])]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps',
    ]
    for path in ('pcpath_producer', 'pcpath_new'):
        checks.append('$magic_method_keyword_new_array_from_callable_producer(S[.CODE = [pcode[.EXPRESSIONS = $newfcc235_without_init(pcode.EXPRESSIONS,' + path + ')]]],pmagicmethodcall.CALLER,porigin_producer,expression_producer) = eps')
    checks += [
        '$api_query_valid(S,papiquery,0)',
        '$node_children(S,HARRAY n_callback) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S),HARRAY n_callback) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_packet) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'n_wrapper = |S.OBJECTS|', 'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS[n_wrapper] = FROMCALLABLECLOSURE pfrommethod',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [FROMCALLABLECLOSURE pfrommethod]',
        'S_wrapped.RESULT = KNOWN PNULL', 'S_wrapped.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_wrapped.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.VALUE = KNOWN (POBJECT n_wrapper)',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
        'pdestructionoperation.CALLER = (pcallcontext_caller)',
        'pdestructionoperation.SOURCE = API_CALLABLE_RESULT papiquery 0',
        '$destructor_operation_valid(S_wrapped,pdestructionoperation)',
        '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) <- S_wrapped.TODO',
        '$heap_count(HOBJECT n_wrapper,$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation)) = 1',
        '$heap_count(HOBJECT n_wrapper,$operand_nodes(S_wrapped.RESULT)) = 0',
        '~pfrommethod.INVOKE', '~pfrommethod.STATIC', 'pfrommethod.ARRAY',
        'pfrommethod.INPUT = POBJECT n_packet', 'pfrommethod.FUNCTION = porigin_method',
        'pfrommethod.FACTORY = eps', 'pfrommethod.CREATION = eps',
        'pfrommethod.CLASS.REQUESTED = porigin_allocated', 'pfrommethod.CLASS.CALLED = porigin_allocated',
        '$from_receiver(pfrommethod) = (n_packet)',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_base', 'pclosurescope.CALLED = porigin_allocated',
        'pclosurescope.RECEIVER = (n_packet)', 'pclosurescope.CREATION = eps',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_wrapped),HOBJECT n_wrapper) = 1',
        '$closure_state_valid(S_wrapped)', '$heap_valid($heap_graph(S_wrapped))',
        'S_ready_found = $kwfrom239_ready_seek(S_wrapped,2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_ready_direct = $kwfrom239_ready_seek(S,2048)', 'S_ready_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', methods.at(READY,'S_ready'),
        'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_producer',
        'phpType7_ready* = phpType7_real*', 'pcallcontext_ready = pcallcontext_caller',
        '~((HARRAY n_callback) <- S_ready.ALLOCATIONS)',
        '$factory182_output(S_ready.EVENTS) = $ptascii("CTOR;")',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_packet) = 1',
        'S_shift_found = $newfcc235_shift_seek(S_ready,2048)', 'S_shift_found.COMPLETION = BUDGET',
        'S_shift = S_shift_found[.COMPLETION = NORMAL]', methods.at(methods.SHIFT,'S_shift'),
        '$lookup($global_table_view(S_shift).ENV,$ptascii("owner")) = (n_owner_cell)',
        'S_shift.STORE[n_owner_cell] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_wrapper) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT n_packet) = 1',
        '$heap_owners($heap_graph(S_shift),HOBJECT pmagicmethodcall.OBJECT) = 1',
        '$magic_method_context_source(S_shift,S_shift.CURRENT,porigin_producer,expression_producer) = false',
        '$magic_method_context_source(S_shift,pmagicmethodcall.CALLER,porigin_producer,expression_producer)',
        'S_body_found = $newfcc235_body_seek(S_shift,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', methods.at(BODY,'S_body'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper',
        'pcallcontext_body.INSTANCE = (n_wrapper)', 'pcallcontext_body.RECEIVER = (n_packet)',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_base)', 'pcallcontext_body.CALLED_CLASS = (porigin_allocated)',
        '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$node_children(S_body,HOBJECT n_wrapper) = [HOBJECT n_packet]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_packet) = 1',
        '$call_current_valid(S_body)', '$call_descriptors_valid(S_body)',
        'S_send_found = $newfcc235_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', methods.at(methods.SEND,'S_send'),
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
    protocol.run({CASE: {'source': ROWS[CASE]['source']}},
                 extra_inputs=(CATALOGUE,Path(__file__),Path(fcc.__file__),fcc.CATALOGUE,Path(methods.__file__),methods.CATALOGUE,Path(names.__file__)),
                 fixture_renderer=render,runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
