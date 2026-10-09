#!/usr/bin/env python3
"""Source-reached MAGIC_GET integer-to-float widening and source conflicts."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer
import magic_property_reference_protocol as reference

cross, ROOT = sources.cross, sources.ROOT
CASES = {
    'reference-kept': 'review-property-magic-float-reference-kept31',
    'reference-drop': 'review-property-magic-float-reference-drop31',
    'value': 'review-property-magic-float-value31',
    'owned': 'review-property-magic-float-owned31',
    'source-conflict': 'review-property-magic-float-source-conflict31',
    'source-exact': 'review-property-magic-float-source-exact31',
}
# Independent IEEE binary64 expectations, rather than the conversion's output.
F7 = 'PFLOAT 4619567317775286272'
F9 = 'PFLOAT 4621256167635550208'
FBIG = 'PFLOAT 4845873199050653696'
PREFIX = integer.PREFIX + r'''
def $integer_get_phase(S, 7, n) = true
  -- if S.CURRENT = eps
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if $trace_slot(S, S.ENV, $ptascii("first")) = PFLOAT 4619567317775286272
  -- if $trace_slot(S, S.ENV, $ptascii("returnCell")) = PINT i
  -- if $trace_slot(S, S.ENV, $ptascii("getCalls")) = PINT 1
  -- if (HOBJECT n) <- S.ALLOCATIONS
'''


def start(run, source, group):
    owned, constrained = group == 'owned', group.startswith('source-')
    strict = group not in ('value', 'source-exact')
    kept = group in ('reference-kept', 'owned', 'source-exact')
    line = next(i for i, row in enumerate(source.splitlines(), 1)
        if b' = $reader->value;' in row or b' = magic_float_owned_factory31()->value;' in row)
    checks = ['S_initial = '+run, '~S_initial.COMPILESTOP',
        *integer.seek('S_initial', 'S_before', 0, '0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_history(S_before, ppropertyget)',
        '$property_get_valid(S_before, ppropertyget, true)',
        '$property_get_owned_source(S_before, ppropertyget)' if owned else '$property_get_source(S_before, ppropertyget)',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        *get.step('S_before', 'S_pending'),
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        f'$property_get_base_count(S_pending.TODO, n_reader, ppropertyget.SITE) = {int(owned)}',
        *integer.seek('S_pending', 'S_return', 1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        'pmethoddesc_get.FUNCTION.ORIGIN = ppropertyget.METHOD',
        f'pmethoddesc_get.FUNCTION.CODE.STRICT = {str(strict).lower()}',
        'ppropertyget.SITE = PORIGIN n_caller pcpath_caller',
        '$code_at(S_return.CODE, n_caller) = (pcode_caller)', f'pcode_caller.STRICT = {str(strict).lower()}',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertyget.DECL = (ppropertydesc_get.ORIGIN)', 'ppropertydesc_get.READONLY',
        'ppropertydesc_get.TYPE = [(PTBRANCH ([PTBUILTIN "float"]))]',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        'S_return_global = $global_table_view(S_return)',
        '$lookup(S_return_global.ENV, $ptascii("returnCell")) = (n_return_cell)',
        'S_return.STORE[n_return_cell] = DEFINED pvalue_raw',
        'S_return.RESULT = '+('KNOWN pvalue_raw' if group == 'value' else 'REFERENCE n_return_cell'),
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps',
        f'$heap_owners($heap_graph(S_return), HOBJECT n_reader) = {2 if kept else 1}',
        f'$heap_owners($heap_graph(S_return), HCELL n_return_cell) = {3 if constrained else 1 if group == "value" else 2}']
    if constrained:
        checks += ['$propref_at(S_return.PROPREFS, n_return_cell) = (ppropref)',
            'ppropref.SOURCES = [pproptypesource_first]', '$proprefs_valid(S_return)',
            '$propref_unique_sources(ppropref.SOURCES)',
            '$propref_sources_valid(S_return, n_return_cell, ppropref.SOURCES)',
            '~$property_get_unconstrained(S_return, S_return.RESULT)',
            '$property_get_propref(S_return, ppropertyget, n_return_cell)', *reference.source_slot()]
    else:
        checks += ['$propref_at(S_return.PROPREFS, n_return_cell) = eps',
            '$property_get_unconstrained(S_return, S_return.RESULT)']
    return checks


def verify(reference_result=True, i=7, value=F7):
    operand = 'REFERENCE n_return_cell' if reference_result else f'KNOWN ({value})'
    changed = f'.STORE[n_return_cell] = DEFINED ({value})' if reference_result else f'.RESULT = KNOWN ({value})'
    return [f'pvalue_raw = PINT {i}',
        f'$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, pmethoddesc_get.FUNCTION.CODE.STRICT) = TYPEVALUE ({value})',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        f'S_verified = S_return[{changed}]',
        '$property_get_verify(S_verified, ppropertyget, S_verified.RESULT) = S_verified',
        '$heap_owners($heap_graph(S_verified), HCELL n_return_cell) = '+str(2 if reference_result else 1),
        'S_verified.PROPREFS = S_return.PROPREFS',
        'S_completed = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        f'S_completed = S_verified[.TODO = (PROPERTY_GET_COPY ppropertyget ({operand})) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']


def boundaries():
    checks = []
    for tag, original, converted in [('bits', 'PINT 7', F9), ('original', 'PINT 9', F9)]:
        checks += [f'S_bad_{tag} = $property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, {original}, TYPEVALUE ({converted}))',
            f'S_bad_{tag} = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]']
    for tag, original in [('string', 'PSTRING ($ptascii("7"))'), ('bool', 'PBOOL true')]:
        converted = F7 if tag == 'string' else 'PFLOAT 4607182418800017408'
        checks += [f'S_{tag} = S_return[.RESULT = KNOWN ({original})]',
            f'$typed_conversion_at(S_{tag}, ppropertydesc_get.TYPE, {original}, false) = TYPEVALUE ({converted})',
            f'$property_get_verify_value(S_{tag}, ppropertyget, ppropertydesc_get, {original}, TYPEVALUE ({converted})) = S_{tag}[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]']
    return checks + ['S_wrong_rv = S_return[.RESULT = KNOWN (PINT 9)]',
        f'$property_get_verify_value(S_wrong_rv, ppropertyget, ppropertydesc_get, PINT 7, TYPEVALUE ({F7})) = S_wrong_rv[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        'S_backed = S_return[.PARAMETERBACKINGS = [{FUNCTION ppropertyget.METHOD, INDEX 0, CELL n_return_cell, LINE ppropertyget.LINE, VALUE ($ptascii("7"))}]]',
        '~$property_get_unconstrained(S_backed, S_backed.RESULT)',
        f'$property_get_verify_value(S_backed, ppropertyget, ppropertydesc_get, PINT 7, TYPEVALUE ({F7})) = S_backed[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        '$property_get_verify(S_backed, ppropertyget, S_backed.RESULT) = S_backed[.COMPLETION = UNSUPPORTED "magic getter typed reference sources"]']


def copied(parent, reference_result=True, value=F7, alive=False):
    return [*integer.seek(parent, 'S_copy', 2),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget poperand_copy) :: ptask_copy_tail*',
        'poperand_copy = '+('REFERENCE n_return_cell' if reference_result else f'KNOWN ({value})'),
        'S_copy.RESULT = KNOWN PNULL', 'S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        f'$property_get_valid(S_copy, ppropertyget, {str(alive).lower()})']


def twice(expected, constrained=False):
    checks = [f'pvalue_raw = {F7}', '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return'] if constrained else verify()+boundaries()
    checks += [*copied('S_return', alive=True), *integer.receive(),
        f'S_received.RESULT = KNOWN ({F7})',
        f'$heap_owners($heap_graph(S_received), HCELL n_return_cell) = {2 if constrained else 1}',
        *integer.seek('S_received', 'S_written', 7),
        'S_written.STORE[n_return_cell] = DEFINED (PINT '+('19' if constrained else '9')+')',
        '$objectprops_at(S_written.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        '$propref_at(S_written.PROPREFS, n_return_cell) = '+('(ppropref)' if constrained else 'eps'),
        *integer.seek('S_written', 'S_before_second', 0, '0'),
        '$property_get_plan(S_before_second) = (ppropertyget_second)',
        'ppropertyget_second.OBJECT = n_reader', 'ppropertyget_second.SITE =/= ppropertyget.SITE',
        *integer.seek('S_before_second', 'S_return_second', 1),
        'S_return_second.TODO = (PROPERTY_GET_RESULT ppropertyget_second) :: ptask_second_tail*',
        'S_return_second.RESULT = REFERENCE n_return_cell',
        'S_return_second.STORE[n_return_cell] = DEFINED ('+(F9 if constrained else 'PINT 9')+')',
        'S_verified_second = $property_get_verify(S_return_second, ppropertyget_second, S_return_second.RESULT)',
        'S_verified_second = '+('S_return_second' if constrained else f'S_return_second[.STORE[n_return_cell] = DEFINED ({F9})]'),
        '$propref_at(S_verified_second.PROPREFS, n_return_cell) = '+('(ppropref)' if constrained else 'eps'),
        '$parameter_backing_at(S_verified_second.PARAMETERBACKINGS, n_return_cell) = eps',
        *integer.seek('S_return_second', 'S_copy_second', 2),
        'S_copy_second.TODO = (PROPERTY_GET_COPY ppropertyget_second (REFERENCE n_return_cell)) :: ptask_copy_second_tail*',
        *get.step('S_copy_second', 'S_receiving_second'), *integer.seek('S_receiving_second', 'S_received_second', 5),
        'S_received_second.TODO = ptask_copy_second_tail*', f'S_received_second.RESULT = KNOWN ({F9})']
    if constrained:
        checks += [*integer.seek('S_received_second', 'S_before_third', 0, '0'),
            '$property_get_plan(S_before_third) = (ppropertyget_third)',
            'ppropertyget_third.OBJECT = n_reader',
            *integer.seek('S_before_third', 'S_return_third', 1),
            'S_return_third.TODO = (PROPERTY_GET_RESULT ppropertyget_third) :: ptask_third_tail*',
            'S_return_third.RESULT = REFERENCE n_return_cell', 'S_return_third.STORE[n_return_cell] = DEFINED (PINT 19)',
            '$propref_at(S_return_third.PROPREFS, n_return_cell) = (ppropref)',
            *error_verify(expected, 'S_return_third', 'ppropertyget_third', 'PINT 19', 'ptask_third_tail*'),
            *get.finish('S_return_third', expected), 'S_done.STORE[n_return_cell] = DEFINED (PINT 19)',
            '$propref_at(S_done.PROPREFS, n_return_cell) = (ppropref)']
    else:
        checks += [*get.finish('S_received_second', expected),
            '$trace_slot(S_done, S_done.ENV, $ptascii("returnCell")) = pvalue_changed',
            '$string_bytes(pvalue_changed) = ($ptascii("changed"))']
    return checks + [f'$trace_slot(S_done, S_done.ENV, $ptascii("first")) = {F7}',
        f'$trace_slot(S_done, S_done.ENV, $ptascii("second")) = {F9}',
        '$trace_slot(S_done, S_done.ENV, $ptascii("getCalls")) = PINT '+('3' if constrained else '2')]


def drop(expected, ref=True):
    return [*verify(ref), *integer.reader('S_return'),
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, poperand_rv))',
        'poperand_rv = '+('REFERENCE n_return_cell' if ref else f'KNOWN ({F7})'),
        'S_reader_dtor.STORE[n_return_cell] = DEFINED ('+(F7 if ref else 'PINT 7')+')',
        'pdestructionoperation_reader.SOURCE = PROPERTY_GET_RESULT ppropertyget',
        *copied('S_reader_dtor', ref), 'S_copy.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '~((HOBJECT n_reader) <- S_copy.ALLOCATIONS)', *integer.receive(),
        'S_received.RESULT = '+('KNOWN pvalue_changed' if ref else f'KNOWN ({F7})'),
        *get.finish('S_received', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("read")) = '+('pvalue_changed' if ref else F7),
        '$weakref_get(S_done, n_reader_weak) = PNULL']


def owned(expected):
    return [*verify(i=9007199254740993, value=FBIG), *copied('S_return', value=FBIG, alive=True),
        'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        *integer.seek('S_copy', 'S_base', 3), 'S_base.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        f'S_base.RESULT = KNOWN ({FBIG})', f'S_base.STORE[n_return_cell] = DEFINED ({FBIG})',
        '$heap_owners($heap_graph(S_base), HCELL n_return_cell) = 1',
        '$heap_owners($heap_graph(S_base), HOBJECT n_reader) = 1',
        '$property_get_base_valid(S_base, ppropertyget)',
        *integer.reader('S_base'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
        f'pdestructionoperation_reader.VALUE = KNOWN ({FBIG})',
        f'S_reader_dtor.STORE[n_return_cell] = DEFINED ({FBIG})',
        *integer.seek('S_reader_dtor', 'S_received', 5), 'S_received.TODO = ptask_base_tail*',
        f'S_received.RESULT = KNOWN ({FBIG})', 'S_received.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '$weakref_get(S_received, n_reader_weak) = PNULL',
        *get.finish('S_received', expected), f'$trace_slot(S_done, S_done.ENV, $ptascii("read")) = {FBIG}']


def error_verify(expected, state='S_return', descriptor='ppropertyget', original='pvalue_raw', tail='ptask_return_tail*'):
    message = cross.invoke.byte_expr(expected.split('caught=', 1)[1].split('/prior=', 1)[0].encode())
    return [f'$propref_class({state}, ppropertydesc_get.TYPE, {original}, pmethoddesc_get.FUNCTION.CODE.STRICT) = PROP_POSSIBLE',
        f'S_verified_error = $property_get_verify({state}, {descriptor}, {state}.RESULT)',
        f'S_verified_error = {state}[.COMPLETION = THROWN "TypeError" {message} {descriptor}.LINE]',
        f'S_completed_error = $property_get_complete({state}, {descriptor}, {state}.RESULT)',
        f'S_completed_error.TODO = (PROPERTY_GET_COPY {descriptor} (REFERENCE n_return_cell)) :: {tail}',
        'S_completed_error.RESULT = KNOWN PNULL', 'S_completed_error.BASE = BASE_VALUE (KNOWN PNULL)',
        f'$throwable_same_frame_continuation({state}, S_completed_error, {tail}) = S_completed_error',
        f'S_transition_error = $throwable_transition({state}, S_completed_error)',
        'S_transition_error.COMPLETION = THROWING n_type_error',
        'S_transition_error.TODO = S_completed_error.TODO',
        '$get_test_message(S_transition_error, n_type_error, '+message+')']


def conflict(expected):
    message = cross.invoke.byte_expr(expected.split('caught=', 1)[1].split('/prior=', 1)[0].encode())
    return ['pvalue_raw = PINT 7',
        f'$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, true) = TYPEVALUE ({F7})',
        f'$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = TYPEVALUE ({F7})',
        f'$property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, pvalue_raw, TYPEVALUE ({F7})) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        *error_verify(expected), *integer.reader('S_return', '(n_type_error)'),
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, REFERENCE n_return_cell))',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED (PINT 7)',
        '$propref_at(S_reader_dtor.PROPREFS, n_return_cell) = (ppropref)',
        '$get_test_message(S_reader_dtor, n_type_error, '+message+')',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_error_tail*',
        f'S_error_copy.STORE[n_return_cell] = DEFINED ({F7})',
        '$propref_at(S_error_copy.PROPREFS, n_return_cell) = eps',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        '$get_test_message(S_error_copy, n_type_error, '+message+')',
        '$weakref_get(S_error_copy, n_reader_weak) = PNULL',
        *get.finish('S_error_copy', expected), '$lookup(S_done.ENV, $ptascii("result")) = eps',
        f'S_done.STORE[n_return_cell] = DEFINED ({F7})', '$propref_at(S_done.PROPREFS, n_return_cell) = eps']


def body(run, source, expected, group):
    checks = start(run, source, group)
    if group in ('reference-kept', 'source-exact'):
        return checks + twice(expected, group == 'source-exact')
    if group in ('reference-drop', 'value'):
        return checks + drop(expected, group == 'reference-drop')
    return checks + (owned(expected) if group == 'owned' else conflict(expected))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-float-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body(run, original, sources.EXPECTED[CASES[args.group]], args.group)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report['state_assertions'] = len(clauses)
        if not args.prepare_only:
            runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
            report['numeric_runner_sha256'] = cross.invoke.sha(runner)
            assert report['numeric_runner_sha256'] == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
            modules = before['ordered_modules']
            result = cross.invoke.process([str(runner), '--sl', *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
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
