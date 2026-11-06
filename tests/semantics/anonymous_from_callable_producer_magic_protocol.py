#!/usr/bin/env python3
"""A normal factory fixes its USER function before invocation argument effects."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_from_callable_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_from_callable_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-from-callable-function-old'
UNPACK = 'magic-from-callable-unpack-refused'
FACTORY = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_factory_tail* '
           '-- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE -- if S.CURRENT = eps')
READY = ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_wrapper_ready) phpType7_ready* 0 eps (porigin_ready) z_ready) :: ptask_ready_tail* '
         '-- if S.CURRENT = eps')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_body) metadata_body])) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("PRODUCER;") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, FACTORY)
for label, front in [('ready', READY), ('body', BODY), ('send', SEND), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$fromfactory222_' + label + '_')
PREFIX += r'''
dec $fromfactory222_outer_one(ptask) : pmagicmethodcall?
def $fromfactory222_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $fromfactory222_outer_one(ptask) = eps -- otherwise
dec $fromfactory222_outer(ptask*) : pmagicmethodcall?
def $fromfactory222_outer(eps) = eps
def $fromfactory222_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $fromfactory222_outer_one(ptask) = (pmagicmethodcall)
def $fromfactory222_outer(ptask :: ptask_tail*) = $fromfactory222_outer(ptask_tail*) -- if $fromfactory222_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', FACTORY,
        '$fromfactory222_outer(ptask_factory_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_outer)', 'porigin_outer = PORIGIN n_unit pcpath_outer',
        'pconfigcall.SITE = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall expression_factory (SEQUENCE phpType7_real*) metadata_outer', '|phpType7_real*| = 2',
        '$magic_method_from_callable_call(expression_outer)', '~$magic_method_firstclass_call(expression_outer)',
        '$magic_method_from_callable_producer(S,porigin_outer,expression_outer) = (pfunction)',
        '$call_argument_origin(S,(pconfigcall.SITE),0) = (porigin_literal)',
        '$origin_node(S.SOURCES,porigin_literal) = (expression_literal)',
        '$magic_method_literal_value(S,porigin_literal,expression_literal) = (pvalue_literal)',
        '$string_bytes(pvalue_literal) = ($ptascii("produce222"))',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_literal)]', '$config_invoke_valid(S,pconfigcall)',
        'n_wrapper = |S.OBJECTS|', 'S_pause = $drive_steps(S,1)', 'S_pause.COMPLETION = BUDGET',
        'S_ready_found = $fromfactory222_ready_seek(S_pause[.COMPLETION = NORMAL],2047)', 'S_ready_found.COMPLETION = BUDGET',
        'S_direct = $fromfactory222_ready_seek(S,2048)', 'S_direct = S_ready_found',
        'S_ready = S_ready_found[.COMPLETION = NORMAL]', READY.replace('S.', 'S_ready.'),
        'n_wrapper_ready = n_wrapper', 'porigin_ready = porigin_outer', 'phpType7_ready* = phpType7_real*',
        'S_ready.OBJECTS = S.OBJECTS ++ [NAMEDCLOSURE pfunction.ORIGIN]',
        '$node_children(S_ready,HOBJECT n_wrapper) = eps', '$call_selected_valid(S_ready,CLOSURE_TARGET n_wrapper,(porigin_outer))',
        '$factory182_output(S_ready.EVENTS) = eps',
        'S_body_found = $fromfactory222_body_seek(S_ready,2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.INSTANCE = (n_wrapper)',
        'pcallcontext_body.RECEIVER = eps', '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_send_found = $fromfactory222_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'), 'pmagicmethodcall_send = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)',
        '$magic_method_from_callable_producer(S_send,porigin_outer,expression_outer) = (pfunction)',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$magic_method_value(S_send,POBJECT n_old)', '$magic_method_primitive(S_send,PINT 9)',
        '$magic_method_fact_values(S_send[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        '$magic_method_fact_values(S_send[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 9)],eps) = eps',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;PRODUCER;")',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $fromfactory222_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_from_callable_producer(S,porigin_producer,expression_producer) = (pfunction)',
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
    checks = unpack_boundary(fixture, filename) if case['source'] == ROWS[UNPACK]['source'] else ownership(fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks), len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=(CASE, UNPACK))
    args = parser.parse_args()
    protocol.run({key: {'source': ROWS[key]['source']} for key in (CASE, UNPACK) if not args.case or key in args.case}, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)), fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
