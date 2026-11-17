#!/usr/bin/env python3
"""Folded STRING bitwise certificates retain plain bytes and actual retirement."""
import output_final_selected_terminal_line_bitwise_cast_chain_return_modulo_error_state as current
import output_final_selected_folded_string_bitwise_cast_chain_return_modulo_error_sources as sources

runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
string, cast, bitwise = current.string, current.cast, current.bitwise
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-folded-string-bitwise-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-single-and-one',
                      'warning-left-constant-unequal-and-zero',
                      'deprecated-both-cv-pair-empty-xor-empty']}


def plain(text):
    return 'PSTRING ($ptascii("' + text + '"))'


TREES = {
 'single-and-one': cast('float', 'PFLOAT 4607182418800017408', cast('int', 'PINT 1',
    bitwise('and', plain('1'), string('3'), string('1')))),
 'single-or-three': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4613937818241073152',
    bitwise('or', plain('3'), string('2'), string('1')))),
 'single-xor-nul': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    bitwise('xor', 'PSTRING ([0])', string('1'), string('1')))),
 'unequal-and-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    bitwise('and', plain('0'), string('20'), string('1')))),
 'nested-or-thirty': cast('float', 'PFLOAT 4629137466983448576', cast('int', 'PINT 30',
    bitwise('or', plain('30'), string('20'), bitwise('and', plain('1'), string('1'), string('3'))))),
 'empty-xor-empty': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    bitwise('xor', plain(''), string(''), string('11'))))}


def modulo_line(name):
    source = sources.CASES['native-selected-folded-string-bitwise-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


terminal_converted, terminal_return_proof = current.converted, current.return_proof


def converted(name, condition):
    return terminal_converted(name, condition).replace('selected_modulo_terminal_line_bitwise_cast_chain_return',
                                                      'selected_modulo_folded_string_bitwise_cast_chain_return')


def node_bytes(node):
    return '($ptascii("' + node[1] + '"))' if node[0] == 'string' else node[3].removeprefix('PSTRING ')


def return_proof(name):
    condition = terminal_return_proof(name)
    for key, node in current.nodes(name).items():
        if len(node[5]) != 2 or not node[3].startswith('PSTRING '):
            continue
        result, operator = node[3], node[1]
        left, right = node[5][0][3], node[5][1][3]
        runtime = ('$binary_apply(S[.RESULT = KNOWN (' + right + ')], ' + operator + ', ' + left + ', ' + right +
                   ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]')
        assert condition.count(runtime) == 1
        origin = 'porigin_' + key
        proof = [
            '$byte_binary(' + operator + ', ' + node_bytes(node[5][0]) + ', ' + node_bytes(node[5][1]) + ') = ' + node_bytes(node),
            '$compiled_effects(S, ' + origin + ') = eps',
            '$compiled_string_value(S, ' + origin + ', ' + result + ') = ' + result,
            '$enter_compiled_task(S, ' + origin + ', EVAL (' + current.expression(name, key) +
            '), S.TODO) = S[.RESULT = KNOWN (' + result + ')]']
        condition = condition.replace(runtime, CONJ.join(proof))
    return condition


current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted, current.return_proof = modulo_line, converted, return_proof
nodes, root_value, expression = current.nodes, current.root_value, current.expression
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
