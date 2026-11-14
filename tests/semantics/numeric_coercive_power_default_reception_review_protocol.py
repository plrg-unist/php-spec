#!/usr/bin/env python3
"""Independent quiet POWER coercions retain scalar identity and raw caches."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('numeric_coercive_power_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [(1, 'integer', 'NINT 4', 'PINT 4', 4),
          (2, 'root', 'NFLOAT 4611686018427387904', 'PFLOAT 4611686018427387904', 2),
          (3, 'falseZero', 'NINT 1', 'PINT 1', 1),
          (4, 'nullOne', 'NINT 0', 'PINT 0', 0)]

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("CoercivePowerAlias240")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base240"),$ptascii("E_WARNING")),($ptascii("One240"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_root,psparam_falseZero,psparam_nullOne,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_integer.BYREF /\ ~psparam_root.BYREF /\ ~psparam_falseZero.BYREF /\ ~psparam_nullOne.BYREF /\ ~psparam_last.BYREF',
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
    '$default_parameter_origin(S,porigin,5) = PORIGIN n_source_unit pcpath_last',
    '$default_at(pfunction.DEFAULTS,5) = ({INDEX 5,ORIGIN PORIGIN n_source_unit (pcpath_last ++ [PCFIELD 6]),KIND PDSTORED})',
    '$compiled_read(S,PORIGIN n_source_unit (pcpath_last ++ [PCFIELD 6])) = (PINT 7)',
    'S.CODE = [pcode]',
]
for index, label, number, value, integer in VALUES:
    cell = f'n_local_{label}'
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_source_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_source_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = ({number})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = ({value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = ({cell})',
        f'S.STORE[{cell}] = DEFINED ({value})',
        rf'~({cell} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL {cell}) = 1',
        f'expression_{label} = NExprBinaryOpPow expression_{label}_left expression_{label}_right metadata_{label}',
        rf'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_left) = eps \/ $lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_right) = eps',
        f'$lossy_optional_integer_power_operand(pfunction.ENV,expression_{label}_left) = (pnumber_{label}_left)',
        f'$lossy_optional_integer_power_operand(pfunction.ENV,expression_{label}_right) = (pnumber_{label}_right)',
        f'$power_warning_number($number_value(pnumber_{label}_left)) = (pnumber_{label}_left)',
        f'$power_warning_number($number_value(pnumber_{label}_right)) = (pnumber_{label}_right)',
        f'$num_pow(pnumber_{label}_left,pnumber_{label}_right) = ({number},false)',
        f'$power_warning_number($number_value({number})) = ({number})',
    ])
checks.extend([
    'expression_integer_left = NScalarString (BYTES "IDIg") metadata_integer_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_integer_left) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_integer_left) = ([32,50,32])',
    '$coerce_number(PSTRING ([32,50,32])) = COERCED (NINT 2) false',
    '$call_name_count(pcode.NAMES,pcpath_integer ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'expression_root_left = NExprBinaryOpPlus expression_root_alias_left expression_root_alias_right metadata_root_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_root_left) = (NINT 4)',
    'expression_root_right = NScalarString (BYTES "MC41") metadata_root_right',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_root_right) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_root_right) = ([48,46,53])',
    '$coerce_number(PSTRING ([48,46,53])) = COERCED (NFLOAT 4602678819172646912) false',
    '$power_prepare(pnumber_root_left,pnumber_root_right) = POWERGENERAL 4607182418800017408 4616189618054758400 4602678819172646912 0 false',
    '$call_name_count(pcode.NAMES,pcpath_root ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_root ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_falseZero_left) = eps',
    '$lossy_optional_integer_special(pfunction.ENV,expression_falseZero_left) = (PBOOL false)',
    '$coerce_number(PBOOL false) = COERCED (NINT 0) false',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_falseZero_right) = (NINT 0)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nullOne_left) = eps',
    '$lossy_optional_integer_special(pfunction.ENV,expression_nullOne_left) = (PNULL)',
    '$coerce_number(PNULL) = COERCED (NINT 0) false',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nullOne_right) = (NINT 1)',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias240")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_root[.VALUE = PFLOAT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,2)',
    'S_wrong_float_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_root[.VALUE = PINT 2])]',
    '$default_caches_valid(S_wrong_float_tag,S_wrong_float_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_float_tag,pfunction,2)',
    'S_wrong_int_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PFLOAT 4616189618054758400])]',
    '$default_caches_valid(S_wrong_int_tag,S_wrong_int_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_int_tag,pfunction,1)',
    'S_wrong_bool_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_falseZero[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_wrong_bool_tag,S_wrong_bool_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_bool_tag,pfunction,3)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_root])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,2)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,2)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2,3]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,2)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Base240"),$ptascii("E_WARNING")),($ptascii("One240"),$ptascii("E_WARNING"))])]',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_falseZero) = (NINT 1)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_falseZero)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],3)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_root (NExprArrayDimFetch expression_root (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
])
previous = 'S_first'
for index, label, number, value, integer in VALUES:
    cell = f'n_local_{label}'
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[{cell}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_nullOne,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias240")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for index, label, number, value, integer in VALUES:
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


def string(text):
    encoded = base64.b64encode(text.encode()).decode()
    return f'NScalarString (BYTES "{encoded}") eps'


def binary(operator, left, right):
    return f'NExprBinaryOp{operator} ({left}) ({right}) eps'


base = constant('E_WARNING')
one = constant('E_ERROR')
zero = binary('Minus', one, one)
negative_one = f'NExprUnaryMinus ({one}) eps'
# Only these eleven old peer expectations change; no old source is executed.
for left, right, expected in [
        (string('2'), one, 'NINT 2'), (base, string('2'), 'NINT 4'),
        (constant('true'), one, 'NINT 1'), (base, constant('true'), 'NINT 2'),
        (constant('null'), one, 'NINT 0'), (base, constant('null'), 'NINT 1'),
        (string('2'), zero, 'NINT 1'),
        (constant('true'), zero, 'NINT 1'), (constant('null'), zero, 'NINT 1'),
        (string('2'), negative_one, 'NFLOAT 4602678819172646912'),
        (constant('true'), negative_one, 'NFLOAT 4607182418800017408'),
]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", left, right)}) = ({expected})')
# Numeric identity stays separate from operation-specific quiet coercion.
for child, expected in [
        (string('2'), 'NINT 2'), (string('2.0'), 'NFLOAT 4611686018427387904'),
        (constant('true'), 'NINT 1'), (constant('false'), 'NINT 0'),
        (constant('null'), 'NINT 0'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric($plempty(false),{child}) = eps',
        f'$lossy_optional_integer_power_operand($plempty(false),{child}) = ({expected})',
    ])
checks.extend([
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", string("2.0"), zero)}) = (NFLOAT 4607182418800017408)',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", base, constant("false"))}) = (NINT 1)',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Plus", string("2"), one)}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Mul", constant("true"), one)}) = eps',
    '$coerce_number(PSTRING ([50,116,97,105,108])) = COERCED (NINT 2) true',
    '$coerce_number(PSTRING ([110,111,110,101])) = BADNUMBER',
    '$num_pow(NINT 0,NINT $(-1)) = (NFLOAT 9218868437227405312,true)',
])
for left, right in [
        (string('2tail'), base), (string('none'), zero),
        (constant('null'), negative_one), (constant('false'), negative_one),
        (string('0'), negative_one), (constant('E_STRICT'), one),
        ('NScalarFloat (FLOAT "10000000000000000") eps', constant('true')),
        (constant('true'), 'NScalarFloat (FLOAT "10000000000000000") eps'),
        ('NScalarInt (INTEGER 9223372036854775808) eps', constant('true')),
        (constant('true'), 'NScalarInt (INTEGER 9223372036854775808) eps'),
]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow", left, right)}) = eps')
for child in [string('2tail'), string('none'), constant('E_STRICT')]:
    checks.append(f'$lossy_optional_integer_power_operand($plempty(false),{child}) = eps')

CASES = {
    'numeric-coercive-power-alias-named-reentry': {
        'source': ROWS['numeric-coercive-power-default-alias-named-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
