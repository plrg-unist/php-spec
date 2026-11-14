#!/usr/bin/env python3
"""Own unary-minus float returns preserve real FINAL MOD Error retirement."""
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_float_return_modulo_error_state as floats
import output_final_selected_negative_float_return_modulo_error_sources as sources

prior, runner = floats.prior, floats.runner
PREFIX = floats.PREFIX
CASES = {name: sources.CASES['native-selected-negative-float-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
BITS = floats.BITS
RETURN_BITS = {'warning-left-constant': 'bff8000000000000',
               'deprecated-both-cv-pair': '8000000000000001',
               'warning-right-cv-pair': '8000000000000000',
               'warning-deprecated-constant-float': 'fff0000000000000'}


def converted(condition):
    return floats.converted(condition).replace('selected_modulo_float_return',
                                               'selected_modulo_negative_float_return')


def return_bindings(name):
    return [binding.replace('NScalarInt (INTEGER 0) metadata_zero',
        'NExprUnaryMinus (NScalarFloat (FLOAT text_float) metadata_float) metadata_negative').replace(
        '(PINT 0)', '(PFLOAT n_return)').replace('_zero', '_negative')
        for binding in zero.return_bindings(name)] + [
        '$origin_node(S.SOURCES, porigin_negative) = (NExprUnaryMinus (NScalarFloat (FLOAT text_float) metadata_float) metadata_negative)',
        '$origin_child((porigin_negative), [PCFIELD 0]) = (porigin_float)',
        'porigin_float = PORIGIN n_negative_handler pcpath_float',
        '$origin_node(S.SOURCES, porigin_float) = (NScalarFloat (FLOAT text_float) metadata_float)',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_float) = ((z_float, b_float))',
        '|text_float| = 16',
        'n_nibble* = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]',
        '(text_float[n_nibble:1] <- ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"])*',
        '$evaluate(NScalarFloat (FLOAT text_float) metadata_float) = VALUE (PFLOAT n_child)',
        '$float_decode(n_child) =/= NOTNUMBER n_child']


def return_proof(name):
    condition = zero.return_proof(name).replace('(PINT 0)', '(PFLOAT n_return)').replace(
        '_zero', '_negative').replace('z_negative = $source_line(metadata_negative)',
        'z_negative = $expression_line(NScalarFloat (FLOAT text_float) metadata_float)')
    condition += (r' /\ pcpath_float = pcpath_negative ++ [PCFIELD 0] /\ '
        r'z_float = $source_line(metadata_float) /\ b_float /\ z_negative = z_float /\ '
        r'text_float = "' + BITS[name] + r'" /\ n_child = $hex_bits(text_float, 0) /\ '
        r'n_return = $hex_bits("' + RETURN_BITS[name] + r'", 0) /\ '
        r'$unary_apply(S, NEGATIVE, PFLOAT n_child, z_negative) = S[.RESULT = KNOWN (PFLOAT n_return)] /\ '
        r'$compiled_read(S_return, porigin_float) = (PFLOAT n_child) /\ '
        r'$compiled_read(S, porigin_float) = (PFLOAT n_child)')
    if prior.two_calls(name):
        condition += r' /\ $compiled_read(S_return_right, porigin_float) = (PFLOAT n_child)'
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'negative float'), converted(condition)) for label, condition in checks]
    checks += [('the exact unary root and raw child retain their folded bits and NULL scratch',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full unary result survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
