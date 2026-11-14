#!/usr/bin/env python3
"""Genuine bare returns precede selected FINAL MOD Error capture."""
import output_final_selected_explicit_null_modulo_error_state as prior
import output_final_selected_bare_return_modulo_error_sources as sources

runner, PREFIX = prior.runner, prior.PREFIX
CASES = {name: sources.CASES['native-selected-bare-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}


def converted(condition):
    return prior.converted(condition).replace('selected_modulo_explicit_null',
                                              'selected_modulo_bare_return')


def return_bindings(name):
    bindings = [
        'S_return.TODO = (RETURN_UNWIND (KNOWN PNULL) (porigin_bare_return)) :: ptask_return_tail*',
        'pfunction_handler.ORIGIN = PORIGIN n_bare_handler pcpath_bare_handler',
        '$origin_child((pfunction_handler.ORIGIN), [PCFIELD 5, PCINDEX 1]) = (porigin_bare_return)',
        '$origin_node(S.SOURCES, porigin_bare_return) = (NStmtReturn ABSENT metadata_bare_return)',
        'statement_bare_return = NStmtReturn ABSENT metadata_bare_return',
        'porigin_bare_return = PORIGIN n_bare_handler pcpath_bare_return',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_bare_return) = ((z_bare_return, b_bare_return))']
    if prior.two_calls(name):
        bindings += [
            'S_return_right.TODO = (RETURN_UNWIND (KNOWN PNULL) (porigin_bare_return)) :: ptask_return_right_tail*']
    return bindings


def return_proof(name):
    condition = (r'pfunction_handler.CODE.UNIT = n_bare_handler /\ '
        r'pfunction_handler.BODY = pcpath_bare_handler ++ [PCFIELD 5] /\ '
        r'pcpath_bare_return = pfunction_handler.BODY ++ [PCINDEX 1] /\ '
        r'z_bare_return = $source_line(metadata_bare_return) /\ ~b_bare_return /\ '
        r'$origin_node(S.SOURCES, PORIGIN n_bare_handler (pcpath_bare_return ++ [PCFIELD 0])) = eps /\ '
        r'$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_bare_return ++ [PCFIELD 0]) = eps /\ '
        r'$compiled_read(S_return, porigin_bare_return) = eps /\ '
        r'$compiled_read(S, porigin_bare_return) = eps /\ '
        r'$call_task_valid(S_return, RETURN_UNWIND (KNOWN PNULL) (porigin_bare_return)) /\ '
        r'porigin_bare_return =/= pfunction_handler.ORIGIN')
    if prior.two_calls(name):
        condition += (r' /\ $compiled_read(S_return_right, porigin_bare_return) = eps /\ '
            r'$call_task_valid(S_return_right, RETURN_UNWIND (KNOWN PNULL) (porigin_bare_return))')
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label, converted(condition)) for label, condition in checks]
    checks += [('the actual bare Return has its own compiled statement/line and no expression/read',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('bare Return source and real returned-frame authority survive capture and retirement',
         return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
