#!/usr/bin/env python3
"""Raw finite FLOAT leaves retain parser-time text and the STRING entry protocol."""
import output_final_selected_parser_integer_concat_cast_chain_return_modulo_error_state as prior
import output_final_selected_parser_float_concat_cast_chain_return_modulo_error_sources as sources

runner, PREFIX, CONJ = prior.runner, prior.PREFIX, prior.CONJ
scaffold, zero, no = prior.scaffold, prior.zero, prior.no
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-parser-float-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-right-empty-fraction', 'warning-left-constant-nested-fraction',
                      'deprecated-both-cv-pair-zero-text']}
TREES = {'right-empty-fraction': (1.5, b''), 'both-floats': (1.5, 0.0), 'left-empty-zero': (b'', 0.0),
         'nested-fraction': (1, (2.5, b'')), 'scientific': (1e20, b''), 'zero-text': (0.0, b'')}
BITS = {0.0: '0000000000000000', 1.5: '3ff8000000000000', 2.5: '4004000000000000',
        1e20: '4415af1d78b58c40'}
TEXT = {0.0: b'0', 1.5: b'1.5', 2.5: b'2.5', 1e20: b'1.0E+20'}
CASTS = {name: prior.CASTS[old] for name, old in [('right-empty-fraction', 'right-empty-one'),
         ('left-empty-zero', 'left-empty-zero'), ('nested-fraction', 'nested-twelve'), ('zero-text', 'zero-text')]}
CASTS['both-floats'] = [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true'),
                       ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4609434218613702656')]
CASTS['scientific'] = [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true'),
                      ('NExprCastInt', 'CASTINT', 1, 'PINT 9223372036854775807')]
integer_raw, integer_expression = prior.raw, prior.expression


def raw(node):
    return TEXT[node] if isinstance(node, float) else integer_raw(node)


def expression(name, key='cast'):
    if key not in ('cast', 'cast_1'):
        node = prior.nodes(name)[key]
        if isinstance(node, float):
            return 'NScalarFloat (FLOAT "' + BITS[node] + '") metadata_' + key
    return integer_expression(name, key)


def modulo_line(name):
    return sources.modulo_line(DETAILS[name][0], sources.CASES['native-selected-parser-float-concat-cast-chain-return-modulo-error-' + name])


shared = prior.prior
shared.DETAILS, shared.TREES, shared.CASTS, shared.sources = DETAILS, TREES, CASTS, sources
shared.raw, shared.expression, shared.modulo_line = raw, expression, modulo_line
nodes, tree, plain, carrier, data = shared.nodes, shared.tree, shared.plain, shared.carrier, shared.data
root_value, default = shared.root_value, shared.default
parser_bindings, return_bindings = shared.parser_bindings, shared.return_bindings
parser_proof, return_proof = shared.parser_proof, shared.return_proof
frontier, lifecycle = shared.frontier, shared.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
