#!/usr/bin/env python3
"""Independent Boolean ordering, integer spaceship tags and quiet NaNs."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_numeric_comparison_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

operands = [
    ('NExprBinaryOpSmaller', 'PBOOL false', 'PBOOL true', 'PBOOL true'),
    ('NExprBinaryOpSmallerOrEqual', 'PBOOL true', 'PBOOL false', 'PBOOL false'),
    ('NExprBinaryOpGreater', 'PBOOL true', 'PBOOL false', 'PBOOL true'),
    ('NExprBinaryOpGreaterOrEqual', 'PBOOL false', 'PBOOL true', 'PBOOL false'),
    ('NExprBinaryOpSpaceship', 'PBOOL false', 'PBOOL true', 'PINT $(-1)'),
    ('NExprBinaryOpSmaller', 'PBOOL false', 'PINT 1', 'PBOOL true'),
    ('NExprBinaryOpSmallerOrEqual', 'PBOOL false', 'PFLOAT 9223372036854775808', 'PBOOL true'),
    ('NExprBinaryOpGreater', 'PBOOL true', 'PFLOAT 9218868437227405312', 'PBOOL false'),
    ('NExprBinaryOpGreaterOrEqual', 'PBOOL false', 'PFLOAT n_bits_8_right', 'PBOOL false'),
    ('NExprBinaryOpSpaceship', 'PBOOL true', 'PFLOAT n_bits_9_right', 'PINT 0'),
    ('NExprBinaryOpSmaller', 'PFLOAT 0', 'PBOOL false', 'PBOOL false'),
    ('NExprBinaryOpSmallerOrEqual', 'PFLOAT 9223372036854775808', 'PBOOL true', 'PBOOL true'),
    ('NExprBinaryOpGreater', 'PFLOAT 18442240474082181120', 'PBOOL false', 'PBOOL true'),
    ('NExprBinaryOpGreaterOrEqual', 'PFLOAT n_bits_13_left', 'PBOOL true', 'PBOOL true'),
    ('NExprBinaryOpSpaceship', 'PFLOAT n_bits_14_left', 'PBOOL false', 'PINT 1'),
    ('NExprBinaryOpGreaterOrEqual', 'PINT 9223372036854775807', 'PBOOL false', 'PBOOL true'),
]
base = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
]
raw = base + [
    '|pfunction.SIGNATURE.PARAMETERS| = 16',
    r'pcallcontext.ARGC = 0 /\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, (constructor, left, right, result) in enumerate(operands):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.KIND = PDDEFERRED',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {result},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({result})',
    ]
    for field, value in enumerate([left, right]):
        if 'n_bits_' in value:
            raw += [
                f'$pfcast_nan({value})',
                f'porigin_nan_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])',
                f'$origin_node(S.SOURCES,porigin_nan_{index}) = (NExprBinaryOpPlus expression_nan_{index} expression_zero_{index} metadata_nan_{index})',
                f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_nan_{index})',
                f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD {field}]) = ((z_nan_{index},false))',
                rf'$pool_value(S.POOLS,porigin_nan_{index}) = eps /\ $compiled_read(S,porigin_nan_{index}) = eps',
                f'$compiled_redirect(S,porigin_nan_{index}) = eps',
            ]
for index in (0, 2, 5, 7, 10, 12):
    raw += [
        f'S_own_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{index} z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_own_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{index} (PINT 0))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
    for side, field in [('left', 0), ('right', 1)]:
        raw += [
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])) = (expression_{side}_{index})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}]))',
            f'S_{side}_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_{index} ++ [PCFIELD {field}]) z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
            f'$lossy_optional_integer_deferred_value_at(S_{side}_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
            f'S_{side}_source_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD {field}]) (NExprBooleanNot expression_{side}_{index} metadata_{index}))] ++ pcunit.OCCURRENCES)]]]',
            f'~$lossy_optional_integer_phase_safe(S_{side}_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
            f'$lossy_optional_integer_deferred_value_at(S_{side}_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        ]
raw += [
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_4[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,4)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_14.ORIGIN) = (PINT 1)',
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
quiet_pairs = [
    (False, '<', False, 'PBOOL true'),
    (False, '>', True, 'PBOOL true'),
    (True, '>=', False, 'PBOOL true'),
    (True, '<=', True, 'PBOOL true'),
    (False, '<=>', False, 'PINT $(-1)'),
    (True, '<=>', True, 'PINT 0'),
]
quiet = base + [
    '|pfunction.SIGNATURE.PARAMETERS| = 6',
    'S.ERRORHANDLER.CALLBACK = (pvalue_handler)',
    '$error_handler_eligible(S,2)',
    'S.EVENTS = eps',
]
quiet_defaults = []
for index, (b, operator, reverse, result) in enumerate(quiet_pairs):
    value = f'(!{boolean})' if b else boolean
    left, right = (nan, value) if reverse else (value, nan)
    quiet_defaults.append(f'$p{index} = ({left} {operator} {right})')
    quiet += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = ({{ORIGIN pdefault_{index}.ORIGIN,VALUE {result},CLASS PVSCALAR}})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
        f'S.STORE[n_quiet_{index}] = DEFINED ({result})',
    ]
quiet += [
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
    'S_done.EVENTS = eps',
    'S_done.ERRORHANDLER = S.ERRORHANDLER',
    '$heap_valid($heap_graph(S_done))',
]
refused_pairs = [(boolean, '<=>', 'NULL'), ('NULL', '<', boolean),
                 (boolean, '>', '"1"'), ('"0"', '<=>', boolean)]
refused = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4']
for index in range(4):
    admitted = {0: 'PINT 0', 1: 'PBOOL false'}.get(index)
    refused += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        (f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({admitted})'
         if admitted is not None else
         f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps'),
        (f'$lossy_optional_integer_deferred(S,pfunction,{index})' if admitted is not None else
         f'~$lossy_optional_integer_deferred(S,pfunction,{index})'),
    ]

stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-boolean-numeric-comparison-wrapper-raw-orderings': {
        'source': ROWS['deferred-boolean-numeric-comparison-wrapper-raw-orderings']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 16 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': raw,
    },
    'deferred-boolean-numeric-comparison-wrapper-derived-quiet-handler': {
        'source': ('<?php function quietHandler284($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults284(' + ', '.join(quiet_defaults) + ') {} '
                   'set_error_handler("quietHandler284"); quietDefaults284();'),
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': quiet,
    },
    'deferred-boolean-numeric-comparison-wrapper-current-unsupported-kinds': {
        'source': '<?php function refused284(' + ', '.join(f'$p{index} = ({left} {operator} {right})'
            for index, (left, operator, right) in enumerate(refused_pairs)) + ') {} refused284();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4',
        'checks': refused,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
