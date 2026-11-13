#!/usr/bin/env python3
"""Genuine quiet deferred integer defaults retain cache and source authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE=Path(__file__).with_name('builtin_float_constant_default_reception_cases.json')
ROWS=json.loads(CATALOGUE.read_text())
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest()==row['source_sha256']
full=next(row['source'] for row in ROWS if row['id']=='builtin-float-constant-precision-modes')
handler=full[:full.index('function valueFirstReceive221(')]
reference=full[full.index('function referenceReceive221('):full.index("set_error_handler('warningReceive221');")]
setup=full[full.index("set_error_handler('warningReceive221');"):full.index('$gotReceive221 = valueFirstReceive221(')]
leading_start=full.index('$gotReceive221 = referenceReceive221(')
leading_end=full.index('$xReceive221 = 1.5;',leading_start)
source=handler+reference+setup+full[leading_start:leading_end]
assert hashlib.sha256(source.encode()).hexdigest()=='43a5544ea6ef5c5c78c5a3930dfa705a83db4a770e617c659321259e668e6677'

metadata_index = 0
fixed_metadata = None


def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    metadata = fixed_metadata or f'metadata_pre_{metadata_index}'
    return constructor + ''.join(f' ({child})' for child in children) + ' ' + metadata


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name, qualified=False):
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{base64.b64encode(name.encode()).decode()}"'))


def compare(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def cast(child):
    return node('NExprCastInt', child)


def unknown():
    return constant('UnselectedReceive221')


def string(value):
    data = value.encode() if isinstance(value, str) else value
    return node('NScalarString', f'BYTES "{base64.b64encode(data).decode()}"')


def ternary(condition, selected, alternative):
    return node('NExprTernary', condition, selected, alternative)


def dimension(base, selector):
    return node('NExprArrayDimFetch', base, selector)


def string_cast(child):
    return node('NExprCastString', child)


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


def negate(child):
    return node('NExprUnaryMinus', child)


yes = lambda: cast(constant('YesReceive221'))
no = lambda: cast(constant('NoReceive221'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: compare('Mul', large(), integer(2))
computed_nan = lambda: compare('Minus', computed_inf(), computed_inf())
def float_cast(child):
    return node('NExprCastDouble', child)






# Distinct metadata per occurrence; actual source binding authenticates each tree.
inf_alias_a = constant('InfinityReceive221')
inf_fqn_a = constant('INF', True)
condition_a = compare('BooleanAnd', compare('Greater', inf_alias_a, float_cast(constant('YesReceive221'))), compare('Greater', inf_fqn_a, float_cast(constant('NoReceive221'))))
nan_alias_b = constant('NanReceive221')
nan_fqn_b = constant('NAN', True)
condition_b = compare('BooleanAnd', compare('NotEqual', nan_alias_b, constant('NanReceive221')), node('NExprBooleanNot', compare('Identical', nan_fqn_b, constant('NAN', True))))
spaceship_c = compare('Spaceship', constant('NanReceive221'), float_cast(constant('NilReceive221')))
condition_c = compare('Identical', spaceship_c, cast(constant('YesReceive221')))
condition_d = constant('InfinityReceive221')
condition_e = compare('BooleanAnd', compare('Smaller', negate(constant('InfinityReceive221')), float_cast(constant('NoReceive221'))), compare('NotIdentical', constant('NanReceive221'), constant('NanReceive221')))
conditions = [condition_a, condition_b, condition_c, condition_d, condition_e]
patterns = [negate(ternary(condition_a, integer(7), unknown())), ternary(condition_b, cast(string('-11tail')), unknown()), ternary(condition_c, cast(string('13tail')), unknown()), ternary(condition_d, cast(string('-9223372036854775808tail')), unknown()), ternary(condition_e, cast(string('9' * 24)), unknown())]
contrasts = [
    ('floatnot','deferredFloatNotReceive221',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive221',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive221',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive221',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive221',cast(dimension(string('10'),compare('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive221',cast(string_cast(ternary(constant('YesReceive221'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive221',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive221',cast(compare('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive221',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive221',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive221',cast(node('NExprBooleanNot',compare('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive221',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive221',cast(compare('Plus',ternary(constant('YesReceive221'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive221',cast(compare('Plus',compare('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive221',cast(compare('Minus',ternary(constant('YesReceive221'),computed_inf(),unknown()),ternary(constant('NoReceive221'),unknown(),computed_inf()))),'eps'),
    ('floatcastnan','deferredNumericFloatCastNanReceive221',cast(float_cast(computed_nan())),'eps'),
    ('floatcastnonfit','deferredNumericFloatCastNonfitReceive221',cast(float_cast(cast(string('9223372036854775807')))),'eps'),
    ('scalarfloatnonfit','deferredScalarFloatCastNonfitReceive221',cast(float_cast(string('1e999'))),'eps'),
    ('selectedscalarfloatnonfit','deferredSelectedScalarFloatCastNonfitReceive221',cast(float_cast(ternary(constant('YesReceive221'),string('1e999'),unknown()))),'eps'),
]

contrasts.extend([
    ('builtinnanint', 'deferredBuiltinNanIntReceive221', cast(constant('NanReceive221')), 'eps'),
    ('builtininfint', 'deferredBuiltinInfIntReceive221', cast(constant('InfinityReceive221')), 'eps'),
    ('builtinnannot', 'deferredBuiltinNanNotReceive221', cast(node('NExprBooleanNot', constant('NanReceive221'))), 'eps'),
    ('absentbuiltin', 'deferredAbsentBuiltinNameReceive221', cast(compare('NotEqual', constant('AbsentNanReceive221'), integer(0))), 'eps'),
    ('lowercasebuiltin', 'deferredLowercaseBuiltinNameReceive221', cast(compare('NotEqual', constant('nan'), integer(0))), 'eps'),
    ('aliascasebuiltin', 'deferredAliasCaseBuiltinNameReceive221', cast(compare('NotEqual', constant('nanReceive221'), integer(0))), 'eps'),
])
stored_boolean_pattern = cast(compare('Identical', constant('FalseNanReceive221'), constant('false')))
checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'plenv_source=pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive221"),$ptascii("true")),($ptascii("NoReceive221"),$ptascii("false")),($ptascii("NilReceive221"),$ptascii("null")),($ptascii("InfinityReceive221"),$ptascii("INF")),($ptascii("NanReceive221"),$ptascii("NAN")),($ptascii("AbsentNanReceive221"),$ptascii("MissingReceive221\\NAN")),($ptascii("FalseNanReceive221"),$ptascii("false"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a,psparam_b,psparam_c,psparam_d,psparam_e]',
    '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS,true)',
    '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS,false)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0,1] /\ pcallcontext.NAMED = eps',
]
for index, (letter, pattern, condition, value) in enumerate(zip('abcde', patterns, conditions, ('$(-7)', '$(-11)', '13', '$(-9223372036854775808)', '9223372036854775807'))):
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "deferred"',
        f'expression_{letter} = {pattern}',
        f'expression_condition_{letter} = {condition}',
        f'$lossy_optional_integer_default_in(plenv_source,expression_{letter}) = ({value})',
        f'$lossy_optional_integer_condition(plenv_source,expression_condition_{letter}) = (true)',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{letter},KIND PDDEFERRED}})',
        f'$compiled_read(S,porigin_{letter}) = eps',
    ])
for suffix, expression, expected in [('infalias', inf_alias_a, 'INF'), ('inffqn', inf_fqn_a, 'INF'), ('nanalias', nan_alias_b, 'NAN'), ('nanfqn', nan_fqn_b, 'NAN')]:
    checks.extend([
        f'expression_{suffix} = {expression}',
        f'expression_{suffix} = NExprConstFetch name_{suffix} metadata_{suffix}',
        f'$pnresolve(plenv_source,PLCONSTANT,name_{suffix}) = PNRESOLVED pnreference_{suffix}',
        f'pnreference_{suffix}.RESOLVED = $ptascii("{expected}")',
        rf'pnreference_{suffix}.FULL /\ pnreference_{suffix}.FALLBACK = eps',
        f'$lossy_optional_integer_numeric(plenv_source,expression_{suffix}) = (NFLOAT {9218868437227405312 if expected == "INF" else 9221120237041090560})',
    ])
checks.extend([
    f'expression_spaceship_c = {spaceship_c}',
    '$lossy_optional_integer_default_in(plenv_source,expression_spaceship_c) = (1)',
    '$lossy_optional_integer_numeric(plenv_source,expression_spaceship_c) = (NINT 1)',
    '$builtin_value_bytes($ptascii("INF")) = (PFLOAT 9218868437227405312)',
    '$builtin_value_bytes($ptascii("NAN")) = (PFLOAT 9221120237041090560)',
])
for suffix,function_name,pattern,projection in contrasts:
    checks.extend([
        f'$call_target(S,$ptascii("{function_name}"),eps) = (pfunction_{suffix})',
        f'pfunction_{suffix}.SIGNATURE.PARAMETERS = [psparam_{suffix}]',
        f'psparam_{suffix}.DEFAULT = PSDEFAULT expression_{suffix} "deferred"',
        f'$default_parameter_origin(S,pfunction_{suffix}.ORIGIN,0) = PORIGIN n_unit pcpath_{suffix}',
        f'porigin_{suffix} = PORIGIN n_unit (pcpath_{suffix} ++ [PCFIELD 6])',
        f'pfunction_{suffix}.DEFAULTS = [{{INDEX 0,ORIGIN porigin_{suffix},KIND PDDEFERRED}}]',
        f'$compiled_read(S,porigin_{suffix}) = eps',
        f'$lossy_optional_integer_default_in(pfunction_{suffix}.ENV,expression_{suffix}) = {projection}',
        f'~$lossy_optional_integer_deferred(S,pfunction_{suffix},0)',
    ])
checks.extend([
    '$call_target(S,$ptascii("storedBooleanAliasReceive221"),eps) = (pfunction_booleanalias)',
    'pfunction_booleanalias.ORIGIN = PORIGIN n_unit pcpath_booleanalias_function',
    'pfunction_booleanalias.ORIGIN =/= porigin',
    'pfunction_booleanalias.SIGNATURE.PARAMETERS = [psparam_booleanalias]',
    r'~psparam_booleanalias.REQUIRED /\ ~psparam_booleanalias.BYREF /\ ~psparam_booleanalias.VARIADIC /\ $ptmasks(psparam_booleanalias.TYPE) = ["int"]',
    'psparam_booleanalias.DEFAULT = PSDEFAULT expression_booleanalias "int"',
    f'expression_booleanalias = {stored_boolean_pattern}',
    '$default_parameter_origin(S,pfunction_booleanalias.ORIGIN,0) = PORIGIN n_unit pcpath_booleanalias',
    'porigin_booleanalias = PORIGIN n_unit (pcpath_booleanalias ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,porigin_booleanalias) = (expression_booleanalias)',
    'pfunction_booleanalias.DEFAULTS = [{INDEX 0,ORIGIN porigin_booleanalias,KIND PDSTORED}]',
    '$compiled_read(S,porigin_booleanalias) = (PINT 1)',
    '$lossy_optional_integer_default_in(pfunction_booleanalias.ENV,expression_booleanalias) = eps',
    '~$lossy_optional_integer_header(S,pfunction_booleanalias,pfunction_booleanalias.SIGNATURE.PARAMETERS,0)',
    '~$lossy_optional_integer_tail(S,pfunction_booleanalias,[psparam_booleanalias],0)',
])
checks.extend([
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'pcallcontext.CALLSITE = (porigin_call)',
    '$named_call_valid(S,porigin,(porigin_call))',
    '$named_call_shape(S,porigin,(porigin_call)) = {SLOTS ([NAMED_HOLE,NAMED_HOLE,NAMED_SENT (KNOWN PNULL)]),NAMED eps}',
    '$lookup(S.ENV,psparam_a.NAME) = (n_a)',
    '$lookup(S.ENV,psparam_b.NAME) = (n_b)',
    '$lookup(S.ENV,psparam_c.NAME) = (n_cell)',
    r'S.STORE[n_a] = DEFINED (PINT $(-7)) /\ S.STORE[n_b] = DEFINED (PINT $(-11))',
    r'~(n_a <- S.REFCELLS) /\ ~(n_b <- S.REFCELLS)',
    r'$heap_owners($heap_graph(S),HCELL n_a) = 1 /\ $heap_owners($heap_graph(S),HCELL n_b) = 1',
    r'S.STORE[n_cell] = DEFINED (PFLOAT 4609434218613702656) /\ n_cell <- S.REFCELLS /\ $heap_owners($heap_graph(S),HCELL n_cell) = 2',
    r'$lookup(S.ENV,psparam_d.NAME) = eps /\ $lookup(S.ENV,psparam_e.NAME) = eps',
    'z = $default_parameter_line(S,porigin,2)',
    r'$typed_receive_valid(S,porigin,2) /\ ~$typed_caller_strict(S)',
    '$lossy_mixed_parameter_ready(S,2,n_cell,4609434218613702656)',
    '$lossy_mixed_parameter_metadata(S,porigin,2,z)',
    '$lossy_mixed_parameter_capture(S) = (LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell 4609434218613702656 1 z)',
    r'S.EVENTS = eps /\ $call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
])

# Prepared named holes have real cache rows; future defaults remain untouched.
checks.extend([
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$default_caches_valid(S,S.DEFAULTCACHE)',
    '$default_current_cache(S,porigin_a) = ({ORIGIN porigin_a,VALUE PINT $(-7),CLASS PVSCALAR})',
    '$default_current_cache(S,porigin_b) = ({ORIGIN porigin_b,VALUE PINT $(-11),CLASS PVSCALAR})',
    '$default_current_cache(S,porigin_c) = eps',
    '$default_current_cache(S,porigin_d) = eps',
    '$default_current_cache(S,porigin_e) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = $plempty(false)],pfunction.SIGNATURE.PARAMETERS,0)',
    '~$lossy_optional_integer_deferred_bindings(S,$plempty(false),porigin_a)',
    '$code_at(S.CODE,n_unit) = (pcode_source)',
    '~$lossy_optional_integer_deferred_bindings(S[.CODE = [pcode_source[.NAMES = eps]]],plenv_source,porigin_a)',
    '~$lossy_optional_integer_deferred_bindings(S[.POOLS = eps],plenv_source,porigin_a)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = eps],pfunction,0)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_PRIVATE 0)])],pfunction,0)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_CALL 0)])],pfunction,0)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET 0])],pfunction,0)',
    '~$lossy_optional_integer_deferred(S,pfunction,5)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,0)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,0)',
])
for index, letter in enumerate('abcde'):
    checks.extend([
        f'$lossy_optional_integer_quiet_shape(expression_{letter})',
        f'$lossy_optional_integer_deferred_bindings(S,plenv_source,porigin_{letter})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
    ])
for value, tag in [('$(-9223372036854775808)', 'correct'), ('0', 'wrong')]:
    checks.extend([
        f'S_{tag}_warm = S[.DEFAULTCACHE = S.DEFAULTCACHE ++ [{{ORIGIN porigin_d,VALUE PINT {value},CLASS PVSCALAR}}]]',
        f'$default_caches_valid(S_{tag}_warm,S_{tag}_warm.DEFAULTCACHE)',
        f'{"" if tag == "correct" else "~"}$lossy_optional_integer_deferred(S_{tag}_warm,pfunction,3)',
    ])
checks.extend([
    '$lossy_optional_integer_header(S_correct_warm,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '~$lossy_optional_integer_deferred(S[.DEFAULTCACHE = S.DEFAULTCACHE ++ [{ORIGIN porigin_d,VALUE PBOOL false,CLASS PVSCALAR}]],pfunction,3)',
    '~$lossy_optional_integer_deferred(S[.DEFAULTCACHE = S.DEFAULTCACHE ++ [{ORIGIN porigin_d,VALUE PINT $(-9223372036854775808),CLASS PVSTRING true}]],pfunction,3)',
    '~$lossy_optional_integer_deferred(S_correct_warm[.DEFAULTCACHE = S_correct_warm.DEFAULTCACHE ++ [{ORIGIN porigin_d,VALUE PINT $(-9223372036854775808),CLASS PVSCALAR}]],pfunction,3)',
    'pfunction.DEFAULTS = [pdefault_a,pdefault_b,pdefault_c,pdefault_d,pdefault_e]',
    '~$lossy_optional_integer_deferred(S,pfunction[.DEFAULTS = [pdefault_a,pdefault_b,pdefault_c,pdefault_d[.KIND = PDSTORED],pdefault_e]],3)',
    '~$lossy_optional_integer_tail(S,pfunction,[psparam_d[.DEFAULT = PSDEFAULT expression_d "int"]],3)',
    'S_present_root = S[.CODE = [pcode_source[.EXPRESSIONS = [CODEEXPR (pcpath_d ++ [PCFIELD 6]) 1 true] ++ pcode_source.EXPRESSIONS]]][.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_d ++ [PCFIELD 6]) (PINT $(-9223372036854775808)))])}]]',
    '$compiled_read(S_present_root,porigin_d) = (PINT $(-9223372036854775808))',
    '~$lossy_optional_integer_deferred(S_present_root,pfunction,3)',
])

# Resolved builtins are typed producers; their existing consumers keep their gates.
fixed_metadata = 'metadata_infalias'
for expression, number, truth in [
    (constant('InfinityReceive221'), '9218868437227405312', '(true)'),
    (constant('INF', True), '9218868437227405312', '(true)'),
    (constant('NanReceive221'), '9221120237041090560', 'eps'),
    (constant('NAN', True), '9221120237041090560', 'eps'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = (NFLOAT {number})',
        f'$lossy_optional_integer_default_in(plenv_source,{expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source,{expression}) = {truth}',
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = eps',
    ])
for name in ['nan', 'inf', 'nanReceive221', 'AbsentNanReceive221', 'PHP_INT_SIZE']:
    expression = constant(name)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source,{expression}) = eps',
    ])
checks.extend([
    'plenv_namespace = $plempty(false)[.NAMESPACE = $ptascii("Shadow221")]',
    f'$lossy_optional_integer_numeric(plenv_namespace,{constant("NAN")}) = eps',
    f'$lossy_optional_integer_numeric(plenv_namespace,{constant("NAN", True)}) = (NFLOAT 9221120237041090560)',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(constant("InfinityReceive221"))}) = (NFLOAT 9218868437227405312)',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(constant("NanReceive221"))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source,{node("NExprBooleanNot",constant("NanReceive221"))}) = eps',
])

# Compile-time DIM projection is deliberately not a runtime-quiet certificate.
offsets = [
    dimension(string('12'), compare('Concat', string_cast(compare('Plus', integer(1), cast(node('NExprBooleanNot', floating('3fe0000000000000'))))), string('tail'))),
    dimension(string('12'), compare('Concat', string_cast(cast(compare('NotIdentical', constant('NAN'), constant('NAN')))), string('tail'))),
]
for expression in offsets:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = (2)',
        f'~$lossy_optional_integer_quiet_shape({cast(expression)})',
    ])
for expression in [
    dimension(string('12'), integer(1)),
    string_cast(floating('3fe0000000000000')),
]:
    if expression.startswith('NExprArrayDimFetch'):
        checks.append(f'~$lossy_optional_integer_quiet_shape({expression})')
    else:
        checks.extend([
            f'$lossy_optional_integer_quiet_shape({expression})',
            f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = eps',
        ])
finite_not = cast(node('NExprBooleanNot', floating('3fe0000000000000')))
deep = cast(compare('NotIdentical', constant('NAN'), constant('NAN')))
for _ in range(8):
    deep = cast(node('NExprBooleanNot', node('NExprBooleanNot', compare('Div', deep, integer(2)))))
checks.extend([
    f'$lossy_optional_integer_quiet_shape({finite_not})',
    f'$lossy_optional_integer_default_in(plenv_source,{finite_not}) = (0)',
    f'$lossy_optional_integer_quiet_shape({deep})',
    f'$lossy_optional_integer_default_in(plenv_source,{deep}) = (1)',
    'S_budget = $drive_steps(S,0)',
    r'S_budget.COMPLETION = BUDGET /\ S_budget.DEFAULTCACHE = S.DEFAULTCACHE /\ S_budget.STORE = S.STORE',
    'S_done = $drive_steps(S,3000)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_a) = ({ORIGIN porigin_a,VALUE PINT $(-7),CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_b) = ({ORIGIN porigin_b,VALUE PINT $(-11),CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_c) = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_d) = ({ORIGIN porigin_d,VALUE PINT $(-9223372036854775808),CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_e) = ({ORIGIN porigin_e,VALUE PINT 9223372036854775807,CLASS PVSCALAR})',
    '$lookup(S_done.ENV,$ptascii("gotReceive221")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'~((HCELL n_a) <- S_done.ALLOCATIONS) /\ ~((HCELL n_b) <- S_done.ALLOCATIONS)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {'builtin-float-constant-deferred-leading-reference': {
    'source': source,
    'stage': 'S.TODO = [TYPE_RECEIVE porigin 2]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))

