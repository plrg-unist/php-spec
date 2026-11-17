#!/usr/bin/env python3
"""Independent ordered numeric relations, unordered NaNs and current type scope."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_numeric_relational_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 13',
    r'pcallcontext.ARGC = 0 /\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
operands = [
    ('NExprBinaryOpSmaller', 'PINT 0', 'PINT 1', 'true'),
    ('NExprBinaryOpSmallerOrEqual', 'PFLOAT 0', 'PFLOAT 0', 'true'),
    ('NExprBinaryOpGreater', 'PINT 1', 'PFLOAT 0', 'true'),
    ('NExprBinaryOpGreaterOrEqual', 'PFLOAT 0', 'PINT 1', 'false'),
    ('NExprBinaryOpGreaterOrEqual', 'PINT 9223372036854775807', 'PFLOAT 4890909195324358656', 'true'),
    ('NExprBinaryOpGreater', 'PFLOAT 4890909195324358656', 'PINT 9223372036854775807', 'false'),
    ('NExprBinaryOpSmaller', 'PFLOAT n_bits_6_left', 'PFLOAT 0', 'false'),
    ('NExprBinaryOpSmallerOrEqual', 'PFLOAT 0', 'PFLOAT n_bits_7_right', 'false'),
    ('NExprBinaryOpGreater', 'PFLOAT n_bits_8_left', 'PINT 0', 'false'),
    ('NExprBinaryOpGreaterOrEqual', 'PINT 0', 'PFLOAT n_bits_9_right', 'false'),
    ('NExprBinaryOpGreater', 'PFLOAT 9218868437227405312', 'PFLOAT 0', 'true'),
    ('NExprBinaryOpSmaller', 'PFLOAT 18442240474082181120', 'PFLOAT 0', 'true'),
    ('NExprBinaryOpGreaterOrEqual', 'PFLOAT n_bits_12_left', 'PFLOAT n_bits_12_right', 'false'),
]
for index, (constructor, left, right, truth) in enumerate(operands):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.KIND = PDDEFERRED',
        f'$default_parameter_origin(S,porigin_function,{index}) = PORIGIN n_unit pcpath_parameter_{index}',
        f'pcpath_{index} = pcpath_parameter_{index} ++ [PCFIELD 6]',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (expression_{index})',
        f'expression_{index} = {constructor} expression_left_{index} expression_right_{index} metadata_{index}',
        f'porigin_left_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_right_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'$origin_node(S.SOURCES,porigin_left_{index}) = (expression_left_{index})',
        f'$origin_node(S.SOURCES,porigin_right_{index}) = (expression_right_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {truth},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'psparam_{index} = pfunction.SIGNATURE.PARAMETERS[{index}]',
        f'$lookup(S.ENV,psparam_{index}.NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED (PBOOL {truth})',
        f'S_own_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{index} z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_own_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{index} (PBOOL {truth}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
for index, (_, left, right, _) in enumerate(operands):
    for field, value in enumerate([left, right]):
        raw.append(f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{"left" if field == 0 else "right"}_{index})')
        nan = 'n_bits_' in value
        if not nan and (index, field) not in [(10, 0), (11, 0)]:
            continue
        side = 'left' if field == 0 else 'right'
        raw += [
            f'{"" if nan else "~"}$pfcast_nan({value})',
            f'$origin_node(S.SOURCES,porigin_{side}_{index}) = (NExprBinaryOpPlus expression_special_{index}_{side} expression_zero_{index}_{side} metadata_special_{index}_{side})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD {field}]) = ((z_special_{index}_{side},false))',
            rf'$pool_value(S.POOLS,porigin_{side}_{index}) = eps /\ $compiled_read(S,porigin_{side}_{index}) = eps',
            f'$compiled_redirect(S,porigin_{side}_{index}) = eps',
        ]
raw.append('n_bits_12_left = n_bits_12_right')
for index, side, field in [(index, side, field) for index in (0, 7, 8, 9) for side, field in [('left', 0), ('right', 1)]]:
    raw += [
        f'S_{side}_{index}_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_{index} ++ [PCFIELD {field}]) z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_{index}_code,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_{side}_{index}_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD {field}]) (NExprBooleanNot expression_{side}_{index} metadata_{index}))] ++ pcunit.OCCURRENCES)]]]',
        f'~$lossy_optional_integer_phase_safe(S_{side}_{index}_source,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_{index}_source,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
raw += [
    'S_no_code = S[.CODE = eps]',
    '$lossy_optional_integer_deferred_value_at(S_no_code,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_0.ORIGIN) = (PBOOL true)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(13):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')


chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
integer = f'((int)({chain}))'
boolean = f'((bool)({chain}))'
nan = f'(NAN + ({chain}))'
unsupported_pairs = [
    ('<', 'NExprBinaryOpSmaller', boolean, f'({chain})', 'PBOOL false', 'PFLOAT 0'),
    ('<=', 'NExprBinaryOpSmallerOrEqual', f'({chain})', boolean, 'PFLOAT 0', 'PBOOL false'),
    ('>', 'NExprBinaryOpGreater', boolean, nan, 'PBOOL false', 'PFLOAT n_nan_2'),
    ('>=', 'NExprBinaryOpGreaterOrEqual', nan, boolean, 'PFLOAT n_nan_3', 'PBOOL false'),
    ('<', 'NExprBinaryOpSmaller', 'NULL', integer, None, 'PINT 0'),
    ('>', 'NExprBinaryOpGreater', integer, '"0"', 'PINT 0', None),
]
unsupported = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 6',
]
for index, (_, constructor, _, _, left, right) in enumerate(unsupported_pairs):
    unsupported += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
    ]
    for field, value in enumerate([left, right]):
        expected = 'eps' if value is None else f'({value})'
        unsupported.append(f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])) = {expected}')
    if index in (2, 3):
        unsupported.append(f'$pfcast_nan(PFLOAT n_nan_{index})')
    admitted = {0: 'false', 1: 'true', 2: 'false', 3: 'true'}.get(index)
    unsupported += [
        (f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {admitted})'
         if admitted is not None else
         f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps'),
        (f'$lossy_optional_integer_deferred(S,pfunction,{index})' if admitted is not None else
         f'~$lossy_optional_integer_deferred(S,pfunction,{index})'),
    ]

zero_pairs = [
    ('NExprBinaryOpSmaller', f'({chain})', f'(-({chain}))', 'PFLOAT 0', 'PFLOAT 9223372036854775808', 'false', '<'),
    ('NExprBinaryOpSmallerOrEqual', f'(-({chain}))', f'({chain})', 'PFLOAT 9223372036854775808', 'PFLOAT 0', 'true', '<='),
    ('NExprBinaryOpGreater', f'({chain})', f'(-({chain}))', 'PFLOAT 0', 'PFLOAT 9223372036854775808', 'false', '>'),
    ('NExprBinaryOpGreaterOrEqual', f'(-({chain}))', f'({chain})', 'PFLOAT 9223372036854775808', 'PFLOAT 0', 'true', '>='),
]
zero = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 4',
]
for index, (constructor, _, _, left, right, truth, _) in enumerate(zero_pairs):
    zero += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
    ]

CASES = {
    'deferred-numeric-relational-wrapper-raw-booleans': {
        'source': ROWS['deferred-numeric-relational-wrapper-raw-booleans']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 13 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-numeric-relational-wrapper-current-unsupported-kinds': {
        'source': '<?php function refused282(' + ', '.join(
            f'$p{index} = ({left} {operator} {right})'
            for index, (operator, _, left, right, _, _) in enumerate(unsupported_pairs)
        ) + ') {} refused282();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6'),
        'checks': unsupported,
    },
    'deferred-numeric-relational-wrapper-derived-opposite-zero': {
        'source': '<?php function zeros282(' + ', '.join(
            f'$p{index} = ({left} {operator} {right})'
            for index, (_, left, right, _, _, _, operator) in enumerate(zero_pairs)
        ) + ') {} zeros282();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 4'),
        'checks': zero,
    },
    'deferred-numeric-relational-wrapper-runtime-result-control': {
        'source': '<?php $left282 = NAN; echo $left282 > 0;',
        'stage': ('S.TODO = (BINARY_RIGHT GREATER poperand_left z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PINT 0)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("left282")) = (n_left)',
            'S.STORE[n_left] = DEFINED (PFLOAT 9221120237041090560)',
            'S_read = $resolve_at(S,poperand_left,z)',
            'S_read.RESULT = KNOWN (PFLOAT 9221120237041090560)',
            'S_after = $drive_steps(S,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PBOOL false)',
            'S_after.TODO = ptask_tail*',
            'S_done = $drive_steps(S_after,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
