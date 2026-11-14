#!/usr/bin/env python3
"""Independent completed FLOAT powers retain raw caches at named reentry."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('numeric_float_power_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [(1, 'unit', 4607182418800017408, 1), (2, 'zero', 0, 0),
          (3, 'selected', 9223372036854775808, 0), (4, 'nonnull', 0, 0)]

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("FloatPowerAlias238")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Infinite238"),$ptascii("INF")),($ptascii("Nan238"),$ptascii("NAN")),($ptascii("One238"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_unit,psparam_zero,psparam_selected,psparam_nonnull,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_unit.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_selected.BYREF /\ ~psparam_nonnull.BYREF /\ ~psparam_last.BYREF',
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
for index, label, bits, value in VALUES:
    cell = f'n_local_{label}'
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NFLOAT {bits})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PFLOAT {bits})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PFLOAT {bits},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = ({cell})',
        f'S.STORE[{cell}] = DEFINED (PFLOAT {bits})',
        rf'~({cell} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL {cell}) = 1',
    ])
checks.extend([
    'expression_unit = NExprBinaryOpPow expression_nan expression_unit_exponent metadata_unit',
    'expression_unit_exponent = NExprBinaryOpMinus expression_one_left expression_one_right metadata_unit_exponent',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nan) = (NFLOAT 9221120237041090560)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one_left) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one_right) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_unit_exponent) = (NINT 0)',
    '$power_prepare(NFLOAT 9221120237041090560,NINT 0) = POWERDONE (NFLOAT 4607182418800017408) false',
    '$call_name_count(pcode.NAMES,pcpath_unit ++ [PCFIELD 6,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_unit ++ [PCFIELD 6,PCFIELD 1,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_unit ++ [PCFIELD 6,PCFIELD 1,PCFIELD 1]) = 1',
    'expression_zero = NExprBinaryOpPow expression_infinite expression_negative_one metadata_zero',
    'expression_negative_one = NExprUnaryMinus expression_one metadata_negative_one',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_infinite) = (NFLOAT 9218868437227405312)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_negative_one) = (NINT $(-1))',
    '$power_prepare(NFLOAT 9218868437227405312,NINT $(-1)) = POWERDONE (NFLOAT 0) false',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 1,PCFIELD 0]) = 1',
    'expression_selected = NExprTernary expression_condition expression_negative_zero_power expression_skipped metadata_selected',
    'expression_condition = NExprBinaryOpPow expression_condition_nan expression_condition_exponent metadata_condition',
    'expression_condition_exponent = NExprBinaryOpMinus expression_condition_left expression_condition_right metadata_condition_exponent',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition_nan) = (NFLOAT 9221120237041090560)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition_left) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition_right) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition_exponent) = (NINT 0)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition) = (NFLOAT 4607182418800017408)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (true)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_skipped) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_negative_zero_power)',
    'expression_negative_zero_power = NExprBinaryOpPow expression_negative_zero expression_selected_one metadata_negative_zero_power',
    'expression_negative_zero = NExprUnaryMinus (NScalarFloat (FLOAT "0000000000000000") metadata_positive_zero) metadata_negative_zero',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_negative_zero) = (NFLOAT 9223372036854775808)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_selected_one) = (NINT 1)',
    '$power_prepare(NFLOAT 9223372036854775808,NINT 1) = POWERDONE (NFLOAT 9223372036854775808) false',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selected) = eps',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1,PCFIELD 1]) = 1',
    '$compiled_read(S,PORIGIN n_unit (pcpath_selected ++ [PCFIELD 6,PCFIELD 1,PCFIELD 0])) = (PFLOAT 9223372036854775808)',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 1,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 2]) = 1',
    'expression_nonnull = NExprBinaryOpCoalesce expression_nonnull_left expression_nonnull_skipped metadata_nonnull',
    'expression_nonnull_left = NExprBinaryOpPow (NScalarFloat (FLOAT "0000000000000000") metadata_nonnull_zero) expression_nonnull_one metadata_nonnull_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nonnull_one) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nonnull_left) = (NFLOAT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_nonnull_left) = (false)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_nonnull_left) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_nonnull) = (expression_nonnull_left)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nonnull_skipped) = eps',
    '$call_name_count(pcode.NAMES,pcpath_nonnull ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_nonnull ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias238")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_unit[.VALUE = PFLOAT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_unit[.VALUE = PINT 1])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_wrong_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_selected[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_sign,S_wrong_sign.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_sign,pfunction,3)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_unit])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2,3]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Infinite238"),$ptascii("INF")),($ptascii("Nan238"),$ptascii("INF")),($ptascii("One238"),$ptascii("E_ERROR"))])]',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_unit) = (NFLOAT 4607182418800017408)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_unit)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_unit (NExprArrayDimFetch expression_unit (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
])
previous = 'S_first'
for index, label, bits, value in VALUES:
    cell = f'n_local_{label}'
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[{cell}] = DEFINED (PINT {value})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_nonnull,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias238")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for index, label, bits, value in VALUES:
    cell = f'n_local_{label}'
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL {cell}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL {cell}) = 0',
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
maximum = constant('PHP_INT_MAX')
zero = binary('Minus', one, one)
# These three exact promoted clauses replace only the old 237 EPS expectations.
for exponent, bits in [
        ('NScalarInt (INTEGER 63) eps', 4890909195324358656),
        (binary('Pow', base, 'NScalarInt (INTEGER 63) eps'), 9218868437227405312),
        (binary('Plus', maximum, 'NScalarInt (INTEGER 1) eps'), 9218868437227405312),
]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", base, exponent)}) = (NFLOAT {bits})')
negative_float_one = 'NScalarFloat (FLOAT "bff0000000000000") eps'
nan_power = binary('Pow', f'NExprUnaryMinus ({base}) eps', 'NScalarFloat (FLOAT "3fe0000000000000") eps')
checks.extend([
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", negative_float_one, maximum)}) = (NFLOAT 4607182418800017408)',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", "NExprUnaryMinus (" + one + ") eps", maximum)}) = (NINT $(-1))',
    f'$lossy_optional_integer_numeric($plempty(false),{nan_power}) = (NFLOAT 18444492273895866368)',
    f'$lossy_optional_integer_condition($plempty(false),{nan_power}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", base, "NScalarInt (INTEGER 64) eps")}) = (NFLOAT 4895412794951729152)',
])
for left, right in [
        (zero, f'NExprUnaryMinus ({one}) eps'),
        ('NScalarFloat (FLOAT "10000000000000000") eps', zero),
        (base, 'NScalarFloat (FLOAT "10000000000000000") eps'),
        (constant('E_STRICT'), zero),
        ('NScalarString (BYTES "Mg==") eps', zero),
        (constant('true'), zero), (constant('null'), zero),
]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", left, right)}) = eps')

CASES = {
    'numeric-float-power-alias-named-reentry': {
        'source': ROWS['numeric-float-power-default-alias-named-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE),
                 runner_flags=('--sl',))
