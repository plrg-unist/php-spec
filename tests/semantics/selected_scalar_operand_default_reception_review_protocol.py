#!/usr/bin/env python3
"""Independent selected-value, raw-cache and named-receive checks."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('selected_scalar_operand_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [(1, 'integer', 'Plus', 'left', 'NINT 2', 'NINT 3', 'PINT 3', 3),
          (2, 'zero', 'Mul', 'left', 'NINT 0', 'NINT 0', 'PINT 0', 0),
          (3, 'floating', 'Plus', 'left', 'NFLOAT 4611686018427387904',
           'NFLOAT 4613937818241073152', 'PFLOAT 4613937818241073152', 3),
          (4, 'power', 'Pow', 'right', 'NINT 1', 'NINT 2', 'PINT 2', 2)]

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("SelectionAlias243")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base243"),$ptascii("E_WARNING")),($ptascii("One243"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_zero,psparam_floating,psparam_power,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_integer.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_floating.BYREF /\ ~psparam_power.BYREF /\ ~psparam_last.BYREF',
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
for index, label, constructor, side, operand, number, value, integer in VALUES:
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
        f'expression_{label}_selection = expression_{label}_{side}',
        f'$lossy_optional_integer_selection_shape(expression_{label}_selection)',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_selection) = eps',
        f'$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_{label}_selection) = (expression_{label}_leaf)',
        f'expression_{label}_leaf =/= expression_{label}_selection',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_leaf) = eps',
        f'$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_{label}_selection) = ({operand})',
        f'$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_{label}_leaf) = ({operand})',
        f'S_bool_cache_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PBOOL false])]',
        f'$default_caches_valid(S_bool_cache_{label},S_bool_cache_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_bool_cache_{label},pfunction,{index})',
    ])
checks.extend([
    'expression_integer_selection = NExprTernary expression_integer_condition expression_integer_leaf expression_integer_skipped metadata_integer_selection',
    'expression_integer_condition = NExprBinaryOpGreater expression_integer_base expression_integer_one metadata_integer_condition',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_integer_base) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_integer_one) = (NINT 1)',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_integer_leaf) = ([32,50,32])',
    'expression_zero_selection = NExprBinaryOpCoalesce expression_zero_coalesced expression_zero_skipped metadata_zero_selection',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero_coalesced) = (expression_zero_leaf)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_leaf) = (PBOOL false)',
    '$lossy_optional_integer_default_in(pfunction.ENV,NExprCastInt expression_zero_leaf metadata_zero_selection) = (0)',
    'expression_floating_selection = NExprBinaryOpCoalesce expression_floating_coalesced expression_floating_leaf metadata_floating_selection',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_floating_coalesced) = (expression_floating_null)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_floating_null) = (PNULL)',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_floating_leaf) = ([50,46,48])',
    'expression_power_selection = NExprTernary expression_power_leaf ABSENT expression_power_skipped metadata_power_selection',
    '$lossy_optional_integer_boolean_shape(expression_power_leaf)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_power_leaf) = (true)',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias243")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PINT 9])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_float = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_floating[.VALUE = PINT 3])]',
    '$default_caches_valid(S_wrong_float,S_wrong_float.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_float,pfunction,3)',
    'S_wrong_integer = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PFLOAT 4613937818241073152])]',
    '$default_caches_valid(S_wrong_integer,S_wrong_integer.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_integer,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_integer])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2,3]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Base243"),$ptascii("E_ERROR")),($ptascii("One243"),$ptascii("E_WARNING"))])]',
    '$lossy_optional_integer_condition(plenv_wrong,expression_integer_condition) = (false)',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_integer) = (NINT 2)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_integer)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'pcpath_integer_base = pcpath_integer ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0,PCFIELD 0]',
    '$origin_node(S.SOURCES,PORIGIN n_source_unit pcpath_integer_base) = (expression_integer_base)',
    'S_forged_source = S[.SOURCES = [pcunit_source[.OCCURRENCES = (PCOCCURRENCE pcpath_integer_base expression_integer_one) :: pcunit_source.OCCURRENCES]]]',
    '~$lossy_optional_integer_deferred_bindings(S_forged_source,pfunction.ENV,porigin_integer)',
    '~$lossy_optional_integer_deferred(S_forged_source,pfunction,1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    'S_two_owners = S[.ENV = (BIND $ptascii("extraSelectionOwner243") n_cell) :: S.ENV]',
    '$heap_owners($heap_graph(S_two_owners),HCELL n_cell) = 2',
    '~$lossy_mixed_parameter_ready(S_two_owners,0,n_cell,n_bits)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'S_first = $write_name(S,psparam_first.NAME,PINT 1)[.TODO = [TYPE_RECEIVE porigin 1]][.ORIGIN = (porigin)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
])
previous = 'S_first'
for index, label, constructor, side, operand, number, value, integer in VALUES:
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_power,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias243")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for index, label, constructor, side, operand, number, value, integer in VALUES:
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
    return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") eps) eps'


def string(text):
    return f'NScalarString (BYTES "{base64.b64encode(text.encode()).decode()}") eps'


def binary(operator, left, right):
    return node('NExprBinaryOp' + operator, left, right)


one, two = 'NScalarInt (INTEGER 1) eps', 'NScalarInt (INTEGER 2) eps'
true = binary('Smaller', one, two)
false = binary('Identical', one, 'NScalarFloat (FLOAT "3ff0000000000000") eps')
unknown = constant('UnknownSelection243')
selections = [
    (node('NExprTernary', true, string('2'), unknown), 'NINT 2'),
    (node('NExprTernary', false, unknown, string('2.0')), 'NFLOAT 4611686018427387904'),
    (node('NExprTernary', string('00'), 'ABSENT', unknown), 'NINT 0'),
    (node('NExprTernary', string('0'), 'ABSENT', string('3')), 'NINT 3'),
    (node('NExprTernary', string('2.5'), 'ABSENT', unknown), 'NFLOAT 4612811918334230528'),
    (node('NExprTernary', true, string('-0.0'), unknown), 'NFLOAT 9223372036854775808'),
    (binary('Coalesce', constant('false'), unknown), 'NINT 0'),
    (binary('Coalesce', constant('null'), string('2.0')), 'NFLOAT 4611686018427387904'),
    (binary('Coalesce', string('0'), unknown), 'NINT 0'),
    (binary('Coalesce', string('2.5'), unknown), 'NFLOAT 4612811918334230528'),
    (node('NExprTernary', true, binary('Coalesce', constant('null'), string('2')), unknown), 'NINT 2'),
]
for expression, expected in selections:
    checks.extend([
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_quiet_operand($plempty(false),{expression}) = ({expected})',
    ])
# Exactly the two affected peer242 formulas, without replaying its campaign.
for expression in [node('NExprTernary', constant('true'), true, constant('UnknownBoolean242')),
                   binary('Coalesce', true, constant('UnknownBoolean242'))]:
    checks.extend([
        f'$lossy_optional_integer_condition($plempty(false),{expression}) = (true)',
        f'~$lossy_optional_integer_boolean_shape({expression})',
        f'$lossy_optional_integer_quiet_operand($plempty(false),{expression}) = (NINT 1)',
    ])
for selection in [
        node('NExprTernary', true, string('2tail'), unknown),
        node('NExprTernary', true, string('bad'), unknown),
        node('NExprTernary', true, unknown, string('2')),
        node('NExprTernary', constant('E_STRICT'), string('2'), string('3')),
        node('NExprTernary', constant('NAN'), string('2'), string('3')),
        binary('Coalesce', constant('INF'), string('2')),
        binary('Coalesce', constant('NAN'), string('2')),
        binary('Coalesce', 'NScalarFloat (FLOAT "43e0000000000000") eps', string('2')),
]:
    checks.append(f'$lossy_optional_integer_quiet_operand($plempty(false),{selection}) = eps')
dimension = node('NExprArrayDimFetch', string('8'), 'NScalarInt (INTEGER 0) eps')
selection_dimension = node('NExprTernary', true, string('2'), dimension)
checks.extend([
    f'$lossy_optional_integer_quiet_operand($plempty(false),{selection_dimension}) = (NINT 2)',
    f'~$lossy_optional_integer_quiet_shape({binary("Plus",selection_dimension,one)})',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Div",two,binary("Coalesce",constant("false"),one))}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Pow",node("NExprTernary",true,constant("false"),unknown),node("NExprUnaryMinus",one))}) = eps',
])

CASES = {'selected-scalar-operand-alias-named-reentry': {
    'source': ROWS['selected-scalar-operand-default-alias-named-reentry']['source'],
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
