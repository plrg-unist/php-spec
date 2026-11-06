#!/usr/bin/env python3
"""CV conversion reads once, stamps outer source and preserves that receipt."""
import argparse
import json
from pathlib import Path
import anonymous_method_closure_factory_protocol as names
import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_cv_invokable_firstclass_producer_magic_cases.json'
CONTROLS = ROOT / 'tests/semantics/anonymous_cv_invokable_firstclass_producer_magic_controls.json'
ROWS = {x['id']: x for p in (CATALOGUE, CONTROLS) for x in json.loads(p.read_text())['cases']}
CASE = 'magic-cv-invoke-fcc-installed-old'
ZERO = 'magic-cv-invoke-fcc-zero'
MISSING = 'magic-cv-invoke-fcc-missing-refused'
UNPACK = 'magic-cv-invoke-fcc-unpack-refused'
READ = ('S.TODO = (FIRSTCLASS_CONVERT porigin_capture z_init z_capture) :: ptask_read_tail* '
        '-- if S.RESULT = VARIABLE ($ptascii("receiver")) z_cv -- if S.CURRENT = eps')
BODY = ('S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text_body) metadata_body) :: expression_echo_tail*)) metadata_echo)) :: ptask_body_tail* '
        '-- if $base64(text_body) = $ptascii("INVOKE:") -- if S.CURRENT = (pcallcontext_body)')
RESULT = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_result) eps 1 ([KNOWN (PBOOL false)]) (porigin_result) z_result) :: ptask_result_tail* '
          '-- if S.RESULT = KNOWN (POBJECT n_old) -- if S.CURRENT = eps')
ZERORESULT = ('S.TODO = (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall_result) eps 0 eps (porigin_result) z_result) :: ptask_result_tail* '
              '-- if S.RESULT = KNOWN (PINT 7) -- if S.CURRENT = eps')
BOUNDARY = ('S.TODO = (EVAL (NExprMethodCall expression_receiver_boundary phpType20_boundary (SEQUENCE phpType7_boundary*) metadata_boundary)) :: ptask_boundary_tail* '
            '-- if $call_unpack_present(phpType7_boundary*) -- if S.CURRENT = eps')
PREFIX = names.PREFIX.replace(names.FRONT, READ)
for label, front in [('body', BODY), ('result', RESULT), ('zeroresult', ZERORESULT), ('boundary', BOUNDARY)]:
    PREFIX += names.PREFIX[names.PREFIX.index('dec $factory182_front'):].replace(names.FRONT, front).replace('$factory182_', '$cvifcc220_' + label + '_')
PREFIX += r'''
dec $cvifcc220_outer_one(ptask) : (pmagicmethodcall,nat)?
def $cvifcc220_outer_one(CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps n poperand* porigin? z) = ((pmagicmethodcall,n))
def $cvifcc220_outer_one(ptask) = eps -- otherwise
dec $cvifcc220_outer(ptask*) : (pmagicmethodcall,nat)?
def $cvifcc220_outer(eps) = eps
def $cvifcc220_outer(ptask :: ptask_tail*) = ((pmagicmethodcall,n)) -- if $cvifcc220_outer_one(ptask) = ((pmagicmethodcall,n))
def $cvifcc220_outer(ptask :: ptask_tail*) = $cvifcc220_outer(ptask_tail*) -- if $cvifcc220_outer_one(ptask) = eps
'''


def read_start(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $factory182_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', READ,
        '$cvifcc220_outer(S.TODO) = ((pmagicmethodcall,n_index))', 'pmagicmethodcall.PRODUCERS = eps',
        '$call_argument_origin(S,(pmagicmethodcall.SITE),n_index) = (porigin_outer)', 'porigin_outer = PORIGIN n_unit pcpath_outer',
        'porigin_capture = PORIGIN n_unit (pcpath_outer ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_outer) = (expression_outer)',
        '$magic_producer_cv_parts(S,porigin_outer,expression_outer) = ((porigin_capture,S.RESULT,$ptascii("__invoke"),phpType7_capture*,phpType7_real*))',
        'phpType7_capture* = [NVariadicPlaceholder metadata_placeholder]',
        '$magic_producer_argument_site(S,porigin_capture) = (porigin_outer)',
        '$firstclass_task_valid(S,porigin_capture,z_init,z_capture)',
    ]


def selection():
    return [
        '$lookup(S.ENV,$ptascii("receiver")) = (n_receiver_cell)', 'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        '$magic_producer_cell(S,$ptascii("receiver")) = (n_receiver)',
        '$object_class_origin(S,n_receiver) = (porigin_class)',
        '$magic_producer_selected_source(S,porigin_outer,porigin_class) = (pmethoddesc)',
        '$method_receiver_value_allowed(S,S.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
        'S_selected = $drive_steps(S,1)', 'S_selected.COMPLETION = BUDGET',
        'S_selected.TODO = (METHOD_CONVERT (METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN) porigin_capture z_capture) :: ptask_selected_tail*',
        '$cvifcc220_outer(ptask_selected_tail*) = ((pmagicmethodcall_selected,n_index))',
        'pmagicproducerfact = {SITE porigin_outer,CLASS porigin_class,METHOD pmethoddesc.FUNCTION.ORIGIN}',
        'pmagicmethodcall_selected = pmagicmethodcall[.PRODUCERS = [pmagicproducerfact]]',
        'n_wrapper = |S_selected.OBJECTS|',
        'S_wrapped = $drive_steps(S_selected[.COMPLETION = NORMAL],1)', 'S_wrapped.COMPLETION = BUDGET',
        'S_direct = $drive_steps(S,2)', 'S_direct = S_wrapped',
        'S_wrapped.OBJECTS = S_selected.OBJECTS ++ [METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN porigin_capture porigin_class eps]',
        '$node_children(S_wrapped,HOBJECT n_wrapper) = [HOBJECT n_receiver]',
    ]


def ownership(fixture, filename):
    return read_start(fixture, filename) + selection() + [
        'n_index = 1', '~(n_receiver_cell <- S.REFCELLS)', '|phpType7_real*| = 2',
        '$factory182_output(S.EVENTS) = $ptascii("INSTALL;")',
        'S_body_found = $cvifcc220_body_seek(S_wrapped[.COMPLETION = NORMAL],2048)', 'S_body_found.COMPLETION = BUDGET',
        'S_body = S_body_found[.COMPLETION = NORMAL]', BODY.replace('S.', 'S_body.'),
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_wrapper', 'pcallcontext_body.INSTANCE = (n_wrapper)',
        'pcallcontext_body.RECEIVER = (n_receiver)', '$call_context_roots(S_body.CURRENT) = [HOBJECT n_wrapper]',
        '$lookup($global_table_view(S_body).ENV,$ptascii("receiver")) = (n_receiver_cell)',
        'S_body.STORE[n_receiver_cell] = DEFINED (POBJECT n_replacement)', 'n_replacement =/= n_receiver',
        '$object_class_origin(S_body,n_replacement) = (porigin_replacement)',
        '$magic_producer_selected_source(S_body,porigin_outer,porigin_replacement) = eps',
        '$lookup(S_body.ENV,$ptascii("saved")) = (n_saved_cell)', 'S_body.STORE[n_saved_cell] = DEFINED (POBJECT n_old)',
        '$lookup($global_table_view(S_body).ENV,$ptascii("argument")) = (n_argument_cell)',
        'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_result_found = $cvifcc220_result_seek(S_body,2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', RESULT.replace('S.', 'S_result.'),
        'pmagicmethodcall_result = pmagicmethodcall_selected',
        '~((HOBJECT n_receiver) <- S_result.ALLOCATIONS)', '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$magic_producer_facts_valid(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[pmagicproducerfact])',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_old)],[pmagicproducerfact]) = ([PBOOL false,POBJECT n_old])',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PBOOL false),KNOWN (POBJECT n_old)],eps) = eps',
        '$factory182_output(S_result.EVENTS) = $ptascii("INSTALL;SHIFT;INVOKE:InvokeBase220:InvokeChild220;INVOKER-END;")',
    ]


def zero_receipt(fixture, filename):
    return read_start(fixture, filename) + selection() + [
        'n_index = 0', 'phpType7_real* = eps',
        'S_result_found = $cvifcc220_zeroresult_seek(S_wrapped[.COMPLETION = NORMAL],2048)', 'S_result_found.COMPLETION = BUDGET',
        'S_result = S_result_found[.COMPLETION = NORMAL]', ZERORESULT.replace('S.', 'S_result.'),
        'pmagicmethodcall_result = pmagicmethodcall_selected',
        'S_result.STORE[n_receiver_cell] = DEFINED PNULL', '~((HOBJECT n_wrapper) <- S_result.ALLOCATIONS)',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7)],[pmagicproducerfact]) = ([PINT 7])',
        '$magic_method_fact_values(S_result,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,[KNOWN (PINT 7)],eps) = eps',
        '$factory182_output(S_result.EVENTS) = $ptascii("ZERO;ZERO-END;")',
    ]


def missing(fixture, filename):
    return read_start(fixture, filename) + [
        'n_index = 1', '$error_handler_eligible(S,2)', '~$error_read_pending(S)',
        '$magic_producer_cell(S,$ptascii("receiver")) = eps',
        '~$method_receiver_value_allowed(S,S.RESULT,$ptascii("__invoke"),phpType7_capture*,z_init)',
        '$factory182_output(S.EVENTS) = $ptascii("FIRST;")',
        '$call_descriptors_valid(S)', '$gc_state_valid(S)', '$heap_valid($heap_graph(S))',
        'S_step = $firstclass_convert(S[.TODO = ptask_read_tail*],porigin_capture,z_init,z_capture)',
        'S_step = S[.TODO = ptask_read_tail*][.COMPLETION = UNSUPPORTED "magic method producer receiver read"]',
        'S_done = $drive_steps(S,1)', 'S_done.COMPLETION = UNSUPPORTED "magic method producer receiver read"',
        '$factory182_output(S_done.EVENTS) = $ptascii("FIRST;")', 'S_done.TODO = eps',
    ]


def unpack_boundary(fixture, filename):
    return [
        'S_initial = $php_run(' + fixture + ',0,' + filename + ')', r'S_initial.COMPLETION = BUDGET /\ ~S_initial.COMPILESTOP',
        'S_found = $cvifcc220_boundary_seek(S_initial,2048)', 'S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', BOUNDARY, 'S.ORIGIN = (porigin_site)',
        'phpType7_boundary* = [phpType7_producer,phpType7_pack]',
        'phpType7_producer = NArg ABSENT expression_producer (BOOLEAN false) (BOOLEAN false) metadata_producer',
        'phpType7_pack = NArg ABSENT (NExprVariable (BYTES text_pack) metadata_pack) (BOOLEAN false) (BOOLEAN true) metadata_pack_arg',
        '$call_argument_origin(S,(porigin_site),0) = (porigin_producer)',
        '$magic_producer_cv_source(S,porigin_producer,expression_producer)', '$magic_method_argument_source(S,porigin_producer,0,expression_producer)',
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


CHECKS = {CASE: ownership, ZERO: zero_receipt, MISSING: missing, UNPACK: unpack_boundary}

def render(case, fixture, filename):
    key = next(key for key in CHECKS if ROWS[key]['source'] == case['source'])
    checks = CHECKS[key](fixture, filename)
    return PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + x + '\n' for x in checks), len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sl', action='store_true')
    parser.add_argument('--case', action='append', choices=tuple(CHECKS))
    args = parser.parse_args()
    protocol.run({key: {'source': ROWS[key]['source']} for key in CHECKS if not args.case or key in args.case}, extra_inputs=(CATALOGUE, CONTROLS, Path(__file__)), fixture_renderer=render, runner_flags=('--sl',) if args.sl else ())


if __name__ == '__main__':
    main()
