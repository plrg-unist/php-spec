#!/usr/bin/env python3
"""Denied getter lookup, lexical backing reads and original-caller history."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import magic_property_get_protocol as get

sources, cross, ROOT = get.sources, get.cross, get.ROOT
CASES = {
    'reference': 'review-property-magic-denied-private-reference27',
    'private-initial': 'review-property-magic-denied-private-initial27',
    'protected-initial': 'review-property-magic-denied-protected-initial27',
    'allowed-value': 'review-property-magic-denied-allowed-value27',
    'getter-throw': 'review-property-magic-denied-throw27',
    'returned-throw': 'review-property-magic-denied-returned-throw27',
}
# Reuse only fixture utilities, with the new sources' actual variable/class names.
def renamed(clauses):
    return [clause.replace('$ptascii("return_cell")', '$ptascii("returned")')
                  .replace('$ptascii("return_weak")', '$ptascii("leaf_weak")')
                  .replace('$ptascii("result")', '$ptascii("value")') for clause in clauses]


PREFIX = get.PREFIX.replace('$ptascii("return_cell")', '$ptascii("returned")').replace(
    'MagicGetReturnedLeaf26', 'DeniedReturnedLeaf27') + r'''
dec $denied_test_phase(pstate, nat) : bool
def $denied_test_phase(S, 100) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata_name) z) :: (DIM_FETCH z) :: ptask_tail*
  -- if S_read = $quiet_operand(S, S.RESULT)
  -- if S_read.RESULT = KNOWN (POBJECT n)
  -- if $property_resolve(S, n, $base64(text)) = PROPERTY_ACCESS ptbytes_key
  -- if $objectprops_at(S.OBJECTPROPS, n) = (ppropertyslot_all*)
  -- if $property_slot_at(ppropertyslot_all*, ptbytes_key) = (ppropertyslot)
  -- if ppropertyslot.STATE = PROP_INITIAL
def $denied_test_phase(S, 101) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $object_name(S, n) = $ptascii("Error")
def $denied_test_phase(S, 110) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata_name) z) :: (DIM_FETCH z) :: ptask_tail*
  -- if S_read = $quiet_operand(S, S.RESULT)
  -- if S_read.RESULT = KNOWN (POBJECT n)
  -- if $property_resolve(S, n, $base64(text)) = PROPERTY_ACCESS ptbytes_key
  -- if $objectprops_at(S.OBJECTPROPS, n) = (ppropertyslot_all*)
  -- if $property_slot_at(ppropertyslot_all*, ptbytes_key) = (ppropertyslot)
  -- if ppropertyslot.STATE = PROP_VALUE pitem
def $denied_test_phase(S, n) = false -- otherwise
dec $denied_test_seek(pstate, nat, nat) : pstate
def $denied_test_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $denied_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $denied_test_phase(S, n_phase)
def $denied_test_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$denied_test_phase(S, n_phase)
def $denied_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$denied_test_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $denied_test_seek(S, n_phase, n) = $denied_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$denied_test_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def seek(parent, state, phase):
    return [f'{state}_found = $denied_test_seek({parent}, {phase}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$denied_test_phase({state}, {phase})', *get.valid(state)]


def start(run, source):
    line = next(i for i, item in enumerate(source.splitlines(), 1) if b'$value = $reader->' in item)
    return ['S_initial = '+run, '~S_initial.COMPILESTOP', *get.seek('S_initial', 'S_before', 0),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_history(S_before, ppropertyget)',
        '$property_get_valid(S_before, ppropertyget, true)',
        '$lookup(S_before.ENV, $ptascii("reader")) = (n_reader_cell)',
        'S_before.STORE[n_reader_cell] = DEFINED (POBJECT n_reader)',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        'ppropertyget.DECL = eps', '~$property_get_public(S_before, n_reader, ppropertyget.NAME)',
        '$property_resolve(S_before, n_reader, ppropertyget.NAME) = PROPERTY_DENIED ppropertydesc_hidden',
        '$property_get_lookup(S_before, ppropertyget) = PROPERTY_DENIED ppropertydesc_hidden',
        'ppropertydesc_hidden.NAME = ppropertyget.NAME', '~ppropertydesc_hidden.STATIC',
        '$objectprops_at(S_before.OBJECTPROPS, n_reader) = (ppropertyslot_hidden_all*)',
        '$property_slot_at(ppropertyslot_hidden_all*, ppropertydesc_hidden.KEY) = (ppropertyslot_hidden)',
        'ppropertyslot_hidden.DECL = (ppropertydesc_hidden.ORIGIN)',
        'ppropertydesc_hidden.KEY =/= ppropertyget.NAME',
        '~$property_get_history(S_before, ppropertyget[.DECL = (ppropertydesc_hidden.ORIGIN)])',
        '~$call_task_valid(S_before, PROPERTY_GET_RESULT ppropertyget[.DECL = (ppropertydesc_hidden.ORIGIN)])',
        *get.step('S_before', 'S_pending'),
        'S_pending.TODO = ptask_call :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_read_tail*',
        'pcalltarget_get = PROPERTY_GET_TARGET n_reader ppropertyget.METHOD',
        'ptask_call = CALL_ARGS pcalltarget_get eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE',
        '$property_get_pending_call(S_pending, pcalltarget_get, ppropertyget.SITE)',
        '$call_task_valid(S_pending, ptask_call)', '$target_nodes(pcalltarget_get) = eps',
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2']


def privileged(state):
    return [f'$property_lookup_scope({state}) = (porigin_privileged)',
        f'$property_declaring_class({state}.CLASSES, ppropertydesc_hidden.ORIGIN) = (porigin_privileged)',
        f'$property_resolve({state}, n_reader, ppropertyget.NAME) = PROPERTY_ACCESS ppropertydesc_hidden.KEY',
        f'$property_get_lookup({state}, ppropertyget) = PROPERTY_DENIED ppropertydesc_hidden',
        f'$property_get_history({state}, ppropertyget)',
        f'$property_get_valid({state}, ppropertyget, true)']


def copy_alive(parent):
    return [*get.seek(parent, 'S_copy', 5),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget poperand_copy) :: ptask_copy_tail*',
        '(HOBJECT n_reader) <- S_copy.ALLOCATIONS',
        '$heap_owners($heap_graph(S_copy), HOBJECT n_reader) = 1',
        *get.receive()]


def allowed_initial(parent, suffix):
    state = 'S_allowed_'+suffix
    error = 'S_initial_error_'+suffix
    return [*seek(parent, state, 100),
        f'{state}.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_allowed_{suffix}) metadata_allowed_{suffix}) z_allowed_{suffix}) :: (DIM_FETCH z_allowed_{suffix}) :: ptask_allowed_{suffix}*',
        f'{state}.ORIGIN = (porigin_allowed_{suffix})',
        f'{state}.CURRENT = (pcallcontext_allowed_{suffix})',
        f'$property_resolve({state}, n_reader, ppropertyget.NAME) = PROPERTY_ACCESS ppropertydesc_hidden.KEY',
        f'$property_lookup_scope({state}) = $closure_source_class({state}, porigin_allowed_{suffix})',
        f'~$property_get_needed({state}, n_reader, ppropertyget.NAME)',
        f'~$property_get_needed({state}, n_reader, ppropertydesc_hidden.KEY)',
        f'$property_get_plan({state}) = eps',
        f'ppropertyget_accessible_{suffix} = ppropertyget[.SITE = porigin_allowed_{suffix}][.LINE = z_allowed_{suffix}]',
        f'$property_get_source({state}, ppropertyget_accessible_{suffix})',
        f'$property_get_lookup({state}, ppropertyget_accessible_{suffix}) = PROPERTY_ACCESS ppropertydesc_hidden.KEY',
        f'~$property_get_history({state}, ppropertyget_accessible_{suffix})',
        *seek(state, error, 101),
        f'{error}.TODO = (THROW_SEARCH n_initial_error_{suffix}) :: ptask_initial_error_{suffix}*',
        f'$get_test_message({error}, n_initial_error_{suffix}, $ptascii("Typed property ") ++ $property_declaring_name({error}.CLASSES, ppropertydesc_hidden.ORIGIN) ++ $ptascii("::$secret must not be accessed before initialization"))']


def initial(run, source, expected, protected):
    checks = [*start(run, source), 'ppropertyslot_hidden.STATE = PROP_INITIAL',
        'ppropertydesc_hidden.TYPE =/= eps',
        *get.getter_body(keep_reader=True), *privileged('S_getter'),
        '$heap_owners($heap_graph(S_getter), HOBJECT n_reader) = 2',
        *get.seek('S_getter', 'S_return', 3), 'S_return.RESULT = KNOWN pvalue_bad',
        '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
        '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
        *copy_alive('S_return'), 'S_received.RESULT = KNOWN pvalue_bad',
        *allowed_initial('S_received', 'parent')]
    if protected:
        checks += ['ppropertydesc_hidden.VISIBILITY = PROPERTY_PROTECTED',
            *allowed_initial('S_initial_error_parent', 'child'),
            'pcallcontext_allowed_parent.LEXICAL_CLASS =/= pcallcontext_allowed_child.LEXICAL_CLASS',
            *get.finish('S_initial_error_child', expected)]
    else:
        checks += ['ppropertydesc_hidden.VISIBILITY = PROPERTY_PRIVATE',
            *get.finish('S_initial_error_parent', expected)]
    return checks


def reference(run, source, expected):
    return [*start(run, source), 'ppropertyslot_hidden.STATE = PROP_VALUE (DIRECT (PINT 3))',
        'ppropertydesc_hidden.TYPE =/= eps', *get.admission(),
        *get.getter_body(), *privileged('S_getter'),
        *renamed(get.returned()), 'S_return.STORE[n_return_cell] = DEFINED pvalue_bad',
        '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
        '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
        *get.saved_admission(),
        *get.receiver_destructor('S_return'), *privileged('S_reader_dtor'),
        'pdestructionoperation_reader.SOURCE = PROPERTY_GET_RESULT ppropertyget',
        '$eager_operation_source_guard(S_reader_dtor, pdestructionoperation_reader)',
        '~$eager_operation_source_guard(S_reader_dtor, pdestructionoperation_reader[.SOURCE = PROPERTY_GET_RESULT ppropertyget[.DECL = (ppropertydesc_hidden.ORIGIN)]])',
        *get.copied(), 'poperand_copy = REFERENCE n_return_cell',
        'S_copy.STORE[n_return_cell] = DEFINED (PINT 17)',
        '$heap_owners($heap_graph(S_copy), HCELL n_return_cell) = 2',
        *get.receive(), 'S_received.RESULT = KNOWN (PINT 17)',
        '$heap_owners($heap_graph(S_received), HCELL n_return_cell) = 1',
        *get.finish('S_received', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("value")) = PINT 17',
        '$trace_slot(S_done, S_done.ENV, $ptascii("returned")) = PINT 19']


def allowed_value(parent, suffix, value):
    state = 'S_value_'+suffix
    return [*seek(parent, state, 110),
        f'{state}.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_{suffix}) metadata_{suffix}) z_{suffix}) :: (DIM_FETCH z_{suffix}) :: ptask_{suffix}*',
        f'{state}.CURRENT = (pcallcontext_{suffix})',
        f'{state}.ORIGIN = (porigin_{suffix})',
        f'S_payload_{suffix} = $quiet_operand({state}, {state}.RESULT)',
        f'S_payload_{suffix}.RESULT = KNOWN (POBJECT n_reader)',
        f'$property_resolve({state}, n_reader, $base64(text_{suffix})) = PROPERTY_ACCESS ptbytes_key_{suffix}',
        f'ptbytes_key_{suffix} =/= $base64(text_{suffix})',
        f'$property_lookup_scope({state}) = $closure_source_class({state}, porigin_{suffix})',
        f'~$property_get_needed({state}, n_reader, $base64(text_{suffix}))',
        f'~$property_get_needed({state}, n_reader, ptbytes_key_{suffix})',
        f'$property_get_plan({state}) = eps',
        *get.step(state, 'S_prepared_'+suffix),
        f'S_prepared_{suffix}.TODO = (DIM_FETCH z_{suffix}) :: ptask_{suffix}*',
        *get.step('S_prepared_'+suffix, 'S_fetching_'+suffix),
        *get.seek('S_fetching_'+suffix, 'S_read_'+suffix, 19),
        f'S_read_{suffix}.RESULT = KNOWN (PINT {value})',
        f'S_read_{suffix}.TODO = ptask_{suffix}*']


def values(run, expected):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP',
        *allowed_value('S_initial', 'parent_secret', 3),
        *allowed_value('S_read_parent_secret', 'parent_guarded', 5),
        *get.seek('S_read_parent_guarded', 'S_child_before', 0),
        '$property_get_plan(S_child_before) = (ppropertyget_child)',
        'ppropertyget_child.OBJECT = n_reader', 'ppropertyget_child.DECL = eps',
        'ppropertyget_child.NAME = $ptascii("secret")',
        '$property_effective_desc(S_child_before, n_reader, ppropertyget_child.NAME) = (ppropertydesc_parent_private)',
        'ppropertydesc_parent_private.KEY = ptbytes_key_parent_secret',
        '$property_resolve(S_child_before, n_reader, ppropertyget_child.NAME) = PROPERTY_ACCESS ppropertyget_child.NAME',
        '$property_get_lookup(S_child_before, ppropertyget_child) = PROPERTY_ACCESS ppropertyget_child.NAME',
        'S_child_before.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.LEXICAL_CLASS = (porigin_child)',
        'pcallcontext_child.LEXICAL_CLASS =/= pcallcontext_parent_secret.LEXICAL_CLASS',
        *get.seek('S_child_before', 'S_child_getter', 15),
        '$property_resolve(S_child_getter, n_reader, ppropertyget_child.NAME) = PROPERTY_ACCESS ptbytes_key_parent_secret',
        '$property_get_lookup(S_child_getter, ppropertyget_child) = PROPERTY_ACCESS ppropertyget_child.NAME',
        '$property_get_history(S_child_getter, ppropertyget_child)',
        *allowed_value('S_child_getter', 'child_guarded', 5),
        *get.seek('S_read_child_guarded', 'S_outside', 0),
        '$property_get_plan(S_outside) = (ppropertyget_outside)', 'S_outside.CURRENT = eps',
        'ppropertyget_outside.OBJECT = n_reader', 'ppropertyget_outside.DECL = eps',
        '$property_get_lookup(S_outside, ppropertyget_outside) = PROPERTY_ACCESS ppropertyget_outside.NAME',
        '$property_get_source(S_outside, ppropertyget_outside)',
        'S_mismatched_scope = S_outside[.CURRENT = (pcallcontext_child)]',
        '$property_lookup_scope(S_mismatched_scope) = (porigin_child)',
        '$closure_source_class(S_mismatched_scope, ppropertyget_outside.SITE) = eps',
        '$property_get_needed(S_mismatched_scope, n_reader, ppropertyget_outside.NAME)',
        '$property_get_history(S_mismatched_scope, ppropertyget_outside)',
        '$property_get_plan(S_mismatched_scope) = eps',
        '~$property_get_capture(S_mismatched_scope, ppropertyget_outside)',
        *get.finish('S_outside', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("get_calls")) = PINT 3']


def throwing(run, source, expected, returned):
    checks = [*start(run, source), 'ppropertyslot_hidden.STATE = PROP_VALUE (DIRECT (PINT 3))',
        *get.getter_body(), *privileged('S_getter')]
    if not returned:
        return checks + get.getter_throw(expected) + [
            *privileged('S_reader_dtor'),
            '$eager_operation_source_guard(S_reader_dtor, pdestructionoperation_reader)']
    checks += [*renamed(get.returned()), 'S_return.STORE[n_return_cell] = DEFINED (POBJECT n_old)',
        '$heap_owners($heap_graph(S_return), HOBJECT n_old) = 1',
        '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
        *get.receiver_destructor('S_return'), *privileged('S_reader_dtor'),
        '$eager_operation_source_guard(S_reader_dtor, pdestructionoperation_reader)',
        *renamed(get.returned_throw(expected)),
        '$throwable_previous_id(S_pending_copy, n_reader_error) = eps',
        '$property_get_history(S_leaf_dtor, ppropertyget)',
        '$property_get_lookup(S_leaf_dtor, ppropertyget) = PROPERTY_DENIED ppropertydesc_hidden',
        'pdestructionoperation_leaf.SOURCE = THROW_SEARCH n_reader_error']
    return checks


def body(run, source, expected, group):
    if group == 'reference': return reference(run, source, expected)
    if group in ('private-initial', 'protected-initial'):
        return initial(run, source, expected, group == 'protected-initial')
    if group == 'allowed-value': return values(run, expected)
    return throwing(run, source, expected, group == 'returned-throw')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-denied-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(),
            *body(run, original, sources.EXPECTED[CASES[args.group]], args.group)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture),
                      assertions=len(clauses))
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
