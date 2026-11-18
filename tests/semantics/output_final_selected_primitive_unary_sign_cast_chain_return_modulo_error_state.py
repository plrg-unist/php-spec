#!/usr/bin/env python3
"""Quiet type-changing signs retain exact source, results and real retirement."""
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_state as prior
import output_final_selected_primitive_unary_sign_cast_chain_return_modulo_error_sources as sources

runner, PREFIX, CONJ = prior.runner, prior.PREFIX, prior.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-primitive-unary-sign-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-numeric-string', 'warning-right-cv-pair-emitted-not-float']}
NODES = {
 'numeric-string': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4622945017495814144', False),
                    ('NExprCastInt', 'CASTINT', 1, 'PINT 12', False),
                    ('NExprUnaryPlus', 'POSITIVE', None, 'PINT 12', True),
                    ('string', '12', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("12"))', True)],
 'minus-true': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true', False),
                ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 13830554455654793216', False),
                ('NExprUnaryMinus', 'NEGATIVE', None, 'PINT $(-1)', True),
                ('keyword', 'true', None, 'PBOOL true', True)],
 'plus-false': [('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False),
                ('NExprUnaryPlus', 'POSITIVE', None, 'PINT 0', True),
                ('keyword', 'false', None, 'PBOOL false', True)],
 'minus-null': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 0', False),
                ('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                ('NExprUnaryMinus', 'NEGATIVE', None, 'PINT 0', True),
                ('keyword', 'null', None, 'PNULL', True)],
 'fraction-string': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 13830554455654793216', False),
                     ('NExprCastInt', 'CASTINT', 1, 'PINT $(-1)', False),
                     ('NExprUnaryMinus', 'NEGATIVE', None, 'PFLOAT 13832806255468478464', True),
                     ('string', '1.5', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5"))', True)],
 'exponent-zero': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False),
                   ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 0', False),
                   ('NExprUnaryPlus', 'POSITIVE', None, 'PFLOAT 0', True),
                   ('string', '0e0', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0e0"))', True)],
 'emitted-not-float': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4607182418800017408', False),
                       ('NExprCastInt', 'CASTINT', 1, 'PINT 1', False),
                       ('NExprUnaryPlus', 'POSITIVE', None, 'PINT 1', False),
                       ('NExprBooleanNot', None, None, 'PBOOL true', False),
                       ('float', '0000000000000000', None, 'PFLOAT 0', True)]}
COERCED = {'numeric-string': 'NINT 12', 'minus-true': 'NINT 1', 'plus-false': 'NINT 0',
           'minus-null': 'NINT 0', 'fraction-string': 'NFLOAT 4609434218613702656',
           'exponent-zero': 'NFLOAT 0', 'emitted-not-float': 'NINT 1'}

original_converted, original_proof = prior.converted, prior.return_proof


def converted(name, condition):
    return original_converted(name, condition).replace('selected_modulo_recursive_numeric_sign_cast_chain_return',
                                                      sources.function_name(DETAILS[name][1]))


def return_proof(name):
    proof = original_proof(name)
    child, result = NODES[DETAILS[name][1]][3][3], NODES[DETAILS[name][1]][2][3]
    old = '$ob_object_cast_chain_sign_number(' + child + ')'
    assert proof.count(old) == 1
    proof = proof.replace(old, '$coerce_number(' + child + ') = COERCED (' + COERCED[DETAILS[name][1]] + ') false' +
                          CONJ + '$value_nodes(' + child + ') = eps')
    old = '$type_bytes(' + result + ') = $type_bytes(' + child + ')' + CONJ
    assert proof.count(old) == 1
    return proof.replace(old, '')


prior.DETAILS, prior.NODES, prior.sources = DETAILS, NODES, sources
prior.converted, prior.return_proof = converted, return_proof
nodes, expression, slot = prior.nodes, prior.expression, prior.slot
root_value, default = prior.root_value, prior.default
return_bindings, frontier, lifecycle = prior.return_bindings, prior.frontier, prior.lifecycle

import output_final_selected_signed_numeric_cast_chain_return_modulo_error_review_state as legacy_signed
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as legacy_recursive
PREFIX = legacy_recursive.PREFIX
prior.DETAILS, prior.NODES, prior.sources = DETAILS, NODES, sources
prior.converted, prior.return_proof = converted, return_proof
base_frontier = frontier


def legacy_promotions():
    bindings = ['pcpath_raw = pcpath_child_3', 'porigin_raw = porigin_child_3',
                'metadata_raw = metadata_child_3', 'z_raw = z_child_3',
                'pcpath_name = pcpath_raw ++ [PCFIELD 0]',
                'pcpath_child_4 = pcpath_child_3 ++ [PCFIELD 0]', 'metadata_child_4 = metadata_child_3',
                '$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    checks = []
    for context in legacy_signed.CASES:
        for raw, typed, result, extra in [
                ('NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_raw) metadata_raw', 'PBOOL true', 'PINT 1',
                 [('pcpath_name', 'NName (BYTES "dHJ1ZQ==") metadata_raw')]),
                ('NScalarString (BYTES "Nw==") metadata_raw', 'PSTRING ($ptascii("7"))', 'PINT 7', [])]:
            state, _, expr = legacy_signed.variant(context, raw, typed, 'NExprUnaryPlus', result, extra)
            actual = 'PBOOL true' if typed == 'PBOOL true' else 'PSTRING_CARRIER INTERNED_STRING ($ptascii("7"))'
            condition = ('~$ob_object_cast_chain_sign_literal(' + raw + ')' + CONJ +
                         '$unary_apply(' + state + '[.RESULT = KNOWN (' + actual + ')], POSITIVE, ' + actual + ', z_sign) = ' +
                         state + '[.RESULT = KNOWN (' + result + ')]' + CONJ +
                         legacy_signed.value(state, expr) + ' = (' + result + ')')
            checks += [('exact old signed query promotes through its original builder: ' + context + '/' + typed, condition)]
    for keyword, raw, payload in [('false', 'PBOOL false', 'ZmFsc2U='), ('null', 'PNULL', 'bnVsbA==')]:
        node = 'NName (BYTES "' + payload + '") metadata_child_4'
        leaf = 'NExprConstFetch (' + node + ') metadata_child_3'
        state, expr, function = legacy_recursive.raw_sign('NExprUnaryPlus', leaf, raw, 'PINT 0', name=node)
        checks += [('exact old recursive ' + keyword + ' query promotes through its original builder',
                    legacy_recursive.value(state, leaf, 'porigin_child_3', function) + ' = (' + raw + ')' + CONJ +
                    legacy_recursive.value(state, expr, function=function) + ' = (PINT 0)')]
    leaf = 'NScalarString (BYTES "Nw==") metadata_child_3'
    state, expr, function = legacy_recursive.raw_sign('NExprUnaryPlus', leaf, 'PSTRING ($ptascii("7"))', 'PINT 7')
    checks += [('exact old recursive STRING query promotes through its original builder',
                legacy_recursive.value(state, leaf, 'porigin_child_3', function) +
                ' = (PSTRING_CARRIER INTERNED_STRING ($ptascii("7")))' + CONJ +
                legacy_recursive.value(state, expr, function=function) + ' = (PINT 7)')]
    raw = 'NScalarInt (INTEGER 1) metadata_child_4'
    child = 'NExprBooleanNot (' + raw + ') metadata_child_3'
    expr = 'NExprUnaryPlus (' + child + ') metadata_sign'
    state, function = legacy_recursive.changed([('pcpath_sign', expr), ('pcpath_child_3', child), ('pcpath_child_4', raw)],
        [('pcpath_sign', '$expression_line(' + child + ')', 'true'),
         ('pcpath_child_3', '$expression_line(' + raw + ')', 'true'),
         ('pcpath_child_4', '$source_line(metadata_child_4)', 'true')],
        [('pcpath_sign', 'PINT 0'), ('pcpath_child_3', 'PBOOL false'), ('pcpath_child_4', 'PINT 1')])
    checks += [('exact old recursive NOT query promotes through its original builder',
                legacy_recursive.value(state, child, 'porigin_child_3', function) + ' = (PBOOL false)' + CONJ +
                legacy_recursive.value(state, expr, function=function) + ' = (PINT 0)')]
    return bindings, checks


def frontier(name, fixture, path):
    bindings, checks = base_frontier(name, fixture, path)
    if DETAILS[name][1] == 'numeric-string':
        extra_bindings, extra_checks = legacy_promotions()
        bindings += extra_bindings
        checks += extra_checks
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
