#!/usr/bin/env python3
"""Independent platform-float named defaults and own-warning continuation checks."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('float_platform_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def authority(index, bits):
    task = f'LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits i z'
    return [
        f'ptask_resume = {task}',
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        'pfunction.ENV.NAMESPACE = $ptascii("PlatformAlias231")',
        'S.CURRENT = (pcallcontext)',
        r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
        r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
        r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
        '$parameter_receive_owner(S.CURRENT) = eps',
        f'pfunction.SIGNATURE.PARAMETERS[{index}] = psparam_later',
        r'~psparam_later.REQUIRED /\ $ptmasks(psparam_later.TYPE) = ["int"]',
        'psparam_later.DEFAULT = PSDEFAULT expression_default "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_parameter',
        'porigin_default = PORIGIN n_unit (pcpath_parameter ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_default,KIND PDDEFERRED}})',
        '$origin_node(S.SOURCES,porigin_default) = (expression_default)',
        r'$pool_value(S.POOLS,porigin_default) = eps /\ $compiled_read(S,porigin_default) = eps',
        '$lossy_optional_integer_default_in(pfunction.ENV,expression_default) = eps',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_default) = (PFLOAT {bits})',
        rf'n_bits = {bits} /\ i = 0',
        '$lossy_parameter_snapshot(n_bits) = ((i,ptbytes))',
        f'z = $default_parameter_line(S,porigin,{index})',
        f'S.ORIGIN = ($default_parameter_origin(S,porigin,{index}))',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        'pdefaultcache_good = {ORIGIN porigin_default,VALUE PFLOAT n_bits,CLASS PVSCALAR}',
        '$default_current_cache(S,porigin_default) = (pdefaultcache_good)',
        '$lookup(S.ENV,psparam_later.NAME) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
        r'(HCELL n_cell) <- S.ALLOCATIONS /\ ~(n_cell <- S.REFCELLS)',
        '$heap_owners($heap_graph(S),HCELL n_cell) = 1',
        '$lossy_parameter_ready(S,n_cell,n_bits)',
        '$lossy_default_parameter_source_valid(S,ptask_resume)',
        '$call_task_valid(S,ptask_resume)',
        '$task_nodes(ptask_resume) = eps',
        f'~$lossy_default_parameter_candidate(S,pfunction,{index},PFLOAT n_bits)',
        r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    ]


def malformed(index):
    return [
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits 2 z)',
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell 4615063718147915776 3 z)',
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits i $(z + 100))',
        '~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 100 n_cell n_bits i z)',
        '~$lossy_default_parameter_source_valid(S[.ORIGIN = (porigin_default)],ptask_resume)',
        '~$lossy_default_parameter_source_valid(S[.SOURCES = eps],ptask_resume)',
        '~$lossy_default_parameter_source_valid(S[.FUNCTIONS = eps],ptask_resume)',
        '~$lossy_default_parameter_source_valid(S[.ENV = eps],ptask_resume)',
        'S.CODE = [pcode]',
        '~$lossy_default_parameter_source_valid(S[.CODE = ([pcode[.NAMES = eps]])],ptask_resume)',
        'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
        '$default_cache_owner(S_unknown) = eps',
        '~$lossy_default_parameter_source_valid(S_unknown,ptask_resume)',
        'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 0])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_default_parameter_source_valid(S_wrong_tag,ptask_resume)',
        'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PFLOAT 4615063718147915776])]',
        '~$lossy_default_parameter_source_valid(S_wrong_bits,ptask_resume)',
        'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.CLASS = PVSTRING false])]',
        '~$lossy_default_parameter_source_valid(S_wrong_class,ptask_resume)',
        'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_good])]',
        '~$default_caches_valid(S_duplicate,S_duplicate.DEFAULTCACHE)',
        '~$lossy_default_parameter_source_valid(S_duplicate,ptask_resume)',
        'S_changed = $write_name(S,psparam_later.NAME,PFLOAT 4615063718147915776)',
        '$lossy_default_parameter_source_valid(S_changed,ptask_resume)',
        '~$lossy_parameter_ready(S_changed,n_cell,n_bits)',
        'PhpStep: S_changed ~> S_refused',
        'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy deferred default receive continuation"]',
        'S_marked = $reference_cell(S,n_cell)',
        '$lossy_default_parameter_source_valid(S_marked,ptask_resume)',
        '~$lossy_parameter_ready(S_marked,n_cell,n_bits)',
        'PhpStep: S_marked ~> S_marked_refused',
        'S_marked_refused = S_marked[.COMPLETION = UNSUPPORTED "lossy deferred default receive continuation"]',
        'S_cleared = S[.ERRORHANDLER.CALLBACK = eps]',
        '~$error_handler_eligible(S_cleared,8192)',
        '$lossy_default_parameter_source_valid(S_cleared,ptask_resume)',
        '$call_task_valid(S_cleared,ptask_resume)',
        'PhpStep: S_cleared ~> S_cleared_bound',
        'S_cleared_bound.STORE[n_cell] = DEFINED (PINT 0)',
        r'S_cleared_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_cleared_bound.EVENTS = S.EVENTS',
    ]


def finish():
    return [
        'S_budget = $drive_steps(S,0)',
        'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'PhpStep: S ~> S_bound',
        'S_bound.STORE[n_cell] = DEFINED (PINT 0)',
        r'S_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_bound.EVENTS = S.EVENTS',
        r'S_bound.CURRENT = S.CURRENT /\ S_bound.FRAMES = S.FRAMES',
        'S_bound.ORIGIN = (porigin)',
        r'S_bound.RESULT = KNOWN PNULL /\ S_bound.BASE = BASE_VALUE (KNOWN PNULL)',
        r'~(n_cell <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_cell) = 1',
        'S_done = $drive_steps(S_bound,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = (pdefaultcache_good)',
        '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
    ]


def named(index):
    checks = [
        r'pcallcontext.ARGC = 4 /\ pcallcontext.HOLES = [1,2]',
        'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_epsilon,psparam_minimum,psparam_last]',
        r'~psparam_first.BYREF /\ psparam_epsilon.BYREF /\ ~psparam_minimum.BYREF /\ ~psparam_last.BYREF',
        '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
        r'S.STORE[n_first] = DEFINED (PINT 1) /\ ~(n_first <- S.REFCELLS)',
        '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
        'S.STORE[n_last] = DEFINED (PINT 8)',
        '$default_parameter_origin(S,porigin,3) = PORIGIN n_unit pcpath_last',
        '$default_at(pfunction.DEFAULTS,3) = ({INDEX 3,ORIGIN PORIGIN n_unit (pcpath_last ++ [PCFIELD 6]),KIND PDSTORED})',
        '$compiled_read(S,PORIGIN n_unit (pcpath_last ++ [PCFIELD 6])) = (PINT 7)',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV,$ptascii("xAlias231")) = (n_global)',
        r'n_global =/= n_first /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    ]
    for position, label, bits, resolved in [
        (1, 'epsilon', 4372995238176751616, 'PHP_FLOAT_EPSILON'),
        (2, 'minimum', 4503599627370496, 'PHP_FLOAT_MIN'),
    ]:
        checks.extend([
            f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
            f'$default_parameter_origin(S,porigin,{position}) = PORIGIN n_unit pcpath_{label}',
            f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
            f'$default_at(pfunction.DEFAULTS,{position}) = ({{INDEX {position},ORIGIN porigin_{label},KIND PDDEFERRED}})',
            f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
            f'expression_{label} = NExprConstFetch name_{label} metadata_{label}',
            f'$pnresolve(pfunction.ENV,PLCONSTANT,name_{label}) = PNRESOLVED pnreference_{label}',
            rf'pnreference_{label}.RESOLVED = $ptascii("{resolved}") /\ pnreference_{label}.FALLBACK = eps',
            rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
            f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NFLOAT {bits})',
            f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PFLOAT {bits})',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
            f'$lossy_optional_integer_deferred(S,pfunction,{position})',
            f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PFLOAT {bits},CLASS PVSCALAR}}',
            f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
            f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
            rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
        ])
    checks.extend([
        'S.STORE[n_minimum] = DEFINED (PFLOAT 4503599627370496)',
        'S.STORE[n_epsilon] = DEFINED (PFLOAT 4372995238176751616)' if index == 1 else 'S.STORE[n_epsilon] = DEFINED (PINT 0)',
        'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Epsilon231"),$ptascii("PHP_FLOAT_MIN")),($ptascii("Minimum231"),$ptascii("PHP_FLOAT_EPSILON"))])]',
        '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_default)',
        '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
        '$error_handler_eligible(S,8192)',
    ])
    return checks


def cleanup(index):
    return [
        f'S_bound.TODO = [TYPE_RECEIVE porigin {index + 1}]',
        r'S_bound.STORE[n_first] = S.STORE[n_first] /\ S_bound.STORE[n_last] = S.STORE[n_last]',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_epsilon) = (pdefaultcache_epsilon)',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_minimum) = (pdefaultcache_minimum)',
        '$lookup(S_done.ENV,$ptascii("xAlias231")) = (n_global)',
        'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
        r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ ~((HCELL n_epsilon) <- S_done.ALLOCATIONS) /\ ~((HCELL n_minimum) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_done),HCELL n_epsilon) = 0',
        '$heap_owners($heap_graph(S_done),HCELL n_minimum) = 0',
    ]


def constant(name, qualified=False):
    kind = 'NNameFullyQualified' if qualified else 'NName'
    encoded = base64.b64encode(name.encode()).decode()
    return f'NExprConstFetch ({kind} (BYTES "{encoded}") eps) eps'


CASES = {}
for index, label, bits in [(1, 'epsilon', 4372995238176751616),
                           (2, 'minimum', 4503599627370496)]:
    checks = authority(index, bits) + named(index) + malformed(index) + finish() + cleanup(index)
    if index == 1:
        for name, expected in [('PHP_FLOAT_DIG', 'NINT 15'),
                               ('PHP_FLOAT_EPSILON', 'NFLOAT 4372995238176751616'),
                               ('PHP_FLOAT_MIN', 'NFLOAT 4503599627370496'),
                               ('PHP_FLOAT_MAX', 'NFLOAT 9218868437227405311')]:
            checks.append(f'$lossy_optional_integer_numeric($plempty(false),{constant(name, True)}) = ({expected})')
        for name in ['php_float_epsilon', 'E_STRICT']:
            checks.append(f'$lossy_optional_integer_numeric($plempty(false),{constant(name)}) = eps')
        checks.append(f'$lossy_optional_integer_numeric($plempty(false),{constant("PHP_VERSION_ID")}) = (NINT 80510)')
        checks.extend([
            'plenv_fallback = $plempty(false)[.NAMESPACE = $ptascii("MissingPlatform231")]',
            f'$lossy_optional_integer_numeric(plenv_fallback,{constant("PHP_FLOAT_MIN")}) = eps',
            f'$lossy_optional_integer_default_in($plempty(false),{constant("PHP_FLOAT_DIG")}) = eps',
        ])
    CASES[f'platform-float-{label}-named-own-receive'] = {
        'source': ROWS['float-platform-default-fraction-alias-named']['source'],
        'stage': f'S.TODO = [LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits i z]',
        'checks': checks,
    }

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
