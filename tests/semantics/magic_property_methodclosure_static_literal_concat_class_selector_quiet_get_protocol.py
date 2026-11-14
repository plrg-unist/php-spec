#!/usr/bin/env python3
"""Check raw class-concat authority composed with literal method concatenation."""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_literal_concat_method_selector_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_concat_class_selector_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

LEFT = 'NScalarString (BYTES text_class_left) metadata_class_left'
RIGHT = 'NScalarString (BYTES text_class_right) metadata_class_right'
CLASS = f'NExprBinaryOpConcat ({LEFT}) ({RIGHT}) metadata_selector'
AUTHORITY = r'''
$origin_child((porigin_selector),[PCFIELD 0]) = (porigin_class_left)
$origin_child((porigin_selector),[PCFIELD 1]) = (porigin_class_right)
$origin_node(S.SOURCES,porigin_class_left) = (LEFT)
$origin_node(S.SOURCES,porigin_class_right) = (RIGHT)
ptbytes_raw = $base64(text_class_left) ++ $base64(text_class_right)
$compiled_read(S,porigin_class_left) = eps
$compiled_read(S,porigin_class_right) = eps
$property_magic_cv_static_method_site_selector(S_trim,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
$compiled_read(S_trim,porigin_selector) = (PSTRING ptbytes_raw)
$compiled_read(S_trim,porigin_class_left) = eps
$compiled_read(S_trim,porigin_class_right) = eps
'''.replace('LEFT', LEFT).replace('RIGHT', RIGHT).strip().splitlines()


def checks(old, index):
    matches = re.findall(r"^\$(?:held|seed) = '([^'\n]+)'::", prior.ROWS[index]['source'], re.M)
    assert len(matches) == 1
    raw = matches[0].replace('\\\\', '\\').encode()
    encoded = json.dumps(base64.b64encode(raw).decode())
    result = [check.replace('phpType19_selector = NScalarString (BYTES text_selector) metadata_selector',
                            'phpType19_selector = ' + CLASS).replace('text_selector', encoded)
              for check in old]
    result += AUTHORITY
    for label, value, extra in (
        ('missing', None, ''),
        ('type', 'PINT 17', ''),
        ('case', 'PSTRING $ptlc(ptbytes_raw)', ''),
        ('child_only', None, ',PCONSTANT (pcpath_site ++ [PCFIELD 0,PCFIELD 0]) (PSTRING ptbytes_raw)'),
    ):
        constants = '[PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING ptbytes_method)'
        if value is not None:
            constants += ',PCONSTANT (pcpath_site ++ [PCFIELD 0]) (' + value + ')'
        constants += extra + ']'
        result += [
            f'S_class_concat_{label} = S[.POOLS = [{{UNIT n_site,CONSTANTS ({constants})}}]]',
            f'$compiled_read(S_class_concat_{label},porigin_selector) = ' + ('eps' if value is None else '(' + value + ')'),
            f'$property_magic_cv_static_method_site_name(S_class_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'$scoped_source_method_origin(S_class_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'$scoped_requested_site(S_class_concat_{label},porigin_site,phpType19_selector,porigin_requested,eps)',
            f'~$property_magic_cv_static_method_site_selector(S_class_concat_{label},porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_class_concat_{label},n_closure)',
        ]
    for label, path, node in (
        ('root', '[PCFIELD 0]', 'NStmtNop metadata_selector'),
        ('left_value', '[PCFIELD 0,PCFIELD 0]', 'NScalarString (BYTES "d3Jvbmc=") metadata_class_left'),
        ('right_value', '[PCFIELD 0,PCFIELD 1]', 'NScalarString (BYTES "d3Jvbmc=") metadata_class_right'),
        ('left_metadata', '[PCFIELD 0,PCFIELD 0]', 'NScalarString (BYTES text_class_left) eps'),
        ('right_metadata', '[PCFIELD 0,PCFIELD 1]', 'NScalarString (BYTES text_class_right) eps'),
        ('left_kind', '[PCFIELD 0,PCFIELD 0]', 'NScalarInt (INTEGER 17) metadata_class_left'),
        ('right_kind', '[PCFIELD 0,PCFIELD 1]', 'NScalarInt (INTEGER 17) metadata_class_right'),
    ):
        result += [
            f'S_class_concat_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {path}) ({node})) :: pcunit.OCCURRENCES]]]',
            f'$origin_node(S_class_concat_{label}.SOURCES,PORIGIN n_site (pcpath_site ++ {path})) = ({node})',
            f'$compiled_read(S_class_concat_{label},porigin_selector) = (PSTRING ptbytes_raw)',
            f'$property_magic_cv_static_method_site_name(S_class_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'~$property_magic_cv_static_method_site_selector(S_class_concat_{label},porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_class_concat_{label},n_closure)',
        ]
    for label, node, origin, expected in (
        ('left_missing', RIGHT, 'porigin_class_right', 'porigin_class_left'),
        ('right_missing', LEFT, 'porigin_class_left', 'porigin_class_right'),
    ):
        path = '[PCFIELD 0,PCFIELD 1]' if label == 'left_missing' else '[PCFIELD 0,PCFIELD 0]'
        occurrences = f'[(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0]) ({CLASS})),(PCOCCURRENCE (pcpath_site ++ {path}) ({node}))]'
        result += [
            f'S_class_concat_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
            f'$origin_node(S_class_concat_{label}.SOURCES,porigin_selector) = (phpType19_selector)',
            f'$origin_node(S_class_concat_{label}.SOURCES,{origin}) = ({node})',
            f'$origin_node(S_class_concat_{label}.SOURCES,{expected}) = eps',
            f'$compiled_read(S_class_concat_{label},porigin_selector) = (PSTRING ptbytes_raw)',
            f'~$property_magic_cv_static_method_site_selector(S_class_concat_{label},porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
        ]
    for label, left in (
        ('nested', f'NExprBinaryOpConcat ({LEFT}) (NScalarString (BYTES "") metadata_class_left) metadata_class_left'),
        ('variable', 'NExprVariable (BYTES "Y2xhc3NQYXJ0") metadata_class_left'),
    ):
        node = f'NExprBinaryOpConcat ({left}) ({RIGHT}) metadata_selector'
        occurrences = f'[(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0]) ({node})),(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 0]) ({left})),(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 1]) ({RIGHT}))'
        if label == 'nested':
            occurrences += f',(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) ({LEFT})),(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 0,PCFIELD 1]) (NScalarString (BYTES "") metadata_class_left))'
        occurrences += '] ++ pcunit.OCCURRENCES'
        result += [
            f'expression_class_{label} = {node}',
            f'S_class_concat_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
            f'$origin_node(S_class_concat_{label}.SOURCES,porigin_selector) = (expression_class_{label})',
            f'$compiled_read(S_class_concat_{label},porigin_selector) = (PSTRING ptbytes_raw)',
            ('' if label == 'nested' else '~') + f'$property_magic_cv_static_method_site_selector(S_class_concat_{label},porigin_site,expression_class_{label},porigin_requested,pclassdesc_requested.NAME)',
        ]
        if label == 'nested':
            result += ['~$property_magic_cv_static_methodclosure(S_class_concat_nested,n_closure)']
    result += ['$parser_literal(expression_class_nested) = (PSTRING ptbytes_raw)']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (prior, prior.prior, prior.prior.original, prior.prior.inherited,
               prior.prior.inherited.prior, prior.prior.inherited.prior.prior,
               prior.prior.inherited.prior.prior.prior)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',))
