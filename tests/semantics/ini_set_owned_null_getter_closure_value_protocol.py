#!/usr/bin/env python3
"""Two retained intrinsic callables survive NULL reception and callback rewrites."""
import json
import os
from pathlib import Path

import ini_set_null_getter_closure_value_protocol as getter
import ini_set_owned_null_stdclass_value_protocol as owner
import ini_set_owned_null_getter_closure_value_sources as sources

driver, common, text, b64 = getter.driver, getter.common, getter.text, getter.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = getter.MESSAGE, getter.VALUE_ERROR, getter.OPTION_ERROR
reach, returned, budget, unchanged = getter.reach, getter.returned, getter.budget, getter.unchanged
assert getter.PREFIX.startswith(getter.shared.PREFIX)
PREFIX = owner.PREFIX + getter.PREFIX[len(getter.shared.PREFIX):]


def front(state, start, explicit=False):
    values = owner.front(state, start, 'positional')
    replacements = {
        state + '.OBJECTS[n_object_' + state + '] = STDINSTANCE':
            state + '.OBJECTS[n_object_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        '$config_ini_rejected_stdclass(' + state + ',n_object_' + state + ')':
            '$config_ini_rejected_getter_closure(' + state + ',n_object_' + state + ')',
    }
    for old, new in replacements.items():
        assert values.count(old) == 1
        values[values.index(old)] = new
    return values + [
        '$compiled_read(' + state + ',porigin_' + state + '_1) = eps',
        '$closure_live_object_valid(' + state + ',n_object_' + state + ')',
        '~$config_ini_rejected_stdclass(' + state + ',n_object_' + state + ')',
        '~$config_ini_quiet_value(' + state + ',POBJECT n_object_' + state + ')',
        '$objectprops_at(' + state + '.OBJECTPROPS,n_object_' + state + ') = eps',
        ('~' if not explicit else '') + '$config_method_receiver(' + state + ',pconfigcall_' + state + ')',
        '~$pipe_site(' + state + ',pconfigcall_' + state + '.SITE)']


def error(state, start, explicit=False, strict=False, default=False):
    return [*owner.error(state, start, explicit=explicit, strict=strict, default=default),
        state + '_error.OBJECTS[n_object_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_GET']


def refusals(state):
    call, held = 'pconfigcall_' + state, 'n_owner_' + state
    return [*getter.refusals(state),
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = eps])',
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (|' + state + '.OBJECTS|)])',
        '~$config_ini_null_valid(' + state + '[.OBJECTS[' + held + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')',
        '~$config_ini_rejected_getter_closure(' + state + ',' + held + ')',
        '~$config_ini_named_stdclass_argument(' + state + ',' + call + ',2)']


def setter(start, held, old_precision, new_precision, strict=False):
    values = owner.recovery(start, held, old_precision, False)
    if new_precision != '11':
        values = [v.replace(text('11'), text(new_precision)) for v in values]
    return values + [('$config_strict' if strict else '~$config_strict') + '(S_recovery,pconfigcall_recovery)']


def partial():
    return ['S_pre_found = $test_ini_owned_std_partial_seek(S_initial,0,3000)',
        r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
        'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_std_partial(S_pre,0)',
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.OWNER = (n_owner_pre)',
        'pconfigcall_pre.SELECTION = eps', 'pconfigcall_pre.PACKS = eps', 'pconfigcall_pre.INDEX = 1',
        '~pconfigcall_pre.NAMED', 'pconfigcall_pre.SENT = [NAMED_SENT (KNOWN PNULL)]',
        '$config_pending_valid(S_pre,pconfigcall_pre,false)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
        '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner_pre]',
        '$task_nodes(CONFIG_ARGS pconfigcall_pre) = [HOBJECT n_owner_pre]',
        'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT n_owner_pre) <- S_pre.ALLOCATIONS',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
        '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_captured)',
        '$lookup(S_pre.ENV,' + text('getterKeep') + ') = (n_getter_keep)', 'S_pre.STORE[n_getter_keep] = DEFINED (POBJECT n_captured)',
        'S_pre.OBJECTS[n_captured] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_captured =/= n_owner_pre',
        '$config_ini_rejected_getter_closure(S_pre,n_captured)', '$node_children(S_pre,HOBJECT n_captured) = eps',
        '$lookup(S_pre.ENV,' + text('option') + ') = (n_option)', 'S_pre.STORE[n_option] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
        'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]


def recovery(start, held, obj, old_precision, new_precision, strict=False):
    return [*getter.getter('S_get_before', start, obj, old_precision, strict),
        *setter('S_get_before_after', held, old_precision, new_precision, strict),
        *getter.getter('S_get_final', 'S_recovered', obj, new_precision, strict),
        'S_final = $drive_steps(S_get_final_after,3000)', 'S_final.COMPLETION = NORMAL']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'owned-null-getter-default-and-explicit-true-keep-both-callables':
        values += [*front('S_default', 'S_initial'), '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', '$compiled_read(S_default,porigin_S_default_0) = (PNULL)',
            *error('S_default', 'S_default', default=True), *front('S_true', 'S_default_error', explicit=True),
            'n_owner_S_true = n_owner_S_default', 'n_object_S_true = n_object_S_default',
            '~$config_strict(S_true,pconfigcall_S_true)', *returned('S_true', '9', 'true'),
            '$lookup(S_true_return.ENV,' + text('call') + ') = (n_call_true)',
            'S_true_return.STORE[n_call_true] = DEFINED (POBJECT n_object_S_default)',
            '$lookup(S_true_return.ENV,' + text('value') + ') = (n_value_true)',
            'S_true_return.STORE[n_value_true] = DEFINED (PINT 0)',
            *error('S_true', 'S_true_resume', explicit=True), *refusals('S_true'),
            *budget('S_default'), *budget('S_true_resume'),
            *recovery('S_true_error', 'n_owner_S_default', 'n_object_S_default', '9', '11'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|I|I|99|1|0|Z|G|9|R|9|11')]
    else:
        strict = name == 'strict-owned-null-getter-ordinary-then-same-owner-explicit-weak'
        assert strict or name == 'captured-owned-null-getter-before-live-callee-becomes-value'
        values += [*partial(), *front('S', 'S_pre'), 'n_owner_S = n_owner_pre', 'n_object_S = n_captured',
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT n_captured))]]',
            'S.STORE[n_call] = DEFINED (POBJECT n_captured)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S.STORE[n_getter_keep] = DEFINED (POBJECT n_captured)', 'S.STORE[n_value] = DEFINED (PINT 0)',
            'S.STORE[n_option] = DEFINED pvalue_option', '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            'S.STORE[n_result] = DEFINED (PINT 99)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            'S.STORE[n_warnings] = DEFINED (PINT 0)', '$test_outputs(S.EVENTS) = ' + text('B|V|')]
        if strict:
            values += ['S.PRECISIONINI = ' + text('9'), '$exit_strict(S,pconfigcall_S.SITE)',
                '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                *error('S', 'S', strict=True), *front('S_weak', 'S_error', explicit=True),
                'n_owner_S_weak = n_owner_pre', 'n_object_S_weak = n_captured',
                '$exit_strict(S_weak,pconfigcall_S_weak.SITE)', '~$config_strict(S_weak,pconfigcall_S_weak)',
                *returned('S_weak', '10', 'true'), *error('S_weak', 'S_weak_resume', explicit=True),
                *budget('S_pre'), *budget('S'), *budget('S_weak_resume'),
                *recovery('S_weak_error', 'n_owner_pre', 'n_captured', '10', '12', strict=True),
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|' + OPTION_ERROR + '|99|1|0|G|0|9|M|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|Z|G|10|R|10|12')]
        else:
            values += ['S.PRECISIONINI = ' + text('7'), '~$config_strict(S,pconfigcall_S)',
                *returned('S', '8', 'false'), 'S_return.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
                'S_return.STORE[n_getter_keep] = DEFINED (POBJECT n_captured)',
                'S_return.STORE[n_call] = DEFINED (POBJECT n_captured)',
                'S_return.STORE[n_option] = DEFINED pvalue_handler_option',
                '$string_bytes(pvalue_handler_option) = (' + text('precision') + ')',
                'S_return.STORE[n_value] = DEFINED pvalue_handler_value',
                '$string_bytes(pvalue_handler_value) = (' + text('handler-value80') + ')',
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
                '$heap_count(HOBJECT n_captured,$tasks_nodes(S_return.TODO)) = 1',
                '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S_return.TODO)) = 1',
                *error('S', 'S_resume'), *refusals('S'), *budget('S_pre'), *budget('S_resume'),
                *recovery('S_error', 'n_owner_pre', 'n_captured', '8', '11'),
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|G|precision|handler-value80|8|Z|G|8|R|8|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    dependencies = (Path(__file__), Path(getter.__file__), Path(owner.__file__), Path(owner.shared.__file__),
        Path(owner.shared.shared.__file__), Path(owner.shared.shared.shared.__file__), Path(sources.__file__))
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path) for path in dependencies})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
