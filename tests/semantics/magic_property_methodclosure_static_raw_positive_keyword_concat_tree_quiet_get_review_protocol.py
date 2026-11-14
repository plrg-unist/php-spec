#!/usr/bin/env python3
"""Check original keyword UnaryPlus inputs and complete source authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_positive_integer_concat_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_positive_keyword_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def positive(sources, origin, expression):
    return f'$property_magic_cv_raw_positive_keyword_string_tree({sources},{origin},{expression})'


def checks(index):
    inherited = prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    result = [line.replace('$property_magic_cv_raw_positive_integer_string_tree(',
                           '$property_magic_cv_raw_positive_keyword_string_tree(')
              for line in inherited]
    for side in ('class', 'method'):
        result.append(f'$property_magic_cv_raw_positive_integer_string_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps')
    leaves = ((('class', (0, 1, 1, 1, 0, 0), 'false', 'NNameFullyQualified'),
               ('class', (0, 1, 1, 1, 0, 1), 'null', 'NName'),
               ('method', (1, 1, 1, 1, 1), 'true', 'NName')) if index == 0 else
              (('class', (0, 0, 1, 1), 'true', 'NNameFullyQualified'),
               ('method', (1, 1, 1, 1, 1, 1, 1, 0), 'false', 'NName'),
               ('method', (1, 1, 1, 1, 1, 1, 1, 1), 'null', 'NNameFullyQualified')))
    for number, (side, parts, word, kind) in enumerate(leaves):
        suffix = str(number)
        origin, fetch_origin, name_origin = ('porigin_positive_' + suffix,
                                             'porigin_keyword_' + suffix, 'porigin_keyword_name_' + suffix)
        metadata, fetch_metadata, name_metadata = ('metadata_positive_' + suffix,
                                                   'metadata_keyword_' + suffix, 'metadata_keyword_name_' + suffix)
        text, expression = 'text_keyword_' + suffix, 'expression_positive_' + suffix
        name = f'{kind} (BYTES {text}) {name_metadata}'
        fetch = f'NExprConstFetch ({name}) {fetch_metadata}'
        node = f'NExprUnaryPlus ({fetch}) {metadata}'
        value = {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}[word]
        integer = 1 if word == 'true' else 0
        original_bytes = '($ptascii("1"))' if word == 'true' else '(eps)'
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'{fetch_metadata} =/= eps', f'{name_metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({fetch_origin})',
                   f'$origin_node(S.SOURCES,{fetch_origin}) = ({fetch})',
                   f'$origin_child(({fetch_origin}),[PCFIELD 0]) = ({name_origin})',
                   f'$origin_node(S.SOURCES,{name_origin}) = ({name})',
                   f'$special_constant($base64({text})) = ({value})',
                   f'$coerce_number({value}) = COERCED (NINT {integer}) false',
                   f'$unary_apply(S,POSITIVE,{value},0) = S[.RESULT = KNOWN (PINT {integer})]',
                   positive('S.SOURCES', origin, expression) + f' = ($ntsigned({integer}))',
                   f'$property_magic_cv_raw_positive_integer_string_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$property_magic_cv_raw_positive_integer_string_tree(S.SOURCES,{fetch_origin},{fetch}) = {original_bytes}',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   f'$compiled_read(S_roots,{fetch_origin}) = eps',
                   f'$compiled_read(S_roots,{name_origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        other = base64.b64encode(('null' if word == 'false' else 'false').encode()).decode()
        other_kind = 'NName' if kind == 'NNameFullyQualified' else 'NNameFullyQualified'
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprUnaryPlus ({fetch}) eps'),
            ('parent_kind', parts, f'NExprUnaryMinus ({fetch}) {metadata}'),
            ('parent_missing', parts, None),
            ('fetch_metadata', parts + (0,), f'NExprConstFetch ({name}) eps'),
            ('fetch_kind', parts + (0,), f'NScalarInt (INTEGER {integer}) {fetch_metadata}'),
            ('fetch_value', parts + (0,), f'NExprConstFetch ({kind} (BYTES "{other}") {name_metadata}) {fetch_metadata}'),
            ('fetch_missing', parts + (0,), None),
            ('name_metadata', parts + (0, 0), f'{kind} (BYTES {text}) eps'),
            ('name_kind', parts + (0, 0), f'{other_kind} (BYTES {text}) {name_metadata}'),
            ('name_value', parts + (0, 0), f'{kind} (BYTES "{other}") {name_metadata}'),
            ('name_missing', parts + (0, 0), None),
        ):
            state = f'S_positive_{number}_{label}'
            path = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       positive(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state)]
            if label == 'name_missing':
                result.append(f'~$property_magic_cv_static_methodclosure({state},n_closure)')
        state = 'S_positive_wrong_child_' + suffix
        missing = f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {raw.path(parts + (0,))})'
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(parts + (1,))}) ({fetch})) :: ({missing})'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   positive(state + '.SOURCES', origin, expression) + ' = eps',
                   '~' + raw.selector(side, state)]
    for field, side in enumerate(('class', 'method')):
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PBOOL true', ()),
            ('case', f'PSTRING $ptlc(ptbytes_{side})', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {raw.path((field, 2))}) (PSTRING ptbytes_{side})',)),
        ):
            state = f'S_positive_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + raw.root_pools(side, value, extra) + ']',
                       positive(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state)]
    for label, child, descendants in (
        ('user', 'NExprConstFetch (NName (BYTES "UEhQX0lOVF9NQVg=") metadata_class) metadata_class',
         (((0, 0), 'NName (BYTES "UEhQX0lOVF9NQVg=") metadata_class'),)),
        ('relative', 'NExprConstFetch (NNameRelative (BYTES "dHJ1ZQ==") metadata_class) metadata_class',
         (((0, 0), 'NNameRelative (BYTES "dHJ1ZQ==") metadata_class'),)),
        ('nested', 'NExprUnaryPlus (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_class) metadata_class) metadata_class',
         (((0, 0), 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_class) metadata_class'),
          ((0, 0, 0), 'NName (BYTES "dHJ1ZQ==") metadata_class'))),
    ):
        node = f'NExprUnaryPlus ({child}) metadata_class'
        state, expression = 'S_control_positive_' + label, 'expression_control_positive_' + label
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), child), *descendants):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   positive(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    literal = prior.prior.prior.literal
    parents = (prior, prior.prior, prior.prior.prior, raw, literal, literal.own, literal.own.prior,
               literal.own.prior.prior, literal.inherited, literal.inherited.prior,
               literal.inherited.prior.prior, literal.inherited.prior.prior.prior,
               literal.own.prior.prior.owning, literal.own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.prior.render)
