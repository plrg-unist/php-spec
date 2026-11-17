#!/usr/bin/env python3
"""Folded STRING NOT certificates retain decoded bytes and actual retirement."""
import output_final_selected_folded_string_bitwise_cast_chain_return_modulo_error_state as prior
import output_final_selected_folded_string_bitnot_cast_chain_return_modulo_error_sources as sources

current = prior.current
runner, PREFIX, CONJ = prior.runner, prior.PREFIX, prior.CONJ
cast, bitwise = prior.cast, prior.bitwise
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-folded-string-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-single-not-one',
                      'warning-left-constant-double-not-zero',
                      'deprecated-both-cv-pair-empty-not-empty']}
BYTE_VALUES = {}


def data(raw):
    return '[' + ', '.join(map(str, raw)) + ']' if raw else 'eps'


def plain(raw):
    return 'PSTRING (' + data(raw) + ')'


def string(raw):
    label = 'bytes_' + raw.hex()
    BYTE_VALUES[label] = '(' + data(raw) + ')'
    return ('string', label, None, 'PSTRING_CARRIER INTERNED_STRING (' + data(raw) + ')', True, [])


def bitnot(result, child):
    return ('NExprBitwiseNot', 'BITNOT', None, plain(result), child[4], [child])


TREES = {
 'single-not-one': cast('float', 'PFLOAT 4607182418800017408', cast('int', 'PINT 1',
    bitnot(b'1', string(b'\xce')))),
 'multi-not-twenty': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4626322717216342016',
    bitnot(b'20', string(b'\xcd\xcf')))),
 'single-not-nul': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    bitnot(b'\0', string(b'\xff')))),
 'double-not-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    bitnot(b'0', bitnot(b'\xcf', string(b'0'))))),
 'bitand-not-two-nul': cast('float', 'PFLOAT 0', cast('int', 'PINT 0',
    bitnot(b'\0\0', bitwise('and', plain(b'\xff\xff'), string(b'\xff\xff'), string(b'\xff\xff'))))),
 'empty-not-empty': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    bitnot(b'', string(b''))))}


def modulo_line(name):
    source = sources.CASES['native-selected-folded-string-bitnot-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


def converted(name, condition):
    return prior.converted(name, condition).replace('selected_modulo_folded_string_bitwise_cast_chain_return',
                                                  'selected_modulo_folded_string_bitnot_cast_chain_return')


def return_proof(name):
    condition = prior.return_proof(name)
    inherited = 'z_cast =/= $expression_line(' + current.expression(name) + ')'
    assert condition.count(inherited) == 1
    condition = condition.replace(inherited, 'z_cast =/= $source_line(metadata_cast)')
    for key, node in current.nodes(name).items():
        if node[0] != 'NExprBitwiseNot' or not node[3].startswith('PSTRING '):
            continue
        result, child = node[3], node[5][0]
        runtime = ('$bitnot_apply(S[.RESULT = KNOWN (' + child[3] + ')], ' + child[3] + ', z_' + key +
                   ') = S[.RESULT = KNOWN (' + result + ')]')
        assert condition.count(runtime) == 1
        origin = 'porigin_' + key
        proof = [
            '$string_not(' + prior.node_bytes(child) + ') = ' + prior.node_bytes(node),
            '$compiled_effects(S, ' + origin + ') = eps',
            '$compiled_string_value(S, ' + origin + ', ' + result + ') = ' + result,
            '$enter_compiled_task(S, ' + origin + ', EVAL (' + current.expression(name, key) +
            '), S.TODO) = S[.RESULT = KNOWN (' + result + ')]']
        condition = condition.replace(runtime, CONJ.join(proof))
    # The inherited ASCII fixture factory supplies markers; authenticate actual bytes.
    for label, raw in BYTE_VALUES.items():
        condition = condition.replace('$ptascii("' + label + '")', raw)
    assert '$ptascii("bytes_' not in condition
    return condition


current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted, current.return_proof = modulo_line, converted, return_proof
nodes, root_value, expression = current.nodes, current.root_value, current.expression
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
