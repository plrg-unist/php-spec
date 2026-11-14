#!/usr/bin/env python3
"""Independent Boolean operand typing, source authority and named reception."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('computed_boolean_operand_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [(1, 'sum', 'Plus', 'NINT 3', 3, 'true'),
          (2, 'power', 'Pow', 'NINT 1', 1, 'true'),
          (3, 'xor', 'Plus', 'NINT 2', 2, 'false'),
          (4, 'disjunction', 'Plus', 'NINT 3', 3, 'true')]
checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BooleanOperandAlias242")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base242"),$ptascii("E_WARNING")),($ptascii("One242"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_sum,psparam_power,psparam_xor,psparam_disjunction,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_sum.BYREF /\ ~psparam_power.BYREF /\ ~psparam_xor.BYREF /\ ~psparam_disjunction.BYREF /\ ~psparam_last.BYREF',
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
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit_source]',
]
for index, label, constructor, number, integer, boolean in VALUES:
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
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {integer})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {integer},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = ({cell})',
        f'S.STORE[{cell}] = DEFINED (PINT {integer})',
        rf'~({cell} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL {cell}) = 1',
        f'expression_{label} = NExprBinaryOp{constructor} expression_{label}_left expression_{label}_right metadata_{label}',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_left) = eps',
        f'$lossy_optional_integer_boolean_shape(expression_{label}_left)',
        f'$lossy_optional_integer_condition(pfunction.ENV,expression_{label}_left) = ({boolean})',
        f'$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_{label}_left) = (NINT {1 if boolean == "true" else 0})',
        f'$lossy_optional_integer_power_operand(pfunction.ENV,expression_{label}_left) = (NINT {1 if boolean == "true" else 0})',
        f'S_bool_cache_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PBOOL {boolean}])]',
        f'$default_caches_valid(S_bool_cache_{label},S_bool_cache_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_bool_cache_{label},pfunction,{index})',
    ])
checks.extend([
    'expression_sum_left = NExprBinaryOpGreater expression_sum_base expression_sum_one metadata_sum_compare',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_sum_base) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_sum_one) = (NINT 1)',
    'expression_power_left = NExprBinaryOpNotIdentical expression_power_one expression_power_base metadata_power_compare',
    'expression_xor_left = NExprBinaryOpLogicalXor expression_xor_base expression_xor_one metadata_xor_child',
    'expression_disjunction_left = NExprBinaryOpBooleanOr expression_disjunction_condition expression_disjunction_skipped metadata_or',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_disjunction_condition) = (true)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_disjunction_skipped) = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias242")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_sum[.VALUE = PINT 9])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_float_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_sum[.VALUE = PFLOAT 4613937818241073152])]',
    '$default_caches_valid(S_float_cache,S_float_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_float_cache,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_sum])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2,3]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Base242"),$ptascii("E_ERROR")),($ptascii("One242"),$ptascii("E_WARNING"))])]',
    '$lossy_optional_integer_condition(plenv_wrong,expression_sum_left) = (false)',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_sum) = (NINT 1)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_sum)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'pcpath_sum_base = pcpath_sum ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]',
    '$origin_node(S.SOURCES,PORIGIN n_source_unit pcpath_sum_base) = (expression_sum_base)',
    'S_forged_source = S[.SOURCES = [pcunit_source[.OCCURRENCES = (PCOCCURRENCE pcpath_sum_base expression_sum_one) :: pcunit_source.OCCURRENCES]]]',
    '$origin_node(S_forged_source.SOURCES,PORIGIN n_source_unit pcpath_sum_base) = (expression_sum_one)',
    '~$lossy_optional_integer_deferred_bindings(S_forged_source,pfunction.ENV,porigin_sum)',
    '~$lossy_optional_integer_deferred(S_forged_source,pfunction,1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    'S_two_owners = S[.ENV = (BIND $ptascii("extraBooleanOwner242") n_cell) :: S.ENV]',
    '$heap_owners($heap_graph(S_two_owners),HCELL n_cell) = 2',
    '$lossy_mixed_parameter_source_valid(S_two_owners,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_two_owners,0,n_cell,n_bits)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'S_first = $write_name(S,psparam_first.NAME,PINT 1)[.TODO = [TYPE_RECEIVE porigin 1]][.ORIGIN = (porigin)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
])
previous = 'S_first'
for index, label, constructor, number, integer, boolean in VALUES:
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_disjunction,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias242")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for index, label, constructor, number, integer, boolean in VALUES:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL n_local_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_local_{label}) = 0',
    ])
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])


def node(constructor, *children):
    return constructor + ' ' + ' '.join(f'({child})' for child in children) + ' eps'


def constant(name):
    encoded = base64.b64encode(name.encode()).decode()
    return f'NExprConstFetch (NName (BYTES "{encoded}") eps) eps'


def integer(value):
    return f'NScalarInt (INTEGER {value}) eps'


def string(text):
    encoded = base64.b64encode(text.encode()).decode()
    return f'NScalarString (BYTES "{encoded}") eps'


def binary(operator, left, right):
    return node('NExprBinaryOp' + operator, left, right)


one, two, zero = integer(1), integer(2), integer(0)
true = binary('Smaller', one, two)
false = binary('Identical', one, 'NScalarFloat (FLOAT "3ff0000000000000") eps')
predicates = [
    (node('NExprBooleanNot', zero), True),
    (node('NExprBooleanNot', one), False),
    (node('NExprCastBool', string('0')), False),
    (node('NExprCastBool', string('00')), True),
    (binary('BooleanAnd', true, false), False),
    (binary('BooleanOr', false, true), True),
    (binary('LogicalAnd', false, constant('E_STRICT')), False),
    (binary('LogicalOr', true, constant('E_STRICT')), True),
    (binary('LogicalXor', true, true), False),
    (binary('Equal', one, 'NScalarFloat (FLOAT "3ff0000000000000") eps'), True),
    (false, False), (binary('NotIdentical', one, two), True),
    (binary('Greater', one, two), False),
    (binary('SmallerOrEqual', two, two), True),
    (binary('GreaterOrEqual', two, two), True),
    (binary('Equal', constant('NAN'), constant('NAN')), False),
    (binary('NotEqual', constant('NAN'), constant('NAN')), True),
]
for expression, truth in predicates:
    checks.extend([
        f'$lossy_optional_integer_boolean_shape({expression})',
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_condition($plempty(false),{expression}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_quiet_operand($plempty(false),{expression}) = (NINT {int(truth)})',
    ])
for operator, left, right, expected in [
        ('Plus', true, two, 'NINT 3'), ('Plus', two, false, 'NINT 2'),
        ('Minus', false, two, 'NINT $(-2)'), ('Minus', two, true, 'NINT 1'),
        ('Mul', two, true, 'NINT 2'), ('Mul', false, two, 'NINT 0'),
        ('Div', two, true, 'NINT 2'), ('Div', false, two, 'NINT 0'),
        ('Div', true, two, 'NFLOAT 4602678819172646912'),
        ('Plus', string('2.5'), false, 'NFLOAT 4612811918334230528'),
        ('Pow', two, true, 'NINT 2'), ('Pow', two, false, 'NINT 1'),
        ('Pow', true, two, 'NINT 1'), ('Pow', false, two, 'NINT 0')]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary(operator,left,right)}) = ({expected})')
for expression in [node('NExprCastBool', constant('NAN')),
                   node('NExprBooleanNot', constant('NAN')),
                   binary('Greater', binary('Plus', string('2tail'), one), two),
                   binary('Greater', constant('E_STRICT'), one),
                   binary('BooleanOr', false, constant('E_STRICT')),
                   binary('BooleanAnd', true, constant('E_STRICT')),
                   binary('LogicalXor', true, constant('E_STRICT'))]:
    checks.extend([
        f'$lossy_optional_integer_boolean_shape({expression})',
        f'$lossy_optional_integer_condition($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_quiet_operand($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_numeric($plempty(false),{binary("Plus",two,expression)}) = eps',
    ])
for selection in [node('NExprTernary', constant('true'), true, constant('UnknownBoolean242')),
                  binary('Coalesce', true, constant('UnknownBoolean242'))]:
    checks.extend([
        f'$lossy_optional_integer_condition($plempty(false),{selection}) = (true)',
        f'~$lossy_optional_integer_boolean_shape({selection})',
        f'$lossy_optional_integer_quiet_operand($plempty(false),{selection}) = eps',
    ])
for expression in [binary('Div', two, false),
                   binary('Pow', false, node('NExprUnaryMinus', one)),
                   binary('Plus', true, constant('E_STRICT'))]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{expression}) = eps')
dimension = node('NExprBooleanNot', node('NExprArrayDimFetch', string('0'), zero))
checks.extend([
    f'$lossy_optional_integer_quiet_operand($plempty(false),{dimension}) = (NINT 1)',
    f'~$lossy_optional_integer_quiet_shape({binary("Plus",two,dimension)})',
])

CASES = {'computed-boolean-operand-alias-named-reentry': {
    'source': ROWS['computed-boolean-operand-default-alias-named-reentry']['source'],
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
