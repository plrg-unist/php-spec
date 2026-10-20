#!/usr/bin/env python3
"""Named reception retains the earlier owning value before option-side COW."""
import json
import os
from pathlib import Path

import ini_set_null_array_value_protocol as shared
import ini_set_named_null_array_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, error, budget = shared.reach, shared.returned, shared.error, shared.budget
PREFIX = shared.shared.PREFIX + r"""
dec $test_ini_named_array_early(pstate) : bool
def $test_ini_named_array_early(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_ini_named_array_early(S) = false -- otherwise
dec $test_ini_named_array_early_seek(pstate, nat) : pstate
def $test_ini_named_array_early_seek(S, 0) = S
def $test_ini_named_array_early_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_named_array_early(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_named_array_early_seek(S, n) = $test_ini_named_array_early_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_named_array_early(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def written(state, mixed=False):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    values = []
    for index, destination, name in ([(0, 0, None), (1, 1, 'value')] if mixed else [(0, 1, 'value'), (1, 0, 'option')]):
        suffix = '_' + state + '_' + str(index)
        values += ['$intrinsic_argument(' + state + ',' + call + '.SITE,' + str(index) + ') = ((expression' + suffix + ',false,preqbytes' + suffix + '?,porigin' + suffix + ',z' + suffix + '))',
            'preqbytes' + suffix + '? = ' + ('eps' if name is None else '(' + text(name) + ')'),
            '$config_destination(' + call + '.KIND,preqbytes' + suffix + '?,' + str(index) + ') = (' + str(destination) + ')',
            '$config_ini_named_array_argument(' + state + ',' + call + ',' + array + ',' + str(index) + ')']
    return values


def front(state, start, mixed=False):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = eps', call + '.PACKS = eps',
        call + '.INDEX = 2', call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY ' + array + '))]',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_array(' + state + ',' + array + ')',
        '$config_nodes(' + call + ') = [HARRAY ' + array + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HARRAY ' + array + ']',
        '$node_children(' + state + ',HARRAY ' + array + ') = eps', *written(state, mixed), *common.public(state)]


def refusals(state):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    return [*[v for v in shared.refusals(state) if '.NAMED = true' not in v],
        '~$config_ini_null_valid(' + state + ',' + call + '[.NAMED = false])',
        '~$config_ini_named_array_argument(' + state + ',' + call + ',' + array + ',2)',
        '~$config_ini_named_array_argument(' + state + '[.CODE = eps],' + call + ',' + array + ',0)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'reversed-and-mixed-null-array-values-return-through-true-handlers':
        values += [*front('S_literal', 'S_initial'), 'pconfigcall_S_literal.SELECTION = eps',
            'S_literal.ARRAYS[n_array_S_literal].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2473))]',
            '$compiled_read(S_literal,porigin_S_literal_0) = (PARRAY n_known)',
            '$compiled_read(S_literal,porigin_S_literal_1) = (PNULL)',
            '$($heap_count(HARRAY n_known,$pools_nodes(S_literal.POOLS)) > 0)',
            *returned('S_literal', 1, '14', 'true'), *error('S_literal', 'S_literal_resume', 'namedNullArrayLiteralCaller71'),
            *front('S_mixed', 'S_literal_error', mixed=True),
            'S_mixed.ARRAYS[n_array_S_mixed].ITEMS = eps', '$compiled_read(S_mixed,porigin_S_mixed_0) = (PNULL)',
            '$compiled_read(S_mixed,porigin_S_mixed_1) = (PARRAY n_empty)',
            *returned('S_mixed', 2, '14', 'true'), *error('S_mixed', 'S_mixed_resume', 'namedNullArrayLiteralCaller71'),
            'S_forged = $allocate_array(S_literal,$array_insert($array_empty(),KINT 0,DIRECT (PINT 2474)))',
            'S_forged.RESULT = KNOWN (PARRAY n_forged)',
            'pconfigcall_forged = pconfigcall_S_literal[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_forged))]]',
            '$config_invoke_valid(S_forged,pconfigcall_forged)', '$config_ini_rejected_array(S_forged,n_forged)',
            '~$config_ini_named_array_argument(S_forged,pconfigcall_forged,n_forged,0)',
            '$config_ini_named_array_argument(S_forged,pconfigcall_forged,n_forged,1)',
            '~$config_ini_null_valid(S_forged,pconfigcall_forged)',
            *refusals('S_literal'), *budget('S_literal'), *budget('S_mixed_resume'),
            'S_final = $drive_steps(S_mixed_error,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|2473|99|1|M|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|2|14|Z')]
    else:
        strict = name == 'strict-reversed-null-array-value-rejects-option-after-both-effects'
        assert strict or name == 'selected-reversed-null-array-value-survives-later-option-cow'
        values += ['S_early_found = $test_ini_named_array_early_seek(S_initial,3000)',
            r'S_early_found.COMPLETION = NORMAL \/ S_early_found.COMPLETION = BUDGET',
            'S_early = S_early_found[.COMPLETION = NORMAL]', '$test_ini_named_array_early(S_early)',
            'S_early.TODO = (CONFIG_ARGS pconfigcall_early) :: ptask_early*',
            'pconfigcall_early.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_captured))]',
            'pconfigcall_early.OWNER = eps', 'pconfigcall_early.PACKS = eps',
            'pconfigcall_early.INDEX = 1', 'pconfigcall_early.NAMED',
            'pconfigcall_early.SELECTION = (n_selection)',
            '$config_pending_valid(S_early,pconfigcall_early,false)', '$call_task_valid(S_early,CONFIG_ARGS pconfigcall_early)',
            '$config_nodes(pconfigcall_early) = [HARRAY n_captured]',
            '$task_nodes(CONFIG_ARGS pconfigcall_early) = [HARRAY n_captured]',
            '$lookup(S_early.ENV,' + text('arrayKeep') + ') = (n_keep)', 'S_early.STORE[n_keep] = DEFINED (PARRAY n_captured)',
            '$lookup(S_early.ENV,' + text('value') + ') = (n_value)', 'S_early.STORE[n_value] = DEFINED (PINT ' + ('0' if strict else '2487') + ')',
            '$lookup(S_early.ENV,' + text('effects') + ') = (n_effects)', 'S_early.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S_early.ENV,' + text('result') + ') = (n_result)', 'S_early.STORE[n_result] = DEFINED (PINT 99)',
            'S_early.PRECISIONINI = ' + text('6'), '$test_outputs(S_early.EVENTS) = ' + text('B|V|'), *common.public('S_early'),
            *front('S', 'S_early'),
            'pconfigcall_S = pconfigcall_early[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
            'n_array_S = n_captured', '$compiled_read(S,porigin_S_0) = eps', '$compiled_read(S,porigin_S_1) = eps',
            'S.STORE[n_effects] = DEFINED (PINT 2)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_keep] = DEFINED (PARRAY n_after_option)', 'n_after_option =/= n_captured',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S.TODO)) = 1',
            'S.ARRAYS[n_captured].ITEMS = S_early.ARRAYS[n_captured].ITEMS',
            '$test_outputs(S.EVENTS) = ' + text('B|V|O|')]
        if strict:
            values += ['S.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2491))]',
                'S.ARRAYS[n_after_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0))]',
                '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                'S.STORE[n_value] = DEFINED (PINT 0)', 'S.PRECISIONINI = ' + text('9'),
                *error('S', 'S', 'strictNamedArrayCaller71', strict=True), *budget('S_early'), *budget('S'),
                'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|' + OPTION_ERROR + '|99|2|0|constant|precision|0|0|9|Z')]
        else:
            values += ['S_early.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_captured),ENTRY (KINT 1) (DIRECT (PINT 2481))]',
                'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-named-array71'),
                '$string_carrier_valid(S_early,pvalue_captured)',
                '$entry_lookup(S.ARRAYS[n_after_option].ITEMS,KINT 0) = (DIRECT pvalue_option_array)',
                '$string_bytes(pvalue_option_array) = (' + text('option-array71') + ')',
                '~$config_strict(S,pconfigcall_S)', 'S.PRECISIONINI = ' + text('7'),
                *returned('S', 1, '8', 'false'),
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 2)',
                'S_return.STORE[n_keep] = DEFINED (PARRAY n_handler_keep)', 'n_handler_keep =/= n_captured',
                '$entry_lookup(S_return.ARRAYS[n_handler_keep].ITEMS,KINT 0) = (DIRECT pvalue_keep)',
                '$string_bytes(pvalue_keep) = (' + text('handler-array71') + ')',
                '$entry_lookup(S_return.ARRAYS[n_handler_keep].ITEMS,KINT 1) = (DIRECT (PINT 2481))',
                *error('S', 'S_resume', 'namedNullArrayCaller71'), *refusals('S'), *budget('S_early'), *budget('S_resume'),
                'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL', 'S_final.PRECISIONINI = ' + text('11'),
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|2|1|ini_restore|precision|handler-value71|handler-array71|2481|8|Z|R|8|11')]
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
