#!/usr/bin/env python3
"""Fresh invokable wrapper releases its receiver before sending the old result."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_invokable_firstclass_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_invokable_firstclass_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-fresh-invoke-fcc-old'
UNPACK = 'magic-fresh-invoke-fcc-unpack-refused'
CAPTURE = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init z_convert) :: ptask_capture_tail* '
           '-- if S.RESULT = KNOWN (POBJECT n_invoker) -- if S.CURRENT = eps')
CONVERT = ('S.TODO = (METHOD_CONVERT (METHOD_TARGET n_invoker_convert porigin_method_convert) porigin_convert z_method_convert) :: ptask_convert_tail* '
           '-- if S.CURRENT = eps')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_string_body) :: expression_echo_tail*)) metadata_echo_body)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("INVOKE:") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, CAPTURE)
for label, front in [('body', BODY), ('send', SEND), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$invokefcc219_' + label + '_')
PREFIX += r'''
dec $invokefcc219_outer_one(ptask) : pmagicmethodcall?
def $invokefcc219_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $invokefcc219_outer_one(ptask) = eps -- otherwise
dec $invokefcc219_outer(ptask*) : pmagicmethodcall?
def $invokefcc219_outer(eps) = eps
def $invokefcc219_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $invokefcc219_outer_one(ptask) = (pmagicmethodcall)
def $invokefcc219_outer(ptask :: ptask_tail*) = $invokefcc219_outer(ptask_tail*) -- if $invokefcc219_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', CAPTURE,
        '$invokefcc219_outer(ptask_capture_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_outer)', 'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        'expression_outer = NExprFuncCall (NExprFuncCall expression_new (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_capture) (SEQUENCE phpType7_real*) metadata_outer',
        '$magic_method_firstclass_site(S,porigin_outer,expression_outer)', '|phpType7_real*| = 2',
        '$magic_method_fresh_receiver(S,PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0,PCFIELD 0]),expression_new) = (porigin_class)',
        '$object_class_origin(S,n_invoker) = (porigin_class)',
        '$magic_method_firstclass_producer(S,porigin_outer,expression_outer) = (pfunction)',
        '$object_invoke_method(S,n_invoker) = (pmethoddesc)', 'pmethoddesc.FUNCTION = pfunction', 'porigin_method = pfunction.ORIGIN',
        '$magic_method_firstclass_producer(S[.CODE = eps],porigin_outer,expression_outer) = eps',
        '$magic_method_fact_values(S[.CODE = eps],pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 9)],eps) = eps',
        'S_one = $drive_steps(S,1)', 'S_one.COMPLETION = BUDGET',
        'S_convert = S_one[.COMPLETION = NORMAL]', CONVERT.replace('S.', 'S_convert.'),
        'n_invoker_convert = n_invoker', 'porigin_method_convert = porigin_method', 'porigin_convert = porigin_capture',
        '$call_selected_valid(S_convert,METHOD_TARGET n_invoker porigin_method,(porigin_capture))',
        '$method_capture_current(S_convert,porigin_capture) = eps',
        'n_wrapper = |S_convert.OBJECTS|',
        'S_wrapped = $drive_steps(S_convert,1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_convert.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_class eps]',
        '$closure_scope_at(S_wrapped.CLOSURESCOPES,n_wrapper) = (pclosurescope)',
        'pclosurescope.RECEIVER = (n_invoker)', 'pclosurescope.CALLED = porigin_class',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_invoker]',
        'S_body_found = $invokefcc219_body_seek(S_wrapped[.COMPLETION = NORMAL],2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.RECEIVER = (n_invoker)',
        'pcallcontext_body.INSTANCE = (n_wrapper)', '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old', 'n_old =/= n_invoker',
        'S_send_found = $invokefcc219_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'pmagicmethodcall_send = pmagicmethodcall',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)', '~((HOBJECT n_invoker) <- S_send.ALLOCATIONS)',
        '(HOBJECT n_old) <- S_send.ALLOCATIONS',
        '$factory182_output(S_send.EVENTS) = $ptascii("SHIFT;INVOKE:InvokeBase219:InvokeChild219;INVOKER-END;")',
        '$magic_method_firstclass_producer(S_send,porigin_outer,expression_outer) = (pfunction)',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $invokefcc219_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_firstclass_producer(S,porigin_producer,expression_producer) = (pfunction)',
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
