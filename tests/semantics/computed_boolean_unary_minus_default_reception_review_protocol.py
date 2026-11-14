#!/usr/bin/env python3
"""Independent Boolean negation, named-cache and quiet-condition controls."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('computed_boolean_unary_minus_default_reception_cases.json')


def node(constructor, *children):
    return constructor + ' ' + ' '.join(f'({child})' for child in children) + ' eps'


def constant(name):
    return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") eps) eps'


def string(text):
    return f'NScalarString (BYTES "{base64.b64encode(text.encode()).decode()}") eps'


def binary(operator, left, right):
    return node('NExprBinaryOp' + operator, left, right)


checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = ($ptascii("BooleanUnaryAlias245") ++ [92] ++ $ptascii("defaults245"))',
    'pfunction.ENV.NAMESPACE = $ptascii("BooleanUnaryAlias245")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base245"),$ptascii("E_WARNING")),($ptascii("One245"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_comparison,psparam_conjunction,psparam_zero,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_comparison.BYREF /\ ~psparam_conjunction.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 5 /\ pcallcontext.HOLES = [1,2,3]',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    r'~(n_cell <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell) = 1',
    'S.STORE[n_cell] = DEFINED (PFLOAT 4609434218613702656)',
    r'n_bits = 4609434218613702656 /\ i = 1',
    'z = $default_parameter_line(S,porigin,0)',
    'ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$call_task_valid(S,ptask_resume)',
    '$task_nodes(ptask_resume) = eps',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit_source]',
]
VALUES = [(1, 'comparison', 'true', '1', '$(-1)'),
          (2, 'conjunction', 'true', '1', '$(-1)'),
          (3, 'zero', 'false', '0', '0')]
for index, label, boolean, operand, result in VALUES:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_source_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_source_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'expression_{label} = NExprUnaryMinus expression_{label}_boolean metadata_{label}',
        f'$lossy_optional_integer_boolean_shape(expression_{label}_boolean)',
        f'~$lossy_optional_integer_selection_shape(expression_{label}_boolean)',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_boolean) = eps',
        f'$lossy_optional_integer_condition(pfunction.ENV,expression_{label}_boolean) = ({boolean})',
        f'$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_{label}_boolean) = (NINT {operand})',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {result})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {result})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {result},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED (PINT {result})',
        rf'~(n_local_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_{label}) = 1',
    ])
checks.extend([
    'expression_comparison_boolean = NExprBinaryOpGreater expression_base expression_one metadata_comparison_child',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_base) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one) = (NINT 1)',
    'expression_conjunction_boolean = NExprBinaryOpBooleanAnd expression_left expression_right metadata_conjunction_child',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_left) = (true)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_right) = (true)',
    'expression_zero_boolean = NExprBinaryOpBooleanOr expression_zero_left expression_zero_right metadata_zero_child',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero_left) = (false)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero_right) = (false)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_comparison[.VALUE = PFLOAT $hex_bits("bff0000000000000",0)])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_conjunction[.VALUE = PINT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,2)',
    'S_wrong_zero = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PBOOL false])]',
    '~$lossy_optional_integer_deferred(S_wrong_zero,pfunction,3)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_zero])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,3)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base245"),$ptascii("E_ERROR")),($ptascii("One245"),$ptascii("E_WARNING"))]]',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_comparison) = (NINT 0)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_comparison)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'pcpath_base = pcpath_comparison ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]',
    '$origin_node(S.SOURCES,PORIGIN n_source_unit pcpath_base) = (expression_base)',
    'S_forged_source = S[.SOURCES = [pcunit_source[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_one) :: pcunit_source.OCCURRENCES]]]',
    '~$lossy_optional_integer_deferred(S_forged_source,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2]])],ptask_resume)',
    'S_two_owners = S[.ENV = (BIND $ptascii("extraBooleanUnaryOwner245") n_cell) :: S.ENV]',
    '$heap_owners($heap_graph(S_two_owners),HCELL n_cell) = 2',
    '~$lossy_mixed_parameter_ready(S_two_owners,0,n_cell,n_bits)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    'S_first.TODO = [TYPE_RECEIVE porigin 1]',
])
previous = 'S_first'
for index, label, boolean, operand, result in VALUES:
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[n_local_{label}] = DEFINED (PINT {result})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_zero,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias245")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for index, label, boolean, operand, result in VALUES:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL n_local_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_local_{label}) = 0',
    ])
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

# Pure derived controls are distinct from source comparisons and reached state.
base, one = constant('E_WARNING'), constant('E_ERROR')
greater = binary('Greater', base, one)
equal = binary('Identical', base, one)
positive = [
    (greater, 'true'),
    (equal, 'false'),
    (node('NExprBooleanNot', base), 'false'),
    (node('NExprBooleanNot', equal), 'true'),
    (node('NExprCastBool', binary('Minus', base, one)), 'true'),
    (node('NExprCastBool', string('0')), 'false'),
    (node('NExprCastBool', string('0.0')), 'true'),
    (node('NExprCastBool', string('')), 'false'),
    (binary('BooleanAnd', greater, binary('Smaller', one, base)), 'true'),
    (binary('BooleanOr', equal, binary('Greater', one, base)), 'false'),
    (binary('LogicalXor', greater, equal), 'true'),
    (binary('BooleanOr', greater, constant('E_STRICT')), 'true'),
    (binary('BooleanAnd', equal, constant('E_STRICT')), 'false'),
    (binary('Identical', constant('NAN'), constant('NAN')), 'false'),
]
derived = []
for expression, boolean in positive:
    parent = node('NExprUnaryMinus', expression)
    result = '$(-1)' if boolean == 'true' else '0'
    derived.extend([
        rf'$lossy_optional_integer_boolean_shape({expression}) /\ ~$lossy_optional_integer_selection_shape({expression})',
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_condition($plempty(false),{expression}) = ({boolean})',
        f'$lossy_optional_integer_numeric($plempty(false),{parent}) = (NINT {result})',
    ])
for expression in [node('NExprBooleanNot', constant('NAN')),
                   node('NExprCastBool', constant('NAN')),
                   binary('BooleanAnd', greater, constant('E_STRICT')),
                   binary('BooleanOr', equal, constant('E_STRICT')),
                   binary('LogicalXor', greater, constant('E_STRICT')),
                   constant('true'), constant('false'), constant('null')]:
    derived.append(f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryMinus", expression)}) = eps')
derived.append(f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryMinus", string("2.5"))}) = (NFLOAT 13836183955189006336)')
for expression, _ in positive[:6]:
    derived.append(f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryPlus", expression)}) = eps')
selected = node('NExprTernary', greater, string('-0.0'), constant('UnknownBooleanUnary245'))
derived.extend([
    rf'$lossy_optional_integer_selection_shape({selected}) /\ ~$lossy_optional_integer_boolean_shape({selected})',
    f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryMinus", selected)}) = (NFLOAT 0)',
    '$typed_conversion([(PTBRANCH ([PTBUILTIN "int"]))],PINT $(-1),true) = TYPEVALUE (PINT $(-1))',
    '$typed_conversion([(PTBRANCH ([PTBUILTIN "int"]))],PINT 0,true) = TYPEVALUE (PINT 0)',
    f'~$lossy_optional_integer_quiet_shape({binary("BooleanOr", greater, node("NExprArrayDimFetch", string("12"), "NScalarInt (INTEGER 0) eps"))})',
])


if __name__ == '__main__':
    import closure_call_protocol as protocol

    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
    for row in rows.values():
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    cases = {
        'computed-boolean-unary-minus-named-front': {
            'source': rows['computed-boolean-unary-minus-alias-named-reentry']['source'],
            'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                      '-- if S.CURRENT = (pcallcontext) -- if pcallcontext.HOLES = [1,2,3]'),
            'checks': checks,
        },
        'computed-boolean-unary-minus-derived-boundaries': {
            'source': '<?php ;',
            'stage': r'S.COMPLETION = NORMAL /\ S.TODO = eps',
            'checks': derived,
        },
    }
    protocol.run(cases, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
