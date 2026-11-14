#!/usr/bin/env python3
"""Independent literal-special plus, integer tags and imported null-string composition."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('literal_special_unary_plus_default_reception_cases.json')


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
    'pfunction.NAME = ($ptascii("StoredSpecialPlusAlias249") ++ [92] ++ $ptascii("defaults249"))',
    'pfunction.ENV.NAMESPACE = $ptascii("StoredSpecialPlusAlias249")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base249"),$ptascii("E_WARNING")),($ptascii("One249"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_truth,psparam_joined,psparam_nullish,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_truth.BYREF /\ ~psparam_joined.BYREF /\ ~psparam_nullish.BYREF /\ ~psparam_last.BYREF',
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
]
for index, label, integer, special, operand in [(1, 'truth', '1', 'PBOOL true', '1'),
                                                (3, 'nullish', '0', 'PNULL', '0')]:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "int"',
        f'expression_{label} = NExprUnaryPlus expression_{label}_literal metadata_{label}_parent',
        f'$lossy_optional_integer_special(pfunction.ENV,expression_{label}_literal) = ({special})',
        f'$coerce_number({special}) = COERCED (NINT {operand}) false',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = ({integer})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {integer})',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_source_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_source_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        f'pdefault_{label} = {{INDEX {index},ORIGIN porigin_{label},KIND PDSTORED}}',
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'$pool_value(S.POOLS,porigin_{label}) = (PINT {integer})',
        f'$compiled_read(S,porigin_{label}) = (PINT {integer})',
        f'$default_current_cache(S,porigin_{label}) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$lossy_optional_integer_tail(S,pfunction,[psparam_{label}],{index})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'~(n_local_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_{label}) = 1',
    ])
checks.extend([
    'psparam_joined.DEFAULT = PSDEFAULT expression_joined "deferred"',
    '$default_parameter_origin(S,porigin,2) = PORIGIN n_source_unit pcpath_joined',
    'porigin_joined = PORIGIN n_source_unit (pcpath_joined ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,porigin_joined) = (expression_joined)',
    '$default_at(pfunction.DEFAULTS,2) = ({INDEX 2,ORIGIN porigin_joined,KIND PDDEFERRED})',
    r'$pool_value(S.POOLS,porigin_joined) = eps /\ $compiled_read(S,porigin_joined) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_joined) = (10)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_joined) = (NINT 10)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_joined) = (PINT 10)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_joined)',
    '$lossy_optional_integer_deferred(S,pfunction,2)',
    'pdefaultcache_joined = {ORIGIN porigin_joined,VALUE PINT 10,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_joined) = (pdefaultcache_joined)',
    '$lookup(S.ENV,psparam_joined.NAME) = (n_local_joined)',
    'S.STORE[n_local_joined] = DEFINED (PINT 10)',
    r'~(n_local_joined <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_joined) = 1',
    'expression_joined = NExprCastInt expression_concat metadata_joined_parent',
    'expression_concat = NExprBinaryOpConcat expression_prefix expression_suffix metadata_joined_concat',
    'expression_prefix = NExprCastString expression_difference_cast metadata_joined_prefix',
    'expression_difference_cast = NExprCastInt expression_difference metadata_joined_difference',
    'expression_suffix = NExprCastString expression_null_plus metadata_joined_suffix',
    'expression_null_plus = NExprUnaryPlus expression_null_literal metadata_joined_null',
    '$lossy_optional_integer_special(pfunction.ENV,expression_null_literal) = (PNULL)',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_null_plus) = (0)',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_prefix) = ([49])',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_suffix) = ([48])',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_concat) = ([49,48])',
    'S_no_pool = S[.POOLS = eps]',
    '$compiled_read(S_no_pool,porigin_truth) = eps',
    '~$lossy_optional_integer_tail(S_no_pool,pfunction,[psparam_truth],1)',
    'S_wrong_bool = S[.POOLS = [{UNIT n_source_unit,CONSTANTS ([(PCONSTANT (pcpath_nullish ++ [PCFIELD 6]) (PBOOL false))])}]]',
    '$compiled_read(S_wrong_bool,porigin_nullish) = (PBOOL false)',
    '~$lossy_optional_integer_tail(S_wrong_bool,pfunction,[psparam_nullish],3)',
    'S_wrong_null = S[.POOLS = [{UNIT n_source_unit,CONSTANTS ([(PCONSTANT (pcpath_nullish ++ [PCFIELD 6]) PNULL)])}]]',
    '$compiled_read(S_wrong_null,porigin_nullish) = (PNULL)',
    '~$lossy_optional_integer_tail(S_wrong_null,pfunction,[psparam_nullish],3)',
    'S_wrong_float = S[.POOLS = [{UNIT n_source_unit,CONSTANTS ([(PCONSTANT (pcpath_nullish ++ [PCFIELD 6]) (PFLOAT 0))])}]]',
    '$compiled_read(S_wrong_float,porigin_nullish) = (PFLOAT 0)',
    '~$lossy_optional_integer_tail(S_wrong_float,pfunction,[psparam_nullish],3)',
    'S_wrong_value = S[.POOLS = [{UNIT n_source_unit,CONSTANTS ([(PCONSTANT (pcpath_truth ++ [PCFIELD 6]) (PINT 0))])}]]',
    '~$lossy_optional_integer_tail(S_wrong_value,pfunction,[psparam_truth],1)',
    'expression_same_value = NScalarInt (INTEGER 1) eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_same_value) = (1)',
    '~$lossy_optional_integer_tail(S,pfunction,[psparam_truth[.DEFAULT = PSDEFAULT expression_same_value "int"]],1)',
    '~$lossy_optional_integer_tail(S,pfunction[.DEFAULTS = [pdefault_truth[.KIND = PDDEFERRED]]],[psparam_truth],1)',
    '~$lossy_optional_integer_tail(S[.SOURCES = eps],pfunction,[psparam_truth],1)',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_joined[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,2)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base249"),$ptascii("E_ERROR")),($ptascii("One249"),$ptascii("E_WARNING"))]]',
    '$lossy_optional_integer_default_in(plenv_wrong,expression_truth) = (1)',
    '$lossy_optional_integer_default_in(plenv_wrong,expression_joined) = ($(-10))',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_joined)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],2)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2]])],ptask_resume)',
    'S_two_owners = S[.ENV = (BIND $ptascii("extraSpecialOwner249") n_cell) :: S.ENV]',
    '$heap_owners($heap_graph(S_two_owners),HCELL n_cell) = 2',
    '~$lossy_mixed_parameter_ready(S_two_owners,0,n_cell,n_bits)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    'S_first.TODO = [TYPE_RECEIVE porigin 1]',
])
previous = 'S_first'
for index, label, integer in [(1, 'truth', '1'), (2, 'joined', '10'), (3, 'nullish', '0')]:
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_nullish,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias249")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_truth) = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_nullish) = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_joined) = (pdefaultcache_joined)',
])
for label in ('truth', 'joined', 'nullish'):
    checks.append(rf'~((HCELL n_local_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_local_{label}) = 0')
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

# These exact new boundary formulas carry fixture source0.
positive = lambda expression: node('NExprUnaryPlus', expression)
negate = lambda expression: node('NExprUnaryMinus', expression)
derived = []
for spelling, value in [('true', '1'), ('TrUe', '1'), ('false', '0'),
                        ('FALSE', '0'), ('null', '0'), ('NuLl', '0')]:
    expression = positive(constant(spelling))
    derived.extend([
        f'$lossy_optional_integer_default_in($plempty(false),{expression}) = ({value})',
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = (NINT {value})',
    ])
true_plus = positive(constant('true'))
false_plus = positive(constant('false'))
null_plus = positive(constant('null'))
for expression, expected in [(node('NExprCastString', null_plus), '[48]'),
                             (node('NExprCastString', constant('null')), 'eps'),
                             (node('NExprCastString', false_plus), '[48]'),
                             (node('NExprCastString', constant('false')), 'eps'),
                             (node('NExprCastString', true_plus), '[49]')]:
    derived.append(f'$lossy_optional_integer_string_in($plempty(false),{expression}) = ({expected})')
cast_null = node('NExprCastString', null_plus)
derived.extend([
    f'$lossy_optional_integer_string_in($plempty(false),{binary("Concat", string("1"), cast_null)}) = ([49,48])',
    f'$lossy_optional_integer_default_in($plempty(false),{node("NExprCastInt", binary("Concat", string("1"), cast_null))}) = (10)',
    f'$lossy_optional_integer_default_in($plempty(false),{negate(true_plus)}) = ($(-1))',
    f'$lossy_optional_integer_default_in($plempty(false),{positive(false_plus)}) = (0)',
    f'$lossy_optional_integer_default_in($plempty(false),{negate(null_plus)}) = (0)',
    f'$lossy_optional_integer_default_in($plempty(false),{binary("Plus", true_plus, "NScalarInt (INTEGER 2) eps")}) = (3)',
])
for child, integer in [(constant('PHP_ZTS'), None), (constant('PHP_DEBUG'), None),
                       (string('-2'), None), (string('-0.0'), None),
                       (binary('Greater', constant('E_WARNING'), constant('E_ERROR')), '1'),
                       (node('NExprCastBool', string('0.0')), '1'),
                       (node('NExprBooleanNot', constant('null')), '1'),
                       (binary('Coalesce', constant('null'), constant('true')), None)]:
    parent = positive(child)
    numeric = 'eps' if integer is None else f'(NINT {integer})'
    derived.extend([
        f'$lossy_optional_integer_default_in($plempty(false),{parent}) = eps',
        f'$lossy_optional_integer_numeric($plempty(false),{parent}) = {numeric}',
    ])
# Pin the pre-existing FLOAT phase split; it supplies no plus-source agreement.
floating = positive(node('NExprCastDouble', string('-0.0')))
derived.extend([
    f'$lossy_optional_integer_default_in($plempty(false),{floating}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{floating}) = (NFLOAT 9223372036854775808)',
    '$num_mul(NFLOAT 9223372036854775808,NINT 1) = NFLOAT 9223372036854775808',
    '$num_add(NINT 0,NFLOAT 9223372036854775808) = NFLOAT 0',
    f'~$lossy_optional_integer_quiet_shape({positive(node("NExprArrayDimFetch", string("1"), "NScalarInt (INTEGER 0) eps"))})',
])


if __name__ == '__main__':
    import closure_call_protocol as protocol

    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
    for row in rows.values():
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    cases = {
        'literal-special-unary-plus-named-stored-deferred-front': {
            'source': rows['literal-special-unary-plus-alias-composition-reentry']['source'],
            'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                      '-- if S.CURRENT = (pcallcontext) -- if pcallcontext.HOLES = [1,2,3]'),
            'checks': checks,
        },
        'literal-special-unary-plus-derived-boundaries': {
            'source': '<?php ;',
            'stage': r'S.COMPLETION = NORMAL /\ S.TODO = eps',
            'checks': derived,
        },
    }
    protocol.run(cases, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
