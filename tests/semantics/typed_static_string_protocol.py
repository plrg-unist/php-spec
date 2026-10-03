#!/usr/bin/env python3
"""Source-reached typed static casts preserve operand owners and paired cleanup."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from recorded_worker import Worker
from typed_static_string_assignment import CASES, REQUEST_CASES, initial_fixture, request_facts

ROOT = Path(__file__).resolve().parents[2]
SOURCES = dict(CASES)
STAGES = ['temporary-owner', 'borrowed-cv-owner', 'retained-cv-owner',
          'returned-reference-owner', 'returned-reference-payload',
          'private-self-context', 'nested-cast', 'callback-throw-finally']
PREFIX = r'''
dec $static_protocol_phase(pstate,nat) : bool
def $static_protocol_phase(S,0) = $static_string_callback_candidate(S[.COMPLETION = NORMAL])
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $static_protocol_phase(S,1) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*
def $static_protocol_phase(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*
  -- if pcallcontext.CALLSITE = (pstaticstring.SITE)
def $static_protocol_phase(S,3) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $static_protocol_phase(S,4) = true
  -- if S.TODO = (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $static_protocol_phase(S,5) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: (STRINGIFY_RESULT n porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*
def $static_protocol_phase(S,7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe_inner :: pframe_outer :: pframe_tail*
  -- if pframe_inner.TODO = (STRINGIFY_RESULT n_inner porigin_inner z_inner) :: (STATIC_STRING_RESULT pstaticstring_inner) :: (STATIC_STRING_CAPTURE pstaticstring_inner) :: ptask_inner*
  -- if pframe_outer.TODO = (STRINGIFY_RESULT n_outer porigin_outer z_outer) :: (STATIC_STRING_RESULT pstaticstring_outer) :: (STATIC_STRING_CAPTURE pstaticstring_outer) :: ptask_outer*
  -- if pcallcontext.CALLSITE = (pstaticstring_inner.SITE)
def $static_protocol_phase(S,n) = false -- otherwise
dec $static_protocol_seek(pstate,nat,nat) : pstate
def $static_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $static_protocol_seek(S,n_phase,n) = S
  -- if $static_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $static_protocol_seek(S,n_phase,0) = S
  -- if ~$static_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $static_protocol_seek(S,n_phase,n) = $static_protocol_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$static_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $static_protocol_output(pevent*) : ptbytes
dec $static_protocol_output_marker(pevent) : bool
def $static_protocol_output_marker(OUTPUT ptbytes) = true
def $static_protocol_output_marker(pevent) = false -- otherwise
def $static_protocol_output(eps) = eps
def $static_protocol_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $static_protocol_output(pevent_tail*)
def $static_protocol_output(pevent :: pevent_tail*) = $static_protocol_output(pevent_tail*)
  -- if ~$static_protocol_output_marker(pevent)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$class_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def owner_checks(state, direct, total):
    return [f'$heap_count(HOBJECT n_original,$heap_graph({state}).ROOTS) = {direct}',
            f'$heap_owners($heap_graph({state}),HOBJECT n_original) = {total}']


def initial_checks(initial):
    return ['S_initial = ' + initial,
            'S_found = $static_protocol_seek(S_initial,0,2048)',
            'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
            'S_assign = S_found[.COMPLETION = NORMAL]',
            'S_assign.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*',
            '$static_string_capture(S_assign,pbase,z) = (pstaticstring)',
            'n_original = pstaticstring.OBJECT',
            'porigin_site = pstaticstring.SITE',
            'S_pending_found = $drive_steps(S_assign,1)',
            'S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]',
            'S_pending.TODO = (CALL_ARGS (METHOD_TARGET n_original porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*',
            'S_pending.HELD = S_assign.HELD',
            '$task_nodes(STATIC_STRING_RESULT pstaticstring) = eps',
            '$task_nodes(STATIC_STRING_CAPTURE pstaticstring) = $operand_nodes(pstaticstring.RHS)',
            '$static_string_capture_count(S_pending.TODO,porigin_site) = 1',
            *valid('S_pending')]


def ownership(initial, name):
    temporary = name == 'temporary-owner'
    retained = name == 'retained-cv-owner'
    reference = name.startswith('returned-reference')
    payload_changed = name == 'returned-reference-payload'
    survives = temporary or retained or (reference and not payload_changed)
    checks = initial_checks(initial)
    if temporary:
        checks += ['pstaticstring.RHS = KNOWN (POBJECT n_original)']
    elif reference:
        checks += ['pstaticstring.RHS = REFERENCE n_rhs',
                   'S_pending.STORE[n_rhs] = DEFINED (POBJECT n_original)',
                   '$heap_count(HCELL n_rhs,$heap_graph(S_pending).ROOTS) = 2']
    else:
        checks += ['pstaticstring.RHS = VARIABLE ([100]) z_rhs']
    checks += owner_checks('S_pending', 3 if temporary else 2, 4 if retained else 3)
    checks += ['S_entered_found = $static_protocol_seek(S_pending,2,2048)',
               'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
               'S_entered = S_entered_found[.COMPLETION = NORMAL]',
               '$static_protocol_phase(S_entered,2)',
               'S_entered.CURRENT = (pcallcontext)',
               'S_entered.FRAMES = pframe :: pframe_tail*',
               'pframe.TODO = (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*',
               '$static_string_task_valid(S_entered[.CURRENT = pframe.CONTEXT][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO],pstaticstring)',
               *valid('S_entered')]
    checks += owner_checks('S_entered', 3 if temporary else 2, 4 if retained else 3)
    checks += ['S_restored_found = $static_protocol_seek(S_entered,3,2048)',
               'S_restored_found.COMPLETION = NORMAL \\/ S_restored_found.COMPLETION = BUDGET',
               'S_restored = S_restored_found[.COMPLETION = NORMAL]',
               'S_restored.TODO = (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*',
               'S_restored.RESULT = KNOWN (PSTRING ([115]))',
               *valid('S_restored')]
    checks += owner_checks('S_restored', 2 if temporary else 1, 2 if survives else 1)
    checks += ['$class_static_at(S_restored.CLASSSTATICS,pstaticstring.DECL) = (pclassstatic)',
               'pclassstatic.STATE = PROP_VALUE (ALIAS n_guard)',
               'S_restored.STORE[n_guard] = DEFINED pvalue_old',
               'S_restored.PROPREFS = [ppropref]',
               'ppropref.CELL = n_guard',
               '$objectprops_record_at(S_restored.OBJECTPROPS,n_original) = (pobjectprops)',
               'pobjectprops.SLOTS = [ppropertyslot]',
               'ppropertyslot.DECL = (ppropertyid_guard)',
               'ppropref.SOURCES = [CLASS_PROP_SOURCE pstaticstring.DECL,OBJECT_PROP_SOURCE n_original ([103,117,97,114,100]) ppropertyid_guard]',
               'S_completed_found = $drive_steps(S_restored,1)',
               'S_completed_found.COMPLETION = BUDGET',
               'S_completed = S_completed_found[.COMPLETION = NORMAL]',
               'S_completed.TODO = (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*',
               'S_completed.RESULT = KNOWN (PSTRING ([115]))',
               *valid('S_completed')]
    checks += owner_checks('S_completed', 1 if temporary else 0, 1 if survives else 0)
    if survives:
        checks += ['HOBJECT n_original <- S_completed.ALLOCATIONS',
                   'S_completed.PROPREFS = S_restored.PROPREFS']
    else:
        checks += ['~(HOBJECT n_original <- S_completed.ALLOCATIONS)',
                   '$objectprops_record_at(S_completed.OBJECTPROPS,n_original) = eps',
                   'S_completed.PROPREFS = [ppropref[.SOURCES = [CLASS_PROP_SOURCE pstaticstring.DECL]]]']
    if reference:
        checks += ['$heap_count(HCELL n_rhs,$heap_graph(S_restored).ROOTS) = ' + ('2' if payload_changed else '1'),
                   '$heap_count(HCELL n_rhs,$heap_graph(S_completed).ROOTS) = ' + ('2' if payload_changed else '1'),
                   'S_completed.STORE[n_rhs] = DEFINED ' + ('PNULL' if payload_changed else '(POBJECT n_original)')]
    checks += ['S_written = $drive_steps(S_completed,1)',
               'S_written.COMPLETION = BUDGET',
               '$static_string_capture_count(S_written.TODO,porigin_site) = 0',
               '$static_string_pairs_valid(S_written.TODO)',
               'S_written.CLASSSTATICS = S_completed.CLASSSTATICS']
    if survives:
        checks += ['S_written.TODO = (THROW_SEARCH n_throw) :: ptask_throw*',
                   'S_written.OBJECTS[n_throw] = THROWABLE pthrowable',
                   'pthrowable.KIND = "TypeError"',
                   'S_written.STORE[n_guard] = DEFINED pvalue_old']
    else:
        checks += ['S_written.RESULT = KNOWN (PSTRING ([115]))',
                   'S_written.STORE[n_guard] = DEFINED (PSTRING ([115]))']
    expected = 'TE|V' if survives else 'TW|s'
    checks += ['S_done = $drive(S_written[.COMPLETION = NORMAL],4096)',
               'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
               '$static_protocol_output(S_done.EVENTS) = $ptascii("' + expected + '")',
               *valid('S_done')]
    if temporary:
        checks += forgeries()
    return checks


def forgeries():
    pair = '(STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*'
    scratch = '(STRINGIFY_RESULT n_original porigin_site z) :: '
    def invalid(tasks, state='S_restored'):
        return f'~$static_string_task_valid({state}[.TODO = {tasks}],pstaticstring)'
    return [
        invalid(scratch + '(STATIC_STRING_RESULT pstaticstring) :: ptask_tail*'),
        invalid(scratch + '(STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*'),
        invalid(scratch + pair + ' ++ [STATIC_STRING_CAPTURE pstaticstring]'),
        invalid(scratch + pair + ' ++ [STATIC_STRING_RESULT pstaticstring,STATIC_STRING_CAPTURE pstaticstring]'),
        invalid(scratch + '(AT porigin_site (STATIC_STRING_RESULT pstaticstring)) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*'),
        invalid(scratch + '(STATIC_STRING_RESULT pstaticstring) :: (AT porigin_site (STATIC_STRING_CAPTURE pstaticstring)) :: ptask_tail*'),
        invalid('(AT porigin_site (STRINGIFY_RESULT n_original porigin_site z)) :: ' + pair),
        invalid('(AT porigin_site (STRINGIFY_RESULT n_original porigin_site z)) :: (ORIGIN_RETURN (porigin_site)) :: ' + pair),
        invalid('(STRINGIFY_RESULT $(n_original + 1) porigin_site z) :: ' + pair),
        invalid('(STRINGIFY_RESULT n_original porigin_site $(z + 1)) :: ' + pair),
        'pstaticstring_bad_line = pstaticstring[.LINE = $(z + 1)]',
        '~$static_string_task_valid(S_restored[.TODO = (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring_bad_line) :: (STATIC_STRING_CAPTURE pstaticstring_bad_line) :: ptask_tail*],pstaticstring_bad_line)',
        '~$static_string_record_valid(S_restored,pstaticstring[.SITE = pstaticstring.CLASS])',
        '~$static_string_record_valid(S_restored,pstaticstring[.CLASS = porigin_site])',
        '~$static_string_record_valid(S_restored,pstaticstring[.DECL = porigin_site])',
        '~$static_string_record_valid(S_restored,pstaticstring[.NAME = ([109,105,115,115,105,110,103])])',
        '~$static_string_task_valid(S_restored[.CODE = eps],pstaticstring)',
        '~$static_string_task_valid(S_restored[.SOURCES = eps],pstaticstring)',
        'pstaticstring_bad_ref = pstaticstring[.RHS = REFERENCE n_guard]',
        '$call_reference_operand_valid(S_restored,pstaticstring_bad_ref.RHS)',
        '~$static_string_rhs_valid(S_restored,pstaticstring_bad_ref)',
        '~$static_string_reference_rhs(NExprFuncCall (NName (BYTES "cmVm") eps) (SEQUENCE ([(NVariadicPlaceholder eps)])) eps)',
        '~$static_string_task_valid(S_restored[.TODO = (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring_bad_ref) :: (STATIC_STRING_CAPTURE pstaticstring_bad_ref) :: ptask_tail*],pstaticstring_bad_ref)',
        '~$static_string_task_valid(S_completed[.RESULT = KNOWN PNULL],pstaticstring)',
        '~$static_string_task_valid(S_completed[.RESULT = KNOWN (POBJECT n_original)],pstaticstring)',
        '~$call_descriptors_valid(S_completed[.RESULT = KNOWN PNULL])',
        '~$call_descriptors_valid(S_completed[.RESULT = KNOWN PNULL][.TODO = (ORIGIN_RETURN (porigin_site)) :: ' + pair + '])',
        '~$call_descriptors_valid(S_restored[.TODO = (AT porigin_site (STRINGIFY_RESULT n_original porigin_site z)) :: ' + pair + '])',
    ]


def special(initial, name):
    checks = initial_checks(initial)
    if name == 'private-self-context':
        checks += ['S_entered_found = $static_protocol_seek(S_pending,2,2048)',
                   'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
                   'S_entered = S_entered_found[.COMPLETION = NORMAL]',
                   '$static_protocol_phase(S_entered,2)',
                   'S_entered.FRAMES = pframe :: pframe_tail*',
                   '$static_string_record_valid(S_entered,pstaticstring)',
                   '~$static_string_target_valid(S_entered[.ORIGIN = (porigin_site)],pstaticstring)',
                   '$static_string_task_valid(S_entered[.CURRENT = pframe.CONTEXT][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO],pstaticstring)',
                   *valid('S_entered'),
                   '~$call_descriptors_valid(S_entered[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: ptask_tail*] :: pframe_tail*])']
        expected = 'Ts|s'
    elif name == 'nested-cast':
        checks += ['S_entered_found = $static_protocol_seek(S_pending,7,4096)',
                   'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
                   'S_entered = S_entered_found[.COMPLETION = NORMAL]',
                   '$static_protocol_phase(S_entered,7)',
                   'S_entered.FRAMES = pframe_inner :: pframe_outer :: pframe_tail*',
                   'pframe_inner.TODO = (STRINGIFY_RESULT n_inner porigin_inner z_inner) :: (STATIC_STRING_RESULT pstaticstring_inner) :: (STATIC_STRING_CAPTURE pstaticstring_inner) :: ptask_inner*',
                   'pframe_outer.TODO = (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*',
                   '$heap_count(HOBJECT n_original,$heap_graph(S_entered).ROOTS) = 3',
                   '$heap_owners($heap_graph(S_entered),HOBJECT n_original) = 3',
                   '$heap_count(HOBJECT n_inner,$heap_graph(S_entered).ROOTS) = 3',
                   '$heap_owners($heap_graph(S_entered),HOBJECT n_inner) = 3',
                   *valid('S_entered')]
        expected = 'DEa|b'
    else:
        checks += ['S_throw_found = $static_protocol_seek(S_pending,5,4096)',
                   'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
                   'S_throw = S_throw_found[.COMPLETION = NORMAL]',
                   'S_throw.TODO = (THROW_SEARCH n_throw) :: (STRINGIFY_RESULT n_original porigin_site z) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*',
                   'S_throw.OBJECTS[n_throw] = THROWABLE pthrowable',
                   'pthrowable.KIND = "Exception"',
                   '$throwable_previous_id(S_throw,n_throw) = eps',
                   *owner_checks('S_throw', 2, 2), *valid('S_throw'),
                   'S_scratch_discarded = $drive_steps(S_throw,1)',
                   'S_scratch_discarded.COMPLETION = BUDGET',
                   'S_scratch_discarded.TODO = (THROW_SEARCH n_throw) :: (STATIC_STRING_RESULT pstaticstring) :: (STATIC_STRING_CAPTURE pstaticstring) :: ptask_tail*',
                   *owner_checks('S_scratch_discarded', 1, 1), *valid('S_scratch_discarded'),
                   'S_discarded = $drive_steps(S_scratch_discarded[.COMPLETION = NORMAL],1)',
                   'S_discarded.COMPLETION = BUDGET',
                   'S_discarded.TODO = (THROW_SEARCH n_throw) :: ptask_tail*',
                   'S_discarded.OBJECTS[n_throw] = S_throw.OBJECTS[n_throw]',
                   '$static_string_capture_count(S_discarded.TODO,porigin_site) = 0',
                   '~(HOBJECT n_original <- S_discarded.ALLOCATIONS)',
                   *valid('S_discarded')]
        expected = 'Exception|cast|none|F|inner'
        checks += ['S_entered = S_discarded']
    checks += ['S_done = $drive(S_entered[.COMPLETION = NORMAL],8192)',
               'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
               '$static_protocol_output(S_done.EVENTS) = $ptascii("' + expected + '")',
               *valid('S_done')]
    return checks


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = [*modules, 'spec/semantics/modules.json', 'frontend/worker.php',
             'frontend/wire.php', '.tools/php/bin/php', '.tools/php-file.so',
             '.tools/request-clock.so', 'native/request_clock.c', 'scripts/build-request-provider.sh',
             '_build/default/adapter/main.exe', 'tests/semantics/recorded_worker.py',
             'tests/semantics/static_types.py', 'frontend/wire.py', 'tests/semantics/profile.json',
             'tests/semantics/typed_static_string_assignment.py',
             'tests/semantics/_build/default/numeric_runner.exe', str(Path(__file__).relative_to(ROOT))]
    before = {name: sha(ROOT / name) for name in names}
    out = Path(tempfile.mkdtemp(prefix='typed-static-string-protocol-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    rows = []
    try:
        for name in STAGES:
            source = SOURCES[name]
            path = out / (name + '.php')
            path.write_bytes(source)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            initial = initial_fixture(checked, path, name)
            checks = ownership(initial, name) if name in STAGES[:5] else special(initial, name)
            fixture = out / (name + '.watsup')
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- if ' + check + '\n' for check in checks))
            command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                       *[str(ROOT / module) for module in modules], str(fixture)]
            timed_out = False
            started = time.monotonic()
            try:
                result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=180)
                stdout, stderr, code = result.stdout, result.stderr, result.returncode
            except subprocess.TimeoutExpired as error:
                stdout, stderr, code, timed_out = error.stdout or b'', error.stderr or b'', None, True
            (out / (name + '.stdout')).write_bytes(stdout)
            (out / (name + '.stderr')).write_bytes(stderr)
            passed = not timed_out and code == 0 and stdout == b'true\n' and not stderr
            rows.append({'id': name, 'pass': passed, 'assertions': len(checks),
                         'source_sha256': sha(path), 'fixture_sha256': sha(fixture),
                         'request': request_facts(path)[0] if name in REQUEST_CASES else None,
                         'command': command, 'timeout': timed_out, 'exit_status': code,
                         'seconds': time.monotonic() - started})
            print(name, passed, len(checks), flush=True)
            if not passed:
                break
    finally:
        frontend.close()
        adapter.close()
    after = {name: sha(ROOT / name) for name in names}
    assert before == after, 'inputs changed during run'
    report = {'result': 'pass' if len(rows) == len(STAGES) and all(row['pass'] for row in rows) else 'nonpass',
              'inputs': before, 'after_inputs': after, 'records': rows,
              'selected': STAGES, 'completed': len(rows)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], flush=True)
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
