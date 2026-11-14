#!/usr/bin/env python3
"""Actual TRUE returns precede selected FINAL MOD Error capture."""
import output_final_selected_explicit_null_modulo_error_state as prior
import output_final_selected_true_return_modulo_error_sources as sources

runner = prior.runner
PREFIX = prior.PREFIX.replace('RETURN_UNWIND (KNOWN PNULL) porigin?',
                             'RETURN_UNWIND (KNOWN (PBOOL true)) porigin?')
CASES = {name: sources.CASES['native-selected-true-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}


def converted(condition):
    condition = prior.converted(condition).replace('selected_modulo_explicit_null',
                                                  'selected_modulo_true_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN PNULL',
                                      state + '.RESULT = KNOWN (PBOOL true)')
    return condition


def return_bindings(name):
    bindings = [
        'S_return.TODO = (RETURN_UNWIND (KNOWN (PBOOL true)) (porigin_true_return)) :: ptask_return_tail*',
        'pfunction_handler.ORIGIN = PORIGIN n_true_handler pcpath_true_handler',
        '$origin_child((pfunction_handler.ORIGIN), [PCFIELD 5, PCINDEX 1]) = (porigin_true_return)',
        '$origin_node(S.SOURCES, porigin_true_return) = (NStmtReturn (NExprConstFetch (NName (BYTES text_true) metadata_true_name) metadata_true) metadata_true_return)',
        'statement_true_return = NStmtReturn (NExprConstFetch (NName (BYTES text_true) metadata_true_name) metadata_true) metadata_true_return',
        'porigin_true_return = PORIGIN n_true_handler pcpath_true_return',
        '$origin_child((porigin_true_return), [PCFIELD 0]) = (porigin_true)',
        'porigin_true = PORIGIN n_true_handler pcpath_true',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_true) = ((z_true, b_true))',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_true_return) = ((z_true_return, b_true_return))']
    if prior.two_calls(name):
        bindings += [
            'S_return_right.TODO = (RETURN_UNWIND (KNOWN (PBOOL true)) (porigin_true_return)) :: ptask_return_right_tail*']
    return bindings


def return_proof(name):
    condition = (r'$ptlc($base64(text_true)) = $ptascii("true") /\ '
        r'pfunction_handler.CODE.UNIT = n_true_handler /\ '
        r'pfunction_handler.BODY = pcpath_true_handler ++ [PCFIELD 5] /\ '
        r'pcpath_true_return = pfunction_handler.BODY ++ [PCINDEX 1] /\ '
        r'pcpath_true = pcpath_true_return ++ [PCFIELD 0] /\ '
        r'z_true = $source_line(metadata_true) /\ b_true /\ '
        r'z_true_return = $source_line(metadata_true_return) /\ ~b_true_return /\ '
        r'$compiled_read(S_return, porigin_true) = (PBOOL true) /\ '
        r'$compiled_read(S, porigin_true) = (PBOOL true) /\ '
        r'$call_task_valid(S_return, RETURN_UNWIND (KNOWN (PBOOL true)) (porigin_true_return)) /\ '
        r'S_return.RESULT = KNOWN PNULL /\ S_return.BASE = BASE_VALUE (KNOWN PNULL) /\ '
        r'S_handler.RESULT = KNOWN (PBOOL true) /\ S.RESULT = KNOWN PNULL /\ '
        r'porigin_true_return =/= pfunction_handler.ORIGIN')
    if prior.two_calls(name):
        condition += (r' /\ $compiled_read(S_return_right, porigin_true) = (PBOOL true) /\ '
            r'$call_task_valid(S_return_right, RETURN_UNWIND (KNOWN (PBOOL true)) (porigin_true_return)) /\ '
            r'S_return_right.RESULT = KNOWN PNULL /\ S_return_right.BASE = BASE_VALUE (KNOWN PNULL) /\ '
            r'S_handler_right.RESULT = KNOWN (PBOOL true)')
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('returns NULL', 'returns true').replace('handled NULL result', 'handled true result'),
               converted(condition)) for label, condition in checks]
    checks += [('the own TRUE child/read and actual Boolean return remain distinct from NULL scratch',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('actual TRUE return and reset NULL scratch survive capture and real retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
