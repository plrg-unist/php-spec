#!/usr/bin/env python3
"""Source-reached MAGIC_GET checks on real typed-property reference cells."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer

cross, ROOT = sources.cross, sources.ROOT
CASES = {
    'exact-kept': 'review-property-magic-ref-exact-kept30',
    'conflict': 'review-property-magic-ref-conflict-repair30',
    'reject': 'review-property-magic-ref-reject-repair30',
    'owned-object': 'review-property-magic-ref-owned-object30',
    'strict': 'review-property-magic-ref-strict-reject30',
    'first-source': 'review-property-magic-ref-first-source30',
}
PREFIX = integer.PREFIX + r'''
dec $reference_get_phase(pstate, nat, nat) : bool
def $reference_get_phase(S, 0, n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("returnCell")) = eps
def $reference_get_phase(S, n_phase, n) = false -- otherwise
dec $reference_get_seek(pstate, nat, nat, nat) : pstate
def $reference_get_seek(S, n_phase, n_object, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $reference_get_seek(S, n_phase, n_object, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $reference_get_phase(S, n_phase, n_object)
def $reference_get_seek(S, n_phase, n_object, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$reference_get_phase(S, n_phase, n_object)
def $reference_get_seek(S, n_phase, n_object, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$reference_get_phase(S, n_phase, n_object)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $reference_get_seek(S, n_phase, n_object, n) = $reference_get_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, n_object, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$reference_get_phase(S, n_phase, n_object)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def start(run, source, group, eval_checks):
    owned = group == 'owned-object'
    line = next(i for i, row in enumerate(source.splitlines(), 1)
                if b' = $reader->value;' in row or b' = magic_reference_owned_factory30()->value;' in row)
    return ['S_initial = '+run, '~S_initial.COMPILESTOP', *eval_checks,
        *integer.seek('S_resumed' if eval_checks else 'S_initial', 'S_before', 0, '0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_history(S_before, ppropertyget)',
        '$property_get_owned_source(S_before, ppropertyget)' if owned else '$property_get_source(S_before, ppropertyget)',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        *get.step('S_before', 'S_pending'),
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        '$property_get_base_count(S_pending.TODO, n_reader, ppropertyget.SITE) = '+str(int(owned)),
        *integer.seek('S_pending', 'S_return', 1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        'pmethoddesc_get.FUNCTION.ORIGIN = ppropertyget.METHOD',
        'pmethoddesc_get.FUNCTION.CODE.STRICT = '+str(group == 'strict').lower(),
        'ppropertyget.SITE = PORIGIN n_caller pcpath_caller',
        '$code_at(S_return.CODE, n_caller) = (pcode_caller)', 'pcode_caller.STRICT = false',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertyget.DECL = (ppropertydesc_get.ORIGIN)', 'ppropertydesc_get.READONLY',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        'S_return_global = $global_table_view(S_return)',
        '$lookup(S_return_global.ENV, $ptascii("returnCell")) = (n_return_cell)',
        'S_return.RESULT = REFERENCE n_return_cell',
        'S_return.STORE[n_return_cell] = DEFINED pvalue_raw',
        '$propref_at(S_return.PROPREFS, n_return_cell) = (ppropref)',
        'ppropref.SOURCES = pproptypesource_first :: pproptypesource_tail*',
        '$propref_unique_sources(ppropref.SOURCES)', '$propref_sources_valid(S_return, n_return_cell, ppropref.SOURCES)',
        '$proprefs_valid(S_return)', '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps',
        '~$property_get_unconstrained(S_return, S_return.RESULT)',
        '$property_get_propref(S_return, ppropertyget, n_return_cell)',
        '$heap_owners($heap_graph(S_return), HCELL n_return_cell) = '+str(4 if group == 'first-source' else 3),
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = '+str(2 if group in ('exact-kept', 'owned-object', 'first-source') else 1)]


def source_slot(state='S_return', name='holder', field='slot'):
    return [f'$trace_slot({state}, {state}.ENV, $ptascii("{name}")) = POBJECT n_holder',
        f'pproptypesource_first = OBJECT_PROP_SOURCE n_holder $ptascii("{field}") porigin_source',
        f'$propref_descriptor({state}, pproptypesource_first) = (ppropertydesc_source)',
        f'$objectprops_at({state}.OBJECTPROPS, n_holder) = (ppropertyslot_source_all*)',
        f'$property_slot_at(ppropertyslot_source_all*, $ptascii("{field}")) = (ppropertyslot_source)',
        'ppropertyslot_source.STATE = PROP_VALUE (ALIAS n_return_cell)']


def boundaries():
    checks = ['S_missing = S_return[.PROPREFS = eps]',
        '~$property_get_propref(S_missing, ppropertyget, n_return_cell)',
        '~$propref_slots_covered(S_missing, S_missing.OBJECTPROPS)',
        'S_empty = S_return[.PROPREFS = [ppropref[.SOURCES = eps]]]',
        '~$property_get_propref(S_empty, ppropertyget, n_return_cell)',
        'S_duplicate = S_return[.PROPREFS = [ppropref[.SOURCES = pproptypesource_first :: ppropref.SOURCES]]]',
        '~$proprefs_valid(S_duplicate)', '~$property_get_propref(S_duplicate, ppropertyget, n_return_cell)',
        'S_wrong_source = S_return[.PROPREFS = [ppropref[.SOURCES = [OBJECT_PROP_SOURCE n_reader ppropertyget.NAME ppropertydesc_get.ORIGIN]]]]',
        '~$proprefs_valid(S_wrong_source)', '~$property_get_propref(S_wrong_source, ppropertyget, n_return_cell)',
        'S_backed = S_return[.PARAMETERBACKINGS = [{FUNCTION ppropertyget.METHOD, INDEX 0, CELL n_return_cell, LINE ppropertyget.LINE, VALUE ($ptascii("7"))}]]',
        '~$property_get_propref(S_backed, ppropertyget, n_return_cell)',
        '$property_get_verify(S_backed, ppropertyget, S_backed.RESULT) = S_backed[.COMPLETION = UNSUPPORTED "magic getter typed reference sources"]',
        '~$property_get_propref(S_return[.RESULT = KNOWN (PINT 7)], ppropertyget, n_return_cell)',
        '$property_get_verify(S_return, ppropertyget, KNOWN (PINT 7)) = S_return',
        '~$property_get_propref(S_return, ppropertyget[.DECL = eps], n_return_cell)']
    # Constructed helper classification boundaries keep real source state fixed.
    for tag, value in [('decimal', 'PSTRING ($ptascii("7.5"))'), ('float', 'PFLOAT $float_of_int(7)'), ('bool', 'PBOOL true')]:
        checks += [f'S_{tag} = $property_get_propref_possible(S_return, ppropertyget, ppropertydesc_get, {value}, pproptypesource_first, TYPEINTEGER ({value}))',
            f'S_{tag} = S_return[.COMPLETION = UNSUPPORTED "magic getter constrained reference coercion"]']
    return checks


def complete_identity(state='S_return', get_name='ppropertyget', cell='n_return_cell', tail='ptask_return_tail*'):
    return [f'$property_get_verify({state}, {get_name}, {state}.RESULT) = {state}',
        f'S_completed = $property_get_complete({state}, {get_name}, {state}.RESULT)',
        f'S_completed = {state}[.TODO = (PROPERTY_GET_COPY {get_name} (REFERENCE {cell})) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']


def kept(expected):
    return ['pvalue_raw = PINT 7', 'pproptypesource_tail* = eps', *source_slot(),
        '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_EXACT',
        *complete_identity(), *boundaries(),
        *integer.copied('S_return', receiver_alive=True),
        'poperand_copy = REFERENCE n_return_cell',
        'S_copy.PROPREFS = S_return.PROPREFS', *integer.receive(),
        'S_received.RESULT = KNOWN (PINT 7)',
        '$heap_owners($heap_graph(S_received), HCELL n_return_cell) = 2',
        *integer.seek('S_received', 'S_before_second', 0, '0'),
        '$property_get_plan(S_before_second) = (ppropertyget_second)',
        'ppropertyget_second.OBJECT = n_reader', 'ppropertyget_second.SITE =/= ppropertyget.SITE',
        *integer.seek('S_before_second', 'S_return_second', 1),
        'S_return_second.TODO = (PROPERTY_GET_RESULT ppropertyget_second) :: ptask_second_tail*',
        'S_return_second.RESULT = REFERENCE n_return_cell', 'S_return_second.STORE[n_return_cell] = DEFINED (PINT 9)',
        'S_return_second.PROPREFS = S_return.PROPREFS',
        '$property_get_propref(S_return_second, ppropertyget_second, n_return_cell)',
        '$property_get_verify(S_return_second, ppropertyget_second, S_return_second.RESULT) = S_return_second',
        '$objectprops_at(S_return_second.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        *get.finish('S_return_second', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("first")) = PINT 7',
        '$trace_slot(S_done, S_done.ENV, $ptascii("second")) = PINT 9',
        '$string_bytes($trace_slot(S_done, S_done.ENV, $ptascii("returnCell"))) = ($ptascii("again"))',
        '$propref_at(S_done.PROPREFS, n_return_cell) = (ppropref)',
        '$parameter_backing_at(S_done.PARAMETERBACKINGS, n_return_cell) = eps',
        '$trace_slot(S_done, S_done.ENV, $ptascii("getCalls")) = PINT 2']


def error_verify(expected, marker='caught=', state='S_return', get_name='ppropertyget', cell='n_return_cell', tail='ptask_return_tail*', suffix=''):
    message = expected.split(marker, 1)[1].split('/prior=', 1)[0].split('|1/1/1', 1)[0]
    quoted = cross.invoke.byte_expr(message.encode())
    verified, completed, transition = ('S_verified'+suffix, 'S_completed'+suffix, 'S_transition'+suffix)
    return [f'{verified} = $property_get_verify({state}, {get_name}, {state}.RESULT)',
        f'{verified} = {state}[.COMPLETION = THROWN "TypeError" {quoted} {get_name}.LINE]',
        f'{completed} = $property_get_complete({state}, {get_name}, {state}.RESULT)',
        f'{completed}.TODO = (PROPERTY_GET_COPY {get_name} (REFERENCE {cell})) :: {tail}',
        f'{completed}.RESULT = KNOWN PNULL', f'{completed}.BASE = BASE_VALUE (KNOWN PNULL)',
        f'$throwable_same_frame_continuation({state}, {completed}, {tail}) = {completed}',
        f'{transition} = $throwable_transition({state}, {completed})',
        f'{transition}.COMPLETION = THROWING n_type_error{suffix}',
        f'{transition}.TODO = {completed}.TODO', f'$get_test_message({transition}, n_type_error{suffix}, {quoted})']


def repair(expected, group):
    strict = group == 'strict'
    field = 'payload' if strict else 'slot'
    message = expected.split('caught=', 1)[1].split('/prior=', 1)[0]
    quoted = cross.invoke.byte_expr(message.encode())
    return [*source_slot(field=field), 'pproptypesource_tail* = eps',
        '$string_bytes(pvalue_raw) = ($ptascii("'+('bad' if group == 'reject' else '7')+'"))',
        '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, pmethoddesc_get.FUNCTION.CODE.STRICT) = '+('PROP_IMPOSSIBLE' if strict else 'PROP_POSSIBLE'),
        '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = '+('TYPEREJECT' if group == 'reject' else 'TYPEINTEGER pvalue_raw'),
        *error_verify(expected), *integer.reader('S_return', '(n_type_error)'),
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, REFERENCE n_return_cell))',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED pvalue_raw',
        '$propref_at(S_reader_dtor.PROPREFS, n_return_cell) = (ppropref)',
        '$heap_owners($heap_graph(S_reader_dtor), HCELL n_return_cell) = 3',
        '$get_test_message(S_reader_dtor, n_type_error, '+quoted+')',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_error_tail*',
        'S_error_copy.STORE[n_return_cell] = DEFINED (PINT 7)',
        '$propref_at(S_error_copy.PROPREFS, n_return_cell) = eps',
        '$heap_owners($heap_graph(S_error_copy), HCELL n_return_cell) = 2',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        '$get_test_message(S_error_copy, n_type_error, '+quoted+')',
        '$weakref_get(S_error_copy, n_reader_weak) = PNULL',
        *get.finish('S_error_copy', expected), '$lookup(S_done.ENV, $ptascii("result")) = eps',
        'S_done.STORE[n_return_cell] = DEFINED (PINT 7)',
        '$propref_at(S_done.PROPREFS, n_return_cell) = eps']


def owned(expected):
    return [*source_slot(field='payload'), 'pproptypesource_tail* = eps', 'pvalue_raw = POBJECT n_leaf',
        '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_EXACT',
        '$heap_owners($heap_graph(S_return), HOBJECT n_leaf) = 1', *complete_identity(),
        *integer.copied('S_return', receiver_alive=True),
        'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        *integer.seek('S_copy', 'S_base', 3), 'S_base.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        'S_base.RESULT = KNOWN (POBJECT n_leaf)',
        '$heap_owners($heap_graph(S_base), HCELL n_return_cell) = 2',
        '$heap_owners($heap_graph(S_base), HOBJECT n_leaf) = 2',
        '$propref_at(S_base.PROPREFS, n_return_cell) = (ppropref)',
        *integer.seek('S_base', 'S_reader_dtor', 4),
        'S_reader_dtor.CURRENT = (pcallcontext_reader)',
        '$destructor_context_call(pcallcontext_reader, S_reader_dtor.CURRENT, S_reader_dtor.FRAMES) = (pdestructorcall_reader)',
        'pdestructorcall_reader.OBJECT = n_reader', 'pdestructorcall_reader.OPERATION = (pdestructionoperation_reader)',
        'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
        'pdestructionoperation_reader.VALUE = KNOWN (POBJECT n_leaf)', 'pdestructionoperation_reader.PENDING = eps',
        '$eager_operation_source_guard(S_reader_dtor, pdestructionoperation_reader)',
        'S_drop_found = $reference_get_seek(S_reader_dtor, 0, n_reader, 2048)',
        r'S_drop_found.COMPLETION = NORMAL \/ S_drop_found.COMPLETION = BUDGET',
        'S_drop = S_drop_found[.COMPLETION = NORMAL]', '$reference_get_phase(S_drop, 0, n_reader)', *get.valid('S_drop'),
        '~((HCELL n_return_cell) <- S_drop.ALLOCATIONS)',
        '$propref_at(S_drop.PROPREFS, n_return_cell) = eps',
        '$heap_owners($heap_graph(S_drop), HOBJECT n_leaf) = 1',
        'S_drop_global = $global_table_view(S_drop)',
        '$trace_slot(S_drop_global, S_drop_global.ENV, $ptascii("leafWeak")) = POBJECT n_leaf_weak',
        '$weakref_get(S_drop, n_leaf_weak) = POBJECT n_leaf',
        *integer.seek('S_drop', 'S_received', 5),
        'S_received.TODO = ptask_base_tail*', 'S_received.RESULT = KNOWN (POBJECT n_leaf)',
        *get.finish('S_received', expected),
        '$weakref_get(S_done, n_leaf_weak) = PNULL', '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
        '$trace_slot(S_done, S_done.ENV, $ptascii("leafDrops")) = PINT 1']


def ordered(expected):
    return ['$string_bytes(pvalue_raw) = ($ptascii("7"))',
        'pproptypesource_tail* = [pproptypesource_second]',
        *source_slot(name='first', field='first'),
        '$trace_slot(S_return, S_return.ENV, $ptascii("second")) = POBJECT n_second',
        'pproptypesource_second = OBJECT_PROP_SOURCE n_second $ptascii("second") porigin_second',
        '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_POSSIBLE',
        *error_verify(expected, marker='first='),
        *integer.seek('S_return', 'S_before_second', 0, '0'),
        '$property_get_plan(S_before_second) = (ppropertyget_second)',
        'ppropertyget_second.SITE =/= ppropertyget.SITE',
        *integer.seek('S_before_second', 'S_return_second', 1, 'ppropertyget_second.OBJECT'),
        'S_return_second.TODO = (PROPERTY_GET_RESULT ppropertyget_second) :: ptask_second_tail*',
        'S_return_second.RESULT = REFERENCE n_second_cell',
        'S_return_second.STORE[n_second_cell] = DEFINED pvalue_second',
        '$string_bytes(pvalue_second) = ($ptascii("7"))',
        '$propref_at(S_return_second.PROPREFS, n_second_cell) = (ppropref_second)',
        'ppropref_second.SOURCES = [pproptypesource_new_second, pproptypesource_new_first]',
        '$propref_sources_valid(S_return_second, n_second_cell, ppropref_second.SOURCES)',
        '$trace_slot(S_return_second, S_return_second.ENV, $ptascii("second")) = POBJECT n_second_object',
        'pproptypesource_new_second = OBJECT_PROP_SOURCE n_second_object $ptascii("second") porigin_second',
        '$trace_slot(S_return_second, S_return_second.ENV, $ptascii("first")) = POBJECT n_first_object',
        'pproptypesource_new_first = OBJECT_PROP_SOURCE n_first_object $ptascii("first") porigin_source',
        '$property_get_propref(S_return_second, ppropertyget_second, n_second_cell)',
        *error_verify(expected, marker='second=', state='S_return_second', get_name='ppropertyget_second', cell='n_second_cell', tail='ptask_second_tail*', suffix='_second'),
        *get.finish('S_return_second', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("getCalls")) = PINT 2']


def body(run, source, expected, group, eval_checks=()):
    checks = start(run, source, group, eval_checks)
    if group == 'exact-kept':
        return checks + kept(expected)
    if group == 'owned-object':
        return checks + owned(expected)
    if group == 'first-source':
        return checks + ordered(expected)
    return checks + repair(expected, group)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-reference-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = integer.prepare_eval(out, 'strict-getter') if args.group == 'strict' else []
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(),
            *body(run, original, sources.EXPECTED[CASES[args.group]], args.group, eval_checks)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture), assertions=len(clauses))
        if not args.prepare_only:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
            assert cross.invoke.sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
            result = cross.invoke.process([str(runner), '--sl',
                *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
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
