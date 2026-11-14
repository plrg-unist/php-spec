#!/usr/bin/env python3
"""Check direct parent spellings without weakening raw empty-root authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_empty_parent_quiet_get_review_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_empty_parent_selector_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

EXTRA = r'''
$base64(text_parent) =/= pclassdesc_parent.NAME
$ptlc($base64(text_parent)) = $ptlc(pclassdesc_parent.NAME)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NName (BYTES text_parent_decl) metadata_extends)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NNameFullyQualified (BYTES text_parent_decl) metadata_extends)
S_parent_raw_case = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_parent,NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parent) metadata_parent_name) ABSENT (SEQUENCE eps) (SEQUENCE eps) metadata_parent)]]]
~$property_magic_cv_static_method_parent(S_parent_raw_case,pclassdesc_target,phpType44_parent)
~$property_magic_cv_static_methodclosure(S_parent_raw_case,n_closure)
~$property_empty_rv_kind(S_parent_raw_case,S.OBJECTS[n_closure])
S_child_resolved_case = S[.CLASSES = [pclassdesc_parent,pclassdesc_target[.PARENT = (pclassdesc_parent.NAME)],pclassdesc_receiver]]
~$property_magic_cv_static_methodclosure(S_child_resolved_case,n_closure)
~$property_empty_rv_kind(S_child_resolved_case,S.OBJECTS[n_closure])
S_child_raw_case = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_class,NStmtClass phpType14_class phpType24_class (NIdentifier (BYTES text_class) metadata_class_name) (NName (BYTES text_parent_decl) metadata_extends) phpType42 (SEQUENCE ([statement_method])) metadata_class)]]]
~$property_magic_cv_static_methodclosure(S_child_raw_case,n_closure)
~$property_empty_rv_kind(S_child_raw_case,S.OBJECTS[n_closure])
S_child_plain = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_class,NStmtClass phpType14_class phpType24_class (NIdentifier (BYTES text_class) metadata_class_name) (NName (BYTES text_parent) metadata_extends) phpType42 (SEQUENCE ([statement_method])) metadata_class)]]]
$property_magic_cv_static_methodclosure(S_child_plain,n_closure)
$property_empty_rv_kind(S_child_plain,S.OBJECTS[n_closure])
'''.strip().splitlines()


def checks(old, constructor):
    result = []
    for check in old:
        check = check.replace('phpType44_parent = NName (BYTES text_parent) metadata_extends',
                              'phpType44_parent = ' + constructor + ' (BYTES text_parent) metadata_extends')
        check = check.replace('NIdentifier (BYTES text_parent) metadata_parent_name',
                              'NIdentifier (BYTES text_parent_decl) metadata_parent_name')
        check = check.replace('pclassdesc_parent.NAME = ptbytes_parent /\\ pclassdesc_parent.KIND',
                              '$ptlc(pclassdesc_parent.NAME) = $ptlc(ptbytes_parent) /\\ pclassdesc_parent.KIND')
        if check in (
            '~$property_magic_cv_static_method_parent(S,pclassdesc_target,NNameFullyQualified (BYTES text_parent) metadata_extends)',
            '~$property_magic_cv_static_methodclosure(S_child_fully_qualified,n_closure)',
            '~$property_empty_rv_kind(S_child_fully_qualified,S.OBJECTS[n_closure])',
        ):
            check = check[1:]
        result.append(check)
        if check.startswith('statement_parent = NStmtClass '):
            result.append('pclassdesc_parent.NAME = $base64(text_parent_decl)')
    return result + EXTRA


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], constructor))
         for row, old, constructor in zip(ROWS, prior.CASES.values(),
                                           ('NName', 'NNameFullyQualified'), strict=True)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.prior.__file__), prior.prior.CATALOGUE,
                  Path(prior.prior.prior.__file__), prior.prior.prior.CATALOGUE,
                  Path(prior.prior.prior.owning.__file__), prior.prior.prior.owning.CATALOGUE,
                  Path(prior.prior.prior.literal.__file__), prior.prior.prior.literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.prior.literal.render)
