#!/usr/bin/env python3
"""FALSE returns report default diagnostics before selected FINAL MOD capture."""
import output_final_selected_explicit_null_modulo_error_state as prior
import output_final_selected_false_return_modulo_error_sources as sources

runner = prior.runner
PREFIX = prior.PREFIX.replace('RETURN_UNWIND (KNOWN PNULL) porigin?',
                             'RETURN_UNWIND (KNOWN (PBOOL false)) porigin?')
CASES = {name: sources.CASES['native-selected-false-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}


def diagnostics(name):
    notices = [('Warning', b'A non-numeric value encountered')]
    if name.startswith('deprecated-both-'):
        notices = [('Deprecated', b'Implicit conversion from float-string "1.5" to int loses precision'),
                   ('Deprecated', b'Implicit conversion from float-string "0.5" to int loses precision')]
    elif name.startswith('warning-deprecated-'):
        notices += [('Deprecated', b'Implicit conversion from float 0.5 to int loses precision')]
    line = 8 if 'cv-pair' in name else 6
    return ['DIAGNOSTIC "' + level + '" ' + prior.homogeneous.prior.value(message) + ' ' + str(line)
            for level, message in notices]


def converted(name, condition):
    condition = prior.converted(condition).replace('selected_modulo_explicit_null',
                                                  'selected_modulo_false_return')
    for state, call in [('S_handler', 'perrorcall_return'),
                        ('S_handler_right', 'perrorcall_return_right')]:
        condition = condition.replace(state + '.RESULT = KNOWN PNULL',
                                      state + '.RESULT = KNOWN (PBOOL false)')
        condition = condition.replace('$error_handler_finish(' + state + ', ' + call + ')',
            '$error_fallback_finish($error_default(' + state + ', ' + call + '.EVENT, ' + call + '.LEVEL), ' + call + ')')
    events = diagnostics(name)
    for state in ['S', 'S_capture']:
        condition = condition.replace(state + '.EVENTS = [OUTPUT ([80])]',
                                      state + '.EVENTS = [OUTPUT ([80]), ' + ', '.join(events) + ']')
    for state in ['S_resume', 'S_warning_right', 'S_invoke_right', 'S_return_right', 'S_handler_right']:
        condition = condition.replace(state + '.EVENTS = [OUTPUT ([80])]',
                                      state + '.EVENTS = [OUTPUT ([80]), ' + events[0] + ']')
    return condition.replace('S_report.EVENTS = [OUTPUT ([80]), STDERR ',
        'S_report.EVENTS = [OUTPUT ([80]), ' + ', '.join(events) + ', STDERR ')


def return_bindings(name):
    bindings = [
        'S_return.TODO = (RETURN_UNWIND (KNOWN (PBOOL false)) (porigin_false_return)) :: ptask_return_tail*',
        'pfunction_handler.ORIGIN = PORIGIN n_false_handler pcpath_false_handler',
        '$origin_child((pfunction_handler.ORIGIN), [PCFIELD 5, PCINDEX 1]) = (porigin_false_return)',
        '$origin_node(S.SOURCES, porigin_false_return) = (NStmtReturn (NExprConstFetch (NName (BYTES text_false) metadata_false_name) metadata_false) metadata_false_return)',
        'statement_false_return = NStmtReturn (NExprConstFetch (NName (BYTES text_false) metadata_false_name) metadata_false) metadata_false_return',
        'porigin_false_return = PORIGIN n_false_handler pcpath_false_return',
        '$origin_child((porigin_false_return), [PCFIELD 0]) = (porigin_false)',
        'porigin_false = PORIGIN n_false_handler pcpath_false',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_false) = ((z_false, b_false))',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_false_return) = ((z_false_return, b_false_return))',
        'S_default = $error_default(S_handler, perrorcall_return.EVENT, perrorcall_return.LEVEL)']
    if prior.two_calls(name):
        bindings += [
            'S_return_right.TODO = (RETURN_UNWIND (KNOWN (PBOOL false)) (porigin_false_return)) :: ptask_return_right_tail*',
            'S_default_right = $error_default(S_handler_right, perrorcall_return_right.EVENT, perrorcall_return_right.LEVEL)']
    return bindings


def fallback_proof(state, call, event, resumed):
    return (state + r'.COMPLETION = NORMAL /\ ' + state + r'.RESULT = KNOWN (PBOOL false) /\ '
        + state + r'.ERRORHANDLER.CALLBACK = eps /\ '
        + state + '.EVENTS = ' + state.replace('S_default', 'S_handler') + '.EVENTS ++ [' + event + r'] /\ '
        + state + '.STORE = ' + state.replace('S_default', 'S_handler') + r'.STORE /\ '
        + state + '.OUTPUTBUFFERS = ' + state.replace('S_default', 'S_handler') + r'.OUTPUTBUFFERS /\ '
        + '$error_handler_finish(' + state + ', ' + call + ') = ' + resumed)


def return_proof(name):
    resumed = 'S' if name == 'warning-right-cv-pair' else 'S_resume'
    events = diagnostics(name)
    condition = (r'$ptlc($base64(text_false)) = $ptascii("false") /\ '
        r'pfunction_handler.CODE.UNIT = n_false_handler /\ '
        r'pfunction_handler.BODY = pcpath_false_handler ++ [PCFIELD 5] /\ '
        r'pcpath_false_return = pfunction_handler.BODY ++ [PCINDEX 1] /\ '
        r'pcpath_false = pcpath_false_return ++ [PCFIELD 0] /\ '
        r'z_false = $source_line(metadata_false) /\ b_false /\ '
        r'z_false_return = $source_line(metadata_false_return) /\ ~b_false_return /\ '
        r'$compiled_read(S_return, porigin_false) = (PBOOL false) /\ '
        r'$compiled_read(S, porigin_false) = (PBOOL false) /\ '
        r'$call_task_valid(S_return, RETURN_UNWIND (KNOWN (PBOOL false)) (porigin_false_return)) /\ '
        r'S_return.RESULT = KNOWN PNULL /\ S_return.BASE = BASE_VALUE (KNOWN PNULL) /\ '
        r'S_handler.RESULT = KNOWN (PBOOL false) /\ S.RESULT = KNOWN PNULL /\ '
        r'$dz_raw(S_handler) = ' + resumed + r' /\ '
        r'porigin_false_return =/= pfunction_handler.ORIGIN /\ '
        + fallback_proof('S_default', 'perrorcall_return', events[0], resumed))
    if prior.two_calls(name):
        condition += (r' /\ $compiled_read(S_return_right, porigin_false) = (PBOOL false) /\ '
            r'$call_task_valid(S_return_right, RETURN_UNWIND (KNOWN (PBOOL false)) (porigin_false_return)) /\ '
            r'S_return_right.RESULT = KNOWN PNULL /\ S_return_right.BASE = BASE_VALUE (KNOWN PNULL) /\ '
            r'S_handler_right.RESULT = KNOWN (PBOOL false) /\ $dz_raw(S_handler_right) = S /\ '
            + fallback_proof('S_default_right', 'perrorcall_return_right', events[1], 'S'))
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'FALSE').replace('handled', 'default-reported'),
               converted(name, condition)) for label, condition in checks]
    checks += [('the own FALSE return reports each diagnostic before NULL scratch and handler restoration',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('actual FALSE fallback order survives capture and real retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
