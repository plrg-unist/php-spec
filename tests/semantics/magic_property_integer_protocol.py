#!/usr/bin/env python3
"""Source-reached unconstrained MAGIC_GET integer-string conversion."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
from recorded_worker import Worker

cross, ROOT = sources.cross, sources.ROOT
CASES = {
    'reference-kept': 'review-property-magic-coerce-reference-kept29',
    'reference-drop': 'review-property-magic-coerce-reference-drop29',
    'value': 'review-property-magic-coerce-value29',
    'owned-reference': 'review-property-magic-coerce-owned-reference29',
    'weak-getter': 'review-property-magic-coerce-weak-getter29',
    'strict-getter': 'review-property-magic-coerce-strict-getter29',
}
PREFIX = get.PREFIX.split('dec $get_test_phase', 1)[0] + r'''
dec $integer_get_phase(pstate, nat, nat) : bool
def $integer_get_phase(S, 0, n) = ($property_get_plan(S) =/= eps)
def $integer_get_phase(S, 1, n) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
def $integer_get_phase(S, 2, n) = true
  -- if S.TODO = (PROPERTY_GET_COPY ppropertyget poperand) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
  -- if S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 3, n) = true
  -- if S.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
  -- if S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 4, n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
  -- if pdestructorcall.OPERATION =/= eps
def $integer_get_phase(S, 5, n) = (S.DESTRUCTION.OPERATIONS = eps)
def $integer_get_phase(S, 6, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget poperand) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
  -- if S.CURRENT = eps
  -- if S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, n_phase, n) = false -- otherwise
dec $integer_get_seek(pstate, nat, nat, nat) : pstate
def $integer_get_seek(S, n_phase, n_object, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $integer_get_seek(S, n_phase, n_object, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $integer_get_phase(S, n_phase, n_object)
def $integer_get_seek(S, n_phase, n_object, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$integer_get_phase(S, n_phase, n_object)
def $integer_get_seek(S, n_phase, n_object, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$integer_get_phase(S, n_phase, n_object)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $integer_get_seek(S, n_phase, n_object, n) = $integer_get_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, n_object, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$integer_get_phase(S, n_phase, n_object)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def seek(parent, state, phase, receiver='n_reader'):
    return [f'{state}_found = $integer_get_seek({parent}, {phase}, {receiver}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$integer_get_phase({state}, {phase}, {receiver})', *get.valid(state)]


def prepare_eval(directory, group):
    if group not in ('weak-getter', 'strict-getter'):
        return []
    ast = json.loads((directory/'frontend/0.response').read_text())['ast']
    evaluations = [statement['fields'][0] for statement in ast['program']
        if statement['node'] == 'Stmt_Expression' and statement['fields'][0]['node'] == 'Expr_Eval']
    assert len(evaluations) == 1
    literal = evaluations[0]['fields'][0]
    assert literal['node'] == 'Scalar_String'
    eval_bytes = base64.b64decode(literal['fields'][0]['bytes'])
    (directory/'eval-source.php').write_bytes(eval_bytes)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], directory/'eval-frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], directory/'eval-adapter')
        parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
            'profile': 'cli-raw-85', 'source': base64.b64encode(eval_bytes).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        (directory/'eval-program.watsup').write_text(checked['fixture']+'\n')
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
    response = '(SOURCE_ACCEPT n_eval pevalcontext_eval.BYTES program_eval)'
    return ['program_eval = '+checked['fixture'],
        'S_eval = $integer_get_seek(S_initial, 0, 0, 2048)',
        'S_eval.COMPLETION = SOURCE_PENDING',
        'S_eval.EVALCONTEXTS = pevalcontext_eval :: pevalcontext_eval_tail*',
        'n_eval = pevalcontext_eval.UNIT',
        'pevalcontext_eval.PHASE = PARSER_WAIT',
        'pevalcontext_eval.BYTES = '+cross.invoke.byte_expr(eval_bytes),
        'S_eval.TODO = (EVAL_AWAIT n_eval) :: pevalcontext_eval.TAIL',
        '$call_descriptors_valid(S_eval)',
        '$eval_response_valid(S_eval, '+response+')',
        'S_resumed = $eval_resume(S_eval, '+response+')',
        'S_resumed.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_resumed)']


def start(run, source, group, eval_checks):
    owned = group == 'owned-reference'
    line = next(i for i, row in enumerate(source.splitlines(), 1)
        if b' = $reader->value;' in row or b' = magic_integer_factory29()->value;' in row)
    return ['S_initial = '+run, '~S_initial.COMPILESTOP', *eval_checks,
        *seek('S_resumed' if eval_checks else 'S_initial', 'S_before', 0, '0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_history(S_before, ppropertyget)',
        '$property_get_valid(S_before, ppropertyget, true)',
        '$property_get_owned_source(S_before, ppropertyget)' if owned else '$property_get_source(S_before, ppropertyget)',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        *get.step('S_before', 'S_pending'),
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_reader]',
        f'$property_get_base_count(S_pending.TODO, n_reader, ppropertyget.SITE) = {int(owned)}']


def returned(group):
    reference = group != 'value'
    kept = group in ('reference-kept', 'weak-getter')
    owned = group == 'owned-reference'
    checks = [*seek('S_pending', 'S_return', 1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = '+str(2 if kept or owned else 1),
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        'pmethoddesc_get.FUNCTION.ORIGIN = ppropertyget.METHOD',
        'ppropertyget.SITE = PORIGIN n_caller_unit pcpath_caller',
        '$code_at(S_return.CODE, n_caller_unit) = (pcode_caller)',
        'pcode_caller.STRICT = '+str(group == 'weak-getter').lower(),
        'pmethoddesc_get.FUNCTION.CODE.STRICT = '+str(group == 'strict-getter').lower(),
        'ppropertyget.DECL = (ppropertyid)',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertydesc_get.TYPE =/= eps', 'ppropertydesc_get.READONLY',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        'S_return_global = $global_table_view(S_return)',
        '$lookup(S_return_global.ENV, $ptascii("returnCell")) = (n_return_cell)',
        'S_return.STORE[n_return_cell] = DEFINED pvalue_raw',
        '$string_bytes(pvalue_raw) = ($ptascii("7"))',
        '$property_get_unconstrained(S_return, S_return.RESULT)',
        '$propref_at(S_return.PROPREFS, n_return_cell) = eps',
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps']
    checks += ['S_return.RESULT = '+('REFERENCE n_return_cell' if reference else 'KNOWN pvalue_raw'),
        '$heap_owners($heap_graph(S_return), HCELL n_return_cell) = '+str(2 if reference else 1)]
    return checks


def verify(reference=True):
    return ['$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, pmethoddesc_get.FUNCTION.CODE.STRICT) = TYPEINTEGER pvalue_raw',
        '$typed_number(pvalue_raw) = (NINT 7)',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        'S_verified = '+('S_return[.STORE[n_return_cell] = DEFINED (PINT 7)]' if reference else 'S_return[.RESULT = KNOWN (PINT 7)]'),
        '$property_get_verify(S_verified, ppropertyget, S_verified.RESULT) = S_verified',
        'S_completed = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_completed.TODO = (PROPERTY_GET_COPY ppropertyget ('+('REFERENCE n_return_cell' if reference else 'KNOWN (PINT 7)')+')) :: ptask_return_tail*',
        'S_completed.RESULT = KNOWN PNULL', 'S_completed.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_completed.COMPLETION = NORMAL']


def boundaries():
    # Constructed helper inputs, not claims about source-reached constraints.
    checks = ['S_mismatched = $property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, PSTRING ($ptascii("9")), TYPEINTEGER (PSTRING ($ptascii("9"))))',
        'S_mismatched = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]']
    for name, value in [('decimal', 'PSTRING ($ptascii("7.5"))'),
                        ('float', 'PFLOAT $float_of_int(7)'), ('bool', 'PBOOL true')]:
        checks += [f'S_{name} = S_return[.RESULT = KNOWN ({value})]',
            f'S_{name}_checked = $property_get_verify_value(S_{name}, ppropertyget, ppropertydesc_get, {value}, TYPEINTEGER ({value}))',
            f'S_{name}_checked = S_{name}[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]']
    checks += ['$typed_number(PSTRING ($ptascii("7.5"))) = (NFLOAT n_decimal)',
        'S_dependent = $property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, pvalue_raw, TYPEDEPENDENT "user object string conversion")',
        'S_dependent = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        'S_other_value = $property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, pvalue_raw, TYPEVALUE (PINT 7))',
        'S_other_value = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        'S_constrained = S_return[.PROPREFS = $propref_attach(S_return.PROPREFS, n_return_cell, OBJECT_PROP_SOURCE n_reader ppropertyget.NAME ppropertyid)]',
        '~$property_get_unconstrained(S_constrained, REFERENCE n_return_cell)',
        '$property_get_verify(S_constrained, ppropertyget, S_constrained.RESULT) = S_constrained[.COMPLETION = UNSUPPORTED "magic getter typed reference sources"]',
        'S_backed = S_return[.PARAMETERBACKINGS = {FUNCTION ppropertyget.METHOD, INDEX 0, CELL n_return_cell, LINE ppropertyget.LINE, VALUE ($ptascii("7"))} :: S_return.PARAMETERBACKINGS]',
        '~$property_get_unconstrained(S_backed, REFERENCE n_return_cell)',
        '$property_get_verify(S_backed, ppropertyget, S_backed.RESULT) = S_backed[.COMPLETION = UNSUPPORTED "magic getter typed reference sources"]']
    return checks


def copied(parent, reference=True, receiver_alive=False):
    checks = [*seek(parent, 'S_copy', 2),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget poperand_copy) :: ptask_copy_tail*',
        'poperand_copy = '+('REFERENCE n_return_cell' if reference else 'KNOWN (PINT 7)'),
        'S_copy.RESULT = KNOWN PNULL', 'S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        '$property_get_valid(S_copy, ppropertyget, '+str(receiver_alive).lower()+')']
    if not receiver_alive:
        checks += ['~((HOBJECT n_reader) <- S_copy.ALLOCATIONS)',
            '$trace_slot(S_copy, S_copy.ENV, $ptascii("readerWeak")) = POBJECT n_reader_weak',
            '$weakref_get(S_copy, n_reader_weak) = PNULL']
    return checks


def receive():
    return [*get.step('S_copy', 'S_receiving'), *seek('S_receiving', 'S_received', 5),
        'S_received.TODO = ptask_copy_tail*']


def reader(parent, pending='eps'):
    return [*seek(parent, 'S_reader_dtor', 4),
        'S_reader_dtor.CURRENT = (pcallcontext_reader)',
        '$destructor_context_call(pcallcontext_reader, S_reader_dtor.CURRENT, S_reader_dtor.FRAMES) = (pdestructorcall_reader)',
        'pdestructorcall_reader.OBJECT = n_reader',
        'pdestructorcall_reader.OPERATION = (pdestructionoperation_reader)',
        'pdestructionoperation_reader.PENDING = '+pending,
        '$destructor_call_pending_valid(S_reader_dtor, pdestructorcall_reader)',
        '$eager_operation_source_guard(S_reader_dtor, pdestructionoperation_reader)',
        'S_reader_global = $global_table_view(S_reader_dtor)',
        '$trace_slot(S_reader_global, S_reader_global.ENV, $ptascii("readerWeak")) = POBJECT n_reader_weak',
        '$weakref_get(S_reader_dtor, n_reader_weak) = POBJECT n_reader',
        '$property_get_history(S_reader_dtor, ppropertyget)']


def twice(expected, weak=False):
    return [*verify(), *(boundaries() if not weak else []),
        *copied('S_return', receiver_alive=True), 'S_copy.STORE[n_return_cell] = DEFINED (PINT 7)',
        '$heap_owners($heap_graph(S_copy), HOBJECT n_reader) = 1',
        '$heap_owners($heap_graph(S_copy), HCELL n_return_cell) = 2',
        *receive(), 'S_received.RESULT = KNOWN (PINT 7)',
        '$heap_owners($heap_graph(S_received), HCELL n_return_cell) = 1',
        *seek('S_received', 'S_before_second', 0, '0'),
        '$property_get_plan(S_before_second) = (ppropertyget_second)',
        'ppropertyget_second.OBJECT = n_reader',
        'ppropertyget_second.SITE =/= ppropertyget.SITE',
        '$property_get_history(S_before_second, ppropertyget_second)',
        *seek('S_before_second', 'S_return_second', 1),
        'S_return_second.TODO = (PROPERTY_GET_RESULT ppropertyget_second) :: ptask_second_tail*',
        'S_return_second.RESULT = REFERENCE n_return_cell',
        'S_return_second.STORE[n_return_cell] = DEFINED pvalue_second',
        '$string_bytes(pvalue_second) = ($ptascii("9"))',
        '$typed_conversion_at(S_return_second, ppropertydesc_get.TYPE, pvalue_second, pmethoddesc_get.FUNCTION.CODE.STRICT) = TYPEINTEGER pvalue_second',
        'S_verified_second = $property_get_verify(S_return_second, ppropertyget_second, S_return_second.RESULT)',
        'S_verified_second = S_return_second[.STORE[n_return_cell] = DEFINED (PINT 9)]',
        '$objectprops_at(S_verified_second.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        '$propref_at(S_verified_second.PROPREFS, n_return_cell) = eps',
        '$parameter_backing_at(S_verified_second.PARAMETERBACKINGS, n_return_cell) = eps',
        *seek('S_return_second', 'S_copy_second', 2),
        'S_copy_second.TODO = (PROPERTY_GET_COPY ppropertyget_second (REFERENCE n_return_cell)) :: ptask_copy_second_tail*',
        'S_copy_second.STORE[n_return_cell] = DEFINED (PINT 9)',
        *get.step('S_copy_second', 'S_receiving_second'), *seek('S_receiving_second', 'S_received_second', 5),
        'S_received_second.TODO = ptask_copy_second_tail*', 'S_received_second.RESULT = KNOWN (PINT 9)',
        *get.finish('S_received_second', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("returnCell")) = pvalue_final',
        ('$trace_slot(S_done, S_done.ENV, $ptascii("returnCell")) = PINT 9' if weak else '$string_bytes(pvalue_final) = ($ptascii("changed"))'),
        '$trace_slot(S_done, S_done.ENV, $ptascii("'+('result' if weak else 'first')+'")) = PINT 7',
        '$trace_slot(S_done, S_done.ENV, $ptascii("'+('again' if weak else 'second')+'")) = PINT 9',
        '$trace_slot(S_done, S_done.ENV, $ptascii("getCalls")) = PINT 2']


def drop(expected, reference=True):
    return [*verify(reference), *reader('S_return'),
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, poperand_rv))',
        'poperand_rv = '+('REFERENCE n_return_cell' if reference else 'KNOWN (PINT 7)'),
        'S_reader_dtor.STORE[n_return_cell] = DEFINED '+('(PINT 7)' if reference else 'pvalue_raw'),
        '$heap_owners($heap_graph(S_reader_dtor), HCELL n_return_cell) = '+str(2 if reference else 1),
        *copied('S_reader_dtor', reference), 'S_copy.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '$typed_conversion_at(S_copy, ppropertydesc_get.TYPE, pvalue_changed, false) = TYPEREJECT',
        '$propref_at(S_copy.PROPREFS, n_return_cell) = eps',
        *receive(), 'S_received.RESULT = '+('KNOWN pvalue_changed' if reference else 'KNOWN (PINT 7)'),
        *get.finish('S_received', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("'+('read' if reference else 'result')+'")) = '+('pvalue_changed' if reference else 'PINT 7'),
        '$weakref_get(S_done, n_reader_weak) = PNULL']


def owned(expected):
    return [*verify(), *copied('S_return', receiver_alive=True),
        'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        *seek('S_copy', 'S_base', 3), 'S_base.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        'S_base.RESULT = KNOWN (PINT 7)', 'S_base.STORE[n_return_cell] = DEFINED (PINT 7)',
        '$heap_owners($heap_graph(S_base), HCELL n_return_cell) = 1',
        '$heap_owners($heap_graph(S_base), HOBJECT n_reader) = 1',
        '$property_get_base_valid(S_base, ppropertyget)',
        *reader('S_base'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
        'pdestructionoperation_reader.VALUE = KNOWN (PINT 7)',
        'S_reader_dtor.RESULT = KNOWN PNULL', 'S_reader_dtor.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED (PINT 7)',
        *seek('S_reader_dtor', 'S_received', 5), 'S_received.TODO = ptask_base_tail*',
        'S_received.RESULT = KNOWN (PINT 7)', 'S_received.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '$weakref_get(S_received, n_reader_weak) = PNULL',
        *get.finish('S_received', expected), '$trace_slot(S_done, S_done.ENV, $ptascii("result")) = PINT 7']


def strict(expected):
    message = expected.split('caught=', 1)[1].split('/prior=', 1)[0]
    quoted = cross.invoke.byte_expr(message.encode())
    return ['$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, true) = TYPEREJECT',
        '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = TYPEINTEGER pvalue_raw',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        'S_verified.COMPLETION = THROWN "TypeError" '+quoted+' ppropertyget.LINE',
        'S_verified.STORE[n_return_cell] = DEFINED pvalue_raw',
        'S_completed = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_completed.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_return_tail*',
        'S_completed.RESULT = KNOWN PNULL', 'S_completed.BASE = BASE_VALUE (KNOWN PNULL)',
        '$throwable_same_frame_continuation(S_return, S_completed, ptask_return_tail*) = S_completed',
        'S_transition = $throwable_transition(S_return, S_completed)',
        'S_transition.COMPLETION = THROWING n_type_error', 'S_transition.TODO = S_completed.TODO',
        '$get_test_message(S_transition, n_type_error, '+quoted+')',
        *reader('S_return', '(n_type_error)'),
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, REFERENCE n_return_cell))',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED pvalue_raw',
        '$get_test_message(S_reader_dtor, n_type_error, '+quoted+')',
        *seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_error_tail*',
        'S_error_copy.RESULT = KNOWN PNULL', 'S_error_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_error_copy.STORE[n_return_cell] = DEFINED (PINT 7)',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        '$get_test_message(S_error_copy, n_type_error, '+quoted+')',
        '$weakref_get(S_error_copy, n_reader_weak) = PNULL',
        *get.finish('S_error_copy', expected), '$lookup(S_done.ENV, $ptascii("result")) = eps',
        'S_done.STORE[n_return_cell] = DEFINED (PINT 7)']


def body(run, source, expected, group, eval_checks=()):
    checks = [*start(run, source, group, eval_checks), *returned(group)]
    if group in ('reference-kept', 'weak-getter'):
        return checks + twice(expected, group == 'weak-getter')
    if group in ('reference-drop', 'value'):
        return checks + drop(expected, group == 'reference-drop')
    return checks + (owned(expected) if group == 'owned-reference' else strict(expected))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-integer-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = prepare_eval(out, args.group)
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
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
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
