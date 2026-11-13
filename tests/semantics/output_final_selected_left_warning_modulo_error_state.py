#!/usr/bin/env python3
"""A real selected LEFT Warning returns before the quiet RHS MOD Error."""
import output_final_selected_warning_modulo_error_state as right
import output_final_selected_left_warning_modulo_error_sources as sources

prior = right.prior
runner = right.previous.previous
PREFIX = right.PREFIX.replace(
    'INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 0',
    'INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 0').replace(
    'INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1',
    'INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1').replace(
    '-- if pintegerconversion.NOTICES = [(2, ptbytes)]',
    '-- if pintegerconversion_left.NOTICES = [(2, ptbytes)]')
CASES = {name: sources.CASES['native-selected-left-warning-modulo-error-' + name]
         for name in ['constant', 'left-cv', 'right-cv', 'cv-pair']}


def bindings_for(name, fixture, path):
    bindings, _ = right.bindings_for(name, fixture, path)
    replacements = {
        'S_warning.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 0) :: ptask_tail*':
            'S_warning.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 0) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 1':
            'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1'}
    for before, after in replacements.items():
        assert bindings.count(before) == 1
        bindings[bindings.index(before)] = after
    before = prior.seek('S', 'S_handler', 9)
    index = bindings.index(before[0])
    assert bindings[index:index + len(before)] == before
    bindings[index:index + len(before)] = [
        'S_resume_found = $drive_steps(S_handler, 1)', 'S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1) :: ptask_tail*',
        'S_left_complete = $dz_raw(S_resume)',
        *prior.seek('S', 'S_resume', 9)]
    if name in ['constant', 'right-cv']:
        index = bindings.index('S_generated.COMPLETION = THROWING n_exception')
        bindings.insert(index, '$compiled_read(S_binary, porigin_left) = (pvalue_left_compiled)')
    return bindings


def original(name):
    cells = [side for side in ['left', 'right'] if name == side + '-cv' or name == 'cv-pair']
    line = 6 + len(cells)
    cvs = '[' + ', '.join('$ptascii("' + side + '")' for side in cells) + ']' if cells else 'eps'
    conditions = [f'z = {line}', 'n = 0', 'i_left = 1',
        f'pfunction.CVS = {cvs}', 'S.CVS = pfunction.CVS', f'|S.ENV| = {len(cells)}',
        'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', 'pvalue_right = PINT 0',
        '$string_long($ptascii("1x")) = STRINT i_left (LEADINGNUMBER :: eps)',
        'pintegeroperation.OP = MODULO', 'pintegeroperation.SWAPPED = false',
        'pintegeroperation.SITE = porigin_operator', 'pintegeroperation.RIGHT = S_binary.RESULT',
        '$integer_operation_valid(S, pintegeroperation)',
        '$integer_warning_valid(S, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, n)',
        '$integer_conversion(pvalue_left) = (pintegerconversion_left)',
        'pintegerconversion_left.INPUT = pvalue_left', 'pintegerconversion_left.VALUE = i_left',
        'pintegerconversion_left.NOTICES = [(2, ($ptascii("A non-numeric value encountered")))]',
        '$integer_conversion(pvalue_right) = (pintegerconversion)',
        'pintegerconversion.INPUT = pvalue_right', 'pintegerconversion.VALUE = 0', 'pintegerconversion.NOTICES = eps',
        '$ob_object_modulo_integer(pvalue_left) = eps', '$ob_object_modulo_integer(pvalue_right) = (0)',
        '$ob_object_string_value(S, pvalue_left)', '$value_nodes(pvalue_left) = eps', '$value_nodes(pvalue_right) = eps',
        '$error_handler_eligible(S, 2)', '~$error_handler_eligible(S, 8192)',
        'S.ERRORHANDLER.LEVELS = 2', 'S.ERRORHANDLER.CALLBACK =/= eps',
        'S.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]',
        'S_binary.EVENTS = [OUTPUT ([80])]', 'S.EVENTS = [OUTPUT ([80])]',
        'S.STORE[0:|S_binary.STORE|] = S_binary.STORE', 'S.RESULT = KNOWN PNULL',
        'S.ERRORHANDLER = S_binary.ERRORHANDLER', 'S.ERRORHANDLERS = S_binary.ERRORHANDLERS',
        'S.HELD = eps', '$tasks_nodes(S.TODO) = eps', 'S.RETIREDOWNERS = eps', '$base_nodes(S.BASE) = eps',
        '$call_current_valid(S)', '$ob_object_final_native_method(S) = (pobobjectreturn)',
        '$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT)',
        '$ob_object_division_operator(S, porigin_operator) = (MODULO)',
        'S_request = $integer_converted(S, pintegeroperation, INTEGER_RIGHT i_left, 0)',
        f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
        'S_request.TODO = ptask_tail*', 'S_request.RESULT = KNOWN PNULL',
        'S_request.EVENTS = S.EVENTS', 'S_request.STORE = S.STORE',
        'S_request.ERRORHANDLER = S.ERRORHANDLER', 'S_request.ERRORHANDLERS = S.ERRORHANDLERS',
        '$ob_object_division_error_source(S_generated, pfunction, pobreturnerror)',
        '$ob_object_return_error_live(S_generated, pobreturnerror)']
    for side in ['left', 'right']:
        operand = 'pintegeroperation.' + side.upper()
        pointer = operand + 'POINTER'
        child = '[PCFIELD ' + str(side == 'right' and 1 or 0) + ']'
        conditions += [f'$integer_pointer_select(S, {operand}) = ({pointer})',
            f'$integer_pointer_value(S_binary, {pointer}) = (pvalue_{side})',
            f'$integer_pointer_value(S, {pointer}) = (pvalue_{side})',
            f'$ob_object_error_operand_value(S, {operand}, {child}, z) = (pvalue_{side})',
            f'$integer_slot_rank(S, porigin_operator, {child}, {operand}) = ({8 if side in cells else 1})',
            f'$code_expression_at_source(S, porigin_operator, {child}) = ({line})']
        if side in cells:
            conditions += [f'n_{side}* = $ptascii("{side}")', f'z_{side} = {line}',
                f'{operand} = VARIABLE n_{side}* z_{side}', f'{pointer} = INTEGER_CV n_{side}*',
                f'$compiled_read(S, porigin_{side}) = eps',
                f'(HCELL n_cell_{side}) <- S.ALLOCATIONS', f'~(n_cell_{side} <- S.REFCELLS)',
                f'$heap_count(HCELL n_cell_{side}, $machine_roots(S)) = 1',
                f'$heap_owners($heap_graph(S), HCELL n_cell_{side}) = 1']
        else:
            conditions += [f'{operand} = KNOWN pvalue_{side}', f'{pointer} = INTEGER_COPY pvalue_{side}']
            conditions += (['pvalue_left_compiled = PSTRING ($ptascii("1x"))',
                '$compiled_read(S, porigin_left) = (pvalue_left_compiled)',
                'pvalue_left = $compiled_string_value(S, porigin_left, pvalue_left_compiled)']
                if side == 'left' else ['$compiled_read(S, porigin_right) = (PINT 0)'])
    if len(cells) == 2:
        conditions += ['n_cell_left =/= n_cell_right']
    return r' /\ '.join(conditions)


def frontier(name, fixture, path):
    bindings = bindings_for(name, fixture, path)
    stop = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    _, inherited = right.frontier(name, fixture, path)
    checks = []
    for label, condition in inherited[:4]:
        condition = condition.replace('INTEGER_RIGHT i_left, pintegerconversion, 0',
                                      'INTEGER_LEFT, pintegerconversion_left, 0')
        condition = condition.replace('selected_rhs_modulo_handler', 'selected_lhs_modulo_handler')
        condition = condition.replace('$error_handler_finish(S_handler, perrorcall_return) = S',
                                      '$error_handler_finish(S_handler, perrorcall_return) = S_resume')
        checks.append((label.replace('cached RHS', 'cached left').replace('RHS', 'LEFT'), condition))
    checks += [
        ('the completed left notice advances through its saved integer before the quiet RHS cursor0',
         r'S_resume.RESULT = KNOWN PNULL /\ '
         r'$integer_warning_valid(S_resume, pintegeroperation, INTEGER_LEFT, pintegerconversion_left, 1) /\ '
         r'S_left_complete = $integer_converted(S_resume, pintegeroperation, INTEGER_LEFT, i_left) /\ '
         r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
         r'S_left_complete.RESULT = KNOWN PNULL /\ S_left_complete.EVENTS = S_resume.EVENTS /\ '
         r'S.ERRORHANDLER = S_resume.ERRORHANDLER /\ S.CURRENT = S_resume.CURRENT /\ '
         r'S.FRAMES = S_resume.FRAMES /\ S.ENV = S_resume.ENV /\ S.CVS = S_resume.CVS /\ '
         r'S.STORE = S_resume.STORE /\ S.ORIGIN = S_resume.ORIGIN /\ '
         r'S.EVENTS = [OUTPUT ([80])] /\ S.OUTPUTBUFFERS = S_resume.OUTPUTBUFFERS /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('original current values/source/caches and native Error precede any new capture', original(name)),
        inherited[6]]
    return bindings[:stop], checks


def lifecycle(name, fixture, path):
    bindings = bindings_for(name, fixture, path)
    _, checks = right.lifecycle(name, fixture, path)
    before = right.original(name)
    assert checks[0][1].count(before) == 1
    checks[0] = ('completed selected LEFT Warning captures only the authentic nonowning Error source',
                 checks[0][1].replace(before, original(name)))
    before = '$error_handler_finish(S_handler, perrorcall_return) = S /\\ '
    assert checks[4][1].count(before) == 1
    checks[4] = (checks[4][0], checks[4][1].replace(before,
                 '$error_handler_finish(S_handler, perrorcall_return) = S_resume /\\ '))
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
