#!/usr/bin/env python3
"""Independent arithmetic phases, DIVZERO refusal and named cache checks."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_arithmetic_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [(0, 'add', 'ADD', 0), (1, 'subtract', 'SUBTRACT', 9223372036854775808),
          (2, 'multiply', 'MULTIPLY', 9223372036854775808),
          (3, 'divide', 'DIVIDE', 9223372036854775808)]

raw_checks = [
    'pfunction.SIGNATURE.PARAMETERS = [psparam_add,psparam_subtract,psparam_multiply,psparam_divide,psparam_folded]',
    'pdefault_add.ORIGIN = PORIGIN n_unit pcpath_add',
    '$code_at(S.CODE,n_unit) = (pcode)',
    'poperand_left = KNOWN (PFLOAT 0)',
    'S.RESULT = KNOWN (PINT 0)',
    'S.BASE = BASE_VALUE (KNOWN PNULL)',
]
for index, label, operator, bits in VALUES:
    raw_checks.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'pdefault_{label}.ORIGIN = PORIGIN n_unit pcpath_{label}',
        f'$origin_node(S.SOURCES,pdefault_{label}.ORIGIN) = (expression_{label})',
        f'$pfshape(expression_{label}) = PFBINARY {operator} expression_left_{label} expression_right_{label}',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{label}) = ((z_{label},false))',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{label}.ORIGIN)',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NFLOAT 0)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{label}.ORIGIN) = (PFLOAT {bits})',
    ])
raw_checks.extend([
    'porigin_left = PORIGIN n_unit (pcpath_add ++ [PCFIELD 0])',
    'porigin_right = PORIGIN n_unit (pcpath_add ++ [PCFIELD 1])',
    '$origin_node(S.SOURCES,porigin_left) = (expression_left_add)',
    '$origin_node(S.SOURCES,porigin_right) = (expression_right_add)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right) = (PINT 0)',
    r'$pool_value(S.POOLS,pdefault_add.ORIGIN) = eps /\ $compiled_read(S,pdefault_add.ORIGIN) = eps',
    '$compiled_redirect(S,pdefault_add.ORIGIN) = eps',
    'S_sparse = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_add z_add false),(CODEEXPR (pcpath_add ++ [PCFIELD 0]) z_add false)])]]]',
    '$lossy_optional_integer_deferred_value_at(S_sparse,pfunction.ENV,pdefault_add.ORIGIN) = (PFLOAT 0)',
    'S_wrong_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_add z_add true),(CODEEXPR (pcpath_add ++ [PCFIELD 0]) z_add false)])]]]',
    '$lossy_optional_integer_deferred_value_at(S_wrong_code,pfunction.ENV,porigin_left) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_wrong_code,pfunction.ENV,pdefault_add.ORIGIN) = eps',
    'S_missing_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_add ++ [PCFIELD 0]) z_add false)])]]]',
    '$lossy_optional_integer_deferred_value_at(S_missing_code,pfunction.ENV,porigin_left) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_missing_code,pfunction.ENV,pdefault_add.ORIGIN) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pooled = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_add (PFLOAT 0))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pooled,pdefault_add.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pooled,pfunction.ENV,pdefault_add.ORIGIN) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_add (pcpath_add ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,pdefault_add.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,pdefault_add.ORIGIN) = eps',
    # Constructed source-zero controls discriminate the NUM-only premise.
    'expression_probe_left = NExprUnaryPlus (NScalarFloat (FLOAT "8000000000000000") eps) eps',
    'expression_probe_zero = NExprBinaryOpDiv expression_probe_left (NScalarInt (INTEGER 0) eps) eps',
    'expression_probe_one = NExprBinaryOpDiv expression_probe_left (NScalarInt (INTEGER 1) eps) eps',
    'pcpath_probe = [PCINDEX 0,PCFIELD 0]',
    'pcunit_probe_zero = $pcsource(n_unit,PROGRAM ([(NStmtExpression expression_probe_zero eps)]))',
    'pcunit_probe_one = $pcsource(n_unit,PROGRAM ([(NStmtExpression expression_probe_one eps)]))',
    'pcode_probe = pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_probe z false),(CODEEXPR (pcpath_probe ++ [PCFIELD 0]) z false)])][.NAMES = eps][.REDIRECTS = eps]',
    'S_probe_zero = S[.SOURCES = [pcunit_probe_zero]][.POOLS = eps][.CODE = [pcode_probe]]',
    'S_probe_one = S_probe_zero[.SOURCES = [pcunit_probe_one]]',
    '$lossy_optional_integer_deferred_value_at(S_probe_zero,pfunction.ENV,PORIGIN n_unit (pcpath_probe ++ [PCFIELD 0])) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_probe_zero,pfunction.ENV,PORIGIN n_unit (pcpath_probe ++ [PCFIELD 1])) = (PINT 0)',
    '$number_binary(DIVIDE,NFLOAT 0,NINT 0) = DIVZERO',
    '$lossy_optional_integer_deferred_value_at(S_probe_zero,pfunction.ENV,PORIGIN n_unit pcpath_probe) = eps',
    '$lossy_optional_integer_deferred_value_at(S_probe_one,pfunction.ENV,PORIGIN n_unit pcpath_probe) = (PFLOAT 0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_add',
    'S_add = S[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 0)]',
    'S_done = $drive_steps(S_add,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    '$default_at(pfunction.DEFAULTS,4) = (pdefault_folded)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_folded.ORIGIN) = ({ORIGIN pdefault_folded.ORIGIN,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '0', ':', '-0', ':', '-0', ':', '-0', ':', '-0', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])
for index, label, operator, bits in VALUES:
    raw_checks.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{label}.ORIGIN) = ({{ORIGIN pdefault_{label}.ORIGIN,VALUE PFLOAT {bits},CLASS PVSCALAR}})')

named_checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("ArithmeticWrapper254")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base254"),$ptascii("E_WARNING")),($ptascii("One254"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_add,psparam_subtract,psparam_multiply,psparam_divide,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_add.BYREF /\ ~psparam_subtract.BYREF /\ ~psparam_multiply.BYREF /\ ~psparam_divide.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    r'pcallcontext.HOLES = [1,2,3,4] /\ pcallcontext.ARGC = 6',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
]
for index, label, operator, bits in VALUES:
    index += 1
    named_checks.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{label}.ORIGIN) = (PFLOAT {bits})',
        f'$default_current_cache(S,pdefault_{label}.ORIGIN) = (pdefaultcache_{label})',
        f'pdefaultcache_{label} = {{ORIGIN pdefault_{label}.ORIGIN,VALUE PFLOAT {bits},CLASS PVSCALAR}}',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PFLOAT {bits})',
        rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'S_sign_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PFLOAT {9223372036854775808-bits}])]',
        f'$default_caches_valid(S_sign_{label},S_sign_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_sign_{label},pfunction,{index})',
        f'S_tag_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PINT 0])]',
        f'$default_caches_valid(S_tag_{label},S_tag_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_tag_{label},pfunction,{index})',
    ])
named_checks.extend([
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base254"),$ptascii("E_ERROR")),($ptascii("One254"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    '~$lossy_optional_integer_deferred(S[.CODE = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
])
previous = 'S_first'
for index, label, operator, bits in VALUES:
    named_checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index+2}] /\ S_{label}.STORE[n_{label}] = DEFINED (PINT 0)',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = S.EVENTS',
    ])
    previous = f'S_{label}'
named_checks.extend([
    'S_done = $drive_steps(S_divide,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])
for index, label, operator, bits in VALUES:
    named_checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{label}.ORIGIN) = (pdefaultcache_{label})',
        rf'~((HCELL n_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_{label}) = 0',
    ])

CASES = {
    'deferred-float-arithmetic-raw-results': {
        'source': ROWS['deferred-float-arithmetic-wrapper-raw-four-operators']['source'],
        'stage': ('S.TODO = (BINARY_RIGHT ADD poperand_left z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawArithmetic254") '
                  '-- if $default_at(pfunction.DEFAULTS,0) = (pdefault_add) '
                  '-- if S.ORIGIN = (pdefault_add.ORIGIN)'),
        'checks': raw_checks,
    },
    'deferred-float-arithmetic-private-named': {
        'source': ROWS['deferred-float-arithmetic-wrapper-alias-named-reentry']['source'],
        'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                  '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
        'checks': named_checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
