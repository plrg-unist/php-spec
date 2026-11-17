#!/usr/bin/env python3
"""Raw fitting INT leaves retain the existing parser STRING entry protocol."""
import output_final_selected_parser_string_concat_cast_chain_return_modulo_error_state as prior
import output_final_selected_parser_integer_concat_cast_chain_return_modulo_error_sources as sources

runner, PREFIX, CONJ = prior.runner, prior.PREFIX, prior.CONJ
scaffold, zero, no = prior.scaffold, prior.zero, prior.no
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-parser-integer-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-right-empty-one', 'warning-left-constant-nested-twelve',
                      'deprecated-both-cv-pair-zero-text']}
TREES = {'right-empty-one': (1, b''), 'both-integers': (2, 0), 'left-empty-zero': (b'', 0),
         'nested-twelve': (1, (2, b'')), 'maximum': (9223372036854775807, b''), 'zero-text': (0, b'')}
CASTS = {name: prior.CASTS[old] for name, old in [('right-empty-one', 'right-empty-one'),
         ('both-integers', 'multiline-twenty'), ('left-empty-zero', 'left-empty-zero'),
         ('nested-twelve', 'nested-twelve'), ('zero-text', 'empty')]}
CASTS['maximum'] = [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true'),
                    ('NExprCastInt', 'CASTINT', 1, 'PINT 9223372036854775807')]
string_raw, string_expression = prior.raw, prior.expression


def raw(node):
    return str(node).encode() if isinstance(node, int) else string_raw(node)


def expression(name, key='cast'):
    if key not in ('cast', 'cast_1'):
        node = prior.nodes(name)[key]
        if isinstance(node, int):
            return 'NScalarInt (INTEGER ' + str(node) + ') metadata_' + key
    return string_expression(name, key)


def modulo_line(name):
    return sources.modulo_line(DETAILS[name][0], sources.CASES['native-selected-parser-integer-concat-cast-chain-return-modulo-error-' + name])


prior.DETAILS, prior.TREES, prior.CASTS, prior.sources = DETAILS, TREES, CASTS, sources
prior.raw, prior.expression, prior.modulo_line = raw, expression, modulo_line
nodes, tree, plain, carrier, data = prior.nodes, prior.tree, prior.plain, prior.carrier, prior.data
root_value, default = prior.root_value, prior.default
parser_bindings, return_bindings = prior.parser_bindings, prior.return_bindings
parser_proof, return_proof = prior.parser_proof, prior.return_proof
frontier, lifecycle = prior.frontier, prior.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
