#!/usr/bin/env python3
"""Check raw Integer/STRING CONCAT truth, every source node and selector authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_concat_not_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_integer_concat_not_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def integer_concat_not(sources, origin, expression):
    return f'$property_magic_cv_raw_integer_concat_not_tree({sources},{origin},{expression})'


def tree(shape, suffix, parts=()):
    key = suffix + '_' + ''.join(map(str, parts))
    metadata = 'metadata_cn_' + key
    if isinstance(shape, bytes):
        text = 'text_cn_' + key
        expression = f'NScalarString (BYTES {text}) {metadata}'
        return expression, [(parts, expression, metadata, text, shape)]
    if isinstance(shape, int):
        integer = 'i_cn_' + key
        expression = f'NScalarInt (INTEGER {integer}) {metadata}'
        return expression, [(parts, expression, metadata, integer, shape)]
    left, nodes_left = tree(shape[0], suffix, parts + (0,))
    right, nodes_right = tree(shape[1], suffix, parts + (1,))
    expression = f'NExprBinaryOpConcat ({left}) ({right}) {metadata}'
    return expression, [(parts, expression, metadata, None, None), *nodes_left, *nodes_right]


def checks(index, section='all'):
    inherited = prior.prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    result = [line.replace('$property_magic_cv_raw_double_not_tree(',
                           '$property_magic_cv_raw_integer_concat_not_tree(') for line in inherited]
    for side in ('class', 'method'):
        result.append(f'$property_magic_cv_raw_concat_not_tree(S.SOURCES,porigin_tree_root_{side},expression_{side}) = eps')
    shared = list(result)
    origin_groups = {}
    samples = ((('class', (0, 1, 1, 1, 0, 0), (b'', 0), b'0'),
                ('class', (0, 1, 1, 1, 0, 1), ((0, b''), b''), b'0'),
                ('method', (1, 1, 1, 1, 1), ((0, 0), b''), b'00')) if index == 0 else
               (('class', (0, 0, 1, 1), (0, 0), b'00'),
                ('method', (1, 1, 1, 1, 1, 1, 1, 0), (b'', 0), b'0'),
                ('method', (1, 1, 1, 1, 1, 1, 1, 1), ((b'', 0), b''), b'0')))
    for number, (side, parts, shape, expected) in enumerate(samples):
        start = len(result)
        suffix = str(number)
        child, descendants = tree(shape, suffix)
        metadata = 'metadata_cn_outer_' + suffix
        node = f'NExprBooleanNot ({child}) {metadata}'
        origin, child_origin = 'porigin_cn_' + suffix, 'porigin_cn_child_' + suffix
        expression, data = 'expression_cn_' + suffix, 'ptbytes_cn_' + suffix
        truth = 'false' if expected in (b'', b'0') else 'true'
        output = '1' if truth == 'false' else ''
        encoded = base64.b64encode(expected).decode()
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({node})', f'{expression} = {node}',
                   f'{metadata} =/= eps', f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{child_origin},{child}) = ({data})',
                   f'{data} = $base64("{encoded}")', f'~(0 <- {data})',
                   f'$truth_value(S,PSTRING {data},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   integer_concat_not('S.SOURCES', origin, expression) + f' = ($ptascii("{output}"))',
                   integer_concat_not('eps', origin, expression) + ' = eps',
                   f'$property_magic_cv_raw_concat_not_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        bindings_end = len(result)
        for count, (subparts, selected, submetadata, text, payload) in enumerate(descendants):
            suborigin = f'porigin_cn_{number}_desc_{count}'
            location = parts + (0,) + subparts
            result += [f'$origin_child((porigin_site),{raw.path(location)}) = ({suborigin})',
                       f'$origin_node(S.SOURCES,{suborigin}) = ({selected})',
                       f'{submetadata} =/= eps', f'$compiled_read(S_roots,{suborigin}) = eps']
            if isinstance(payload, int):
                result += [f'{text} = {payload}', f'$long_range({text})',
                           f'$ntsigned({text}) = $ptascii("{payload}")']
            elif text is not None:
                result.append(f'$base64({text}) = $base64("{base64.b64encode(payload).decode()}")')
            forged = selected[:-len(submetadata)] + 'eps'
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(location)}) ({forged})) :: pcunit.OCCURRENCES'
            state = f'S_cn_desc_{number}_{count}'
            result += [f'{state} = ' + raw.source_state(occurrences),
                       integer_concat_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state)]
        boundary_start = len(result)
        for label, changed_parts, forged in (
            ('outer_metadata', parts, f'NExprBooleanNot ({child}) eps'),
            ('outer_kind', parts, f'NExprUnaryPlus ({child}) {metadata}'),
            ('outer_missing', parts, None),
            ('concat_kind', parts + (0,), f'NExprBinaryOpPlus ({descendants[1][1]}) ({descendants[-1][1]}) {descendants[0][2]}'),
            ('concat_missing', parts + (0,), None),
            ('leaf_missing', parts + (0,) + descendants[-1][0], None),
        ):
            state = f'S_cn_{number}_{label}'
            path = 'pcpath_site ++ ' + raw.path(changed_parts)
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if forged is None else
                           f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       integer_concat_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                       '~' + raw.selector(side, state), raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
        selected_leaf = next(item for item in descendants if item[4] == 0) if expected == b'0' else descendants[-1]
        leafparts, leaf, leafmetadata, leaftext, payload = selected_leaf
        replacement = b'' if expected == b'0' else b'0' if expected == b'' else b'x'
        encoded_replacement = base64.b64encode(replacement).decode()
        forged = f'NScalarString (BYTES "{encoded_replacement}") {leafmetadata}'
        state = 'S_cn_same_truth_' + suffix
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(parts + (0,) + leafparts)}) ({forged})) :: pcunit.OCCURRENCES'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   integer_concat_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + ' = eps',
                   '~' + raw.selector(side, state), f'~$property_magic_cv_static_methodclosure({state},n_closure)']
        state = 'S_cn_wrong_child_' + suffix
        missing = f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {raw.path(parts + (0,))})'
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path(parts + (1,))}) ({child})) :: ({missing})'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   integer_concat_not(state + '.SOURCES', origin, expression) + ' = eps', '~' + raw.selector(side, state)]
        origin_groups.setdefault(side, []).extend(result[start:])
        origin_groups[str(number)] = result[start:]
        origin_groups[str(number) + '-descendants'] = result[start:boundary_start]
        origin_groups[str(number) + '-mutations'] = result[start:bindings_end] + result[boundary_start:]
    origins_end = len(result)
    for field, side in enumerate(('class', 'method')):
        for label, value, extra in (
            ('missing', None, ()), ('type', 'PBOOL true', ()),
            ('case', f'PSTRING $ptlc(ptbytes_{side})', ()),
            ('wrong_slot', None, (f'PCONSTANT (pcpath_site ++ {raw.path((field, 2))}) (PSTRING ptbytes_{side})',)),
        ):
            state = f'S_cn_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = ' + raw.root_pools(side, value, extra) + ']',
                       integer_concat_not(state + '.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})',
                       '~' + raw.selector(side, state), raw.selector('method' if side == 'class' else 'class', state),
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)']
    for number, (left, right) in enumerate(((b'', b''), (b'', 0), (0, b''), (0, 0),
                                          (b'-', 0), (b' ', 0), (b'0.', 0),
                                          (b'fal', b'se'), (0, b'\xff'), (b'\0', 0), (0, b'\0b'),
                                          (-1, b''), (b'', -9223372036854775808),
                                          (9223372036854775807, b''), (9223372036854775808, b''),
                                          (b'', -9223372036854775809))):
        leaves = [f'NScalarInt (INTEGER $({value})) metadata_class' if isinstance(value, int) else
                  f'NScalarString (BYTES "{base64.b64encode(value).decode()}") metadata_class'
                  for value in (left, right)]
        child = f'NExprBinaryOpConcat ({leaves[0]}) ({leaves[1]}) metadata_class'
        node = f'NExprBooleanNot ({child}) metadata_class'
        state, expression = 'S_cn_truth_' + str(number), 'expression_cn_truth_' + str(number)
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), child), ((0, 0), leaves[0]), ((0, 1), leaves[1])):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        data = b''.join(str(value).encode() if isinstance(value, int) else value for value in (left, right))
        refused = b'\0' in data or any(isinstance(value, int) and not -2**63 <= value < 2**63 for value in (left, right))
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   integer_concat_not(state + '.SOURCES', 'porigin_tree_root_class', expression) +
                   (' = eps' if refused else f' = ($ptascii("{"1" if data in (b"", b"0") else ""}"))')]
    for label, leaf in (('float', 'NScalarFloat (FLOAT "0000000000000000") metadata_class'),
                        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_class'),
                        ('positive', 'NExprUnaryPlus (NScalarString (BYTES "MA==") metadata_class) metadata_class'),
                        ('negative', 'NExprUnaryMinus (NScalarInt (INTEGER 0) metadata_class) metadata_class'),
                        ('not', 'NExprBooleanNot (NScalarString (BYTES "MA==") metadata_class) metadata_class'),
                        ('keyword', 'NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_class) metadata_class')):
        right = 'NScalarString (BYTES "") metadata_class'
        child = f'NExprBinaryOpConcat ({leaf}) ({right}) metadata_class'
        node = f'NExprBooleanNot ({child}) metadata_class'
        state, expression = 'S_cn_control_' + label, 'expression_cn_control_' + label
        occurrences = 'pcunit.OCCURRENCES'
        children = [((), node), ((0,), child), ((0, 0), leaf), ((0, 1), right)]
        if label == 'keyword':
            children.append(((0, 0, 0), 'NName (BYTES "ZmFsc2U=") metadata_class'))
        elif label in ('positive', 'not'):
            children.append(((0, 0, 0), 'NScalarString (BYTES "MA==") metadata_class'))
        elif label == 'negative':
            children.append(((0, 0, 0), 'NScalarInt (INTEGER 0) metadata_class'))
        for parts, selected in children:
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'{expression} = {node}', f'{state} = ' + raw.source_state(occurrences),
                   integer_concat_not(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    leaf = 'NScalarString (BYTES "MA==") metadata_class'
    inner = f'NExprBooleanNot ({leaf}) metadata_class'
    middle = f'NExprBooleanNot ({inner}) metadata_class'
    outer = f'NExprBooleanNot ({middle}) metadata_class'
    occurrences = 'pcunit.OCCURRENCES'
    for parts, selected in (((), outer), ((0,), middle), ((0, 0), inner), ((0, 0, 0), leaf)):
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({selected})) :: ({occurrences})'
    result += [f'expression_cn_triple = {outer}', 'S_cn_triple = ' + raw.source_state(occurrences),
               integer_concat_not('S_cn_triple.SOURCES', 'porigin_tree_root_class', 'expression_cn_triple') + ' = eps']
    if section in ('method-2-descendants', 'method-2-mutations'):
        return shared + origin_groups['2-' + section.rsplit('-', 1)[1]]
    if section in ('method-1-origins', 'method-2-origins'):
        return shared + origin_groups[section.split('-')[1]]
    if section in ('class-origins', 'method-origins'):
        return shared + origin_groups[section.split('-')[0]]
    if section == 'origins':
        return result[:origins_end]
    if section == 'controls':
        return shared + result[origins_end:]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    original = row['derived_from']['id']
    old = prior.CASES[original if original in prior.CASES else original + '-origins']
    for section, suffix in ((('all', ''),) if index == 0 else
                            (('class-origins', '-class-origins'), ('method-1-origins', '-method-1-origins'),
                             ('method-2-descendants', '-method-2-descendants'),
                             ('method-2-mutations', '-method-2-mutations'),
                             ('controls', '-controls'))):
        CASES[row['id'] + suffix] = dict(old, source=row['source'], checks=checks(index, section))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = []
    parent = prior
    while hasattr(parent, 'prior'):
        parents.append(parent)
        parent = parent.prior
    parents.append(parent)
    literal = raw.literal
    parents += [raw, literal, literal.own, literal.own.prior, literal.own.prior.prior,
                literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
                literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
                literal.own.prior.prior.literal]
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.prior.prior.prior.prior.prior.prior.prior.prior.render)
