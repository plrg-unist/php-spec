#!/usr/bin/env python3
"""Independent produced-string negation, raw-cache and quiet-coercion controls."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('produced_string_unary_minus_default_reception_cases.json')


def node(constructor, *children):
    return constructor + ' ' + ' '.join(f'({child})' for child in children) + ' eps'


def constant(name):
    return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") eps) eps'


def string(text):
    return f'NScalarString (BYTES "{base64.b64encode(text.encode()).decode()}") eps'


def binary(operator, left, right):
    return node('NExprBinaryOp' + operator, left, right)


checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = ($ptascii("StringUnaryAlias246") ++ [92] ++ $ptascii("defaults246"))',
    'pfunction.ENV.NAMESPACE = $ptascii("StringUnaryAlias246")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base246"),$ptascii("E_WARNING")),($ptascii("One246"),$ptascii("E_ERROR")),($ptascii("Eight246"),$ptascii("E_NOTICE"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_zero,psparam_floating,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_integer.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_floating.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 5 /\ pcallcontext.HOLES = [1,2,3]',
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
VALUES = [(1, 'integer', '[50,50]', 'NINT 22', 'NINT $(-22)', 'PINT $(-22)', '$(-22)'),
          (2, 'zero', '[45,48,46,48]', 'NFLOAT 9223372036854775808', 'NFLOAT 0', 'PFLOAT 0', '0'),
          (3, 'floating', '[48,46,48]', 'NFLOAT 0', 'NFLOAT 9223372036854775808', 'PFLOAT 9223372036854775808', '0')]
for index, label, payload, operand, number, value, integer in VALUES:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_source_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_source_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'expression_{label} = NExprUnaryMinus expression_{label}_string metadata_{label}_parent',
        rf'~$lossy_optional_integer_selection_shape(expression_{label}_string) /\ ~$lossy_optional_integer_boolean_shape(expression_{label}_string)',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_string) = eps',
        f'$lossy_optional_integer_string_in(pfunction.ENV,expression_{label}_string) = ({payload})',
        f'$coerce_number(PSTRING ({payload})) = COERCED ({operand}) false',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = ({number})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = ({value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED ({value})',
        rf'~(n_local_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_{label}) = 1',
    ])
checks.extend([
    'expression_integer_string = NExprBinaryOpConcat expression_integer_literal expression_integer_cast metadata_integer_concat',
    'expression_integer_cast = NExprCastString expression_integer_int metadata_integer_stringcast',
    'expression_integer_int = NExprCastInt expression_base metadata_integer_intcast',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_base) = (NINT 2)',
    'expression_zero_string = NExprBinaryOpConcat expression_zero_literal expression_zero_cast metadata_zero_concat',
    'expression_zero_cast = NExprCastString expression_zero_int metadata_zero_stringcast',
    'expression_zero_int = NExprCastInt expression_zero_arithmetic metadata_zero_intcast',
    'expression_zero_arithmetic = NExprBinaryOpMinus expression_zero_difference expression_one metadata_zero_minus',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one) = (NINT 1)',
    'S_wrong_integer_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PFLOAT $hex_bits("c036000000000000",0)])]',
    '$default_caches_valid(S_wrong_integer_tag,S_wrong_integer_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_integer_tag,pfunction,1)',
    'S_wrong_zero_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PINT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_zero_tag,pfunction,2)',
    'S_wrong_zero_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PFLOAT 9223372036854775808])]',
    '~$lossy_optional_integer_deferred(S_wrong_zero_sign,pfunction,2)',
    'S_wrong_float_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_floating[.VALUE = PFLOAT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_float_sign,pfunction,3)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_zero])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base246"),$ptascii("E_ERROR")),($ptascii("One246"),$ptascii("E_WARNING")),($ptascii("Eight246"),$ptascii("E_NOTICE"))]]',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_integer) = (NINT $(-21))',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_integer)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'pcpath_base = pcpath_integer ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1,PCFIELD 0,PCFIELD 0]',
    '$origin_node(S.SOURCES,PORIGIN n_source_unit pcpath_base) = (expression_base)',
    'S_forged_source = S[.SOURCES = [pcunit_source[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_one) :: pcunit_source.OCCURRENCES]]]',
    '~$lossy_optional_integer_deferred(S_forged_source,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2]])],ptask_resume)',
    'S_two_owners = S[.ENV = (BIND $ptascii("extraStringUnaryOwner246") n_cell) :: S.ENV]',
    '$heap_owners($heap_graph(S_two_owners),HCELL n_cell) = 2',
    '~$lossy_mixed_parameter_ready(S_two_owners,0,n_cell,n_bits)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    'S_first.TODO = [TYPE_RECEIVE porigin 1]',
])
previous = 'S_first'
for index, label, payload, operand, number, value, integer in VALUES:
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_floating,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias246")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for index, label, payload, operand, number, value, integer in VALUES:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL n_local_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_local_{label}) = 0',
    ])
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

# These helper controls never acquire an owned runtime string or source credit.
base, one = constant('E_WARNING'), constant('E_ERROR')
intcast = lambda expression: node('NExprCastInt', expression)
textcast = lambda expression: node('NExprCastString', expression)
zero = binary('Minus', binary('Minus', base, one), one)
produced = [
    (binary('Concat', string('2'), textcast(intcast(base))), 'NINT $(-22)'),
    (binary('Concat', string('-0.'), textcast(intcast(zero))), 'NFLOAT 0'),
    (binary('Concat', string('0.'), textcast(intcast(zero))), 'NFLOAT 9223372036854775808'),
    (binary('Concat', textcast(intcast(base)), string('.5')), 'NFLOAT 13836183955189006336'),
    (binary('Concat', string('-922337203685477580'), textcast(intcast(constant('E_NOTICE')))), 'NFLOAT 4890909195324358656'),
    (textcast(binary('Greater', base, one)), 'NINT $(-1)'),
    (binary('BitwiseAnd', string('3'), string('2')), 'NINT $(-2)'),
    (binary('BitwiseOr', string('0'), string('1')), 'NINT $(-1)'),
    (binary('BitwiseXor', string('R'), string('`')), 'NINT $(-2)'),
]
derived = []
for expression, result in produced:
    derived.extend([
        rf'~$lossy_optional_integer_selection_shape({expression}) /\ ~$lossy_optional_integer_boolean_shape({expression})',
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryMinus", expression)}) = ({result})',
    ])
for expression in [binary('Concat', string('2tail'), textcast(intcast(zero))),
                   binary('Concat', string('bad'), textcast(intcast(base))),
                   textcast(binary('Identical', base, one)),
                   constant('true'), constant('false'), constant('null')]:
    derived.append(f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryMinus", expression)}) = eps')
for expression, _ in produced[:6]:
    derived.append(f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryPlus", expression)}) = eps')
literal = node('NExprUnaryMinus', string('2.5'))
derived.extend([
    f'$lossy_optional_integer_numeric($plempty(false),{literal}) = (NFLOAT 13836183955189006336)',
    f'$lossy_optional_integer_default_in($plempty(false),{node("NExprUnaryMinus", string("2"))}) = eps',
    '$coerce_number(PSTRING ([50,0])) = COERCED (NINT 2) true',
    '$lossy_optional_integer_numeric($plempty(false),NExprUnaryMinus (NScalarString (BYTES "MgA=") eps) eps) = eps',
    f'~$lossy_optional_integer_quiet_shape({node("NExprUnaryMinus", node("NExprArrayDimFetch", string("12"), "NScalarInt (INTEGER 0) eps"))})',
])


if __name__ == '__main__':
    import closure_call_protocol as protocol

    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
    for row in rows.values():
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    cases = {
        'produced-string-unary-minus-named-front': {
            'source': rows['produced-string-unary-minus-alias-named-reentry']['source'],
            'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                      '-- if S.CURRENT = (pcallcontext) -- if pcallcontext.HOLES = [1,2,3]'),
            'checks': checks,
        },
        'produced-string-unary-minus-derived-boundaries': {
            'source': '<?php ;',
            'stage': r'S.COMPLETION = NORMAL /\ S.TODO = eps',
            'checks': derived,
        },
    }
    protocol.run(cases, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
