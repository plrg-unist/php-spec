#!/usr/bin/env python3
"""Check actual fully qualified keyword children in quiet method captures."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_review_protocol as prior

raw = prior.prior
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_fqn_keyword_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def tree(side, state='S'):
    return (f'$property_magic_cv_raw_fqn_keyword_string_tree({state}.SOURCES,'
            f'porigin_tree_root_{side},expression_{side})')


def checks(index):
    result = [
        'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
        '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
        '$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)',
        'porigin_site = PORIGIN n_unit pcpath_site', 'S.SOURCES = [pcunit]',
        '$origin_node(S.SOURCES,porigin_site) = (NExprStaticCall (NExprBinaryOpConcat expression_class_left expression_class_right metadata_class) (NExprBinaryOpConcat expression_method_left expression_method_right metadata_method) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site)',
        'expression_class = NExprBinaryOpConcat expression_class_left expression_class_right metadata_class',
        'expression_method = NExprBinaryOpConcat expression_method_left expression_method_right metadata_method',
    ]
    for field, side in enumerate(('class', 'method')):
        result += [f'$origin_child((porigin_site),[PCFIELD {field}]) = (porigin_tree_root_{side})',
                   tree(side) + f' = (ptbytes_{side})',
                   f'$property_magic_cv_raw_keyword_string_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps',
                   f'$compiled_read(S,porigin_tree_root_{side}) = (PSTRING ptbytes_{side})',
                   raw.selector(side)]
    result += ['$property_magic_cv_static_methodclosure(S,n_closure)',
               '$property_empty_rv_kind(S,S.OBJECTS[n_closure])',
               'S_roots = S[.POOLS = ' + raw.root_pools('class', 'PSTRING ptbytes_class') + ']',
               '$property_magic_cv_static_methodclosure(S_roots,n_closure)']
    keywords = ((('class', (0, 1, 1, 1, 0, 0), 'false'),
                 ('class', (0, 1, 1, 1, 0, 1), 'null'),
                 ('method', (1, 1, 1, 1, 1), 'true')) if index == 0 else
                (('class', (0, 0, 1, 1), 'true'),
                 ('method', (1, 1, 1, 1, 1, 1, 1, 0), 'false'),
                 ('method', (1, 1, 1, 1, 1, 1, 1, 1), 'null')))
    for number, (side, parts, word) in enumerate(keywords):
        suffix = str(number)
        origin = 'porigin_keyword_' + suffix
        name_origin = 'porigin_name_' + suffix
        text = 'text_keyword_' + suffix
        metadata = 'metadata_keyword_' + suffix
        name_metadata = 'metadata_name_' + suffix
        expression = 'expression_keyword_' + suffix
        name = f'NNameFullyQualified (BYTES {text}) {name_metadata}'
        node = f'NExprConstFetch ({name}) {metadata}'
        value = {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}[word]
        rendered = '($ptascii("1"))' if word == 'true' else '(eps)'
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'{name_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({name_origin})',
                   f'$origin_node(S.SOURCES,{name_origin}) = ({name})',
                   f'$special_constant($base64({text})) = ({value})',
                   f'$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,{origin},{expression}) = {rendered}',
                   f'$property_magic_cv_raw_keyword_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   f'$compiled_read(S_roots,{name_origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        other = base64.b64encode(('null' if word == 'false' else 'false').encode()).decode()
        for label, changed_parts, forged in (
            ('expression_metadata', parts, f'NExprConstFetch ({name}) eps'),
            ('expression_type', parts, f'NExprVariable (BYTES {text}) {metadata}'),
            ('expression_value', parts, f'NExprConstFetch (NNameFullyQualified (BYTES "{other}") {name_metadata}) {metadata}'),
            ('expression_missing', parts, None),
            ('name_metadata', parts + (0,), f'NNameFullyQualified (BYTES {text}) eps'),
            ('name_type', parts + (0,), f'NName (BYTES {text}) {name_metadata}'),
            ('name_value', parts + (0,), f'NNameFullyQualified (BYTES "{other}") {name_metadata}'),
            ('name_missing', parts + (0,), None),
        ):
            state = f'S_keyword_{number}_{label}'
            location = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{location})' if forged is None else
                           f'(PCOCCURRENCE ({location}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       tree(side, state) + ' = eps',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    for field, side in enumerate(('class', 'method')):
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PBOOL true', ()),
            ('case', f'PSTRING $ptlc(ptbytes_{side})', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {raw.path((field, 2))}) (PSTRING ptbytes_{side})',)),
        ):
            state = f'S_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + raw.root_pools(side, value, extra) + ']',
                       tree(side, state) + f' = (ptbytes_{side})',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    plain = 'NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_site) metadata_site'
    qualified = 'NExprConstFetch (NNameFullyQualified (BYTES "bnVsbA==") metadata_site) metadata_site'
    mixed = f'NExprBinaryOpConcat ({plain}) ({qualified}) metadata_site'
    nodes = [((), mixed), ((0,), plain), ((0, 0), 'NName (BYTES "ZmFsc2U=") metadata_site'),
             ((1,), qualified), ((1, 0), 'NNameFullyQualified (BYTES "bnVsbA==") metadata_site')]
    occurrences = 'pcunit.OCCURRENCES'
    for parts, node in nodes:
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({node})) :: ({occurrences})'
    result += ['expression_mixed = ' + mixed, 'S_mixed = ' + raw.source_state(occurrences),
               '$property_magic_cv_raw_fqn_keyword_string_tree(S_mixed.SOURCES,porigin_tree_root_class,expression_mixed) = (eps)',
               '$property_magic_cv_raw_keyword_string_tree(S_mixed.SOURCES,porigin_tree_root_class,expression_mixed) = eps',
               '$property_magic_cv_raw_fqn_keyword_string_tree(eps,porigin_tree_root_class,expression_mixed) = eps']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    literal = prior.literal
    parents = (prior, raw, literal, literal.own, literal.own.prior, literal.own.prior.prior,
               literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
               literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
               literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=prior.render)
