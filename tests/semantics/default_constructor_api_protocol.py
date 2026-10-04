#!/usr/bin/env python3
"""Source-reached callable deprecation retains a genuine default constructor owner."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from default_constructor_sources import CASES, ROOT
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $default_api_phase(pstate) : bool
def $default_api_phase(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLABLE_RESULT papiquery n
def $default_api_phase(S) = false -- otherwise
dec $default_api_seek(pstate,nat) : pstate
def $default_api_seek(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $default_api_seek(S,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $default_api_phase(S)
def $default_api_seek(S,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$default_api_phase(S)
def $default_api_seek(S,n) = $default_api_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$default_api_phase(S) /\ $(n > 0)
dec $default_api_output(pevent*) : ptbytes
def $default_api_output(eps) = eps
def $default_api_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $default_api_output(pevent*)
dec $default_api_is_output(pevent) : bool
def $default_api_is_output(OUTPUT ptbytes) = true
def $default_api_is_output(pevent) = false -- otherwise
def $default_api_output(pevent :: pevent_tail*) = $default_api_output(pevent_tail*)
  -- if ~$default_api_is_output(pevent)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$class_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def assertions(initial):
    return [
        'S_initial = ' + initial, '~S_initial.COMPILESTOP',
        'S_found = $default_api_seek(S_initial,4096)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_handler = S_found[.COMPLETION = NORMAL]',
        '$default_api_phase(S_handler)', *valid('S_handler'),
        'S_handler.CURRENT = (pcallcontext_handler)',
        'S_handler.FRAMES = pframe_api :: pframe_ctor :: pframe_tail*',
        'pframe_api.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_api*',
        'perrorcall.RESUME = API_CALLABLE_RESULT papiquery n_phase',
        'n_phase = 1',
        'pframe_ctor.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_ctor*',
        'papiquery.SOURCE = TYPE_RECEIVE pdefaultctor.FUNCTION 0',
        r'perrorcall.LEVEL = 8192 /\ perrorcall.LINE = papiquery.LINE',
        '$error_context_kind(S_handler,pcallcontext_handler)',
        '~$default_ctor_context_kind(S_handler,pcallcontext_handler)',
        'S_ctor = $api_saved_frame_scope($constant_frame_scope(S_handler,pframe_api,pframe_ctor :: pframe_tail*),pframe_api,pframe_ctor :: pframe_tail*)',
        'S_ctor.CURRENT = (pcallcontext_ctor)',
        '$default_ctor_context_kind(S_ctor,pcallcontext_ctor)',
        '$default_ctor_context_valid(S_ctor,pcallcontext_ctor)',
        '$api_query_valid(S_ctor,papiquery,n_phase)',
        'S_missing = S_handler[.FRAMES = pframe_api :: pframe_ctor[.TODO = ptask_ctor*] :: pframe_tail*]',
        '$heap_valid($heap_graph(S_missing))',
        '~$call_descriptors_valid(S_missing)',
        'pframe_missing = pframe_ctor[.TODO = ptask_ctor*]',
        'S_missing_ctor = $api_saved_frame_scope($constant_frame_scope(S_missing,pframe_api,pframe_missing :: pframe_tail*),pframe_api,pframe_missing :: pframe_tail*)',
        '~$default_ctor_context_valid(S_missing_ctor,pcallcontext_ctor)',
        'S_done = $drive_steps(S_handler,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$default_api_output(S_done.EVENTS) = $ptascii("D4|C1|T0|F0|s")',
        '~((HOBJECT pdefaultctor.NEW.OBJECT) <- S_done.ALLOCATIONS)',
        r'S_done.PARAMETERBACKINGS = eps /\ S_done.REFCOERCIONS = eps /\ S_done.HELD = eps',
        *valid('S_done')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='default-constructor-api-owner-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(CASES['deprecated-callable-constructor-composition'])
    report = {'passed': False, 'head': before['identity']['head'], 'before': before,
              'source_sha256': sha(source), 'profile': cross.invoke.types.PROFILE,
              'mode': 'unused' if args.elaborate_only else 'source-reached'}
    print(out, flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
        clauses = ['program_source = ' + checked['fixture'], *assertions(initial)]
        (out / 'assertions.json').write_text(json.dumps(clauses, indent=2) + '\n')
        body = 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + c + '\n' for c in clauses)
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX + body + '\ndec $main() : bool\ndef $main() = ' +
                           ('true' if args.elaborate_only else '$body()') + '\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
            *[str(ROOT / module) for module in modules], str(fixture)], out / 'numeric', 120, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, assertions=len(clauses), fixture_sha256=sha(fixture),
            state_assertions_evaluated=0 if args.elaborate_only else len(clauses),
            unused_body_assertions=len(clauses) if args.elaborate_only else 0)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
