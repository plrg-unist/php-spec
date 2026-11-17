#!/usr/bin/env python3
"""Independent typed Boolean equality and quiet NaN default reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_numeric_equality_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

operands = [
    ('NExprBinaryOpEqual', 'PBOOL false', 'PBOOL false', 'true'),
    ('NExprBinaryOpNotEqual', 'PBOOL true', 'PBOOL false', 'true'),
    ('NExprBinaryOpEqual', 'PBOOL true', 'PBOOL false', 'false'),
    ('NExprBinaryOpNotEqual', 'PBOOL true', 'PBOOL true', 'false'),
    ('NExprBinaryOpEqual', 'PBOOL false', 'PINT 0', 'true'),
    ('NExprBinaryOpNotEqual', 'PINT 1', 'PBOOL true', 'false'),
    ('NExprBinaryOpEqual', 'PBOOL true', 'PINT 9223372036854775807', 'true'),
    ('NExprBinaryOpEqual', 'PINT 2', 'PBOOL true', 'true'),
    ('NExprBinaryOpEqual', 'PBOOL false', 'PFLOAT 9223372036854775808', 'true'),
    ('NExprBinaryOpNotEqual', 'PFLOAT 0', 'PBOOL false', 'false'),
    ('NExprBinaryOpEqual', 'PBOOL true', 'PFLOAT 9218868437227405312', 'true'),
    ('NExprBinaryOpNotEqual', 'PFLOAT 18442240474082181120', 'PBOOL true', 'false'),
    ('NExprBinaryOpEqual', 'PBOOL true', 'PFLOAT n_bits_12_right', 'true'),
    ('NExprBinaryOpNotEqual', 'PFLOAT n_bits_13_left', 'PBOOL true', 'false'),
    ('NExprBinaryOpNotEqual', 'PBOOL false', 'PFLOAT n_bits_14_right', 'true'),
    ('NExprBinaryOpEqual', 'PFLOAT n_bits_15_left', 'PBOOL false', 'false'),
]
raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 16',
    r'pcallcontext.ARGC = 0 /\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, (constructor, left, right, truth) in enumerate(operands):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.KIND = PDDEFERRED',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'porigin_left_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_right_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'$origin_node(S.SOURCES,porigin_left_{index}) = (expression_left_{index})',
        f'$origin_node(S.SOURCES,porigin_right_{index}) = (expression_right_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {truth},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'psparam_{index} = pfunction.SIGNATURE.PARAMETERS[{index}]',
        f'$lookup(S.ENV,psparam_{index}.NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED (PBOOL {truth})',
    ]
    for field, value in enumerate([left, right]):
        side = 'left' if field == 0 else 'right'
        safe = (index, field) == (8, 1)
        raw.append(f'{"" if safe else "~"}$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{side}_{index})')
        if 'n_bits_' in value:
            raw += [
                f'$pfcast_nan({value})',
                f'$origin_node(S.SOURCES,porigin_{side}_{index}) = (NExprBinaryOpPlus expression_nan_{index} expression_zero_{index} metadata_nan_{index})',
                f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD {field}]) = ((z_nan_{index},false))',
                rf'$pool_value(S.POOLS,porigin_{side}_{index}) = eps /\ $compiled_read(S,porigin_{side}_{index}) = eps',
                f'$compiled_redirect(S,porigin_{side}_{index}) = eps',
            ]
for index in (0, 4, 13):
    raw += [
        f'S_own_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{index} z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_own_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{index} (PBOOL true))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
    for side, field in [('left', 0), ('right', 1)]:
        raw += [
            f'S_{side}_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_{index} ++ [PCFIELD {field}]) z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
            f'$lossy_optional_integer_deferred_value_at(S_{side}_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
            f'S_{side}_source_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD {field}]) (NExprBooleanNot expression_{side}_{index} metadata_{index}))] ++ pcunit.OCCURRENCES)]]]',
            f'~$lossy_optional_integer_phase_safe(S_{side}_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
            f'$lossy_optional_integer_deferred_value_at(S_{side}_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        ]
raw += [
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 1])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_14.ORIGIN) = (PBOOL true)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(16):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
boolean = f'((bool)({chain}))'
nan = f'(NAN + ({chain}))'
quiet_pairs = [(b, op, reverse) for b in (False, True) for op in ('==', '!=') for reverse in (False, True)]
quiet = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 8',
    'S.ERRORHANDLER.CALLBACK = (pvalue_handler)',
    '$error_handler_eligible(S,2)',
    'S.EVENTS = eps',
]
quiet_defaults = []
for index, (b, op, reverse) in enumerate(quiet_pairs):
    value = f'(!{boolean})' if b else boolean
    left, right = (nan, value) if reverse else (value, nan)
    quiet_defaults.append(f'$p{index} = ({left} {op} {right})')
    truth = str(b == (op == '==')).lower()
    quiet += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = ({{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {truth},CLASS PVSCALAR}})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
        f'S.STORE[n_quiet_{index}] = DEFINED (PBOOL {truth})',
    ]
quiet += [
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
    'S_done.EVENTS = eps',
    'S_done.ERRORHANDLER = S.ERRORHANDLER',
    '$heap_valid($heap_graph(S_done))',
]
refused_pairs = [
    (boolean, 'NULL', 'NExprBinaryOpEqual', '=='),
    ('NULL', f'(!{boolean})', 'NExprBinaryOpNotEqual', '!='),
    (f'(!{boolean})', '"1"', 'NExprBinaryOpEqual', '=='),
    ('"0"', boolean, 'NExprBinaryOpNotEqual', '!='),
]
refused = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 4',
]
for index, (_, _, constructor, _) in enumerate(refused_pairs):
    refused += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        (f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL true)' if index < 2 else
         f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps'),
        (f'$lossy_optional_integer_deferred(S,pfunction,{index})' if index < 2 else
         f'~$lossy_optional_integer_deferred(S,pfunction,{index})'),
    ]

CASES = {
    'deferred-boolean-numeric-equality-wrapper-raw-booleans': {
        'source': ROWS['deferred-boolean-numeric-equality-wrapper-raw-booleans']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 16 -- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-boolean-numeric-equality-wrapper-derived-quiet-handler': {
        'source': ('<?php function quietHandler283($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults283(' + ', '.join(quiet_defaults) + ') {} '
                   'set_error_handler("quietHandler283"); quietDefaults283();'),
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': quiet,
    },
    'deferred-boolean-numeric-equality-wrapper-current-unsupported-kinds': {
        'source': '<?php function refused283(' + ', '.join(f'$p{index} = ({left} {operator} {right})'
            for index, (left, right, _, operator) in enumerate(refused_pairs)) + ') {} refused283();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 4'),
        'checks': refused,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
