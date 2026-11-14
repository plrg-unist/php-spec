#!/usr/bin/env python3
"""Actual integer-zero returns precede selected FINAL MOD Error capture."""
import output_final_selected_explicit_null_modulo_error_state as prior
import output_final_selected_zero_return_modulo_error_sources as sources

runner = prior.runner
PREFIX = prior.PREFIX.replace('RETURN_UNWIND (KNOWN PNULL) porigin?',
                             'RETURN_UNWIND (KNOWN (PINT 0)) porigin?')
CASES = {name: sources.CASES['native-selected-zero-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}


def converted(condition):
    condition = prior.converted(condition).replace('selected_modulo_explicit_null',
                                                  'selected_modulo_zero_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN PNULL',
                                      state + '.RESULT = KNOWN (PINT 0)')
    return condition


def return_bindings(name):
    bindings = [
        'S_return.TODO = (RETURN_UNWIND (KNOWN (PINT 0)) (porigin_zero_return)) :: ptask_return_tail*',
        'pfunction_handler.ORIGIN = PORIGIN n_zero_handler pcpath_zero_handler',
        '$origin_child((pfunction_handler.ORIGIN), [PCFIELD 5, PCINDEX 1]) = (porigin_zero_return)',
        '$origin_node(S.SOURCES, porigin_zero_return) = (NStmtReturn (NScalarInt (INTEGER 0) metadata_zero) metadata_zero_return)',
        'statement_zero_return = NStmtReturn (NScalarInt (INTEGER 0) metadata_zero) metadata_zero_return',
        'porigin_zero_return = PORIGIN n_zero_handler pcpath_zero_return',
        '$origin_child((porigin_zero_return), [PCFIELD 0]) = (porigin_zero)',
        'porigin_zero = PORIGIN n_zero_handler pcpath_zero',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_zero) = ((z_zero, b_zero))',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_zero_return) = ((z_zero_return, b_zero_return))']
    if prior.two_calls(name):
        bindings += [
            'S_return_right.TODO = (RETURN_UNWIND (KNOWN (PINT 0)) (porigin_zero_return)) :: ptask_return_right_tail*']
    return bindings


def return_proof(name):
    resumed = 'S' if name == 'warning-right-cv-pair' else 'S_resume'
    condition = (r'pfunction_handler.CODE.UNIT = n_zero_handler /\ '
        r'pfunction_handler.BODY = pcpath_zero_handler ++ [PCFIELD 5] /\ '
        r'pcpath_zero_return = pfunction_handler.BODY ++ [PCINDEX 1] /\ '
        r'pcpath_zero = pcpath_zero_return ++ [PCFIELD 0] /\ '
        r'z_zero = $source_line(metadata_zero) /\ b_zero /\ '
        r'z_zero_return = $source_line(metadata_zero_return) /\ ~b_zero_return /\ '
        r'$compiled_read(S_return, porigin_zero) = (PINT 0) /\ '
        r'$compiled_read(S, porigin_zero) = (PINT 0) /\ '
        r'$call_task_valid(S_return, RETURN_UNWIND (KNOWN (PINT 0)) (porigin_zero_return)) /\ '
        r'S_return.RESULT = KNOWN PNULL /\ S_return.BASE = BASE_VALUE (KNOWN PNULL) /\ '
        r'S_handler.RESULT = KNOWN (PINT 0) /\ S_handler.RESULT =/= KNOWN (PBOOL false) /\ '
        r'S.RESULT = KNOWN PNULL /\ $dz_raw(S_handler) = ' + resumed + r' /\ '
        r'porigin_zero_return =/= pfunction_handler.ORIGIN')
    if prior.two_calls(name):
        condition += (r' /\ $compiled_read(S_return_right, porigin_zero) = (PINT 0) /\ '
            r'$call_task_valid(S_return_right, RETURN_UNWIND (KNOWN (PINT 0)) (porigin_zero_return)) /\ '
            r'S_return_right.RESULT = KNOWN PNULL /\ S_return_right.BASE = BASE_VALUE (KNOWN PNULL) /\ '
            r'S_handler_right.RESULT = KNOWN (PINT 0) /\ $dz_raw(S_handler_right) = S')
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('returns NULL', 'returns integer zero').replace('handled NULL result', 'handled zero result'),
               converted(condition)) for label, condition in checks]
    checks += [('the own zero child/read and actual integer return stay distinct from FALSE and NULL scratch',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('actual zero return and reset NULL scratch survive capture and real retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
