#!/usr/bin/env python3
"""Independent Numeric integer powers at actual named warning reentry."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('numeric_power_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("PowerAlias237")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base237"),$ptascii("E_WARNING")),($ptascii("One237"),$ptascii("E_ERROR")),($ptascii("Bottom237"),$ptascii("PHP_INT_MIN"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_power,psparam_nested,psparam_selected,psparam_zero,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_power.BYREF /\ ~psparam_nested.BYREF /\ ~psparam_selected.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 6 /\ pcallcontext.HOLES = [1,2,3,4]',
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
    '$default_parameter_origin(S,porigin,5) = PORIGIN n_unit pcpath_last',
    '$default_at(pfunction.DEFAULTS,5) = ({INDEX 5,ORIGIN PORIGIN n_unit (pcpath_last ++ [PCFIELD 6]),KIND PDSTORED})',
    '$compiled_read(S,PORIGIN n_unit (pcpath_last ++ [PCFIELD 6])) = (PINT 7)',
    'S.CODE = [pcode]',
]
for index, label, value in [(1, 'power', 4), (2, 'nested', 4),
                            (3, 'selected', -9223372036854775808), (4, 'zero', 0)]:
    integer = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {integer})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {integer})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {integer},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PINT {integer})',
        rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
    ])
checks.extend([
    'expression_power = NExprBinaryOpPow expression_base expression_fqn_warning metadata_power',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_base) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_fqn_warning) = (NINT 2)',
    '$call_name_count(pcode.NAMES,pcpath_power ++ [PCFIELD 6,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_power ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'expression_nested = NExprBinaryOpPow expression_inner expression_one metadata_nested',
    'expression_inner = NExprBinaryOpPow expression_base_left expression_base_right metadata_inner',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_base_left) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_base_right) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_inner) = (NINT 4)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one) = (NINT 1)',
    '$call_name_count(pcode.NAMES,pcpath_nested ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_nested ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_nested ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'expression_selected = NExprTernary expression_condition expression_bottom_power expression_skipped metadata_selected',
    'expression_condition = NExprBinaryOpPow expression_condition_base (NScalarInt (INTEGER 0) metadata_exponent_zero) metadata_condition',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition_base) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition) = (NINT 1)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (true)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_skipped) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_bottom_power)',
    'expression_bottom_power = NExprBinaryOpPow expression_bottom expression_selected_one metadata_bottom_power',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_bottom) = (NINT $(-9223372036854775808))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_selected_one) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_bottom_power) = (NINT $(-9223372036854775808))',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selected) = eps',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$compiled_read(S,PORIGIN n_unit (pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1])) = (PINT 0)',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 1,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 1,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 2]) = 1',
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_skipped metadata_zero',
    'expression_zero_left = NExprBinaryOpPow expression_zero_base expression_zero_exponent metadata_zero_left',
    'expression_zero_base = NExprBinaryOpMinus expression_zero_base_left expression_zero_base_right metadata_zero_base',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_base_left) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_base_right) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_base) = (NINT 0)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_exponent) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero_left) = (false)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_skipped) = eps',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias237")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_power[.VALUE = PINT 9])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_power[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_power])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2,3]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Base237"),$ptascii("E_NOTICE"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_power)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_power (NExprArrayDimFetch expression_power (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
])
previous = 'S_first'
for index, label, value in [(1, 'power', 4), (2, 'nested', 4),
                            (3, 'selected', -9223372036854775808), (4, 'zero', 0)]:
    integer = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[n_{label}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_zero,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias237")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for label in ['power', 'nested', 'selected', 'zero']:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL n_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_{label}) = 0',
    ])
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])


def constant(name):
    encoded = base64.b64encode(name.encode()).decode()
    return f'NExprConstFetch (NName (BYTES "{encoded}") eps) eps'


def binary(operator, left, right):
    return f'NExprBinaryOp{operator} ({left}) ({right}) eps'


base = constant('E_WARNING')
one = constant('E_ERROR')
negative_one = f'NExprUnaryMinus ({one}) eps'
negative_base = f'NExprUnaryMinus ({base}) eps'
maximum = constant('PHP_INT_MAX')
minimum = constant('PHP_INT_MIN')
zero = binary('Minus', base, base)
for left, right, value in [
        (base, 'NScalarInt (INTEGER 0) eps', 1),
        (zero, 'NScalarInt (INTEGER 0) eps', 1),
        (minimum, one, -9223372036854775808),
        (maximum, one, 9223372036854775807),
        (negative_one, maximum, -1),
        (one, maximum, 1),
        (negative_base, 'NScalarInt (INTEGER 3) eps', -8),
        (negative_base, 'NScalarInt (INTEGER 63) eps', -9223372036854775808),
        (base, 'NScalarInt (INTEGER 62) eps', 4611686018427387904),
]:
    expression = binary('Pow', left, right)
    integer = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_default_in($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = (NINT {integer})',
    ])
for left, right, expected in [
        (base, negative_one, 'eps'), (zero, negative_one, 'eps'),
        (negative_one, negative_one, 'eps'),
        (base, 'NScalarInt (INTEGER 63) eps', '(NFLOAT 4890909195324358656)'),
        (minimum, base, 'eps'),
        (base, binary('Pow', base, 'NScalarInt (INTEGER 63) eps'), '(NFLOAT 9218868437227405312)'),
        ('NScalarInt (INTEGER 9223372036854775808) eps', one, 'eps'),
        (base, 'NScalarInt (INTEGER 9223372036854775808) eps', 'eps'),
]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", left, right)}) = {expected}')
for child in ['NScalarFloat (FLOAT "4000000000000000") eps',
              'NScalarString (BYTES "Mg==") eps', constant('true'), constant('null'),
              constant('E_STRICT'),
              binary('Plus', maximum, 'NScalarInt (INTEGER 1) eps')]:
    expected_right = '(NFLOAT 9218868437227405312)' if child == binary('Plus', maximum, 'NScalarInt (INTEGER 1) eps') else 'eps'
    checks.extend([
        f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", child, one)}) = eps',
        f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", base, child)}) = {expected_right}',
    ])

CASES = {
    'numeric-power-alias-named-reentry': {
        'source': ROWS['numeric-power-default-alias-named-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE),
                 runner_flags=('--sl',))
