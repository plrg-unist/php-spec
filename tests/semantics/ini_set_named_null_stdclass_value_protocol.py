#!/usr/bin/env python3
"""Named reception retains an owning stdClass slot across shared updates."""
import json
import os
from pathlib import Path

import ini_set_null_stdclass_value_protocol as shared
import ini_set_named_null_stdclass_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, error, budget, mark = shared.reach, shared.error, shared.budget, shared.mark
PREFIX = shared.shared.PREFIX + r"""
dec $test_ini_named_std_front(pstate, nat) : bool
def $test_ini_named_std_front(S, 0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.OWNER = eps
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.SELECTION = (n_selection)
def $test_ini_named_std_front(S, 1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_object))]
def $test_ini_named_std_front(S, n_stage) = false -- otherwise
dec $test_ini_named_std_seek(pstate, nat, nat) : pstate
def $test_ini_named_std_seek(S, n_stage, 0) = S
def $test_ini_named_std_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_named_std_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_named_std_seek(S, n_stage, n) = $test_ini_named_std_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_named_std_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def partial(state, start, stage):
    return [state + '_found = $test_ini_named_std_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_named_std_front(' + state + ',' + str(stage) + ')']


def written(state, mixed=False):
    call = 'pconfigcall_' + state
    values = []
    for index, destination, name in ([(0, 0, None), (1, 1, 'value')] if mixed else [(0, 1, 'value'), (1, 0, 'option')]):
        suffix = '_' + state + '_' + str(index)
        values += ['$intrinsic_argument(' + state + ',' + call + '.SITE,' + str(index) + ') = ((expression' + suffix + ',false,preqbytes' + suffix + '?,porigin' + suffix + ',z' + suffix + '))',
            'preqbytes' + suffix + '? = ' + ('eps' if name is None else '(' + text(name) + ')'),
            '$config_destination(' + call + '.KIND,preqbytes' + suffix + '?,' + str(index) + ') = (' + str(destination) + ')',
            '$config_ini_named_stdclass_argument(' + state + ',' + call + ',' + str(index) + ')']
    return values


def front(state, start, mixed=False):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = eps', call + '.PACKS = eps',
        call + '.INDEX = 2', call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT ' + obj + '))]',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_stdclass(' + state + ',' + obj + ')',
        state + '.OBJECTS[' + obj + '] = STDINSTANCE', '(HOBJECT ' + obj + ') <- ' + state + '.ALLOCATIONS',
        '$object_table_at(' + state + '.OBJECTTABLES,' + obj + ') = eps',
        '$node_children(' + state + ',HOBJECT ' + obj + ') = eps',
        '$config_nodes(' + call + ') = [HOBJECT ' + obj + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + obj + ']',
        *written(state, mixed), *common.public(state)]


def returned(state, precision, result, spelling, warnings=1, empty=False):
    values = shared.returned(state, precision, result, spelling)
    old = state + '_return.STORE[n_warnings_' + state + '] = DEFINED (PINT 1)'
    assert values.count(old) == 1
    values[values.index(old)] = old.replace('PINT 1', 'PINT ' + str(warnings))
    if empty:
        old = mark(state + '_return', 'n_object_' + state,
            '(PSTRING_CARRIER INTERNED_STRING ' + text(spelling) + ')')[0]
        assert values.count(old) == 1
        values[values.index(old)] = '$objectprops_at(' + state + '_return.OBJECTPROPS,n_object_' + state + ') = (eps)'
    return values


def refusals(state):
    call = 'pconfigcall_' + state
    return [*[v for v in shared.refusals(state) if '.NAMED = true' not in v],
        '~$config_ini_null_valid(' + state + ',' + call + '[.NAMED = false])',
        '~$config_ini_named_stdclass_argument(' + state + ',' + call + ',2)',
        '~$config_ini_named_stdclass_argument(' + state + '[.CODE = eps],' + call + ',0)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'reversed-and-mixed-null-stdclass-values-return-through-true-handlers':
        values += [*front('S_true', 'S_initial'), 'pconfigcall_S_true.SELECTION = eps',
            '$compiled_read(S_true,porigin_S_true_0) = eps', '$compiled_read(S_true,porigin_S_true_1) = (PNULL)',
            *mark('S_true', 'n_object_S_true', '(PSTRING_CARRIER INTERNED_STRING ' + text('start72') + ')'),
            *returned('S_true', '14', 'true', 'true72'), *error('S_true', 'S_true_resume', 'namedNullStdTrueCaller72'),
            *front('S_mixed', 'S_true_error', mixed=True), 'n_object_S_mixed =/= n_object_S_true',
            '$objectprops_at(S_mixed.OBJECTPROPS,n_object_S_mixed) = (eps)',
            '$compiled_read(S_mixed,porigin_S_mixed_0) = (PNULL)', '$compiled_read(S_mixed,porigin_S_mixed_1) = eps',
            *returned('S_mixed', '14', 'true', 'true72', warnings=2, empty=True),
            *error('S_mixed', 'S_mixed_resume', 'namedNullStdTrueCaller72'),
            *refusals('S_true'), *budget('S_true'), *budget('S_mixed_resume'),
            'S_final = $drive_steps(S_mixed_error,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|I|true72|99|1|M|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|2|14|Z')]
    else:
        strict = name == 'strict-reversed-null-stdclass-value-rejects-option-after-shared-effects'
        assert strict or name == 'selected-reversed-null-stdclass-value-preserves-shared-option-updates'
        values += [*partial('S_pre', 'S_initial', 0),
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*',
            'pconfigcall_pre.SELECTION = (n_selection)', 'pconfigcall_pre.SENT = eps',
            '$config_pending_valid(S_pre,pconfigcall_pre,false)',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('old') + ') = (n_old)', 'S_pre.STORE[n_old] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]
        if not strict:
            values += [*mark('S_pre', 'n_captured', 'pvalue_captured'),
                'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_mark) ' + text('captured-std72'),
                '$string_carrier_valid(S_pre,pvalue_captured)']
        values += [*partial('S_early', 'S_pre', 1),
            'S_early.TODO = (CONFIG_ARGS pconfigcall_early) :: ptask_early*',
            'pconfigcall_early = pconfigcall_pre[.INDEX = 1][.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_captured))]][.NAMED = true]',
            '$config_pending_valid(S_early,pconfigcall_early,false)', '$call_task_valid(S_early,CONFIG_ARGS pconfigcall_early)',
            '$config_nodes(pconfigcall_early) = [HOBJECT n_captured]', '$task_nodes(CONFIG_ARGS pconfigcall_early) = [HOBJECT n_captured]',
            'S_early.STORE[n_effects] = DEFINED (PINT 1)', 'S_early.STORE[n_value] = DEFINED (PINT ' + ('0' if strict else '2527') + ')',
            'S_early.STORE[n_keep] = DEFINED (POBJECT n_captured)', 'S_early.STORE[n_old] = DEFINED (POBJECT n_captured)',
            *mark('S_early', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('strict-value72' if strict else 'value72') + ')'),
            '$test_outputs(S_early.EVENTS) = ' + text('B|V|'), 'S_early.PRECISIONINI = ' + text('14'), *common.public('S_early'),
            *front('S', 'S_early'),
            'pconfigcall_S = pconfigcall_early[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT n_captured))]]',
            'n_object_S = n_captured', '$compiled_read(S,porigin_S_0) = eps', '$compiled_read(S,porigin_S_1) = eps',
            'S.STORE[n_effects] = DEFINED (PINT 2)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_keep] = DEFINED (POBJECT n_captured)', 'S.STORE[n_old] = DEFINED (POBJECT n_captured)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|O|')]
        if strict:
            values += [*mark('S', 'n_object_S', '(PSTRING_CARRIER INTERNED_STRING ' + text('strict-option72') + ')'),
                '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                'S.STORE[n_value] = DEFINED (PINT 0)', 'S.PRECISIONINI = ' + text('9'),
                *error('S', 'S', 'strictNamedStdCaller72', strict=True), *budget('S_early'), *budget('S'),
                'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|' + OPTION_ERROR + '|99|2|0|constant|precision|0|S|strict-option72|9|Z')]
        else:
            values += [*mark('S', 'n_object_S', '(PSTRING_CARRIER INTERNED_STRING ' + text('option72') + ')'),
                '~$config_strict(S,pconfigcall_S)', 'S.STORE[n_value] = DEFINED (PINT 2531)', 'S.PRECISIONINI = ' + text('7'),
                *returned('S', '8', 'false', 'handler72'),
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 2)',
                'S_return.STORE[n_keep] = DEFINED (POBJECT n_captured)', 'S_return.STORE[n_old] = DEFINED (POBJECT n_captured)',
                '$heap_count(HOBJECT n_captured,$tasks_nodes(S_return.TODO)) = 1',
                *error('S', 'S_resume', 'namedNullStdCaller72'), *refusals('S'), *budget('S_pre'), *budget('S_resume'),
                *reach('S_recovery', 'S_error', 3), 'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
                '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
                '~$config_ini_named_stdclass_argument(S_recovery,pconfigcall_recovery,0)',
                '~$config_ini_named_stdclass_argument(S_recovery,pconfigcall_recovery,1)',
                *common.step('S_recovered', 'S_recovery'), 'S_recovered.RESULT = KNOWN pvalue_precision',
                '$string_bytes(pvalue_precision) = (' + text('8') + ')', 'S_recovered.PRECISIONINI = ' + text('11'),
                'S_recovered.TODO = ptask_recovery*', *common.public('S_recovered'),
                'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|2|1|ini_restore|precision|handler-value72|S|handler72|8|Z|R|8|11')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(shared.__file__), Path(shared.shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
