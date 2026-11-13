#!/usr/bin/env python3
"""Independent late-default error, named-hole and reference continuation checks."""
import base64
import hashlib
import json
from pathlib import Path


def literal(tag, *children):
    return tag + ''.join(f' ({child})' for child in children) + ' eps'


def constant(name):
    return literal('NExprConstFetch', literal('NName', f'BYTES "{base64.b64encode(name.encode()).decode()}"'))


def checks_for(name, global_name, byref):
    checks = [
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        f'pfunction.NAME = $ptascii("{name}")',
        'S.CURRENT = (pcallcontext)',
        r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
        r'pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps /\ pcallcontext.LEXICAL_CLASS = eps',
        'pfunction.SIGNATURE.PARAMETERS[0] = psparam_first',
        'pfunction.SIGNATURE.PARAMETERS[1] = psparam_later',
        r'psparam_first.REQUIRED /\ psparam_first.DEFAULT = PSNONE /\ $ptmasks(psparam_first.TYPE) = ["int"]',
        f'psparam_first.BYREF = {str(byref).lower()}',
        r'~psparam_later.REQUIRED /\ ~psparam_later.BYREF /\ $ptmasks(psparam_later.TYPE) = ["int"]',
        'psparam_later.DEFAULT = PSDEFAULT expression_later "deferred"',
        'expression_later = NExprConstFetch name_later metadata_later',
        '$pnresolve(pfunction.ENV,PLCONSTANT,name_later) = PNRESOLVED pnreference',
        'pnreference.RESOLVED = $ptascii("INF")',
        '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_later',
        'porigin_later = PORIGIN n_unit (pcpath_later ++ [PCFIELD 6])',
        '$origin_node(S.SOURCES,porigin_later) = (expression_later)',
        '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_later,KIND PDDEFERRED})',
        r'$pool_value(S.POOLS,porigin_later) = eps /\ $compiled_read(S,porigin_later) = eps',
        '$lossy_optional_integer_default_in(pfunction.ENV,expression_later) = eps',
        '$lossy_optional_integer_numeric(pfunction.ENV,expression_later) = (NFLOAT 9218868437227405312)',
        '$typed_weak(["int"],PFLOAT 9218868437227405312) = TYPEREJECT',
        '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_later) = (PFLOAT 9218868437227405312)',
        '$lossy_optional_integer_quiet_shape(expression_later)',
        '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_later)',
        '~$default_scope_dependent(S,porigin_later)',
        '$default_at(pfunction.DEFAULTS,1) = (pdefault_later)',
        '$default_receive_recipient(S,pfunction,pdefault_later)',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        '$default_caches_valid(S,S.DEFAULTCACHE)',
        '$lossy_optional_integer_deferred(S,pfunction,1)',
        '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
        '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
        'n_bits = 4609434218613702656',
        'i = 1',
        'z = $default_parameter_line(S,porigin,0)',
        '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
        '$lossy_mixed_parameter_metadata(S,porigin,0,z)',
        '$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
        '$call_task_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
        '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
        '~$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits 2 z)',
        '$lossy_mixed_parameter_capture(S) = eps',
        ('$lossy_mixed_parameter_capture(S[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)]) = '
         + ('(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell 4615063718147915776 3 z)' if byref
            else '(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)')),
        r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
        'S.GLOBALTABLE = (psymboltable_global)',
        f'$lookup(psymboltable_global.ENV,$ptascii("{global_name}")) = (n_global)',
        'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    ]
    if byref:
        checks.extend([
            'pcallcontext.ARGC = 1',
            'pcallcontext.HOLES = eps',
            'n_cell = n_global',
            r'n_cell <- S.REFCELLS /\ $heap_owners($heap_graph(S),HCELL n_cell) = 2',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            '$lookup(S.ENV,psparam_later.NAME) = eps',
            '$default_current_cache(S,porigin_later) = eps',
        ])
    else:
        checks.extend([
            'pcallcontext.ARGC = 3',
            'pcallcontext.HOLES = [1]',
            r'n_cell =/= n_global /\ ~(n_cell <- S.REFCELLS)',
            '$heap_owners($heap_graph(S),HCELL n_cell) = 1',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4609434218613702656)',
            '$lookup(S.ENV,psparam_later.NAME) = (n_later)',
            'S.STORE[n_later] = DEFINED (PFLOAT 9218868437227405312)',
            r'~(n_later <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_later) = 1',
            '$default_current_cache(S,porigin_later) = ({ORIGIN porigin_later,VALUE PFLOAT 9218868437227405312,CLASS PVSCALAR})',
            '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[2].NAME) = (n_last)',
            'S.STORE[n_last] = DEFINED (PINT 8)',
            '$named_call_valid(S,porigin,pcallcontext.CALLSITE)',
        ])
    checks.extend([
        'pdefaultcache_good = {ORIGIN porigin_later,VALUE PFLOAT 9218868437227405312,CLASS PVSCALAR}',
        'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good)]',
        '$default_caches_valid(S_good,S_good.DEFAULTCACHE)',
        '$lossy_optional_integer_deferred(S_good,pfunction,1)',
        'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PFLOAT 9221120237041090560])]',
        '$default_caches_valid(S_wrong_bits,S_wrong_bits.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_bits,pfunction,1)',
        'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 0])]',
        '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
        'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.CLASS = PVSTRING false])]',
        '~$lossy_optional_integer_deferred(S_wrong_class,pfunction,1)',
        'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_good])]',
        '~$default_caches_valid(S_duplicate,S_duplicate.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
        'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
        '$default_cache_owner(S_unknown) = eps',
        '~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
        '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_PRIVATE 0)])],pfunction,1)',
        '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET 0])],pfunction,1)',
        '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
        '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
        'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("INF"),$ptascii("NAN"))])]',
        '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_later)',
        '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
        'S_budget = $drive_steps(S,0)',
        'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'PhpStep: S ~> S_next',
        r'S_next.STORE[n_cell] = DEFINED (PINT 1) /\ S_next.TODO = [TYPE_RECEIVE porigin 1]',
        'S_next.DEFAULTCACHE = S.DEFAULTCACHE',
        'S_done = $drive_steps(S_next,2500)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        'S_done.CONSTCONTEXT = eps',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = ({ORIGIN porigin_later,VALUE PFLOAT 9218868437227405312,CLASS PVSCALAR})',
        '$parameter_receive_state_valid(S_done)',
        r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    ])
    if byref:
        checks.extend([
            'S_done.STORE[n_global] = DEFINED (PINT 1)',
            '$heap_owners($heap_graph(S_done),HCELL n_global) = 1',
        ])
    return checks


CATALOGUE = Path(__file__).with_name('deferred_float_default_type_error_reception_cases.json')
rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
CASES = {}
for case_id, row_id, expected_hash, function, global_name, byref in [
    ('reference-late-default-error', 'deferred-inf-default-type-error-precision', '7d41758090b3ae0db4bf77c6295250c638847af39859d1879d7576e9efc44dea', 'referenceFutureDefault222', 'xFuture222', True),
    ('named-hole-late-default-error', 'deferred-default-type-error-cache-order', '0ec289a05f8018aa44fec60f2c428961ea177b383c4eee9af7afdd598598e268', 'namedDefault222', 'xOrder222', False),
]:
    row = rows[row_id]
    assert row['source_sha256'] == expected_hash
    assert hashlib.sha256(row['source'].encode()).hexdigest() == expected_hash
    CASES[case_id] = {
        'source': row['source'],
        'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                  f'-- if $callable_at(S.CALLABLES,$ptascii("{function.lower()}")) = (porigin)'),
        'checks': checks_for(function, global_name, byref),
    }

for expression, expected in [
    (constant('INF'), '(PFLOAT 9218868437227405312)'),
    (constant('NAN'), '(PFLOAT 9221120237041090560)'),
    (constant('nan'), 'eps'),
    (constant('PHP_INT_SIZE'), 'eps'),
    (literal('NScalarFloat', 'FLOAT "43e0000000000000"'), '(PFLOAT 4890909195324358656)'),
    (literal('NScalarFloat', 'FLOAT "43dfffffffffffff"'), '(PFLOAT 4890909195324358655)'),
    (literal('NScalarFloat', 'FLOAT "c3e0000000000000"'), '(PFLOAT 14114281232179134464)'),
    (literal('NScalarFloat', 'FLOAT "c3e0000000000001"'), '(PFLOAT 14114281232179134465)'),
    (literal('NScalarFloat', 'FLOAT "3ff8000000000000"'), '(PFLOAT 4609434218613702656)'),
    (literal('NScalarFloat', 'FLOAT "10000000000000000"'), 'eps'),
    (literal('NScalarInt', 'INTEGER 17'), '(PINT 17)'),
    (literal('NExprCastInt', constant('NAN')), 'eps'),
    (literal('NExprCastInt', literal('NExprBooleanNot', constant('NAN'))), 'eps'),
]:
    CASES['reference-late-default-error']['checks'].append(
        f'$lossy_optional_integer_deferred_value($plempty(false),{expression}) = {expected}')

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
