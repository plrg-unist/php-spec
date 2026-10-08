"""Genuine adapted FCC birth/default/static checkpoint, without forged positives."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import closure_call_protocol as protocol

ROWS = [('alias-public', 'U', 'q', 7)]
CATALOGUE = HERE / 'trait_data_unpublished_fcc_adaptation_cases.json'
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())['cases']}
INPUTS = (Path(__file__).resolve(), CATALOGUE)
STAGE = ('S.TODO = (STATIC_INIT porigin_static) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if pcallcontext.TARGET = CLOSURE_TARGET n_fcc '
         '-- if pcallcontext.LEXICAL_CLASS = (porigin_exporter) '
         '-- if $class_at(S.CLASSES, porigin_exporter) = (pclassdesc_exporter) '
         '-- if pcallcontext.CALLED_CLASS = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

CHECKS = [
    '$call_current_valid(S)',
    '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
    '$constant_callable_first(S.CONSTANTCLOSURES, pconstantclosure.SITE) = (pconstantclosure)',
    '$trait_real_birth_at(S.CLASSCONSTANTHISTORY, n_fcc) = ((pconstantclosure.SITE, ptraitcachecause))',
    '$trait_cache_cause_selected(S, ptraitcachecause) = (pclassconstantdesc_y)',
    '$trait_fcc_receipt_methods(S, ptraitcachecause) = ((S_copy, ptraitmethod*))',
    '$class_method_origin(S.CLASSES, pcallcontext.FUNCTION) = (pmethoddesc)',
    'pmethoddesc.OWNER = porigin_c',
    'pmethoddesc.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_c porigin_source ptbytes_method',
    '$trait_fetch(S, $trait_plan(S, pclassdesc_c).TRAITS, eps) = TRAITFETCHED pclassdesc_traits*',
    '$trait_fcc_import_source(S, pclassdesc_c, pmethoddesc, pclassdesc_traits*, pconstantclosure.PREFIX) = eps',
    '$trait_fcc_adapted(S, pclassdesc_c, pmethoddesc, pconstantclosure.PREFIX) = (pmethoddesc_unfixed)',
    '$trait_fcc_unfixed(S, porigin_c, $ptlc(pmethoddesc.NAME), pconstantclosure.PREFIX) = (pmethoddesc_unfixed)',
    'pmethoddesc_unfixed.OWNER = porigin_exporter',
    'pmethoddesc_unfixed[.OWNER = porigin_c] = pmethoddesc',
    'pmethoddesc_unfixed.VISIBILITY = PROPERTY_PUBLIC',
    '$method_accessible(S, pmethoddesc_unfixed, (porigin_c))',
    '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
    'pclosurescope.LEXICAL = porigin_exporter',
    'pclosurescope.CALLED = porigin_c',
    r'pclosurescope.RECEIVER = eps /\ pclosurescope.CREATION = eps',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_c, pclosurescope) = (porigin_c)',
    '$constant_callable_record_valid(S, pconstantclosure)',
    '$target_function(S, CLOSURE_TARGET n_fcc) = (pfunction)',
    'pfunction = pmethoddesc.FUNCTION',
    '$default_at(pfunction.DEFAULTS, 0) = (pdefault)',
    'pdefault.KIND = PDSTORED',
    '$lookup(S.ENV, $ptascii("v")) = (n_parameter)',
    '$state_static_at(S, porigin_static) = eps',
    '$trait_static_key(S, porigin_static) = TRAIT_ORIGIN porigin_c porigin_static ptbytes_method',
    'PhpStep: S ~> S_static',
    'S_static.COMPLETION = NORMAL',
    'S_static.CURRENT = S.CURRENT',
    '$state_static_at(S_static, porigin_static) = (n_static)',
    '$lookup(S_static.ENV, $ptascii("n")) = (n_static)',
    'S_static.STORE[n_static] = DEFINED (PINT 0)',
    '$static_at(S_static.STATICS, TRAIT_ORIGIN porigin_c porigin_static ptbytes_method) = (n_static)',
    '$trait_fcc_adapted(S, pclassdesc_c, pmethoddesc, 0) = eps',
    '$trait_fcc_adapted(S, pclassdesc_c, pmethoddesc[.FUNCTION = pmethoddesc.FUNCTION[.DEFAULTS = eps]], pconstantclosure.PREFIX) = eps',
    '$trait_fcc_adapted(S, pclassdesc_c, pmethoddesc[.FUNCTION = pmethoddesc.FUNCTION[.ORIGIN = TRAIT_ORIGIN porigin_c porigin_source $ptascii("forged")]], pconstantclosure.PREFIX) = eps',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_c, pclosurescope[.LEXICAL = porigin_c]) = eps',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_c, pclosurescope[.RECEIVER = (n_fcc)]) = eps',
]

CASES = {
    f'{name}-fcc-default-and-static-identity': {
        'source': SOURCES[name],
        'stage': STAGE + f' -- if pclassdesc_exporter.NAME = $ptascii("{exporter}")',
        'checks': [*CHECKS[:9], f'pmethoddesc.NAME = $ptascii("{method}")',
                   *CHECKS[9:29], f'S.STORE[n_parameter] = DEFINED (PINT {default})',
                   *CHECKS[29:]],
    }
    for name, exporter, method, default in ROWS
}

if __name__ == '__main__':
    protocol.run(CASES, INPUTS)
