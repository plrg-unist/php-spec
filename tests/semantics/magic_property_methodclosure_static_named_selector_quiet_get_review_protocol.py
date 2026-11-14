#!/usr/bin/env python3
"""Check direct mixed-case static selectors without widening source or cache authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_clone_quiet_get_review_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_named_selector_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def front(constructor):
    checks = []
    for check in prior.FRONT:
        check = check.replace('NName (BYTES text_requested) metadata_requested',
                              constructor + ' (BYTES text_requested) metadata_requested')
        check = check.replace('$base64(text_requested) = pclassdesc_target.NAME',
                              '$ptlc($base64(text_requested)) = $ptlc(pclassdesc_target.NAME)')
        check = check.replace('((pclassdesc_target.NAME,eps))',
                              '(($base64(text_requested),eps))')
        checks.append(check)
    return checks


def source_counterfact(label, class_name):
    site = ('NExprStaticCall (' + class_name + ') '
            '(NIdentifier (BYTES text_selected) metadata_selected) '
            '(SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site')
    return [
        f'S_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_site,{site})]]]',
        f'~$property_magic_cv_static_methodclosure(S_{label},n_closure)',
        f'~$property_empty_rv_kind(S_{label},S.OBJECTS[n_closure])',
    ]


SELECTOR = r'''
$property_magic_cv_static_method_selector(NName (BYTES text_requested) metadata_requested,pclassdesc_target.NAME)
$property_magic_cv_static_method_selector(NNameFullyQualified (BYTES text_requested) metadata_requested,pclassdesc_target.NAME)
$base64(text_requested) =/= pclassdesc_target.NAME
~$property_magic_cv_static_method_selector(NNameRelative (BYTES text_requested) metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_method_selector(NExprVariable (BYTES text_requested) metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_method_selector(NScalarString (BYTES text_requested) metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_method_selector(NName (BYTES "T3RoZXI=") metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_method_selector(NNameFullyQualified (BYTES "T3RoZXI=") metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_method_selector(NName (BYTES "c2VsZg==") metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_method_selector(NName (BYTES "cGFyZW50") metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_method_selector(NName (BYTES "c3RhdGlj") metadata_requested,pclassdesc_target.NAME)
~$property_magic_cv_static_methodclosure(S[.CLASSNAMES = eps],n_closure)
~$property_magic_cv_static_methodclosure(S[.CODE = [pcode[.NAMES = [CODENAME pcpath_site pclassdesc_receiver.NAME eps]]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CODE = [pcode[.NAMES = [CODENAME pcpath_site pclassdesc_target.NAME (pclassdesc_receiver.NAME)]]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = [pclosurecache_original,pclosurecache_intermediate,pclosurecache[.FUNCTION = pmethoddesc.FUNCTION.ORIGIN]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLOSURECACHES = [pclosurecache_original,pclosurecache_intermediate,pclosurecache[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]],n_closure)
'''.strip().splitlines()
for label, class_name in (
    ('named_other', 'NName (BYTES "T3RoZXI=") metadata_requested'),
    ('fqn_other', 'NNameFullyQualified (BYTES "T3RoZXI=") metadata_requested'),
    ('alias', 'NName (BYTES "QWxpYXM=") metadata_requested'),
    ('relative', 'NNameRelative (BYTES text_requested) metadata_requested'),
    ('dynamic', 'NExprVariable (BYTES "aGVsZA==") metadata_requested'),
    ('string', 'NScalarString (BYTES text_requested) metadata_requested'),
    ('keyword', 'NName (BYTES "c2VsZg==") metadata_requested'),
):
    SELECTOR += source_counterfact(label, class_name)

STAGE = prior.STAGE
CASES = {
    ROWS[0]['id']: {
        'source': ROWS[0]['source'], 'stage': STAGE,
        'checks': front('NNameFullyQualified') + prior.AUTHORITY + SELECTOR + [
            '$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
            '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
        ] + prior.LIFETIME + prior.DONE + [
            'S_done.STORE[n_destination] = DEFINED (PBOOL false)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("WARM;SOURCES_GONE;I;G;RECEIVER;WRAPPER_GONE;FALSE;CAPTURE;RECEIVER_GONE;STATIC;DONE;")',
        ],
    },
    ROWS[1]['id']: {
        'source': ROWS[1]['source'], 'stage': STAGE,
        'checks': front('NName') + prior.BASIC + SELECTOR + [
            '~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
        ] + prior.LIFETIME + prior.THROW + prior.DONE + [
            'S_done.STORE[n_destination] = DEFINED (PINT 42)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("WARM;SOURCES_GONE;I;G;RECEIVER;WRAPPER_GONE;CAUGHT;KEEP;CAPTURE;RECEIVER_GONE;STATIC;DONE;")',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.owning.__file__), prior.owning.CATALOGUE,
                  Path(prior.literal.__file__), prior.literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=prior.literal.render)
