#!/usr/bin/env python3
"""Check two raw method-name strings with folded-root and source authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_literal_selector_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_concat_method_selector_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

LEFT = 'NScalarString (BYTES text_left) metadata_left'
RIGHT = 'NScalarString (BYTES text_right) metadata_right'
CONCAT = f'NExprBinaryOpConcat ({LEFT}) ({RIGHT}) metadata_selected'
NAME = r'''
S.SOURCES = [pcunit]
pcunit.ID = n_site
phpType20_method = METHOD
$origin_child((porigin_site),[PCFIELD 1]) = (porigin_name)
porigin_name = PORIGIN n_site (pcpath_site ++ [PCFIELD 1])
$origin_node(S.SOURCES,porigin_name) = (phpType20_method)
$origin_child((porigin_name),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_name),[PCFIELD 1]) = (porigin_right)
$origin_node(S.SOURCES,porigin_left) = (LEFT)
$origin_node(S.SOURCES,porigin_right) = (RIGHT)
ptbytes_method = $base64(text_left) ++ $base64(text_right)
$compiled_read(S,porigin_name) = (PSTRING ptbytes_method)
$compiled_read(S,porigin_left) = eps
$compiled_read(S,porigin_right) = eps
$ptlc(ptbytes_method) = $ptlc(pmethoddesc_method.NAME)
$ptlc(ptbytes_method) =/= ptbytes_method
$scoped_source_method_origin(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_name,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S[.SOURCES = eps],porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pclassdesc_requested.NAME)
S_trim = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_raw),PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING ptbytes_method)])}]]
$compiled_read(S_trim,porigin_left) = eps
$compiled_read(S_trim,porigin_right) = eps
$property_magic_cv_static_method_site_name(S_trim,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_methodclosure(S_trim,n_closure)
$property_empty_rv_kind(S_trim,S_trim.OBJECTS[n_closure])
'''.replace('METHOD', CONCAT).replace('LEFT', LEFT).replace('RIGHT', RIGHT).strip().splitlines()


def checks(old):
    result = [check.replace('NIdentifier (BYTES text_selected) metadata_selected', CONCAT)
              .replace('$base64(text_selected)', '($base64(text_left) ++ $base64(text_right))')
              for check in old]
    result += NAME
    for label, value in (('missing', None), ('type', 'PINT 17'),
                         ('case', 'PSTRING $ptlc(ptbytes_method)'),
                         ('slash', 'PSTRING (92 :: ptbytes_method)')):
        constants = '[PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_raw)'
        if value is not None:
            constants += ',PCONSTANT (pcpath_site ++ [PCFIELD 1]) (' + value + ')'
        constants += ']'
        result += [
            f'S_concat_{label} = S[.POOLS = [{{UNIT n_site,CONSTANTS ({constants})}}]]',
            f'$compiled_read(S_concat_{label},porigin_name) = ' + ('eps' if value is None else '(' + value + ')'),
            f'$property_magic_cv_static_method_site_selector(S_concat_{label},porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
            f'$scoped_source_method_origin(S_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'~$property_magic_cv_static_method_site_name(S_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_concat_{label},n_closure)',
            f'~$property_empty_rv_kind(S_concat_{label},S_concat_{label}.OBJECTS[n_closure])',
        ]
    for label, path, node in (
        ('root', '[PCFIELD 1]', 'NStmtNop metadata_selected'),
        ('left_value', '[PCFIELD 1,PCFIELD 0]', 'NScalarString (BYTES "d3Jvbmc=") metadata_left'),
        ('right_value', '[PCFIELD 1,PCFIELD 1]', 'NScalarString (BYTES "d3Jvbmc=") metadata_right'),
        ('left_metadata', '[PCFIELD 1,PCFIELD 0]', 'NScalarString (BYTES text_left) eps'),
        ('right_metadata', '[PCFIELD 1,PCFIELD 1]', 'NScalarString (BYTES text_right) eps'),
    ):
        result += [
            f'S_concat_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {path}) ({node})) :: pcunit.OCCURRENCES]]]',
            f'$origin_node(S_concat_{label}.SOURCES,PORIGIN n_site (pcpath_site ++ {path})) = ({node})',
            f'$compiled_read(S_concat_{label},porigin_name) = (PSTRING ptbytes_method)',
            f'~$property_magic_cv_static_method_site_name(S_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_concat_{label},n_closure)',
        ]
    for label, left, right, value in (
        ('nested', f'NExprBinaryOpConcat ({LEFT}) (NScalarString (BYTES "") metadata_left) metadata_left', RIGHT, 'ptbytes_method'),
        ('numeric', 'NScalarString (BYTES "Q29VblRlUg==") metadata_left', 'NScalarInt (INTEGER 0) metadata_right', '($ptascii("CoUnTeR0"))'),
        ('variable', f'NExprVariable (BYTES text_left) metadata_left', RIGHT, 'ptbytes_method'),
        ('raw_slash', 'NScalarString (BYTES "XENvVW5UZVI=") metadata_left', 'NScalarString (BYTES "") metadata_right', '(92 :: $ptascii("CoUnTeR"))'),
    ):
        node = f'NExprBinaryOpConcat ({left}) ({right}) metadata_selected'
        occurrences = f'[(PCOCCURRENCE (pcpath_site ++ [PCFIELD 1]) ({node})),(PCOCCURRENCE (pcpath_site ++ [PCFIELD 1,PCFIELD 0]) ({left})),(PCOCCURRENCE (pcpath_site ++ [PCFIELD 1,PCFIELD 1]) ({right}))] ++ pcunit.OCCURRENCES'
        result += [
            f'expression_{label} = {node}',
            f'S_concat_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]][.POOLS = [{{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING {value})])}}]]',
            f'$origin_node(S_concat_{label}.SOURCES,porigin_name) = (expression_{label})',
            f'$compiled_read(S_concat_{label},porigin_name) = (PSTRING {value})',
            ('' if label == 'numeric' else '~') + f'$property_magic_cv_static_method_site_name(S_concat_{label},porigin_site,expression_{label},' + (value if label == 'numeric' else 'pmethoddesc_method.NAME') + ')',
        ]
        if label == 'numeric':
            result.append('~$property_magic_cv_static_methodclosure(S_concat_numeric,n_closure)')
    result += [
        '$parser_literal(expression_nested) = (PSTRING ptbytes_method)',
        '$parser_literal(expression_numeric) = (PSTRING $ptascii("CoUnTeR0"))',
        '$parser_literal(expression_raw_slash) = (PSTRING (92 :: $ptascii("CoUnTeR")))',
        '$ppcall_literal_name(92 :: $ptascii("CoUnTeR")) = $ptascii("CoUnTeR")',
    ]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks']))
         for row, old in zip(ROWS, prior.CASES.values(), strict=True)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (prior, prior.original, prior.inherited, prior.inherited.prior,
               prior.inherited.prior.prior, prior.inherited.prior.prior.prior)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',))
