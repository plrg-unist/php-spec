#!/usr/bin/env python3
"""Independent Numeric MOD/shift defaults at actual named warning reentry."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('numeric_integer_operator_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("IntOpsAlias236")',
    'pfunction.ENV.CONSTANTS = [($ptascii("All236"),$ptascii("E_ALL")),($ptascii("Word236"),$ptascii("PHP_INT_SIZE")),($ptascii("Flag236"),$ptascii("E_WARNING"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_mod,psparam_shifted,psparam_selected,psparam_zero,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_mod.BYREF /\ ~psparam_shifted.BYREF /\ ~psparam_selected.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_last.BYREF',
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
for index, label, value in [(1, 'mod', 7), (2, 'shifted', -2),
                            (3, 'selected', 32), (4, 'zero', 0)]:
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
    'expression_mod = NExprBinaryOpMod expression_all expression_word metadata_mod',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_all) = (NINT 30719)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_word) = (NINT 8)',
    '$call_name_count(pcode.NAMES,pcpath_mod ++ [PCFIELD 6,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_mod ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'expression_shifted = NExprBinaryOpShiftRight expression_not_flag expression_error metadata_shifted',
    'expression_not_flag = NExprBitwiseNot expression_flag metadata_not_flag',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_flag) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_not_flag) = (NINT $(-3))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_error) = (NINT 1)',
    '$call_name_count(pcode.NAMES,pcpath_shifted ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_shifted ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'expression_selected = NExprTernary expression_condition expression_skipped expression_left metadata_selected',
    'expression_condition = NExprBinaryOpMod expression_all_left expression_all_right metadata_condition',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_all_left) = (NINT 30719)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_all_right) = (NINT 30719)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (false)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_skipped) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_left)',
    'expression_left = NExprBinaryOpShiftLeft expression_selected_word expression_selected_flag metadata_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_selected_word) = (NINT 8)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_selected_flag) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_left) = (NINT 32)',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selected) = eps',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 2,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 2,PCFIELD 1]) = 1',
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_skipped metadata_zero',
    'expression_zero_left = NExprBinaryOpShiftRight expression_word_left expression_word_right metadata_zero_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_word_left) = (NINT 8)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_word_right) = (NINT 8)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero_left) = (false)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_skipped) = eps',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 1]) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias236")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_mod[.VALUE = PINT 8])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_mod[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_mod])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2,3]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("All236"),$ptascii("E_NOTICE"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_mod)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_mod (NExprArrayDimFetch expression_mod (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
])
previous = 'S_first'
for index, label, value in [(1, 'mod', 7), (2, 'shifted', -2),
                            (3, 'selected', 32), (4, 'zero', 0)]:
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
    '$lookup(S_done.ENV,$ptascii("xAlias236")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for label in ['mod', 'shifted', 'selected', 'zero']:
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


word = constant('PHP_INT_SIZE')
error = constant('E_ERROR')
negative_error = f'NExprUnaryMinus ({error}) eps'
maximum = constant('PHP_INT_MAX')
minimum = constant('PHP_INT_MIN')
for operator, left, right, value in [
        ('Mod', minimum, negative_error, 0),
        ('Mod', f'NExprUnaryMinus ({constant("E_ALL")}) eps', word, -7),
        ('Mod', constant('E_ALL'), f'NExprUnaryMinus ({word}) eps', 7),
        ('ShiftLeft', minimum, error, 0),
        ('ShiftLeft', maximum, 'NScalarInt (INTEGER 63) eps', -9223372036854775808),
        ('ShiftLeft', constant('E_ALL'), 'NScalarInt (INTEGER 65) eps', 0),
        ('ShiftRight', minimum, 'NScalarInt (INTEGER 64) eps', -1),
        ('ShiftRight', maximum, 'NScalarInt (INTEGER 64) eps', 0),
        ('ShiftRight', maximum, 'NScalarInt (INTEGER 0) eps', 9223372036854775807),
]:
    expression = binary(operator, left, right)
    integer = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_default_in($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = (NINT {integer})',
    ])
checks.extend([
    f'$lossy_optional_integer_numeric($plempty(false),{binary("Mod", word, "NScalarInt (INTEGER 0) eps")}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("ShiftLeft", word, negative_error)}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{binary("ShiftRight", word, negative_error)}) = eps',
])
for operator in ['Mod', 'ShiftLeft', 'ShiftRight']:
    for child in ['NScalarFloat (FLOAT "4000000000000000") eps',
                  'NScalarString (BYTES "Mg==") eps', constant('true'), constant('null'),
                  constant('E_STRICT'),
                  binary('Plus', maximum, 'NScalarInt (INTEGER 1) eps')]:
        checks.append(f'$lossy_optional_integer_numeric($plempty(false),{binary(operator, child, error)}) = eps')

CASES = {
    'numeric-integer-operator-alias-named-reentry': {
        'source': ROWS['numeric-integer-operator-default-alias-named-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE),
                 runner_flags=('--sl',))
