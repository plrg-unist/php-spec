#!/usr/bin/env python3
"""Source-reached readonly admission, saved callbacks and detached references."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from readonly_lifecycle_sources import CASES, EXPECTED
import instance_set_access_protocol as old

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $readonly_review_output(pevent*) : ptbytes
dec $readonly_review_is_output(pevent) : bool
def $readonly_review_output(eps) = eps
def $readonly_review_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $readonly_review_output(pevent*)
def $readonly_review_output(pevent :: pevent_tail*) = $readonly_review_output(pevent_tail*) -- if ~$readonly_review_is_output(pevent)
def $readonly_review_is_output(OUTPUT ptbytes) = true
def $readonly_review_is_output(pevent) = false -- otherwise
dec $readonly_review_phase(pstate,nat) : bool
def $readonly_review_phase(S,0) = $property_string_callback_candidate(S[.COMPLETION = NORMAL])
def $readonly_review_phase(S,1) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring) :: ptask_tail*
def $readonly_review_phase(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring) :: ptask_tail*
  -- if $location_slot(S,PROPERTY ppropertystring.TARGET ppropertystring.KEY) = DEFINED (PSTRING $ptascii("inner"))
def $readonly_review_phase(S,3) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING $ptascii("outer"))
def $readonly_review_phase(S,4) = true
  -- if S.TODO = (PROPERTY_STRING_RESULT ppropertystring) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING $ptascii("outer"))
def $readonly_review_phase(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = porigin_function
  -- if pcallcontext.INSTANCE = eps /\ pcallcontext.RECEIVER = eps
  -- if pcallcontext.ARGC = 1
def $readonly_review_phase(S,6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe_new :: pframe_middle :: pframe_old :: pframe_tail*
  -- if pframe_new.TODO = (STRINGIFY_RESULT n_new porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring_new) :: ptask_new_tail*
  -- if pframe_old.TODO = (STRINGIFY_RESULT n_old porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring_old) :: ptask_old_tail*
  -- if n_new =/= n_old
def $readonly_review_phase(S,n) = false -- otherwise
dec $readonly_review_terminal(pstate) : bool
def $readonly_review_terminal(S) = (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $readonly_review_seek(pstate,nat,nat) : pstate
def $readonly_review_seek(S,n_phase,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $readonly_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $readonly_review_phase(S,n_phase)
def $readonly_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$readonly_review_phase(S,n_phase)
  -- if n = 0 \/ $readonly_review_terminal(S)
def $readonly_review_seek(S,n_phase,n) = $readonly_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$readonly_review_phase(S,n_phase) /\ ~$readonly_review_terminal(S) /\ $(n > 0)
'''

def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']

def seek(parent, state, phase):
    return [f'{state}_found = $readonly_review_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$readonly_review_phase({state},{phase})', *valid(state)]

def complete(state, expected):
    encoded = '[' + ', '.join(str(c) for c in expected.encode()) + ']'
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$readonly_review_output(S_done.EVENTS) = ' + encoded, *valid('S_done')]

def reject(name, changed_state, predicate):
    state = 'S_bad_' + name
    return [f'{state} = {changed_state}', f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})', '~' + predicate.replace('STATE', state)]

def reentry(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_ready',0),
        'S_ready.TODO = (ASSIGN_ARRAY pbase z b) :: ptask_ready_tail*',
        '$property_string_capture(S_ready,pbase,z) = (ppropertystring)',
        '$property_string_record_valid(S_ready,ppropertystring)',
        '~$property_readonly_written(S_ready,ppropertystring.TARGET,ppropertystring.KEY)',
        '~$property_set_denied(S_ready,ppropertystring.TARGET,ppropertystring.KEY)',
        'S_ready.CURRENT = (pcallcontext_owner)',
        '$this_receiver(S_ready) = (ppropertystring.TARGET)',
        '$class_named(S_ready.CLASSNAMES,$ptascii("owner")) = (porigin_owner)',
        '$class_named(S_ready.CLASSNAMES,$ptascii("unrelated")) = (porigin_unrelated)',
        'pcallcontext_owner.LEXICAL_CLASS = (porigin_owner)',
        'S_global = $global_table_view(S_ready)',
        '$lookup(S_global.ENV,$ptascii("otherOwner")) = (n_other_owner_cell)',
        '$lookup(S_global.ENV,$ptascii("otherBox")) = (n_other_box_cell)',
        'S_ready.STORE[n_other_owner_cell] = DEFINED (POBJECT n_other_owner)',
        'S_ready.STORE[n_other_box_cell] = DEFINED (POBJECT n_other_box)',
        'n_other_owner =/= ppropertystring.TARGET', 'n_other_box =/= ppropertystring.OBJECT',
        '$property_readonly_desc(S_ready,n_other_owner,ppropertystring.KEY) = (ppropertydesc_other)',
        'ppropertydesc_other.ORIGIN = ppropertystring.DECL',
        '$stringable_instance(S_ready,n_other_box)',
        *seek('S_ready','S_pending',1),
        'S_pending.TODO = ptask_call :: ptask_stringify :: (PROPERTY_STRING_RESULT ppropertystring) :: ptask_pending_tail*',
        '$task_nodes(PROPERTY_STRING_RESULT ppropertystring) = [HOBJECT ppropertystring.TARGET,HOBJECT ppropertystring.OBJECT] ++ $operand_nodes(ppropertystring.RHS)']
    for name, changed in [
        ('target','ppropertystring[.TARGET = n_other_owner]'),
        ('key','ppropertystring[.KEY = $ptascii("y")]'),
        ('line','ppropertystring[.LINE = $(ppropertystring.LINE + 1)]'),
        ('rhs','ppropertystring[.RHS = VARIABLE $ptascii("wrong") ppropertystring.LINE]')]:
        task = 'PROPERTY_STRING_RESULT ' + changed
        checks += reject(name, 'S_pending[.TODO = ptask_call :: ptask_stringify :: (' + task + ') :: ptask_pending_tail*]',
                         '$call_task_valid(STATE,' + task + ')')
    task = 'PROPERTY_STRING_RESULT ppropertystring[.OBJECT = n_other_box]'
    checks += reject('receiver',
        'S_pending[.TODO = ptask_call :: ptask_stringify :: (' + task + ') :: ptask_pending_tail*]',
        '$property_string_consumer_guard(STATE,ppropertystring.OBJECT,' + task + ')')
    checks += reject('origin', 'S_pending[.ORIGIN = $origin_child((ppropertystring.SITE),[PCFIELD 1])]',
                     '$property_string_record_valid(STATE,ppropertystring)')
    checks += [*seek('S_pending','S_body',2), 'S_body.CURRENT = (pcallcontext_box)',
        'S_body.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (STRINGIFY_RESULT ppropertystring.OBJECT ppropertystring.SITE ppropertystring.LINE) :: (PROPERTY_STRING_RESULT ppropertystring) :: ptask_body_tail*',
        'S_saved = $constant_frame_scope(S_body,pframe,pframe_tail*)',
        'S_saved.CURRENT = (pcallcontext_owner)',
        '$this_receiver(S_saved) = (ppropertystring.TARGET)',
        '$property_readonly_written(S_saved,ppropertystring.TARGET,ppropertystring.KEY)',
        '$property_set_denied(S_saved,ppropertystring.TARGET,ppropertystring.KEY)',
        '$property_string_record_valid(S_saved,ppropertystring)',
        '$stringify_context_frame_valid(S_saved,pcallcontext_box,pframe)',
        '$($heap_owners($heap_graph(S_body),HOBJECT ppropertystring.TARGET) > 0)',
        '$($heap_owners($heap_graph(S_body),HOBJECT ppropertystring.OBJECT) > 0)',
        'S_wrong_scope = S_saved[.CURRENT = (pcallcontext_owner[.LEXICAL_CLASS = (porigin_unrelated)])]',
        '$heap_valid($heap_graph(S_wrong_scope))',
        '~$property_string_record_valid(S_wrong_scope,ppropertystring)',
        '~$stringify_context_frame_valid(S_wrong_scope,pcallcontext_box,pframe)']
    checks += reject('consumer',
        'S_body[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT ppropertystring.OBJECT ppropertystring.SITE ppropertystring.LINE) :: DISCARD :: ptask_body_tail*] :: pframe_tail*]',
        '$stringify_chain_valid(STATE,STATE.CURRENT,STATE.FRAMES)')
    checks += [*seek('S_body','S_returned',3),
        '$stringify_result_valid(S_returned,ppropertystring.OBJECT,ppropertystring.SITE,ppropertystring.LINE)',
        *seek('S_returned','S_store',4),
        '$property_set_denied(S_store,ppropertystring.TARGET,ppropertystring.KEY)',
        '$property_string_record_valid(S_store,ppropertystring)', *complete('S_store',expected),
        '$location_slot(S_done,PROPERTY ppropertystring.TARGET ppropertystring.KEY) = DEFINED (PSTRING $ptascii("outer"))',
        '$location_slot(S_done,PROPERTY n_other_owner ppropertystring.KEY) = UNDEFINED']
    return checks

def detached(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_body',5),
        'S_body.CURRENT = (pcallcontext)', 'pcallcontext.ARGC = 1',
        '$lookup(S_body.ENV,$ptascii("value")) = (n_cell)',
        'S_global = $global_table_view(S_body)',
        '$lookup(S_global.ENV,$ptascii("o")) = (n_owner_cell)',
        'S_body.STORE[n_owner_cell] = DEFINED (POBJECT n_owner)',
        '$objectprops_record_at(S_body.OBJECTPROPS,n_owner) = (pobjectprops)',
        '$property_slot_at(pobjectprops.SLOTS,$ptascii("box")) = (ppropertyslot)',
        'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_box))',
        '$property_readonly_desc(S_body,n_owner,$ptascii("box")) = (ppropertydesc)',
        'ppropertydesc.READONLY', 'S_body.STORE[n_cell] = DEFINED (POBJECT n_box)',
        '$propref_at(S_body.PROPREFS,n_cell) = eps',
        '$property_receiver_copy(S_body,n_owner,$ptascii("box"))',
        'S_checked = $property_reference_check(S_body,n_owner,$ptascii("box"),1)',
        'S_checked.COMPLETION = NORMAL',
        'S_target = $property_reference_target_check(S_body,n_owner,$ptascii("box"),1)',
        'S_target.COMPLETION = THROWN "Error" $ptascii("Cannot assign by reference to overloaded object") 1',
        r'S_target.STORE = S_body.STORE /\ S_target.OBJECTPROPS = S_body.OBJECTPROPS',
        'S_copy = $property_reference_copy(S_body,n_owner,$ptascii("box"))',
        'S_copy.CELL = |S_body.STORE|', 'S_copy.RESULT = REFERENCE S_copy.CELL',
        'S_copy.STORE[S_copy.CELL] = DEFINED (POBJECT n_box)',
        'S_copy.OBJECTPROPS = S_body.OBJECTPROPS', '$propref_at(S_copy.PROPREFS,S_copy.CELL) = eps',
        *valid('S_copy'),
        'ppropertyslot_alias = ppropertyslot[.STATE = PROP_VALUE (ALIAS n_cell)]',
        'S_bad_alias = S_body[.OBJECTPROPS = $objectprops_set(S_body.OBJECTPROPS,n_owner,$property_slot_set(pobjectprops.SLOTS,$ptascii("box"),ppropertyslot_alias.STATE))]',
        '$heap_valid($heap_graph(S_bad_alias))', '~$objectprops_valid(S_bad_alias,S_bad_alias.OBJECTPROPS)',
        '~$call_descriptors_valid(S_bad_alias)',
        'S_bad_source = S_bad_alias[.PROPREFS = $propref_attach(S_bad_alias.PROPREFS,n_cell,OBJECT_PROP_SOURCE n_owner $ptascii("box") ppropertydesc.ORIGIN)]',
        '$heap_valid($heap_graph(S_bad_source))',
        '~$propref_source_valid(S_bad_source,n_cell,OBJECT_PROP_SOURCE n_owner $ptascii("box") ppropertydesc.ORIGIN)',
        '~$proprefs_valid(S_bad_source)', '~$call_descriptors_valid(S_bad_source)',
        *complete('S_body',expected),
        '$location_slot(S_done,PROPERTY n_owner $ptascii("box")) = DEFINED (POBJECT n_box)',
        '$propref_at(S_done.PROPREFS,n_cell) = eps']
    return checks

def recursive(initial, expected):
    return ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_nested', 6),
        'S_nested.CURRENT = (pcallcontext_new)',
        'S_nested.FRAMES = pframe_new :: pframe_middle :: pframe_old :: pframe_tail*',
        'pframe_new.TODO = (STRINGIFY_RESULT n_new porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring_new) :: ptask_new_tail*',
        'pframe_old.TODO = (STRINGIFY_RESULT n_old porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring_old) :: ptask_old_tail*',
        'pframe_middle.CONTEXT = (pcallcontext_old)',
        'pcallcontext_new.TARGET = METHOD_TARGET n_new porigin_method',
        'pcallcontext_old.TARGET = METHOD_TARGET n_old porigin_method',
        'n_new =/= n_old',
        'ppropertystring_new.OBJECT = n_new', 'ppropertystring_old.OBJECT = n_old',
        r'ppropertystring_new.SITE = porigin_site /\ ppropertystring_old.SITE = porigin_site',
        'ppropertystring_new.TARGET = ppropertystring_old.TARGET',
        'ppropertystring_new[.OBJECT = n_old] = ppropertystring_old',
        'S_new_caller = $constant_frame_scope(S_nested,pframe_new,pframe_middle :: pframe_old :: pframe_tail*)',
        'S_old_caller = $constant_frame_scope(S_nested,pframe_old,pframe_tail*)',
        '$this_receiver(S_new_caller) = (ppropertystring_new.TARGET)',
        '$this_receiver(S_old_caller) = (ppropertystring_old.TARGET)',
        '$property_string_record_valid(S_new_caller,ppropertystring_new)',
        '$property_string_record_valid(S_old_caller,ppropertystring_old)',
        '$property_string_record_valid(S_new_caller,ppropertystring_old)',
        '$property_string_record_valid(S_old_caller,ppropertystring_new)',
        '$stringify_context_frame_valid(S_new_caller,pcallcontext_new,pframe_new)',
        '$stringify_context_frame_valid(S_old_caller,pcallcontext_old,pframe_old)',
        'pframe_bad_new = pframe_new[.TODO = (STRINGIFY_RESULT n_new porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring_old) :: ptask_new_tail*]',
        '~$stringify_context_frame_valid(S_new_caller,pcallcontext_new,pframe_bad_new)',
        'S_bad_new = S_nested[.FRAMES = pframe_bad_new :: pframe_middle :: pframe_old :: pframe_tail*]',
        '$heap_valid($heap_graph(S_bad_new))', '~$call_descriptors_valid(S_bad_new)',
        '~$stringify_chain_valid(S_bad_new,S_bad_new.CURRENT,S_bad_new.FRAMES)',
        'pframe_bad_old = pframe_old[.TODO = (STRINGIFY_RESULT n_old porigin_site z) :: (PROPERTY_STRING_RESULT ppropertystring_new) :: ptask_old_tail*]',
        '~$stringify_context_frame_valid(S_old_caller,pcallcontext_old,pframe_bad_old)',
        'S_bad_old = S_nested[.FRAMES = pframe_new :: pframe_middle :: pframe_bad_old :: pframe_tail*]',
        '$heap_valid($heap_graph(S_bad_old))', '~$call_descriptors_valid(S_bad_old)',
        '~$stringify_chain_valid(S_bad_old,S_bad_old.CURRENT,S_bad_old.FRAMES)',
        *complete('S_nested', expected),
        '$location_slot(S_done,PROPERTY ppropertystring_old.TARGET ppropertystring_old.KEY) = DEFINED (PSTRING $ptascii("outer"))']


def affected_reference(initial, expected):
    checks = old.interiors(initial, expected.encode())
    index = next(i for i, clause in enumerate(checks) if clause.startswith('S_ref = '))
    return [*checks[:16], *checks[index:index + 3],
        'S_copy = $call_location_reference(S_raw[.LOCATION = PROPERTY n_holder $ptascii("box")])',
        'S_copy.COMPLETION = NORMAL', 'S_copy.CELL = |S_raw.STORE|',
        'S_copy.RESULT = REFERENCE S_copy.CELL',
        'S_copy.STORE[S_copy.CELL] = DEFINED (POBJECT n_raw)',
        'S_copy.OBJECTPROPS = S_raw.OBJECTPROPS',
        '$propref_at(S_copy.PROPREFS,S_copy.CELL) = eps',
        '$property_slot_at(pobjectprops.SLOTS,$ptascii("box")) = (ppropertyslot)',
        'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_raw))', *old.valid('S_copy')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True,
                        choices=['reentry', 'detached', 'recursive', 'affected-reference'])
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--prepare', action='store_true', help='frontend/adapter only; no model credit')
    args = parser.parse_args()
    names = {'reentry': 'readonly-state-first-string-reentry',
             'detached': 'readonly-object-reference-detached',
             'recursive': 'readonly-string-recursive-same-destination',
             'affected-reference': 'setter-object-interior-raw-versus-alias'}
    name = names[args.group]
    source_bytes = old.CASES[name] if args.group == 'affected-reference' else CASES[name]
    expected = old.EXPECTED[name].decode() if args.group == 'affected-reference' else EXPECTED[name]
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='readonly-lifecycle-'+args.group+'-', dir=ROOT/'.tools')).resolve()
    path = out/'source.php'; path.write_bytes(source_bytes)
    report = {'passed': False, 'before': before, 'group': args.group, 'source': str(path),
              'source_sha256': sha(path), 'state_assertions_evaluated': 0,
              'mode': 'prepared; model UNRUN' if args.prepare else 'source-reached',
              'profile': cross.invoke.types.PROFILE, 'runner_mode': 'AL', 'jobs': 1}
    frontend = adapter = None
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source_bytes).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(path)).decode())+')'
        function = affected_reference if args.group == 'affected-reference' else globals()[args.group]
        clauses = ['program_source = '+checked['fixture'], *function(initial, expected)]
        fixture = out/'protocol.watsup'
        fixture.write_text((old.PREFIX if args.group == 'affected-reference' else PREFIX)+
            'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+
            '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report['prepared_assertions'] = len(clauses)
        if not args.prepare:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
                *[str(ROOT/p) for p in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report.update(passed=True, state_assertions_evaluated=len(clauses))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = cross.snapshot(args.freeze)
        report['source_unchanged'] = report['source_sha256'] == sha(path)
        report['passed'] = report['passed'] and report['before'] == report['after'] and report['source_unchanged']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['mode'] if args.prepare else report['passed'], flush=True)
    assert args.prepare or report['passed']


if __name__ == '__main__':
    main()
