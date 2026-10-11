#!/usr/bin/env python3
"""Compact source-reached NaN bool warning, payload and cleanup checks."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer
import magic_property_scalar_boolean_protocol as boolean
import magic_property_nan_string_protocol as nan_string

cross, ROOT = sources.cross, sources.ROOT
CASES = {group: 'review-property-magic-nan-boolean-' + original + '45' for group, original in (
    ('reference-masked', 'reference-kept'), ('reference-entry', 'reference-kept'),
    ('reference-resume', 'reference-kept'), ('reference-zero', 'reference-kept'),
    ('reference-drop', 'reference-drop'), ('value', 'value'), ('owned', 'owned'),
    ('source-conflict', 'source-conflict'), ('handler-throw', 'handler-throw'),
    ('strict-getter', 'strict-getter'))}
NAN = 9221120237041090560
MESSAGE = '$ptascii("unexpected NAN value was coerced to bool")'
PREFIX = boolean.PREFIX + r'''
def $integer_get_phase(S, 7, n) = true
  -- if S.TODO = (PROPERTY_GET_BOOL_NAN ppropertyboolnan) :: ptask_tail*
  -- if ppropertyboolnan.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 9, n) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_GET_BOOL_NAN ppropertyboolnan
  -- if ppropertyboolnan.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 10, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask :: ptask_tail*
  -- if $source_operand_marker(ptask) = PROPERTY_GET_BOOL_NAN ppropertyboolnan
  -- if ppropertyboolnan.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
dec $nan_bool_resumed(pstate) : bool
def $nan_bool_resumed(S) = true
  -- if S.TODO = (PROPERTY_GET_BOOL_NAN ppropertyboolnan) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if S_global = $global_table_view(S)
  -- if $trace_slot(S_global, S_global.ENV, $ptascii("getCalls")) = PINT 2
  -- if $trace_slot(S_global, S_global.ENV, $ptascii("warnings")) = PINT 1
def $nan_bool_resumed(S) = false -- otherwise
dec $nan_bool_seek_resume(pstate, nat) : pstate
def $nan_bool_seek_resume(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nan_bool_seek_resume(S, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $nan_bool_resumed(S[.COMPLETION = NORMAL])
def $nan_bool_seek_resume(S, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$nan_bool_resumed(S[.COMPLETION = NORMAL])
def $nan_bool_seek_resume(S, n) = $nan_bool_seek_resume($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$nan_bool_resumed(S[.COMPLETION = NORMAL])
  -- if $(n > 0)
'''


def eval_group(group):
    return 'weak-getter' if group.startswith('reference-') and group != 'reference-drop' else group


def initial(run, eval_checks):
    return ['S_initial = ' + run, '~S_initial.COMPILESTOP', *eval_checks]


def start(run, source, group, eval_checks):
    count = 3 if group == 'reference-zero' else 2 if group in ('reference-entry', 'source-conflict') else 1
    lines = [i for i, row in enumerate(source.splitlines(), 1) if b' = $reader->value;' in row or b' = magic_nan_boolean_owned_reader45()->value;' in row]
    checks = [*initial(run, eval_checks),
        'S_return_found = $bool_get_seek(' + ('S_resumed' if eval_checks else 'S_initial') + f', {count}, 4096)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', f'$bool_get_return(S_return, {count})',
        *get.valid('S_return'), 'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        'n_reader = ppropertyget.OBJECT', f'ppropertyget.LINE = {lines[count-1]}',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        f'pmethoddesc_get.FUNCTION.CODE.STRICT = {str(group == "strict-getter").lower()}',
        'ppropertyget.SITE = PORIGIN n_caller pcpath_caller', '$code_at(S_return.CODE, n_caller) = (pcode_caller)',
        f'pcode_caller.STRICT = {str(group.startswith("reference-") and group != "reference-drop").lower()}',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertydesc_get.READONLY', 'ppropertydesc_get.TYPE = [(PTBRANCH ([PTBUILTIN "bool"]))]',
        'S_global = $global_table_view(S_return)', '$lookup(S_global.ENV, $ptascii("returnCell")) = (n_cell)',
        f'pvalue_raw = PFLOAT {NAN}', 'S_return.STORE[n_cell] = DEFINED pvalue_raw',
        'S_return.RESULT = ' + ('KNOWN pvalue_raw' if group == 'value' else 'REFERENCE n_cell'),
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_cell) = eps']
    if group == 'source-conflict':
        checks += ['$propref_at(S_return.PROPREFS, n_cell) = (ppropref)', 'ppropref.SOURCES = [pproptypesource_first]',
            '$proprefs_valid(S_return)', '$property_get_propref(S_return, ppropertyget, n_cell)',
            '$propref_label(S_return, pproptypesource_first) = $ptascii("property MagicNaNBooleanSource45::$slot of type float|bool")']
    else:
        checks += ['$property_get_unconstrained(S_return, S_return.RESULT)']
    return checks


def dispatch(handler=True, constrained=False):
    checks = ['$property_get_bool_nan_ready(S_return, ppropertyget)',
        '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = TYPEBOOL pvalue_raw',
        'ppropertyboolnan = {GET ppropertyget, INPUT S_return.RESULT, FLOAT ' + str(NAN) + ', SOURCES ' + ('([pproptypesource_first])' if constrained else 'eps') + ', OWNER (|S_return.FRAMES|), TAIL ptask_return_tail*}',
        'S_dispatch = $property_get_complete(S_return, ppropertyget, S_return.RESULT)']
    if handler:
        checks += ['S_return.ERRORHANDLER.CALLBACK = (pvalue_handler)', '$error_handler_eligible(S_return, 2)',
            'perrorcall = {SITE ppropertyget.SITE, LEVEL 2, MESSAGE (' + MESSAGE + '), LINE ppropertyget.LINE, EVENT DIAGNOSTIC "Warning" (' + MESSAGE + ') ppropertyget.LINE, CALLBACK pvalue_handler, TARGET eps, RESUME PROPERTY_GET_BOOL_NAN ppropertyboolnan}',
            'S_dispatch = S_return[.ERRORFATALTRACE = eps][.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$error_call_valid(S_dispatch, perrorcall)']
    else:
        checks += ['S_return.REPORTING = 0', '~$error_handler_eligible(S_return, 2)',
            'S_dispatch = S_return[.ERRORFATALTRACE = eps][.TODO = (PROPERTY_GET_BOOL_NAN ppropertyboolnan) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    return checks + ['$property_get_bool_nan_valid(S_dispatch, ppropertyboolnan)',
        '$task_nodes(PROPERTY_GET_BOOL_NAN ppropertyboolnan) = [HOBJECT n_reader] ++ $operand_nodes(S_return.RESULT)',
        '$property_get_carriers(S_dispatch.TODO, n_reader, ppropertyget.SITE) = 1',
        *nan_string.budget('S_return', 'S_dispatch')]


def callback(changed):
    return [*integer.seek('S_dispatch', 'S_handler_result', 9),
        'S_handler_result.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_return_tail*',
        'perrorcall_done.RESUME = PROPERTY_GET_BOOL_NAN ppropertyboolnan',
        'S_handler_result.RESULT = KNOWN (PBOOL true)', 'S_handler_result.ERRORHANDLER.CALLBACK = eps',
        f'S_handler_result.STORE[n_cell] = DEFINED ({changed})',
        *integer.seek('S_handler_result', 'S_nan', 7),
        'S_nan.TODO = (PROPERTY_GET_BOOL_NAN ppropertyboolnan) :: ptask_return_tail*',
        'S_nan.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)', f'S_nan.STORE[n_cell] = DEFINED ({changed})',
        '$property_get_bool_nan_valid(S_nan, ppropertyboolnan)']


def commit(state, truth, byval=False):
    value = 'PBOOL ' + str(truth).lower()
    change = '.RESULT = KNOWN (' + value + ')' if byval else '.STORE[n_cell] = DEFINED (' + value + ')][.RESULT = REFERENCE n_cell'
    operand = 'KNOWN (' + value + ')' if byval else 'REFERENCE n_cell'
    return [f'$property_get_bool_nan_decision({state}, ppropertyboolnan.INPUT) = ({str(truth).lower()})',
        f'S_committed = $property_get_bool_nan_commit({state}, ppropertyboolnan)', f'S_committed = {state}[{change}]',
        f'S_finished = $property_get_bool_nan_finish({state}, ppropertyboolnan)',
        'S_finished = S_committed[.TODO = (PROPERTY_GET_COPY ppropertyget (' + operand + ')) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *nan_string.budget(state, 'S_finished')]


def receive(state, value, cells):
    return [clause.replace('n_return_cell', 'n_cell') for clause in boolean.receive(state, 'ppropertyget', 'ptask_copy_tail*', value, cells=cells)]


def guards():
    checks = ['$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        '$property_get_complete(S_return, ppropertyget, KNOWN (PBOOL false)) = S_return[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for label, update in [('input', 'INPUT KNOWN (PINT 7)'), ('bits', 'FLOAT 18446744073709551616'), ('finite', 'FLOAT 0'),
                          ('owner', 'OWNER $(|S_dispatch.FRAMES| + 1)'), ('tail', 'TAIL eps'),
                          ('line', 'GET ppropertyget[.LINE = $(ppropertyget.LINE + 1)]')]:
        field, value = update.split(' ', 1)
        checks += [f'ppropertyboolnan_bad_{label} = ppropertyboolnan[.{field} = {value}]',
            f'S_bad_{label} = S_dispatch[.TODO = (PROPERTY_GET_BOOL_NAN ppropertyboolnan_bad_{label}) :: ptask_return_tail*]',
            f'~$property_get_bool_nan_valid(S_bad_{label}, ppropertyboolnan_bad_{label})']
    checks += ['~$property_get_bool_nan_valid(S_dispatch[.ORIGIN = (ppropertyget.METHOD)], ppropertyboolnan)',
        'S_parameter = S_dispatch[.PARAMETERBACKINGS = [{FUNCTION ppropertyget.METHOD, INDEX 0, CELL n_cell, LINE ppropertyget.LINE, VALUE ($ptascii("float"))}]]',
        '~$property_get_bool_nan_valid(S_parameter, ppropertyboolnan)']
    for index, value in enumerate(('PBOOL false', nan_string.string('0'), 'PFLOAT 18446744073709551616', 'PINT 9223372036854775808')):
        checks += [f'S_payload{index} = S_dispatch[.STORE[n_cell] = DEFINED ({value})]',
            f'$property_get_bool_nan_decision(S_payload{index}, REFERENCE n_cell) = eps',
            f'$property_get_bool_nan_finish(S_payload{index}, ppropertyboolnan) = S_payload{index}[.COMPLETION = UNSUPPORTED "magic getter NaN bool raw payload type change"]']
    return checks


def resumed(run, eval_checks):
    return [*initial(run, eval_checks),
        'S_nan_found = $nan_bool_seek_resume(' + ('S_resumed' if eval_checks else 'S_initial') + ', 4096)',
        r'S_nan_found.COMPLETION = NORMAL \/ S_nan_found.COMPLETION = BUDGET',
        'S_nan = S_nan_found[.COMPLETION = NORMAL]', '$nan_bool_resumed(S_nan)', *get.valid('S_nan'),
        'S_nan.TODO = (PROPERTY_GET_BOOL_NAN ppropertyboolnan) :: ptask_return_tail*',
        'ppropertyget = ppropertyboolnan.GET', 'n_reader = ppropertyget.OBJECT',
        'S_global = $global_table_view(S_nan)', '$lookup(S_global.ENV, $ptascii("returnCell")) = (n_cell)',
        'ppropertyboolnan.INPUT = REFERENCE n_cell', f'ppropertyboolnan.FLOAT = {NAN}', 'ppropertyboolnan.SOURCES = eps',
        'ppropertyboolnan.TAIL = ptask_return_tail*', '$property_get_bool_nan_valid(S_nan, ppropertyboolnan)',
        'S_nan.STORE[n_cell] = DEFINED (PINT (-9223372036854775808))',
        'S_nan.ERRORHANDLER.CALLBACK = (pvalue_handler)', '$string_bytes(pvalue_handler) = ($ptascii("magic_nan_boolean_kept_handler45"))',
        '$heap_owners($heap_graph(S_nan), HOBJECT n_reader) = 2', '$heap_owners($heap_graph(S_nan), HCELL n_cell) = 3',
        *commit('S_nan', False), *receive('S_nan', 'PBOOL false', 2),
        '$heap_owners($heap_graph(S_received), HOBJECT n_reader) = 1', 'S_received.STORE[n_cell] = DEFINED (PBOOL false)']


def ordinary(group):
    changed = 'PINT 7' if group == 'owned' else 'PINT 0'
    truth = group != 'reference-drop'
    checks = [*dispatch(), *callback(changed), *commit('S_nan', truth, group == 'value')]
    if group == 'owned':
        checks += [*receive('S_nan', 'PBOOL true', 1),
            'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
            'S_received.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
            'S_received.STORE[n_cell] = DEFINED (PBOOL true)',
            *nan_string.reader('S_received'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
            'pdestructionoperation_reader.VALUE = KNOWN (PBOOL true)',
            *integer.seek('S_reader_dtor', 'S_detached', 5), 'S_detached.RESULT = KNOWN (PBOOL true)',
            'S_detached.STORE[n_cell] = DEFINED (' + nan_string.string('owned45') + ')', '$weakref_get(S_detached, n_weak) = PNULL']
    else:
        raw = 'PINT 0' if group == 'value' else 'PBOOL false'
        final = 'PBOOL true' if group == 'value' else 'PINT 7'
        checks += [*nan_string.reader('S_nan'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BOOL_NAN ppropertyboolnan',
            f'S_reader_dtor.STORE[n_cell] = DEFINED ({raw})',
            *receive('S_reader_dtor', final, 1 if group == 'value' else 2), '$weakref_get(S_received, n_weak) = PNULL']
    return checks


def conflict(expected):
    message = cross.invoke.byte_expr(expected.split('caught=', 1)[1].split('/prior=', 1)[0].encode())
    return [*dispatch(constrained=True), *callback('PBOOL false'),
        'S_nan.PROPREFS = S_return.PROPREFS',
        '$typed_conversion_at(S_nan, ppropertydesc_get.TYPE, PBOOL false, true) = TYPEVALUE (PBOOL false)',
        '$property_get_bool_nan_commit(S_nan, ppropertyboolnan) = S_nan[.COMPLETION = THROWN "TypeError" (' + message + ') ppropertyget.LINE]',
        'S_finished = $property_get_bool_nan_finish(S_nan, ppropertyboolnan)',
        'S_finished = S_nan[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = THROWN "TypeError" (' + message + ') ppropertyget.LINE]',
        *nan_string.budget('S_nan', 'S_finished'),
        'ppropertyboolnan_bad_source = ppropertyboolnan[.SOURCES = eps]',
        '~$property_get_bool_nan_valid(S_nan[.TODO = (PROPERTY_GET_BOOL_NAN ppropertyboolnan_bad_source) :: ptask_return_tail*], ppropertyboolnan_bad_source)',
        *nan_string.reader('S_nan', '(n_type_error)'), '$get_test_message(S_reader_dtor, n_type_error, ' + message + ')',
        'S_reader_dtor.STORE[n_cell] = DEFINED (PBOOL false)',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        'S_error_copy.STORE[n_cell] = DEFINED (PBOOL true)', '$propref_at(S_error_copy.PROPREFS, n_cell) = eps',
        '$get_test_message(S_error_copy, n_type_error, ' + message + ')', '$throwable_previous_id(S_error_copy, n_type_error) = eps']


def throwing():
    value = nan_string.string('0')
    return [*dispatch(), *integer.seek('S_dispatch', 'S_throw', 10),
        'S_throw.TODO = (THROW_SEARCH n_warning) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_return_tail*',
        'perrorcall_throw.RESUME = PROPERTY_GET_BOOL_NAN ppropertyboolnan',
        '$get_test_message(S_throw, n_warning, $ptascii("warning45"))', f'S_throw.STORE[n_cell] = DEFINED ({value})',
        'S_discard = S_throw[.TODO = (THROW_SEARCH n_warning) :: ptask_return_tail*]',
        'S_abrupt = $property_get_bool_nan_abrupt(S_discard, ppropertyboolnan)',
        'S_abrupt = S_discard[.TODO = (THROW_SEARCH n_warning) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$error_read_discard(S_discard, PROPERTY_GET_BOOL_NAN ppropertyboolnan) = S_abrupt',
        'S_wrapper = S_abrupt[.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)]',
        '$return_discard(S_discard, ERROR_HANDLER_RESULT perrorcall_throw) = S_wrapper', *nan_string.budget('S_throw', 'S_wrapper'),
        *nan_string.reader('S_throw', '(n_warning)'), f'S_reader_dtor.STORE[n_cell] = DEFINED ({value})',
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, REFERENCE n_cell))',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.TODO = (THROW_SEARCH n_cleanup) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        '$get_test_message(S_error_copy, n_cleanup, $ptascii("cleanup45"))', '$throwable_previous_id(S_error_copy, n_cleanup) = (n_warning)',
        '$throwable_previous_id(S_error_copy, n_warning) = eps', 'S_error_copy.STORE[n_cell] = DEFINED (' + nan_string.string('throw45') + ')']


def strict(expected):
    message = cross.invoke.byte_expr(expected.split('caught=', 1)[1].split('/prior=', 1)[0].encode())
    return ['~$property_get_bool_nan_ready(S_return, ppropertyget)',
        '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, true) = TYPEREJECT',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        'S_verified = S_return[.COMPLETION = THROWN "TypeError" (' + message + ') ppropertyget.LINE]',
        'S_finished = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_finished = S_verified[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *nan_string.budget('S_return', 'S_finished'), *nan_string.reader('S_return', '(n_type_error)'),
        'S_reader_dtor.STORE[n_cell] = DEFINED pvalue_raw', '$get_test_message(S_reader_dtor, n_type_error, ' + message + ')',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.STORE[n_cell] = DEFINED (PFLOAT 9223372036854775808)',
        '$get_test_message(S_error_copy, n_type_error, ' + message + ')', '$throwable_previous_id(S_error_copy, n_type_error) = eps']


def body(run, source, expected, group, eval_checks=()):
    if group == 'reference-resume':
        return resumed(run, eval_checks)
    checks = start(run, source, group, eval_checks)
    if group == 'reference-masked':
        return checks + dispatch(handler=False) + commit('S_dispatch', True) + guards() + receive('S_dispatch', 'PBOOL true', 2)
    if group == 'reference-entry':
        return checks + dispatch() + ['S_return.REPORTING = 0', '$heap_owners($heap_graph(S_dispatch), HOBJECT n_reader) = 2', '$heap_owners($heap_graph(S_dispatch), HCELL n_cell) = 3']
    if group == 'reference-zero':
        return checks + dispatch() + callback('PFLOAT 9223372036854775808') + commit('S_nan', False) + receive('S_nan', 'PBOOL false', 2)
    if group in ('reference-drop', 'value', 'owned'):
        return checks + ordinary(group)
    if group == 'source-conflict':
        return checks + conflict(expected)
    if group == 'handler-throw':
        return checks + throwing()
    return checks + strict(expected)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-nan-boolean-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = integer.prepare_eval(out, eval_group(args.group))
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body(run, original, sources.EXPECTED[CASES[args.group]], args.group, eval_checks)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report['state_assertions'] = len(clauses)
        if not args.prepare_only:
            runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
            report['numeric_runner_sha256'] = cross.invoke.sha(runner)
            assert report['numeric_runner_sha256'] == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
            result = cross.invoke.process([str(runner), '--sl', *[str(ROOT/module) for module in before['ordered_modules']], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
