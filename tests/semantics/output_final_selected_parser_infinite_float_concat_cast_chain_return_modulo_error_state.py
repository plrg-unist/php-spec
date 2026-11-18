#!/usr/bin/env python3
"""Raw positive infinity retains parser bytes and real selected-call retirement."""
import output_final_selected_parser_float_concat_cast_chain_return_modulo_error_state as prior
import output_final_selected_parser_infinite_float_concat_cast_chain_return_modulo_error_sources as sources

runner, PREFIX, CONJ = prior.runner, prior.PREFIX, prior.CONJ
scaffold, zero, no, shared = prior.scaffold, prior.zero, prior.no, prior.shared
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-parser-infinite-float-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-right-empty-infinity', 'deprecated-both-cv-pair-infinity-false']}
INFINITY = float('inf')
TREES = {'right-empty-infinity': (INFINITY, b''), 'left-empty-infinity': (b'', INFINITY),
         'infinity-false': (INFINITY, b''), 'infinity-finite': (INFINITY, 1.5)}
CASTS = {
 'right-empty-infinity': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 0'), ('NExprCastInt', 'CASTINT', 1, 'PINT 0')],
 'left-empty-infinity': [('NExprCastInt', 'CASTINT', 1, 'PINT 1'), ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true')],
 'infinity-false': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false'), ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 0')],
 'infinity-finite': [('NExprCastInt', 'CASTINT', 1, 'PINT 1'), ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true')]}
prior.BITS[INFINITY], prior.TEXT[INFINITY] = '7ff0000000000000', b'INF'


def modulo_line(name):
    return sources.modulo_line(DETAILS[name][0], sources.CASES[
        'native-selected-parser-infinite-float-concat-cast-chain-return-modulo-error-' + name])


shared.DETAILS, shared.TREES, shared.CASTS, shared.sources = DETAILS, TREES, CASTS, sources
shared.raw, shared.expression, shared.modulo_line = prior.raw, prior.expression, modulo_line
nodes, tree, plain, carrier, data = shared.nodes, shared.tree, shared.plain, shared.carrier, shared.data
root_value, default, expression = shared.root_value, shared.default, shared.expression
parser_bindings, return_bindings = shared.parser_bindings, shared.return_bindings
parser_proof, return_proof = shared.parser_proof, shared.return_proof
frontier, lifecycle = shared.frontier, shared.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
