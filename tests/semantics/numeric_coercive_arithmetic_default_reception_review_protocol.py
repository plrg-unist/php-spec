#!/usr/bin/env python3
"""Independent quiet arithmetic defaults preserve typed caches and named receives."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('numeric_coercive_arithmetic_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [(1, 'sum', 'Plus', 'ADD', 'NINT 3', 'PINT 3', 3),
          (2, 'difference', 'Minus', 'SUBTRACT', 'NFLOAT 4613937818241073152',
           'PFLOAT 4613937818241073152', 3),
          (3, 'product', 'Mul', 'MULTIPLY', 'NINT 2', 'PINT 2', 2),
          (4, 'zero', 'Div', 'DIVIDE', 'NINT 0', 'PINT 0', 0)]

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("ArithmeticAlias241")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base241"),$ptascii("E_WARNING")),($ptascii("One241"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_sum,psparam_difference,psparam_product,psparam_zero,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_sum.BYREF /\ ~psparam_difference.BYREF /\ ~psparam_product.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_last.BYREF',
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
for index, label, constructor, operator, number, value, integer in VALUES:
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
        f'expression_{label} = NExprBinaryOp{constructor} expression_{label}_left expression_{label}_right metadata_{label}',
        rf'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_left) = eps \/ $lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_right) = eps',
        f'$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_{label}_left) = (pnumber_{label}_left)',
        f'$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_{label}_right) = (pnumber_{label}_right)',
        f'$power_warning_number($number_value(pnumber_{label}_left)) = (pnumber_{label}_left)',
        f'$power_warning_number($number_value(pnumber_{label}_right)) = (pnumber_{label}_right)',
        f'$number_binary({operator},pnumber_{label}_left,pnumber_{label}_right) = NUM ({number})',
        f'$power_warning_number($number_value({number})) = ({number})',
    ])
checks.extend([
    'expression_sum_right = NScalarString (BYTES "IDIg") metadata_sum_right',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_sum_right) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_sum_right) = ([32,50,32])',
    '$coerce_number(PSTRING ([32,50,32])) = COERCED (NINT 2) false',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_sum_left) = (NINT 1)',
    '$call_name_count(pcode.NAMES,pcpath_sum ++ [PCFIELD 6,PCFIELD 0]) = 1',
    'expression_difference_left = NScalarString (BYTES "NS4w") metadata_difference_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_difference_left) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_difference_left) = ([53,46,48])',
    '$coerce_number(PSTRING ([53,46,48])) = COERCED (NFLOAT 4617315517961601024) false',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_difference_right) = (NINT 2)',
    '$call_name_count(pcode.NAMES,pcpath_difference ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_product_left) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_product_right) = eps',
    '$lossy_optional_integer_special(pfunction.ENV,expression_product_right) = (PBOOL true)',
    '$coerce_number(PBOOL true) = COERCED (NINT 1) false',
    '$call_name_count(pcode.NAMES,pcpath_product ++ [PCFIELD 6,PCFIELD 0]) = 1',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = (PNULL)',
    '$coerce_number(PNULL) = COERCED (NINT 0) false',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_right) = (NINT 2)',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias241")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_sum[.VALUE = PINT 9])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_float_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_difference[.VALUE = PINT 3])]',
    '$default_caches_valid(S_wrong_float_tag,S_wrong_float_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_float_tag,pfunction,2)',
    'S_wrong_int_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_sum[.VALUE = PFLOAT 4613937818241073152])]',
    '$default_caches_valid(S_wrong_int_tag,S_wrong_int_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_int_tag,pfunction,1)',
    'S_wrong_null_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PNULL])]',
    '$default_caches_valid(S_wrong_null_tag,S_wrong_null_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_null_tag,pfunction,4)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_sum])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2,3]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Base241"),$ptascii("E_WARNING")),($ptascii("One241"),$ptascii("E_WARNING"))])]',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_sum) = (NINT 4)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_sum)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_sum (NExprArrayDimFetch expression_sum (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'S_first = $write_name(S,psparam_first.NAME,PINT 1)[.TODO = [TYPE_RECEIVE porigin 1]][.ORIGIN = (porigin)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
])
previous = 'S_first'
for index, label, constructor, operator, number, value, integer in VALUES:
    cell = f'n_local_{label}'
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[{cell}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_zero,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias241")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for index, label, constructor, operator, number, value, integer in VALUES:
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
# Promote only the two affected peer240 helper clauses, without replaying source.
for operator, left, right, expected in [
        ('Plus', string('2'), one, 'NINT 3'),
        ('Mul', constant('true'), one, 'NINT 1'),
]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary(operator,left,right)}) = ({expected})')
# The same new arithmetic arm composes through existing truth and FLOAT casts.
# These nine affected peer213/215/216/218 clauses retain zero old-source credit.
for suffix in (213, 215, 216, 218):
    checks.append(f'plenv_old{suffix} = $plempty(false)[.CONSTANTS = [($ptascii("YesReceive{suffix}"),$ptascii("true")),($ptascii("NoReceive{suffix}"),$ptascii("false")),($ptascii("NilReceive{suffix}"),$ptascii("null"))]]')
for expression in [binary('Plus',constant('YesReceive213'),'NScalarInt (INTEGER 1) eps'),
                   binary('Plus',string('1'),'NScalarInt (INTEGER 1) eps')]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_old213,{expression}) = (NINT 2)')
checks.append(f'$lossy_optional_integer_numeric(plenv_old216,{binary("Plus",constant("YesReceive216"),"NScalarInt (INTEGER 1) eps")}) = (NINT 2)')
for expression, number in [
        (binary('Plus',constant('YesReceive215'),'NScalarFloat (FLOAT "3fe0000000000000") eps'),
         'NFLOAT 4609434218613702656'),
        (binary('Mul',string('2'),'NScalarInt (INTEGER 1) eps'),'NINT 2'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_old215,{expression}) = ({number})',
        f'$lossy_optional_integer_condition(plenv_old215,{expression}) = (true)',
    ])
for expression, number in [
        (binary('Plus',constant('YesReceive218'),'NScalarInt (INTEGER 1) eps'),
         'NFLOAT 4611686018427387904'),
        (binary('Mul',string('2'),'NScalarInt (INTEGER 2) eps'),'NFLOAT 4616189618054758400'),
]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_old218,NExprCastDouble ({expression}) eps) = ({number})')
for child, expected in [
        (string('2'), 'NINT 2'), (string('2.0'), 'NFLOAT 4611686018427387904'),
        (constant('true'), 'NINT 1'), (constant('false'), 'NINT 0'),
        (constant('null'), 'NINT 0'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric($plempty(false),{child}) = eps',
        f'$lossy_optional_integer_quiet_operand($plempty(false),{child}) = ({expected})',
        f'$lossy_optional_integer_power_operand($plempty(false),{child}) = ({expected})',
    ])
for operator, left, right, expected in [
        ('Plus', string('2'), base, 'NINT 4'),
        ('Plus', base, string('2.0'), 'NFLOAT 4616189618054758400'),
        ('Minus', string('5'), base, 'NINT 3'),
        ('Minus', base, string('5'), 'NINT $(-3)'),
        ('Mul', constant('null'), base, 'NINT 0'),
        ('Mul', base, string('-0.0'), 'NFLOAT 9223372036854775808'),
        ('Div', string('6'), base, 'NINT 3'),
        ('Div', string('5'), base, 'NFLOAT 4612811918334230528'),
        ('Div', base, string('2.0'), 'NFLOAT 4607182418800017408'),
        ('Div', string('-0.0'), base, 'NFLOAT 9223372036854775808'),
        ('Plus', string('9223372036854775807'), one, 'NFLOAT 4890909195324358656'),
        ('Minus', string('-9223372036854775808'), one, 'NFLOAT 14114281232179134464'),
        ('Div', string('-9223372036854775808'), f'NExprUnaryMinus ({one}) eps', 'NFLOAT 4890909195324358656'),
        ('Pow', string('2'), base, 'NINT 4'),
]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary(operator,left,right)}) = ({expected})')
for operator in ('Plus', 'Minus', 'Mul', 'Div'):
    for left, right in [
            (string('2tail'), base), (base, string('2tail')),
            (string('none'), zero), (zero, string('none')),
            (constant('E_STRICT'), string('2')), (string('2'), constant('E_STRICT')),
            ('NScalarFloat (FLOAT "10000000000000000") eps', constant('true')),
            (constant('true'), 'NScalarFloat (FLOAT "10000000000000000") eps'),
            ('NScalarInt (INTEGER 9223372036854775808) eps', constant('true')),
            (constant('true'), 'NScalarInt (INTEGER 9223372036854775808) eps'),
    ]:
        checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary(operator,left,right)}) = eps')
for right in [constant('null'), constant('false'), string('0'), string('-0.0')]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary("Div",base,right)}) = eps')
for child in [string('2tail'), string('none'), constant('E_STRICT')]:
    checks.append(f'$lossy_optional_integer_quiet_operand($plempty(false),{child}) = eps')

CASES = {
    'numeric-coercive-arithmetic-alias-named-reentry': {
        'source': ROWS['numeric-coercive-arithmetic-default-alias-named-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
