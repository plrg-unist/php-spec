#!/usr/bin/env python3
"""Compiled scalar CONCAT keeps child certificates and actual frame retirement."""
import base64
import output_final_selected_terminal_line_bitwise_cast_chain_return_modulo_error_state as prior
import output_final_selected_compiled_scalar_concat_cast_chain_return_modulo_error_sources as sources

runner, PREFIX, CONJ = prior.runner, prior.PREFIX, prior.CONJ
zero, no, scaffold = prior.zero, prior.no, prior.prior
integer, string, cast, negative, unary = prior.integer, prior.string, prior.cast, prior.negative, prior.unary
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-compiled-scalar-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-negative-fraction', 'warning-left-constant-negative-integer',
                      'warning-deprecated-constant-float-arithmetic', 'deprecated-both-cv-pair-nested-zero']}


def floating(bits):
    return ('floating', bits, None, 'PFLOAT ' + str(int(bits, 16)), True, [])


def constant(name):
    return ('constant', name, None, 'PBOOL true' if name == 'true' else 'PNULL', True, [])


def concat(text, left, right):
    result = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + text + '"))'
    return ('NExprBinaryOpConcat', 'CONCAT', None, result, True, [left, right])


TREES = {
 'negative-fraction': cast('float', 'PFLOAT 13830554455654793216', cast('int', 'PINT $(-1)',
    concat('-1.5', unary('NExprUnaryMinus', 'NEGATIVE', 'PFLOAT 13832806255468478464',
                         floating('3ff8000000000000')), string('')))),
 'positive-both': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4609434218613702656',
    concat('1.50', unary('NExprUnaryPlus', 'POSITIVE', 'PFLOAT 4609434218613702656',
                         floating('3ff8000000000000')), floating('0000000000000000')))),
 'negative-zero-right': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    concat('-0', string(''), unary('NExprUnaryMinus', 'NEGATIVE', 'PFLOAT 9223372036854775808',
                                 floating('0000000000000000'))))),
 'negative-integer': cast('float', 'PFLOAT 13846317054350589952', cast('int', 'PINT $(-12)',
    concat('-12', negative(12), string('')))),
 'arithmetic': cast('bool', 'PBOOL true', cast('int', 'PINT 4',
    concat('4', ('NExprBinaryOpPlus', 'ADD', None, 'PFLOAT 4616189618054758400', True,
                 [floating('3ff8000000000000'), floating('4004000000000000')]), string('')))),
 'nested-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    concat('-00', concat('-0', unary('NExprUnaryMinus', 'NEGATIVE', 'PFLOAT 9223372036854775808',
                                    floating('0000000000000000')), string('')), string('0')))),
 'keyword-suffix': cast('bool', 'PBOOL true', cast('int', 'PINT $(-1)',
    concat('-1.51', concat('-1.51', unary('NExprUnaryMinus', 'NEGATIVE', 'PFLOAT 13832806255468478464',
                                        floating('3ff8000000000000')), constant('true')), constant('null')))),
 'negative-infinity': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    concat('-INF', unary('NExprUnaryMinus', 'NEGATIVE', 'PFLOAT 18442240474082181120',
                         floating('7ff0000000000000')), string(''))))}

children = prior.children


def nodes(name):
    result = {}
    def visit(key, node):
        result[key] = node
        for (child, _), descendant in zip(children(key, node), node[5]):
            visit(child, descendant)
    visit('cast', TREES[DETAILS[name][1]])
    return result


def expression(name, key='cast'):
    kind, spelling, _, _, _, _ = nodes(name)[key]
    metadata = 'metadata_' + key
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
    if kind == 'floating':
        return 'NScalarFloat (FLOAT "' + spelling + '") ' + metadata
    if kind == 'string':
        return 'NScalarString (BYTES text_' + key + ') ' + metadata
    if kind == 'constant':
        payload = base64.b64encode(spelling.encode()).decode()
        return 'NExprConstFetch (NName (BYTES "' + payload + '") ' + metadata + '_name) ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child, _ in children(key, nodes(name)[key])) + ' ' + metadata


def modulo_line(name):
    return sources.modulo_line(DETAILS[name][0], sources.CASES[
        'native-selected-compiled-scalar-concat-cast-chain-return-modulo-error-' + name])


original_converted, original_proof = prior.converted, prior.return_proof


def converted(name, condition):
    return original_converted(name, condition).replace('selected_modulo_terminal_line_bitwise_cast_chain_return',
                                                      sources.function_name(DETAILS[name][1]))


def return_proof(name):
    proof = original_proof(name)
    terminal = 'z_cast =/= $expression_line(' + expression(name) + ')'
    assert proof.count(terminal) == 1
    proof = proof.replace(terminal, '$(z_cast > 0)')
    states = ['S_return', 'S', *(['S_return_right'] if scaffold.two_calls(DETAILS[name][0]) else [])]
    for key, node in nodes(name).items():
        if node[0] != 'NExprBinaryOpConcat':
            continue
        result, left, right = node[3], node[5][0][3], node[5][1][3]
        plain = result.replace('PSTRING_CARRIER INTERNED_STRING', 'PSTRING')
        for state in states:
            old = '$compiled_read(' + state + ', porigin_' + key + ') = (' + result + ')'
            assert proof.count(old) == 1
            proof = proof.replace(old, '$compiled_read(' + state + ', porigin_' + key + ') = (' + plain + ')')
        old = ('$binary_apply(S[.RESULT = KNOWN (' + right + ')], CONCAT, ' + left + ', ' + right + ', z_' + key +
               ') = S[.RESULT = KNOWN (' + result + ')]')
        assert proof.count(old) == 1
        parts = ['$source_precision(S, (porigin_' + key + ')) = (14)',
                 '$parser_literal_at(' + expression(name, key) + ', 14) = eps',
                 '$compiled_special_concat_bytes(S, porigin_' + key + ') = ' + result[len('PSTRING_CARRIER INTERNED_STRING '):],
                 '$compiled_effects(S, porigin_' + key + ') = eps',
                 '$compiled_string_value(S, porigin_' + key + ', ' + plain + ') = ' + result,
                 '$enter_compiled_task(S, porigin_' + key + ', EVAL (' + expression(name, key) + '), S.TODO) = S[.RESULT = KNOWN (' + result + ')]']
        parts += ['$compiled_precision(S, (porigin_' + origin + ')) = (14)' for origin in [key, key + '_left', key + '_right']]
        proof = proof.replace(old, CONJ.join(parts))
    return proof


prior.DETAILS, prior.TREES = DETAILS, TREES
prior.nodes, prior.expression = nodes, expression
prior.modulo_line, prior.converted, prior.return_proof = modulo_line, converted, return_proof
root_value, default = prior.root_value, prior.default
return_bindings, frontier, lifecycle = prior.return_bindings, prior.frontier, prior.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
