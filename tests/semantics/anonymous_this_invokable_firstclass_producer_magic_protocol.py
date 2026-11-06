#!/usr/bin/env python3
"""This callable capture adds a wrapper edge while the original caller owns This."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_this_invokable_firstclass_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_this_invokable_firstclass_producer_magic_controls.json'
ROWS = {row['id']: row for p in (CATALOGUE, CONTROLS) for row in json.loads(p.read_text())['cases']}
CASE = 'magic-this-invoke-fcc-old'
UNPACK = 'magic-this-invoke-fcc-unpack-refused'
READ = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init z_capture) :: ptask_read_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_this) -- if S.CURRENT = (pcallcontext_caller) '
        '-- if $dynamic_this_site(S,porigin_capture)')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_string_body) :: expression_echo_tail*)) metadata_echo_body)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("INVOKE:") -- if S.CURRENT = (pcallcontext_body)')
SEND = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_send) eps 0 eps (porigin_send) z_send) :: ptask_send_tail* '
        '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = (pcallcontext_send)')
RETURN = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text_return) metadata_string_return])) metadata_echo_return)) :: ptask_return_tail* '
          '-- if $base64(text_return) = $ptascii("RETURN;") -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = (pcallcontext_boundary)')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('body', BODY), ('send', SEND), ('return', RETURN), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$thisfcc221_' + label + '_')
PREFIX += r'''
dec $thisfcc221_outer_one(ptask) : pmagicmethodcall?
def $thisfcc221_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 0 eps porigin? z) = (pmagicmethodcall)
def $thisfcc221_outer_one(ptask) = eps -- otherwise
dec $thisfcc221_outer(ptask*) : pmagicmethodcall?
def $thisfcc221_outer(eps) = eps
def $thisfcc221_outer(ptask :: ptask_tail*) = (pmagicmethodcall) -- if $thisfcc221_outer_one(ptask) = (pmagicmethodcall)
def $thisfcc221_outer(ptask :: ptask_tail*) = $thisfcc221_outer(ptask_tail*) -- if $thisfcc221_outer_one(ptask) = eps
'''


def ownership(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READ,
        '$thisfcc221_outer(ptask_read_tail*) = (pmagicmethodcall)', 'pmagicmethodcall.CALLER = (pcallcontext_caller)',
        'pmagicmethodcall.PRODUCERS = eps', 'pcallcontext_caller.RECEIVER = (n_this)',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),0) = (porigin_outer)', 'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        '$magic_method_this_invokable_producer(S,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_producer_cv_parts(S,porigin_outer,expression_outer) = eps',
        '$dynamic_operand_valid(S,porigin_capture)',
        '$magic_method_this_invokable_producer(S,eps,porigin_outer,expression_outer) = eps',
        '$magic_method_this_invokable_producer(S[.CODE = eps],pmagicmethodcall.CALLER,porigin_outer,expression_outer) = eps',
        '$magic_method_context_values(S[.CODE = eps],pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 9)],eps) = eps',
        'porigin_method = pmethoddesc.FUNCTION.ORIGIN',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (METHOD_CONVERT (METHOD_TARGET n_this porigin_method) porigin_capture z_capture) :: ptask_selected_tail*',
        '$thisfcc221_outer(ptask_selected_tail*) = (pmagicmethodcall)',
        'n_wrapper = |S_selected.OBJECTS|', '$method_capture_current(S_selected,porigin_capture) = eps',
        'S_wrapped = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_selected.OBJECTS ++ [METHODCLOSURE porigin_method porigin_capture porigin_class eps]',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_this]',
        'S_body_found = $thisfcc221_body_seek(S_wrapped[.COMPLETION = NORMAL],2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.INSTANCE = (n_wrapper)',
        'pcallcontext_body.RECEIVER = (n_this)', '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$heap_owners($heap_graph(S_body),HOBJECT n_this) = 2',
        '$lookup($global_table_view(S_body).ENV,$ptascii("runner")) = (n_runner_cell)', 'S_body.STORE[n_runner_cell] = DEFINED PNULL',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_send_found = $thisfcc221_send_seek(S_body,2048)', 'S_send_found.COMPLETION = BUDGET',
        'S_send = S_send_found[.COMPLETION = NORMAL]', SEND.replace('S.', 'S_send.'),
        'pmagicmethodcall_send = pmagicmethodcall', 'pcallcontext_send = pcallcontext_caller',
        '~((HOBJECT n_wrapper) <- S_send.ALLOCATIONS)', '$heap_owners($heap_graph(S_send),HOBJECT n_this) = 1',
        '$magic_method_context_values(S_send,pmagicmethodcall.CALLER,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = ([POBJECT n_old])',
        '$magic_method_fact_values(S_send,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (POBJECT n_old)],eps) = eps',
        'S_root_found = $thisfcc221_return_seek(S_send,2048)', 'S_root_found.COMPLETION = BUDGET',
        'S_root = S_root_found[.COMPLETION = NORMAL]', RETURN.replace('S.', 'S_root.'),
        '~((HOBJECT n_this) <- S_root.ALLOCATIONS)',
        '$magic_method_this_invokable_producer(S_root,pmagicmethodcall.CALLER,porigin_outer,expression_outer) = ((n_this,porigin_class,pmethoddesc))',
        '$magic_method_this_invokable_producer(S_root,S_root.CURRENT,porigin_outer,expression_outer) = eps',
        '$factory182_output(S_root.EVENTS) = $ptascii("SHIFT;INVOKE:InvokeBase221:InvokeChild221;NEW;HANDLER:OLD;OLD;OWNER;THIS-END;")',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $thisfcc221_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_method_this_invokable_producer(S,S.CURRENT,porigin_producer,expression_producer) = ((n_this,porigin_class,pmethoddesc))',
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
