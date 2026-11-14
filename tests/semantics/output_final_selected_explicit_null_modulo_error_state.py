#!/usr/bin/env python3
"""Genuine explicit NULL returns precede selected FINAL MOD Error capture."""
import output_final_selected_both_mask_modulo_error_state as homogeneous
import output_final_selected_mixed_modulo_error_state as mixed
import output_final_selected_explicit_null_modulo_error_sources as sources

prior, runner = homogeneous.prior, homogeneous.runner
PREFIX = homogeneous.PREFIX
CASES = {name: sources.CASES['native-selected-explicit-null-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}


def base_for(name):
    return mixed if name.startswith('warning-deprecated-') else homogeneous


def two_calls(name):
    return name.startswith('warning-deprecated-') or '-both-' in name


def converted(condition):
    return condition.replace('selected_modulo_both_mask', 'selected_modulo_explicit_null').replace(
        'selected_modulo_mixed', 'selected_modulo_explicit_null')


def return_bindings(name):
    bindings = [
        'S_return.TODO = (RETURN_UNWIND (KNOWN PNULL) (porigin_explicit_return)) :: ptask_return_tail*',
        'pfunction_handler.ORIGIN = PORIGIN n_explicit_handler pcpath_explicit_handler',
        '$origin_child((pfunction_handler.ORIGIN), [PCFIELD 5, PCINDEX 1]) = (porigin_explicit_return)',
        '$origin_node(S.SOURCES, porigin_explicit_return) = (NStmtReturn (NExprConstFetch (NName (BYTES text_explicit_null) metadata_explicit_null_name) metadata_explicit_null) metadata_explicit_return)',
        'statement_explicit_return = NStmtReturn (NExprConstFetch (NName (BYTES text_explicit_null) metadata_explicit_null_name) metadata_explicit_null) metadata_explicit_return',
        '$origin_child((porigin_explicit_return), [PCFIELD 0]) = (porigin_explicit_null)',
        'porigin_explicit_null = PORIGIN n_explicit_handler pcpath_explicit_null',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_explicit_null) = ((z_explicit_null, b_explicit_null))']
    if two_calls(name):
        bindings += [
            'S_return_right.TODO = (RETURN_UNWIND (KNOWN PNULL) (porigin_explicit_return)) :: ptask_return_right_tail*']
    return bindings


def return_proof(name):
    condition = (r'$ptlc($base64(text_explicit_null)) = $ptascii("null") /\ '
        r'pfunction_handler.CODE.UNIT = n_explicit_handler /\ '
        r'pfunction_handler.BODY = pcpath_explicit_handler ++ [PCFIELD 5] /\ '
        r'pcpath_explicit_null = pfunction_handler.BODY ++ [PCINDEX 1, PCFIELD 0] /\ '
        r'z_explicit_null = $source_line(metadata_explicit_null) /\ '
        r'$compiled_read(S_return, porigin_explicit_null) = (PNULL) /\ '
        r'$compiled_read(S, porigin_explicit_null) = (PNULL) /\ '
        r'$call_task_valid(S_return, RETURN_UNWIND (KNOWN PNULL) (porigin_explicit_return)) /\ '
        r'porigin_explicit_return =/= pfunction_handler.ORIGIN')
    if two_calls(name):
        condition += (r' /\ $compiled_read(S_return_right, porigin_explicit_null) = (PNULL) /\ '
            r'$call_task_valid(S_return_right, RETURN_UNWIND (KNOWN PNULL) (porigin_explicit_return))')
    return condition


def original(name):
    return converted(base_for(name).original(name))


def frontier(name, fixture, path):
    bindings, checks = base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label, converted(condition)) for label, condition in checks]
    checks += [('the actual explicit Return has its own raw NULL, compiled read/line and unwind source',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('explicit NULL source and real returned-frame authority survive capture and retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
