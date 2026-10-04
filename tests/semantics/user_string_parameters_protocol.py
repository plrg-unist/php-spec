#!/usr/bin/env python3
"""Source-reached formal-cell ownership, same-site receives and throw cleanup."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

from recorded_worker import Worker
from user_string_parameters import CASES, EXPECTED, ROOT, inputs, sha
import typed_static_invoke_set_protocol as driver

STAGES = ['free-reference-mutation', 'same-site-reentry', 'conversion-throw', 'constant-closure-parameter']
PREFIX = r'''
dec $parameter_protocol_output(pevent*) : ptbytes
dec $parameter_protocol_is_output(pevent) : bool
def $parameter_protocol_is_output(OUTPUT ptbytes) = true
def $parameter_protocol_is_output(pevent) = false -- otherwise
def $parameter_protocol_output(eps) = eps
def $parameter_protocol_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $parameter_protocol_output(pevent_tail*)
def $parameter_protocol_output(pevent :: pevent_tail*) = $parameter_protocol_output(pevent_tail*)
  -- if ~$parameter_protocol_is_output(pevent)
dec $parameter_protocol_phase(pstate,nat) : bool
def $parameter_protocol_phase(S,0) = $parameter_string_candidate(S)
def $parameter_protocol_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = [STRINGIFY_RESULT n_object porigin_site z, PARAMETER_STRING_RESULT pparameterstring]
def $parameter_protocol_phase(S,2) = true
  -- if S.TODO = [PARAMETER_STRING_RESULT pparameterstring]
  -- if S.RESULT = KNOWN (PSTRING n_text*)
def $parameter_protocol_phase(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: (STRINGIFY_RESULT n_object porigin_site z) :: (PARAMETER_STRING_RESULT pparameterstring) :: eps
def $parameter_protocol_phase(S,4) = true
  -- if $parameter_protocol_phase(S,1)
  -- if S.FRAMES = pframe_new :: pframe_converter :: pframe_old :: pframe_tail*
  -- if pframe_old.TODO = [STRINGIFY_RESULT n_old porigin_site z, PARAMETER_STRING_RESULT pparameterstring_old]
def $parameter_protocol_phase(S,n) = false -- otherwise
dec $parameter_protocol_seek(pstate,nat,nat) : pstate
def $parameter_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $parameter_protocol_seek(S,n_phase,n) = S
  -- if $parameter_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $parameter_protocol_seek(S,n_phase,0) = S
  -- if ~$parameter_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $parameter_protocol_seek(S,n_phase,n) = $parameter_protocol_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$parameter_protocol_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$class_state_valid(' + state + ')',
            '$heap_valid($heap_graph(' + state + '))']


def seek(parent, state, phase):
    return [state + '_found = $parameter_protocol_seek(' + parent + ',' + str(phase) + ',4096)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$parameter_protocol_phase(' + state + ',' + str(phase) + ')']


def terminal(parent, expected):
    output = ('$base64(' + json.dumps(base64.b64encode(expected).decode()) + ')' if b'\0' in expected
              else '$ptascii(' + json.dumps(expected.decode()) + ')')
    return ['S_done = $drive_steps(' + parent + ',4096)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
            'S_done.HELD = eps', '$parameter_protocol_output(S_done.EVENTS) = ' + output,
            *valid('S_done')]


def checks(initial, name):
    clauses = ['S_initial = ' + initial]
    if name == 'constant-closure-parameter':
        return clauses + [*seek('S_initial', 'S_entered', 1),
            'S_entered.CURRENT = (pcallcontext_converter)',
            'S_entered.FRAMES = pframe_receive :: pframe_tail*',
            'pframe_receive.CONTEXT = (pcallcontext_receive)',
            'pframe_receive.TODO = [STRINGIFY_RESULT n_object porigin_site z,PARAMETER_STRING_RESULT pparameterstring]',
            '$context_target(pcallcontext_receive) = CLOSURE_TARGET n_closure',
            'pcallcontext_receive.FUNCTION = pparameterstring.FUNCTION /\\ pcallcontext_receive.ARGC = 1',
            'pcallcontext_converter.ARGC = 0 /\\ pcallcontext_converter.RECEIVER = (n_object)',
            'pframe_receive.LOCALS = (psymboltable_receive)',
            '$lookup(psymboltable_receive.ENV,$ptascii("s")) = (pparameterstring.CELL)',
            'S_entered.STORE[pparameterstring.CELL] = DEFINED (POBJECT n_object)',
            '$parameter_string_scope_valid(S_entered,pparameterstring)',
            '$constant_callable_record(S_entered.CONSTANTCLOSURES,n_closure) = (pconstantclosure)',
            'pconstantclosure.SITE = pparameterstring.FUNCTION',
            'S_entered.OBJECTS[n_closure] = CONSTANTCLOSURE pconstantclosure.SITE (REALCLOSURE pconstantclosure.SITE eps pstaticcell*)',
            '$class_constant_origin(S_entered.CLASSES,pconstantclosure.DECL) = (pclassconstantdesc)',
            'pclassconstantdesc.NAME = $ptascii("F") /\\ pclassconstantdesc.OWNERNAME = $ptascii("A")',
            '$default_cache_at(S_entered.CLASSCONSTANTCACHE,pconstantclosure.DECL) = (pdefaultcache)',
            'pdefaultcache.VALUE = POBJECT n_closure /\\ pdefaultcache.CLASS = PVCLOSURE n_closure pconstantclosure.SITE',
            '$closure_scope_at(S_entered.CLOSURESCOPES,n_closure) = (pclosurescope)',
            'pclosurescope.LEXICAL = pclassconstantdesc.OWNER /\\ pclosurescope.CALLED = pclassconstantdesc.OWNER',
            'pcallcontext_receive.LEXICAL_CLASS = (pclassconstantdesc.OWNER) /\\ pcallcontext_receive.CALLED_CLASS = (pclassconstantdesc.OWNER)',
            '$constant_callable_record_valid(S_entered,pconstantclosure)',
            '$stringify_context_frame_valid(S_entered,pcallcontext_converter,pframe_receive)',
            '~$parameter_string_scope_valid(S_entered,pparameterstring[.CELL = $(|S_entered.STORE| + 1)])',
            '~$call_descriptors_valid(S_entered[.CONSTANTCLOSURES = eps])',
            *valid('S_entered'), *terminal('S_entered',EXPECTED[name]),
            '~((HCELL pparameterstring.CELL) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
            '(HOBJECT n_closure) <- S_done.ALLOCATIONS',
            '$heap_count(HOBJECT n_closure,$heap_graph(S_done).ROOTS) = 1 /\\ $heap_owners($heap_graph(S_done),HOBJECT n_closure) = 1',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE,pconstantclosure.DECL) = (pdefaultcache)',
            '$constant_callable_record_valid(S_done,pconstantclosure)']
    if name == 'same-site-reentry':
        return clauses + [*seek('S_initial', 'S_nested', 4),
            'S_nested.FRAMES = pframe_new :: pframe_converter :: pframe_old :: pframe_tail*',
            'pframe_new.TODO = [STRINGIFY_RESULT n_new porigin_site z, PARAMETER_STRING_RESULT pparameterstring_new]',
            'pframe_old.TODO = [STRINGIFY_RESULT n_old porigin_site z, PARAMETER_STRING_RESULT pparameterstring_old]',
            'pparameterstring_new.FUNCTION = pparameterstring_old.FUNCTION /\\ pparameterstring_new.INDEX = pparameterstring_old.INDEX',
            'pparameterstring_new.CELL =/= pparameterstring_old.CELL /\\ n_new = n_old',
            'pparameterstring_new.OBJECT = n_new /\\ pparameterstring_old.OBJECT = n_old',
            'pframe_new.LOCALS = (psymboltable_new)',
            'pframe_old.LOCALS = (psymboltable_old)',
            '$lookup(psymboltable_new.ENV,$ptascii("s")) = (pparameterstring_new.CELL)',
            '$lookup(psymboltable_old.ENV,$ptascii("s")) = (pparameterstring_old.CELL)',
            '$parameter_string_scope_valid(S_nested,pparameterstring_new)',
            '$parameter_string_scope_valid($parameter_string_frame_scope(S_nested,pframe_old,pframe_tail*),pparameterstring_old)',
            '~$parameter_string_scope_valid(S_nested,pparameterstring_new[.CELL = pparameterstring_old.CELL])',
            'S_forged = S_nested[.FRAMES = pframe_new[.TODO = [STRINGIFY_RESULT n_new porigin_site z,PARAMETER_STRING_RESULT pparameterstring_new[.CELL = pparameterstring_old.CELL]]] :: pframe_converter :: pframe_old :: pframe_tail*]',
            '~$call_descriptors_valid(S_forged)',
            '$stringify_chain_valid(S_nested,S_nested.CURRENT,S_nested.FRAMES)',
            *valid('S_nested'),
            *terminal('S_nested', EXPECTED[name]),
            '~((HCELL pparameterstring_new.CELL) <- S_done.ALLOCATIONS)',
            '~((HCELL pparameterstring_old.CELL) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_new) <- S_done.ALLOCATIONS)']
    clauses += [*seek('S_initial', 'S_begin', 0), *valid('S_begin'),
        'S_begin.CURRENT = (pcallcontext_receive)',
        'S_pending_found = $drive_steps(S_begin,1)',
        'S_pending_found.COMPLETION = BUDGET',
        'S_pending = S_pending_found[.COMPLETION = NORMAL]',
        'S_pending.TODO = [CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_site) z, STRINGIFY_RESULT n_object porigin_site z, PARAMETER_STRING_RESULT pparameterstring]',
        'pparameterstring.FUNCTION = pcallcontext_receive.FUNCTION /\\ pparameterstring.INDEX = 0',
        'pparameterstring.OBJECT = n_object /\\ pparameterstring.LINE = z',
        '$lookup(S_pending.ENV,$ptascii("s")) = (pparameterstring.CELL)',
        '$parameter_string_scope_valid(S_pending,pparameterstring)',
        '$task_nodes(PARAMETER_STRING_RESULT pparameterstring) = [HCELL pparameterstring.CELL,HOBJECT n_object]',
        '~$parameter_string_scope_valid(S_pending[.SOURCES = eps],pparameterstring)',
        '~$parameter_string_scope_valid(S_pending,pparameterstring[.CELL = $(|S_pending.STORE| + 1)])',
        '~$parameter_string_scope_valid(S_pending,pparameterstring[.OBJECT = $(|S_pending.OBJECTS| + 1)])',
        '~$parameter_string_scope_valid(S_pending,pparameterstring[.LINE = $(z + 1)])',
        '~$parameter_string_scope_valid(S_pending,pparameterstring[.INDEX = 1])',
        '~$parameter_string_current(S_pending[.CURRENT = (pcallcontext_receive[.ARGC = 0])],pparameterstring)',
        *valid('S_pending'), *seek('S_pending', 'S_entered', 1),
        'S_entered.CURRENT = (pcallcontext_converter)',
        'pcallcontext_converter.ARGC = 0 /\\ pcallcontext_converter.RECEIVER = (n_object)',
        'S_entered.FRAMES = pframe_receive :: pframe_tail*',
        'pframe_receive.CONTEXT = (pcallcontext_receive)',
        'pframe_receive.TODO = [STRINGIFY_RESULT n_object porigin_site z, PARAMETER_STRING_RESULT pparameterstring]',
        'pframe_receive.LOCALS = (psymboltable_receive)',
        '$lookup(psymboltable_receive.ENV,$ptascii("s")) = (pparameterstring.CELL)',
        '$parameter_string_scope_valid(S_entered,pparameterstring)',
        '$stringify_context_frame_valid(S_entered,pcallcontext_converter,pframe_receive)',
        *valid('S_entered')]
    if name == 'free-reference-mutation':
        return clauses + [*seek('S_entered', 'S_result', 2),
            'S_result.TODO = [PARAMETER_STRING_RESULT pparameterstring]',
            'S_result.CURRENT = (pcallcontext_receive)',
            'S_result.RESULT = KNOWN (PSTRING $ptascii("converted"))',
            'S_result.STORE[pparameterstring.CELL] = DEFINED (PSTRING $ptascii("side"))',
            '$propref_at(S_result.PROPREFS,pparameterstring.CELL) = eps',
            '$parameter_string_scope_valid(S_result,pparameterstring)',
            '(HOBJECT n_object) <- S_result.ALLOCATIONS',
            '$heap_count(HOBJECT n_object,$heap_graph(S_result).ROOTS) = 1 /\\ $heap_owners($heap_graph(S_result),HOBJECT n_object) = 1',
            *valid('S_result'),
            'S_stored_found = $drive_steps(S_result,1)',
            'S_stored_found.COMPLETION = BUDGET',
            'S_stored = S_stored_found[.COMPLETION = NORMAL]',
            'S_stored.STORE[pparameterstring.CELL] = DEFINED (PSTRING $ptascii("converted"))',
            'S_stored.CURRENT = (pcallcontext_receive) /\\ S_stored.ORIGIN = (pparameterstring.FUNCTION)',
            'S_stored.RESULT = KNOWN PNULL /\\ S_stored.BASE = BASE_VALUE (KNOWN PNULL)',
            '~((HOBJECT n_object) <- S_stored.ALLOCATIONS)',
            *valid('S_stored'), *terminal('S_stored', EXPECTED[name]),
            '$lookup(S_done.ENV,$ptascii("v")) = (pparameterstring.CELL)',
            'S_done.STORE[pparameterstring.CELL] = DEFINED (PSTRING $ptascii("converted"))',
            '$heap_count(HCELL pparameterstring.CELL,$heap_graph(S_done).ROOTS) = 1 /\\ $heap_owners($heap_graph(S_done),HCELL pparameterstring.CELL) = 1']
    return clauses + [*seek('S_entered', 'S_throw', 3),
        'S_throw.TODO = [THROW_SEARCH n_throw,STRINGIFY_RESULT n_object porigin_site z,PARAMETER_STRING_RESULT pparameterstring]',
        'S_throw.OBJECTS[n_throw] = THROWABLE pthrowable',
        'pthrowable.KIND = "Exception"',
        '$throwable_previous_id(S_throw,n_throw) = eps',
        '$parameter_string_scope_valid(S_throw,pparameterstring)',
        'S_throw.STORE[pparameterstring.CELL] = DEFINED (PSTRING $ptascii("side"))',
        *valid('S_throw'), *terminal('S_throw', EXPECTED[name]),
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        'S_done.STORE[pparameterstring.CELL] = DEFINED (PSTRING $ptascii("side"))',
        '$heap_count(HCELL pparameterstring.CELL,$heap_graph(S_done).ROOTS) = 1 /\\ $heap_owners($heap_graph(S_done),HCELL pparameterstring.CELL) = 1']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', help='Comma-separated exact stage IDs')
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else STAGES
    assert selected and len(selected) == len(set(selected)) and all(n in STAGES for n in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = inputs(args.freeze)
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    out = Path(tempfile.mkdtemp(prefix='string-parameters-protocol-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'selected': selected, 'records': [], 'inputs': before,
              'profile': driver.types.PROFILE, 'state_assertions_evaluated': 0,
              'unused_body_assertions': 0, 'mode': 'unused' if args.elaborate_only else 'source-reached'}
    frontend = adapter = None
    unused = []
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *driver.types.FLAGS, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in selected:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            row = {'id': name, 'source_sha256': sha(path), 'completed': False, 'passed': False}
            report['records'].append(row)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            initial = '$php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')'
            clauses = checks(initial, name)
            (directory / 'assertions.json').write_text(json.dumps(clauses, indent=2) + '\n')
            body = 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + c + '\n' for c in clauses)
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = $body()\n')
            row.update(assertions=len(clauses), fixture_sha256=sha(fixture))
            if args.elaborate_only:
                unused.append(body.replace('$body', '$unused_' + str(len(unused))))
                report['unused_body_assertions'] += len(clauses)
            else:
                result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    *[str(ROOT / module) for module in modules], str(fixture)], directory / 'numeric', 120, ROOT)
                assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                report['state_assertions_evaluated'] += len(clauses)
                row['passed'] = True
            row['completed'] = True
            print(name, 'prepared' if args.elaborate_only else 'pass', len(clauses), flush=True)
        if args.elaborate_only:
            fixture = out / 'all-unused.watsup'
            fixture.write_text(PREFIX + '\n'.join(unused) + '\ndec $main() : bool\ndef $main() = true\n')
            result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                *[str(ROOT / module) for module in modules], str(fixture)], out / 'unused-numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report['result'] = 'prepared' if args.elaborate_only else 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        cleanup = []
        for worker in [adapter, frontend]:
            if worker is not None:
                try:
                    worker.close()
                except BaseException as error:
                    cleanup.append({'type': type(error).__name__, 'message': str(error)})
        report['cleanup_errors'] = cleanup
        report['after_inputs'] = inputs(args.freeze)
        if cleanup or report['after_inputs'] != before:
            report['result'] = 'fail'
        report['raw_files'] = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'bytes': p.stat().st_size,
            'mode': oct(p.stat().st_mode & 0o7777)} for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)
    assert report['result'] == ('prepared' if args.elaborate_only else 'pass')


if __name__ == '__main__':
    main()
