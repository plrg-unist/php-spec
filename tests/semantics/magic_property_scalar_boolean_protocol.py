#!/usr/bin/env python3
"""Reached quiet scalar-to-bool getter verification and receiver cleanup."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer
import magic_property_float_protocol as floating
import magic_property_reference_protocol as reference

cross, ROOT = sources.cross, sources.ROOT
CASES = {group: 'review-property-magic-scalar-boolean-'+group+'44' for group in
    ('reference-kept', 'float-kept', 'reference-drop', 'value', 'owned', 'source-conflict', 'strict-getter')}
PREFIX = integer.PREFIX + r'''
dec $bool_get_return(pstate, nat) : bool
def $bool_get_return(S, n) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S_global = $global_table_view(S)
  -- if $trace_slot(S_global, S_global.ENV, $ptascii("getCalls")) = PINT n
def $bool_get_return(S, n) = false -- otherwise
dec $bool_get_seek(pstate, nat, nat) : pstate
def $bool_get_seek(S, n_read, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bool_get_seek(S, n_read, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $bool_get_return(S[.COMPLETION = NORMAL], n_read)
def $bool_get_seek(S, n_read, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$bool_get_return(S[.COMPLETION = NORMAL], n_read)
def $bool_get_seek(S, n_read, n) = $bool_get_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_read, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$bool_get_return(S[.COMPLETION = NORMAL], n_read)
  -- if $(n > 0)
'''


def later(parent, state, descriptor, tail, count):
    return [f'{state}_found = $bool_get_seek({parent}, {count}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$bool_get_return({state}, {count})', *get.valid(state),
        f'{state}.TODO = (PROPERTY_GET_RESULT {descriptor}) :: {tail}',
        f'{descriptor}.OBJECT = n_reader', f'{state}.RESULT = REFERENCE n_return_cell',
        f'$property_get_valid({state}, {descriptor}, true)', f'$property_get_tail_valid({state}, {descriptor})']


def start(run, source, group, eval_checks):
    owned = group == 'owned'
    constrained = group == 'source-conflict'
    kept = group in ('reference-kept', 'float-kept', 'source-conflict', 'owned')
    line = next(i for i, row in enumerate(source.splitlines(), 1)
        if b' = $reader->value;' in row or b' = magic_scalar_boolean_owned_factory44()->value;' in row)
    checks = ['S_initial = '+run, '~S_initial.COMPILESTOP', *eval_checks,
        *integer.seek('S_resumed' if eval_checks else 'S_initial', 'S_before', 0, '0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_history(S_before, ppropertyget)',
        '$property_get_owned_source(S_before, ppropertyget)' if owned else '$property_get_source(S_before, ppropertyget)',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        *get.step('S_before', 'S_pending'), '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        f'$property_get_base_count(S_pending.TODO, n_reader, ppropertyget.SITE) = {int(owned)}',
        *integer.seek('S_pending', 'S_return', 1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        f'pmethoddesc_get.FUNCTION.CODE.STRICT = {str(group == "strict-getter").lower()}',
        'ppropertyget.SITE = PORIGIN n_caller pcpath_caller', '$code_at(S_return.CODE, n_caller) = (pcode_caller)',
        f'pcode_caller.STRICT = {str(group == "reference-kept").lower()}',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertydesc_get.READONLY', 'ppropertydesc_get.TYPE = [(PTBRANCH ([PTBUILTIN "bool"]))]',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET', 'S_return_global = $global_table_view(S_return)',
        '$lookup(S_return_global.ENV, $ptascii("returnCell")) = (n_return_cell)',
        'S_return.STORE[n_return_cell] = DEFINED pvalue_raw',
        'S_return.RESULT = '+('KNOWN pvalue_raw' if group == 'value' else 'REFERENCE n_return_cell'),
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps',
        f'$heap_owners($heap_graph(S_return), HOBJECT n_reader) = {2 if kept else 1}',
        f'$heap_owners($heap_graph(S_return), HCELL n_return_cell) = {4 if constrained else 3 if group == "reference-kept" else 1 if group == "value" else 2}']
    if constrained:
        checks += ['$propref_at(S_return.PROPREFS, n_return_cell) = (ppropref)',
            'ppropref.SOURCES = [pproptypesource_first]', '$proprefs_valid(S_return)',
            '$property_get_propref(S_return, ppropertyget, n_return_cell)', *reference.source_slot()]
    else:
        checks += ['$propref_at(S_return.PROPREFS, n_return_cell) = eps',
            '$property_get_unconstrained(S_return, S_return.RESULT)']
    return checks


def conversion(state, descriptor, tail, raw, truth, label, byval=False):
    value = 'PBOOL '+str(truth).lower()
    rv = f'KNOWN ({value})' if byval else 'REFERENCE n_return_cell'
    update = f'.RESULT = KNOWN ({value})' if byval else f'.STORE[n_return_cell] = DEFINED ({value})'
    verified, completed = 'S_verified'+label, 'S_completed'+label
    checks = [raw,
        f'$typed_conversion_at({state}, ppropertydesc_get.TYPE, '+('pvalue_raw' if label == '' else f'pvalue_raw{label}')+', false) = TYPEBOOL '+('pvalue_raw' if label == '' else f'pvalue_raw{label}'),
        f'{verified} = $property_get_verify({state}, {descriptor}, {state}.RESULT)',
        f'{verified} = {state}[{update}]',
        f'$property_get_verify({verified}, {descriptor}, {verified}.RESULT) = {verified}',
        f'{completed} = $property_get_complete({state}, {descriptor}, {state}.RESULT)',
        f'{completed} = {verified}[.TODO = (PROPERTY_GET_COPY {descriptor} ({rv})) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
        f'$drive_steps({state}, 1) = $gc_transition_owners({state}, $destruction_transition_owners({state}, $sensitive_trace_freeze($source_exception_transition({state}, $throwable_transition({state}, {completed})))))[.COMPLETION = BUDGET]']
    return checks


def receive(state, descriptor, tail, value, label='', cells=1):
    copied, receiving, received = 'S_copy'+label, 'S_receiving'+label, 'S_received'+label
    return [*integer.seek(state, copied, 2),
        f'{copied}.TODO = (PROPERTY_GET_COPY {descriptor} poperand_copy{label}) :: {tail}',
        *get.step(copied, receiving), *integer.seek(receiving, received, 5),
        f'{received}.TODO = {tail}', f'{received}.RESULT = KNOWN ({value})',
        f'$heap_owners($heap_graph({received}), HCELL n_return_cell) = {cells}']


def guards():
    unsupported = '.COMPLETION = UNSUPPORTED "magic getter property type coercion"'
    checks = [f'$property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, pvalue_raw, TYPESTRING pvalue_raw) = S_return[{unsupported}]',
        'ppropertydesc_wrong = ppropertydesc_get[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]',
        f'$property_get_verify_value(S_return, ppropertyget, ppropertydesc_wrong, pvalue_raw, TYPEBOOL pvalue_raw) = S_return[{unsupported}]',
        'S_wrong = S_return[.RESULT = KNOWN (PINT 7)]',
        f'$property_get_verify_value(S_wrong, ppropertyget, ppropertydesc_get, pvalue_raw, TYPEBOOL pvalue_raw) = S_wrong[{unsupported}]',
        'S_invalid_rv = S_return[.RESULT = REFERENCE (|S_return.STORE|)]',
        f'$property_get_verify_value(S_invalid_rv, ppropertyget, ppropertydesc_get, pvalue_raw, TYPEBOOL pvalue_raw) = S_invalid_rv[{unsupported}]',
        'S_backed = S_return[.PARAMETERBACKINGS = [{FUNCTION ppropertyget.METHOD, INDEX 0, CELL n_return_cell, LINE ppropertyget.LINE, VALUE ($ptascii("bool"))}]]',
        f'$property_get_verify_value(S_backed, ppropertyget, ppropertydesc_get, pvalue_raw, TYPEBOOL pvalue_raw) = S_backed[{unsupported}]']
    for index, value in enumerate(('PBOOL true', 'PNULL', 'PFLOAT 9221120237041090560', 'PFLOAT 18446744073709551616', 'PINT 9223372036854775808', 'PARRAY 0', 'POBJECT n_reader', 'PSTRING_CARRIER (REQUEST_STRING (|S_return.STRINGDATA|)) ($ptascii("0"))')):
        checks += [f'S_guard{index} = S_return[.RESULT = KNOWN ({value})]',
            f'$property_get_verify_value(S_guard{index}, ppropertyget, ppropertydesc_get, {value}, TYPEBOOL ({value})) = S_guard{index}[{unsupported}]']
    checks += ['S_plain = S_return[.RESULT = KNOWN (PSTRING ([48]))]',
        '$property_get_verify(S_plain, ppropertyget, S_plain.RESULT) = S_plain[.RESULT = KNOWN (PBOOL false)]',
        'S_zero_byte = S_return[.RESULT = KNOWN (PSTRING ([48,0]))]',
        '$property_get_verify(S_zero_byte, ppropertyget, S_zero_byte.RESULT) = S_zero_byte[.RESULT = KNOWN (PBOOL true)]']
    return checks


def error(state, descriptor, tail, expected, label='caught=', suffix=''):
    message = cross.invoke.byte_expr(expected.split(label, 1)[1].split('/prior=', 1)[0].encode())
    verified, completed, transitioned = 'S_verified_error'+suffix, 'S_completed_error'+suffix, 'S_transition_error'+suffix
    return [f'{verified} = $property_get_verify({state}, {descriptor}, {state}.RESULT)',
        f'{verified} = {state}[.COMPLETION = THROWN "TypeError" {message} {descriptor}.LINE]',
        f'{completed} = $property_get_complete({state}, {descriptor}, {state}.RESULT)',
        f'{completed} = {verified}[.TODO = (PROPERTY_GET_COPY {descriptor} (REFERENCE n_return_cell)) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        f'{transitioned} = $throwable_transition({state}, {completed})',
        f'{transitioned}.COMPLETION = THROWING n_type_error',
        f'{transitioned}.TODO = {completed}.TODO', f'$get_test_message({transitioned}, n_type_error, {message})']


def kept(expected, float_values=False):
    first = 'pvalue_raw = PFLOAT 9223372036854775808' if float_values else '$string_bytes(pvalue_raw) = ($ptascii("0"))'
    checks = [*conversion('S_return', 'ppropertyget', 'ptask_return_tail*', first, False, ''),
        *([] if float_values else guards()),
        *receive('S_return', 'ppropertyget', 'ptask_copy_tail*', 'PBOOL false', cells=1 if float_values else 2)]
    for count, raw, truth in ((2, 'PFLOAT 0', False), (3, 'PFLOAT 9218868437227405312', True)) if float_values else ((2, 'string', True),):
        suffix = '_'+str(count)
        parent = 'S_received' if count == 2 else 'S_received_2'
        state, descriptor, tail = 'S_return'+suffix, 'ppropertyget'+suffix, 'ptask_return_tail'+suffix+'*'
        checks += [*later(parent, state, descriptor, tail, count), f'{state}.STORE[n_return_cell] = DEFINED pvalue_raw{suffix}',
            *conversion(state, descriptor, tail, f'pvalue_raw{suffix} = {raw}' if float_values else f'$string_bytes(pvalue_raw{suffix}) = ($ptascii("0.0"))', truth, suffix),
            *receive(state, descriptor, 'ptask_copy_tail'+suffix+'*', 'PBOOL '+str(truth).lower(), suffix, 1 if float_values else 2),
            f'{state}.STRINGDATA = S_return.STRINGDATA' if float_values else f'S_verified{suffix}.STRINGDATA = {state}.STRINGDATA']
    if not float_values:
        checks += [*later('S_received_2', 'S_return_null', 'ppropertyget_null', 'ptask_null_tail*', 3),
            'S_return_null.STORE[n_return_cell] = DEFINED PNULL',
            '$typed_conversion_at(S_return_null, ppropertydesc_get.TYPE, PNULL, false) = TYPEREJECT',
            *error('S_return_null', 'ppropertyget_null', 'ptask_null_tail*', expected, 'null='),
            *get.finish('S_return_null', expected)]
    else:
        checks += [*get.finish('S_received_3', expected)]
    return checks


def drop(expected, group):
    byval = group == 'value'
    raw = 'pvalue_raw = PINT 0' if byval else '$string_bytes(pvalue_raw) = ($ptascii("notnumeric44"))'
    value = 'PBOOL '+str(not byval).lower()
    return [*conversion('S_return', 'ppropertyget', 'ptask_return_tail*', raw, not byval, '', byval),
        *integer.reader('S_return'), '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, poperand_rv))',
        'poperand_rv = '+(f'KNOWN ({value})' if byval else 'REFERENCE n_return_cell'),
        'pdestructionoperation_reader.SOURCE = PROPERTY_GET_RESULT ppropertyget',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED '+('pvalue_raw' if byval else f'({value})'),
        *floating.copied('S_reader_dtor', not byval, value),
        'S_copy.STORE[n_return_cell] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        *integer.receive(), 'S_received.RESULT = '+(f'KNOWN ({value})' if byval else 'KNOWN pvalue_changed'),
        '$weakref_get(S_received, n_reader_weak) = PNULL', *get.finish('S_received', expected)]


def owned(expected):
    value = 'PBOOL true'
    return [*conversion('S_return', 'ppropertyget', 'ptask_return_tail*', 'pvalue_raw = PINT (-7)', True, ''),
        *floating.copied('S_return', value=value, alive=True),
        'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        *integer.seek('S_copy', 'S_base', 3), 'S_base.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        f'S_base.RESULT = KNOWN ({value})', f'S_base.STORE[n_return_cell] = DEFINED ({value})',
        '$heap_owners($heap_graph(S_base), HCELL n_return_cell) = 1', '$heap_owners($heap_graph(S_base), HOBJECT n_reader) = 1',
        *integer.reader('S_base'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
        f'pdestructionoperation_reader.VALUE = KNOWN ({value})',
        *integer.seek('S_reader_dtor', 'S_received', 5), 'S_received.TODO = ptask_base_tail*',
        f'S_received.RESULT = KNOWN ({value})', 'S_received.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))', '$weakref_get(S_received, n_reader_weak) = PNULL',
        *get.finish('S_received', expected)]


def rejected(expected, constrained=False):
    if constrained:
        first = ['$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_EXACT',
            'pvalue_raw = PBOOL false', '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
            'S_completed_exact = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
            'S_completed_exact = S_return[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            *receive('S_return', 'ppropertyget', 'ptask_copy_tail*', 'PBOOL false', cells=3),
            'S_received.PROPREFS = S_return.PROPREFS', 'S_received.OBJECTPROPS = S_return.OBJECTPROPS',
            *later('S_received', 'S_return_conflict', 'ppropertyget_conflict', 'ptask_conflict_tail*', 2),
            'S_return_conflict.STORE[n_return_cell] = DEFINED pvalue_conflict',
            '$string_bytes(pvalue_conflict) = ($ptascii("0"))',
            'S_return_conflict.PROPREFS = S_return.PROPREFS',
            '$property_get_propref(S_return_conflict, ppropertyget_conflict, n_return_cell)',
            '$propref_class(S_return_conflict, ppropertydesc_get.TYPE, pvalue_conflict, false) = PROP_POSSIBLE',
            '$typed_conversion_at(S_return_conflict, ppropertydesc_source.TYPE, pvalue_conflict, true) = TYPEVALUE pvalue_conflict',
            '$typed_conversion_at(S_return_conflict, ppropertydesc_source.TYPE, PBOOL false, true) = TYPEVALUE (PBOOL false)',
            '$property_type_name(S_return_conflict, ppropertydesc_source) = $ptascii("string|bool")']
        for value in ('PFLOAT 9221120237041090560', 'PFLOAT 18446744073709551616'):
            first += [f'$property_get_propref_possible(S_return_conflict, ppropertyget_conflict, ppropertydesc_get, {value}, pproptypesource_first, TYPEBOOL ({value})) = S_return_conflict[.COMPLETION = UNSUPPORTED "magic getter constrained reference coercion"]']
        state, descriptor, tail = 'S_return_conflict', 'ppropertyget_conflict', 'ptask_conflict_tail*'
    else:
        first = ['$string_bytes(pvalue_raw) = ($ptascii("0.0"))',
            '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, true) = TYPEREJECT']
        state, descriptor, tail = 'S_return', 'ppropertyget', 'ptask_return_tail*'
    message = cross.invoke.byte_expr(expected.split('caught=', 1)[1].split('/prior=', 1)[0].encode())
    checks = [*first, *error(state, descriptor, tail, expected), *integer.reader(state, '(n_type_error)'),
        f'pdestructionoperation_reader.SOURCE = PROPERTY_GET_RESULT {descriptor}',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED '+('pvalue_conflict' if constrained else 'pvalue_raw'),
        '$get_test_message(S_reader_dtor, n_type_error, '+message+')',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        f'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY {descriptor} (REFERENCE n_return_cell)) :: ptask_error_tail*',
        'S_error_copy.STORE[n_return_cell] = DEFINED (PBOOL true)' if not constrained else 'S_error_copy.STORE[n_return_cell] = DEFINED (PBOOL false)',
        '$propref_at(S_error_copy.PROPREFS, n_return_cell) = eps', '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        '$get_test_message(S_error_copy, n_type_error, '+message+')', '$weakref_get(S_error_copy, n_reader_weak) = PNULL',
        *get.finish('S_error_copy', expected)]
    return checks


def body(run, source, expected, group, eval_checks=()):
    checks = start(run, source, group, eval_checks)
    if group in ('reference-kept', 'float-kept'):
        return checks + kept(expected, group == 'float-kept')
    if group in ('reference-drop', 'value'):
        return checks + drop(expected, group)
    if group == 'owned':
        return checks + owned(expected)
    return checks + rejected(expected, group == 'source-conflict')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-scalar-boolean-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = integer.prepare_eval(out, 'weak-getter' if args.group == 'reference-kept' else args.group)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body(run, original, sources.EXPECTED[CASES[args.group]], args.group, eval_checks)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
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
