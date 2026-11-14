#!/usr/bin/env python3
"""Check folded class roots before one-prefix normalization and method composition."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_literal_selector_quiet_get_review_protocol as literal
import magic_property_methodclosure_static_literal_concat_method_selector_quiet_get_review_protocol as method

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_concat_class_selector_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

LEFT = 'NScalarString (BYTES text_class_left) metadata_class_left'
RIGHT = 'NScalarString (BYTES text_class_right) metadata_class_right'
CLASS = f'NExprBinaryOpConcat ({LEFT}) ({RIGHT}) metadata_requested'
METHOD_POOL = 'PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING ptbytes_method)'


def pools(value=None, extra=()):
    constants = [METHOD_POOL]
    if value is not None:
        constants.append('PCONSTANT (pcpath_site ++ [PCFIELD 0]) (' + value + ')')
    constants.extend(extra)
    return '[{UNIT n_unit,CONSTANTS ([' + ','.join(constants) + '])}]'


def refusal(label, state):
    return [f'S_class_concat_{label} = {state}',
            f'~$property_magic_cv_static_method_site_selector(S_class_concat_{label},porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_class_concat_{label},n_closure)',
            f'~$property_empty_rv_kind(S_class_concat_{label},S_class_concat_{label}.OBJECTS[n_closure])']


def source_state(changes):
    occurrences = 'pcunit.OCCURRENCES'
    for path, node in changes:
        occurrences = f'$rc_review_occurrence({occurrences},pcpath_site ++ {path},{node})'
    return 'S[.SOURCES = [pcunit[.OCCURRENCES = ' + occurrences + ']]]'


def coherent_class(node, left, right, value):
    site = ('NExprStaticCall (' + node + ') phpType20_method '
            '(SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site')
    state = source_state((('eps', site), ('[PCFIELD 0]', node),
                          ('[PCFIELD 0,PCFIELD 0]', left),
                          ('[PCFIELD 0,PCFIELD 1]', right)))
    return state + '[.POOLS = ' + pools('PSTRING ' + value) + ']'


SELECTOR = r'''
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)
phpType19_selector = CLASS
$origin_child((porigin_site),[PCFIELD 0]) = (porigin_selector)
porigin_selector = PORIGIN n_unit (pcpath_site ++ [PCFIELD 0])
$origin_child((porigin_selector),[PCFIELD 0]) = (porigin_class_left)
$origin_child((porigin_selector),[PCFIELD 1]) = (porigin_class_right)
$origin_node(S.SOURCES,porigin_selector) = (phpType19_selector)
$origin_node(S.SOURCES,porigin_class_left) = (LEFT)
$origin_node(S.SOURCES,porigin_class_right) = (RIGHT)
ptbytes_class_raw = $base64(text_class_left) ++ $base64(text_class_right)
ptbytes_class_raw = $base64(text_requested)
$compiled_read(S,porigin_selector) = (PSTRING ptbytes_class_raw)
$compiled_read(S,porigin_class_left) = eps
$compiled_read(S,porigin_class_right) = eps
$ptlc(ptbytes_class_raw) =/= ptbytes_class_raw
$ptlc($ppcall_literal_name(ptbytes_class_raw)) = $ptlc(pclassdesc_requested.NAME)
$class_named(S.CLASSNAMES,$ptlc($ppcall_literal_name(ptbytes_class_raw))) = (porigin_requested)
$scoped_requested_site(S,porigin_site,phpType19_selector,porigin_requested,eps)
$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_selector(phpType19_selector,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_selector,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_method,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_requested,pclassdesc_receiver.NAME)
~$property_magic_cv_static_method_site_selector(S[.SOURCES = eps],porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S[.CLASSNAMES = eps],porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
'''.replace('phpType19_selector = CLASS', 'phpType19_selector = ' + CLASS).replace('LEFT', LEFT).replace('RIGHT', RIGHT).strip().splitlines()


def checks(old, index):
    raw_class = ('\\qUIETmETHODsTATICiNHERITEDcvtARGET' if index == 0
                 else 'qUIETmETHODsTATICiNHERITEDlITERALtARGET')
    encoded = base64.b64encode(raw_class.encode()).decode()
    result = [f'text_requested = "{encoded}"']
    inherited_checks = literal.checks(old, index)
    # Reuse the genuine member, cache and lifetime proof without old selector tests.
    inherited_checks = inherited_checks[:inherited_checks.index(literal.SELECTOR[0])]
    for check in inherited_checks:
        if check.startswith('$origin_node(S.SOURCES,porigin_site) = ') or check.startswith('$scoped_requested_site(S,porigin_site,'):
            check = check.replace('NScalarString (BYTES text_requested) metadata_requested', CLASS)
        result.append(check.replace('NIdentifier (BYTES text_selected) metadata_selected', method.METHOD)
                      .replace('$base64(text_selected)', '($base64(text_left) ++ $base64(text_right))'))
    result += SELECTOR
    for check in method.NAME:
        if check.startswith('S_concat_root_only = '):
            break
        result.append(check.replace('phpType19_class', 'phpType19_selector'))
    result += [
        'S_class_concat_root_only = S[.POOLS = ' + pools('PSTRING ptbytes_class_raw') + ']',
        '$compiled_read(S_class_concat_root_only,porigin_class_left) = eps',
        '$compiled_read(S_class_concat_root_only,porigin_class_right) = eps',
        '$property_magic_cv_static_method_site_selector(S_class_concat_root_only,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
        '$property_magic_cv_static_methodclosure(S_class_concat_root_only,n_closure)',
        '$property_empty_rv_kind(S_class_concat_root_only,S_class_concat_root_only.OBJECTS[n_closure])',
    ]
    prefix = '$ppcall_literal_name(ptbytes_class_raw)' if index == 0 else '(92 :: ptbytes_class_raw)'
    result += ['ptbytes_class_prefix = ' + prefix, 'ptbytes_class_prefix =/= ptbytes_class_raw']
    for label, value, extra in (
        ('missing', None, ()), ('type', 'PINT 17', ()),
        ('case', 'PSTRING $ptlc(ptbytes_class_raw)', ()),
        ('prefix', 'PSTRING ptbytes_class_prefix', ()),
        ('wrong_slot', None, ('PCONSTANT (pcpath_site ++ [PCFIELD 0,PCFIELD 2]) (PSTRING ptbytes_class_raw)',)),
        ('children_only', None, ('PCONSTANT (pcpath_site ++ [PCFIELD 0,PCFIELD 0]) (PSTRING $base64(text_class_left))',
                                 'PCONSTANT (pcpath_site ++ [PCFIELD 0,PCFIELD 1]) (PSTRING $base64(text_class_right))')),
    ):
        result += refusal(label, 'S[.POOLS = ' + pools(value, extra) + ']')
        result += [f'$compiled_read(S_class_concat_{label},porigin_selector) = ' + ('eps' if value is None else '(' + value + ')'),
                   f'$scoped_requested_site(S_class_concat_{label},porigin_site,phpType19_selector,porigin_requested,eps)',
                   f'$property_magic_cv_static_method_site_name(S_class_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)']
    for label, path, node in (
        ('root_kind', '[PCFIELD 0]', 'NStmtNop metadata_requested'),
        ('root_order', '[PCFIELD 0]', f'NExprBinaryOpConcat ({RIGHT}) ({LEFT}) metadata_requested'),
        ('root_metadata', '[PCFIELD 0]', f'NExprBinaryOpConcat ({LEFT}) ({RIGHT}) eps'),
        ('left_value', '[PCFIELD 0,PCFIELD 0]', 'NScalarString (BYTES "T3RoZXI=") metadata_class_left'),
        ('right_value', '[PCFIELD 0,PCFIELD 1]', 'NScalarString (BYTES "T3RoZXI=") metadata_class_right'),
        ('left_metadata', '[PCFIELD 0,PCFIELD 0]', 'NScalarString (BYTES text_class_left) eps'),
        ('right_metadata', '[PCFIELD 0,PCFIELD 1]', 'NScalarString (BYTES text_class_right) eps'),
        ('left_kind', '[PCFIELD 0,PCFIELD 0]', 'NExprVariable (BYTES text_class_left) metadata_class_left'),
        ('right_kind', '[PCFIELD 0,PCFIELD 1]', 'NExprVariable (BYTES text_class_right) metadata_class_right'),
        ('left_missing', '[PCFIELD 0,PCFIELD 0]', 'NStmtNop metadata_class_left'),
        ('right_missing', '[PCFIELD 0,PCFIELD 1]', 'NStmtNop metadata_class_right'),
    ):
        result += refusal(label, source_state(((path, node),)))
        result += [f'$origin_node(S_class_concat_{label}.SOURCES,PORIGIN n_unit (pcpath_site ++ {path})) = ({node})',
                   f'$compiled_read(S_class_concat_{label},porigin_selector) = (PSTRING ptbytes_class_raw)',
                   f'$scoped_requested_site(S_class_concat_{label},porigin_site,phpType19_selector,porigin_requested,eps)',
                   f'$property_magic_cv_static_method_site_name(S_class_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)']
    for label, left, right in (
        ('nested', LEFT, f'NExprBinaryOpConcat ({RIGHT}) (NScalarString (BYTES "") metadata_class_right) metadata_class_right'),
        ('numeric', 'NScalarInt (INTEGER 0) metadata_class_left', RIGHT),
        ('variable', 'NExprVariable (BYTES text_class_left) metadata_class_left', RIGHT),
    ):
        node = f'NExprBinaryOpConcat ({left}) ({right}) metadata_requested'
        result += [f'phpType19_{label} = {node}',
                   f'S_class_concat_{label} = ' + coherent_class(node, left, right, 'ptbytes_class_raw'),
                   f'$origin_node(S_class_concat_{label}.SOURCES,porigin_selector) = (phpType19_{label})',
                   f'$compiled_read(S_class_concat_{label},porigin_selector) = (PSTRING ptbytes_class_raw)',
                   f'$scoped_requested_site(S_class_concat_{label},porigin_site,phpType19_{label},porigin_requested,eps)',
                   f'$property_magic_cv_static_method_site_name(S_class_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
                   f'~$property_magic_cv_static_method_site_selector(S_class_concat_{label},porigin_site,phpType19_{label},porigin_requested,pclassdesc_requested.NAME)',
                   f'~$property_magic_cv_static_methodclosure(S_class_concat_{label},n_closure)']
    double = base64.b64encode(('\\\\' + raw_class.removeprefix('\\')).encode()).decode()
    left = f'NScalarString (BYTES "{double}") metadata_class_left'
    right = 'NScalarString (BYTES "") metadata_class_right'
    node = f'NExprBinaryOpConcat ({left}) ({right}) metadata_requested'
    result += [
        'ptbytes_class_double = 92 :: (92 :: $ppcall_literal_name(ptbytes_class_raw))',
        f'phpType19_double = {node}',
        'S_class_concat_double = ' + coherent_class(node, left, right, 'ptbytes_class_double'),
        '$compiled_read(S_class_concat_double,porigin_selector) = (PSTRING ptbytes_class_double)',
        '$ppcall_literal_name(ptbytes_class_double) = 92 :: $ppcall_literal_name(ptbytes_class_raw)',
        '$class_named(S_class_concat_double.CLASSNAMES,$ptlc($ppcall_literal_name(ptbytes_class_double))) = eps',
        '~$scoped_requested_site(S_class_concat_double,porigin_site,phpType19_double,porigin_requested,eps)',
        '~$property_magic_cv_static_method_site_selector(S_class_concat_double,porigin_site,phpType19_double,porigin_requested,pclassdesc_requested.NAME)',
        '~$property_magic_cv_static_methodclosure(S_class_concat_double,n_closure)',
        '~$property_empty_rv_kind(S_class_concat_double,S_class_concat_double.OBJECTS[n_closure])',
    ]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, literal.OLD, strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (literal, method, literal.own, literal.own.prior, literal.own.prior.prior,
               literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
               literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
               literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=literal.own.prior.prior.literal.render)
