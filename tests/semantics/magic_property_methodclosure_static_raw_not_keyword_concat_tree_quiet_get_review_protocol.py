#!/usr/bin/env python3
"""Check reserved-keyword BooleanNot and exact raw selector authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_positive_string_concat_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_not_keyword_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def keyword_not(sources, origin, expression):
    return f'$property_magic_cv_raw_not_keyword_string_tree({sources},{origin},{expression})'


def checks(index):
    inherited = prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    result = [line.replace('$property_magic_cv_raw_positive_string_tree(',
                           '$property_magic_cv_raw_not_keyword_string_tree(')
              for line in inherited]
    for side in ('class', 'method'):
        result.append(f'$property_magic_cv_raw_positive_string_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps')
    leaves = ((('class', (0, 1, 1, 1, 0, 0), 'NNameFullyQualified', 'fAlSe', 'PBOOL false', 'false', '1'),
               ('class', (0, 1, 1, 1, 0, 1), 'NName', 'NuLl', 'PNULL', 'false', '1'),
               ('method', (1, 1, 1, 1, 1), 'NName', 'TrUe', 'PBOOL true', 'true', '')) if index == 0 else
              (('class', (0, 0, 1, 1), 'NNameFullyQualified', 'TRUE', 'PBOOL true', 'true', ''),
               ('method', (1, 1, 1, 1, 1, 1, 1, 0), 'NName', 'false', 'PBOOL false', 'false', '1'),
               ('method', (1, 1, 1, 1, 1, 1, 1, 1), 'NNameFullyQualified', 'nUlL', 'PNULL', 'false', '1')))
    for number, (side, parts, kind, word, value, truth, output) in enumerate(leaves):
        suffix = str(number)
        origin, child_origin, name_origin = ('porigin_not_' + suffix, 'porigin_not_child_' + suffix,
                                             'porigin_not_name_' + suffix)
        metadata, child_metadata, name_metadata = ('metadata_not_' + suffix, 'metadata_not_child_' + suffix,
                                                   'metadata_not_name_' + suffix)
        text, data, expression = 'text_not_' + suffix, 'ptbytes_not_' + suffix, 'expression_not_' + suffix
        value_name = 'pvalue_not_' + suffix
        name = f'{kind} (BYTES {text}) {name_metadata}'
        child = f'NExprConstFetch ({name}) {child_metadata}'
        node = f'NExprBooleanNot ({child}) {metadata}'
        complement = 'false' if truth == 'true' else 'true'
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'{child_metadata} =/= eps', f'{name_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
                   f'$origin_child(({child_origin}),[PCFIELD 0]) = ({name_origin})',
                   f'$origin_node(S.SOURCES,{name_origin}) = ({name})',
                   f'{data} = $base64({text})', f'{data} = $ptascii("{word}")',
                   f'$special_constant({data}) = ({value_name})', f'{value_name} = {value}',
                   f'$truth(S,{value}) = {truth}',
                   f'$truth_value(S,{value},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$echo_value(PBOOL ({value_name} =/= PBOOL true)) = $ptascii("{output}")',
                   f'$echo_value(PBOOL {complement}) = $ptascii("{output}")',
                   keyword_not('S.SOURCES', origin, expression) + f' = ($ptascii("{output}"))',
                   keyword_not('eps', origin, expression) + ' = eps',
                   f'$property_magic_cv_raw_positive_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   f'$compiled_read(S_roots,{child_origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        other_kind = 'NName' if kind == 'NNameFullyQualified' else 'NNameFullyQualified'
        other_word = base64.b64encode(('true' if truth == 'true' else 'null' if value != 'PNULL' else 'false').encode()).decode()
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprBooleanNot ({child}) eps'),
            ('parent_kind', parts, f'NExprUnaryPlus ({child}) {metadata}'),
            ('parent_missing', parts, None),
            ('child_metadata', parts + (0,), f'NExprConstFetch ({name}) eps'),
            ('child_kind', parts + (0,), f'NScalarInt (INTEGER 1) {child_metadata}'),
            ('child_missing', parts + (0,), None),
            ('name_metadata', parts + (0, 0), f'{kind} (BYTES {text}) eps'),
            ('name_kind', parts + (0, 0), f'{other_kind} (BYTES {text}) {name_metadata}'),
            ('name_value', parts + (0, 0), f'{kind} (BYTES "{other_word}") {name_metadata}'),
            ('name_missing', parts + (0, 0), None),
        ):
            state = f'S_not_{number}_{label}'
            path = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       keyword_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
        state = 'S_not_wrong_name_' + suffix
        missing = f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {raw.path(parts + (0, 0))})'
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(parts + (0, 1))}) ({name})) :: ({missing})'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   keyword_not(state + '.SOURCES', origin, expression) + ' = eps',
                   '~' + raw.selector(side, state)]
    for field, side in enumerate(('class', 'method')):
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PBOOL true', ()),
            ('case', f'PSTRING $ptlc(ptbytes_{side})', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {raw.path((field, 2))}) (PSTRING ptbytes_{side})',)),
        ):
            state = f'S_not_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + raw.root_pools(side, value, extra) + ']',
                       keyword_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state)]
    for label, child, descendants in (
        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_class', ()),
        ('integer', 'NScalarInt (INTEGER 1) metadata_class', ()),
        ('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_class', ()),
        ('string', 'NScalarString (BYTES "MQ==") metadata_class', ()),
        ('relative', 'NExprConstFetch (NNameRelative (BYTES "dHJ1ZQ==") metadata_class) metadata_class',
         (((0, 0), 'NNameRelative (BYTES "dHJ1ZQ==") metadata_class'),)),
        ('other_word', 'NExprConstFetch (NName (BYTES "b3RoZXI=") metadata_class) metadata_class',
         (((0, 0), 'NName (BYTES "b3RoZXI=") metadata_class'),)),
        ('nested', 'NExprBooleanNot (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_class) metadata_class) metadata_class',
         (((0, 0), 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_class) metadata_class'),
          ((0, 0, 0), 'NName (BYTES "dHJ1ZQ==") metadata_class'))),
    ):
        node = f'NExprBooleanNot ({child}) metadata_class'
        state, expression = 'S_control_not_' + label, 'expression_control_not_' + label
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), child), *descendants):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   keyword_not(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    literal = prior.prior.prior.prior.prior.literal
    parents = (prior, prior.prior, prior.prior.prior, prior.prior.prior.prior,
               prior.prior.prior.prior.prior, raw, literal, literal.own,
               literal.own.prior, literal.own.prior.prior, literal.inherited,
               literal.inherited.prior, literal.inherited.prior.prior, literal.inherited.prior.prior.prior,
               literal.own.prior.prior.owning, literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.prior.prior.prior.render)
