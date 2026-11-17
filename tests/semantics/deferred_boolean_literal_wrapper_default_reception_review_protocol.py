#!/usr/bin/env python3
"""Independent Boolean leaf certificates and tagged default composition."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_literal_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

operands = [
    ('NExprBinaryOpEqual', 'false', 'PFLOAT 0', 'PBOOL true'),
    ('NExprBinaryOpNotEqual', 'false', 'PFLOAT 0', 'PBOOL false'),
    ('NExprBinaryOpEqual', 'true', 'PFLOAT n_nan_2', 'PBOOL true'),
    ('NExprBinaryOpNotEqual', 'true', 'PFLOAT n_nan_3', 'PBOOL false'),
    ('NExprBinaryOpSmaller', 'false', 'PFLOAT n_nan_4', 'PBOOL true'),
    ('NExprBinaryOpSmallerOrEqual', 'true', 'PFLOAT n_nan_5', 'PBOOL true'),
    ('NExprBinaryOpGreater', 'true', 'PFLOAT 9218868437227405312', 'PBOOL false'),
    ('NExprBinaryOpGreaterOrEqual', 'false', 'PFLOAT 18442240474082181120', 'PBOOL true'),
    ('NExprBinaryOpSpaceship', 'false', 'PBOOL true', 'PINT $(-1)'),
    ('NExprBinaryOpSpaceship', 'true', 'PBOOL false', 'PINT $(-1)'),
    ('NExprBinaryOpSpaceship', 'true', 'PFLOAT n_nan_10', 'PINT 0'),
    ('NExprBinaryOpSpaceship', 'false', 'PFLOAT n_nan_11', 'PINT 1'),
    ('NExprBinaryOpIdentical', 'false', 'PBOOL false', 'PBOOL true'),
    ('NExprBinaryOpNotIdentical', 'false', 'PBOOL true', 'PBOOL true'),
    ('NExprBinaryOpIdentical', 'true', 'PINT 1', 'PBOOL false'),
    ('NExprBinaryOpNotIdentical', 'false', 'PINT 0', 'PBOOL true'),
]
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 16', 'S.CODE = [pcode]',
              'S.SOURCES = [pcunit]', 'S.POOLS = [ppool]']
for index, (constructor, boolean, sibling, result) in enumerate(operands):
    field = index % 2
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.KIND = PDDEFERRED',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'porigin_bare_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])',
        f'porigin_sibling_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {1-field}])',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_bare_{index}) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_sibling_{index}) = ({sibling})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {result},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({result})',
    ]
    if 'n_nan_' in sibling:
        raw.append(f'$pfcast_nan({sibling})')
for index in (0, 3):
    _, boolean, _, result = operands[index]
    field = index % 2
    raw += [
        f'pcpath_bare_{index} = pcpath_{index} ++ [PCFIELD {field}]',
        f'$origin_node(S.SOURCES,porigin_bare_{index}) = (expression_bare_{index})',
        f'$lossy_optional_integer_special(pfunction.ENV,expression_bare_{index}) = (PBOOL {boolean})',
        f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_bare_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_bare_{index}) = ((z_bare_{index},true))',
        f'$compiled_read(S,porigin_bare_{index}) = (PBOOL {boolean})',
        f'S_bare_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_bare_{index} z_bare_{index} false)] ++ pcode.EXPRESSIONS)]]]',
        f'$compiled_read(S_bare_code_{index},porigin_bare_{index}) = eps',
        f'$lossy_optional_integer_phase_safe(S_bare_code_{index},pfunction.ENV,porigin_bare_{index})',
        f'$lossy_optional_integer_deferred_value_at(S_bare_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
        f'S_bare_source_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_bare_{index} (NExprBooleanNot expression_bare_{index} metadata_{index}))] ++ pcunit.OCCURRENCES)]]]',
        f'~$lossy_optional_integer_phase_safe(S_bare_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S_bare_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
    for tag, value in [('tag', 'PINT 1'), ('value', f'PBOOL {"true" if boolean == "false" else "false"}')]:
        raw += [
            f'S_bare_{tag}_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_bare_{index} ({value}))] ++ ppool.CONSTANTS)]]]',
            f'~$lossy_optional_integer_phase_safe(S_bare_{tag}_{index},pfunction.ENV,porigin_bare_{index})',
            f'$lossy_optional_integer_deferred_value_at(S_bare_{tag}_{index},pfunction.ENV,porigin_bare_{index}) = eps',
            f'$lossy_optional_integer_deferred_value_at(S_bare_{tag}_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        ]
raw += [
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 1])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_11.ORIGIN) = (PINT 1)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(16):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
nan = f'(NAN + ({chain}))'
quiet_defaults = [f'\\FALSE == ({chain})', f'{nan} <=> \\TRUE',
                  f'TrUe !== ((int)(!((bool)({chain}))))', f'((bool)({chain})) <=> fAlSe']
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4',
    'pfunction.ENV.NAMESPACE = $ptascii("BooleanLiteral285Peer")',
    'S.ERRORHANDLER.CALLBACK = (pvalue_handler)', '$error_handler_eligible(S,2)', 'S.EVENTS = eps']
for index, result in enumerate(['PBOOL true', 'PINT 0', 'PBOOL true', 'PINT 0']):
    quiet += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
        f'S.STORE[n_quiet_{index}] = DEFINED ({result})',
    ]
quiet += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
    'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
refused = base + ['|pfunction.SIGNATURE.PARAMETERS| = 2']
for index in range(2):
    refused += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
                f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
                f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-boolean-literal-wrapper-raw-tagged-results': {
        'source': ROWS['deferred-boolean-literal-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 16 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': raw,
    },
    'deferred-boolean-literal-wrapper-derived-qualified-quiet-handler': {
        'source': ('<?php namespace BooleanLiteral285Peer; '
                   'use const E_WARNING; use const E_ERROR; use const NAN; '
                   'function quietHandler285($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults285(' + ', '.join(f'$p{i} = ({s})' for i, s in enumerate(quiet_defaults)) + ') {} '
                   'set_error_handler("BooleanLiteral285Peer\\\\quietHandler285"); quietDefaults285();'),
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': quiet,
    },
    'deferred-boolean-literal-wrapper-current-unsupported-kinds': {
        'source': '<?php function refused285(' + ', '.join(
            f'$p{index} = ({left} {operator} ((int)({chain})))'
            for index, (left, operator) in enumerate([('NULL', '=='), ('"0"', '!=')])
        ) + ') {} refused285();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 2',
        'checks': refused,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
