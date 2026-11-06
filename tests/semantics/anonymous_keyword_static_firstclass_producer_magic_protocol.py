#!/usr/bin/env python3
"""Keyword FCC capture, real invocation args and unaliased wrapper retirement."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_keyword_static_firstclass_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_keyword_static_firstclass_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-keyword-static-firstclass-pending-leaf'
UNPACK = 'magic-keyword-static-firstclass-unpack-refused'
CONVERT = ('S.TODO = (METHOD_CONVERT (SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) porigin_capture z_capture) :: ptask_convert_tail* '
           '-- if S.CURRENT = (pcallcontext_caller)')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_outer_ready) z_call) :: ptask_ready_tail* '
         '-- if S.CURRENT = (pcallcontext_ready)')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_string_body) :: expression_echo_tail*)) metadata_echo_body)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = (pcallcontext_send)')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = (pcallcontext_boundary)')
PREFIX = names.PREFIX.replace(names.FRONT, CONVERT)
for label, front in [('ready', READY), ('body', BODY), ('send', SEND), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$keywordfcc215_' + label + '_')
PREFIX += r'''
dec $keywordfcc215_outer_one(ptask) : pmagicmethodcall?
def $keywordfcc215_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $keywordfcc215_outer_one(ptask) = eps -- otherwise
dec $keywordfcc215_outer(ptask*) : pmagicmethodcall?
def $keywordfcc215_outer(eps) = eps
def $keywordfcc215_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $keywordfcc215_outer_one(ptask) = (pmagicmethodcall)
def $keywordfcc215_outer(ptask :: ptask_tail*) = $keywordfcc215_outer(ptask_tail*) -- if $keywordfcc215_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CONVERT,
        '$keywordfcc215_outer(S.TODO) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (PORIGIN n_unit pcpath_outer)',
        'porigin_outer = PORIGIN n_unit pcpath_outer', 'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_capture (SEQUENCE phpType7_real*) metadata_outer',
        'expression_capture = NExprStaticCall (NName (BYTES text_keyword) metadata_keyword) (NIdentifier (BYTES text_method) metadata_method) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture',
        '|phpType7_real*| = 2',
        '$code_at(S.CODE,n_unit) = (pcode)', '$code_call_init(pcode.EXPRESSIONS,pcpath_outer) = (z_outer_init)',
        '$code_call_init(pcode.EXPRESSIONS,pcpath_outer ++ [PCFIELD 0]) = (z_capture_init)',
        '$class_named(S.CLASSNAMES,$ptascii("producerscope215")) = (porigin_requested)',
        '$class_named(S.CLASSNAMES,$ptascii("producerchild215")) = (porigin_called)',
        '$class_named(S.CLASSNAMES,$ptascii("producerbase215")) = (porigin_declaring)',
        '$magic_method_keyword_static_producer(S,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((porigin_requested,porigin_called,pmethoddesc))',
        'pmethoddesc.OWNER = porigin_declaring', 'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
        '$target_nodes(SCOPED_TARGET porigin_requested porigin_method porigin_called eps poperand_selector) = eps',
        '$method_capture_current(S,porigin_capture) = eps', 'n_wrapper = |S.OBJECTS|',
        'S_wrapped = $drive_steps(S,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_wrapped.OBJECTS = S.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_requested eps]',
        'S_wrapped.RESULT = KNOWN (POBJECT n_wrapper)',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.LEXICAL = porigin_declaring', 'pclosurescope.CALLED = porigin_called',
        'pclosurescope.RECEIVER = eps', '$node_children(S_wrapped,HOBJECT n_wrapper) = eps',
        'S_ready_found = $keywordfcc215_ready_seek(S_wrapped[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $keywordfcc215_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_outer_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        'pcallcontext_ready = pcallcontext_caller', '$heap_owners($heap_graph(S_ready),HOBJECT n_wrapper) = 1',
        'S_body_found = $keywordfcc215_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.INSTANCE = (n_wrapper)',
        'pcallcontext_body.RECEIVER = eps', '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_send_found = $keywordfcc215_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'pmagicmethodcall_send = pmagicmethodcall', 'pcallcontext_send = pcallcontext_caller',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)',
        '$magic_method_keyword_static_producer(S_send,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((porigin_requested,porigin_called,pmethoddesc))',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        '$magic_method_context_values(S_send,eps,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        '$magic_method_keyword_static_producer(S_send[.CODE = eps],pmagicmethodcall.CALLER,porigin_outer,expression_outer) = eps',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $keywordfcc215_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_keyword_static_producer(S,S.CURRENT,porigin_producer,expression_producer) = ((porigin_requested,porigin_called,pmethoddesc))',
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
