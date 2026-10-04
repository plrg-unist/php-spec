#!/usr/bin/env python3
"""Source-reached prepared internal default values retain nested previous owners."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from internal_default_constructor_sources import OWNER_SOURCE, ROOT
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

PREFIX = r'''
dec $internal_protocol_output(pevent*) : ptbytes
def $internal_protocol_output(eps) = eps
def $internal_protocol_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $internal_protocol_output(pevent*)
dec $internal_protocol_is_output(pevent) : bool
def $internal_protocol_is_output(OUTPUT ptbytes) = true
def $internal_protocol_is_output(pevent) = false -- otherwise
def $internal_protocol_output(pevent :: pevent_tail*) = $internal_protocol_output(pevent_tail*)
  -- if ~$internal_protocol_is_output(pevent)
dec $internal_protocol_phase(pstate,nat) : bool
def $internal_protocol_phase(S,0) = true
  -- if S.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*
  -- if |pdefaultnew.ARGUMENTS| = 3 /\ pdefaultnew.INDEX = 3
def $internal_protocol_phase(S,n) = true
  -- if n = 1 \/ n = 3
  -- if S.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall) :: ptask_tail*
  -- if |pdefaultnew.ARGUMENTS| = 3 /\ pctorcall.INDEX = n
def $internal_protocol_phase(S,n) = false -- otherwise
dec $internal_protocol_seek(pstate,nat,nat) : pstate
def $internal_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $internal_protocol_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $internal_protocol_phase(S,n_phase)
def $internal_protocol_seek(S,n_phase,0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$internal_protocol_phase(S,n_phase)
def $internal_protocol_seek(S,n_phase,n) = $internal_protocol_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$internal_protocol_phase(S,n_phase) /\ $(n > 0)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$class_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $internal_protocol_seek({parent},{phase},4096)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$internal_protocol_phase({state},{phase})', *valid(state)]


def reject(name, expression):
    return [f'S_bad_{name} = {expression}', f'$heap_valid($heap_graph(S_bad_{name}))',
            f'~$call_descriptors_valid(S_bad_{name})']


def assertions(initial):
    return [
        'S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *seek('S_initial','S_values',0),
        'S_values.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_values*',
        'pdefaultnew.VALUES = [POBJECT n_previous,PINT 7,PSTRING ptbytes_message]',
        r'pdefaultnew.CLASS = $ptascii("Exception") /\ pdefaultnew.LINE = 2',
        'ptbytes_message = $ptascii("outer")',
        '$throwable_field(S_values,n_previous,"message") = PSTRING $ptascii("inner")',
        '$heap_owners($heap_graph(S_values),HOBJECT pdefaultnew.OBJECT) = 1',
        '$heap_owners($heap_graph(S_values),HOBJECT n_previous) = 1',
        *seek('S_values','S_prefix',1),
        'S_prefix.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall_prefix) :: ptask_prefix*',
        'pctorcall_prefix.SENT = [NAMED_HOLE,NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_previous))]',
        r'pctorcall_prefix.MODE = CTOR_NEW /\ pctorcall_prefix.BASE = "Exception"',
        r'pctorcall_prefix.SITE = pdefaultnew.SITE /\ pctorcall_prefix.LINE = pdefaultnew.LINE',
        '$default_internal_valid(S_prefix,pdefaultnew,pctorcall_prefix)',
        '$heap_owners($heap_graph(S_prefix),HOBJECT n_previous) = 2',
        *seek('S_prefix','S_full',3),
        'S_full.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall) :: ptask_full*',
        'pctorcall.SENT = [NAMED_SENT (KNOWN (PSTRING ptbytes_message)),NAMED_SENT (KNOWN (PINT 7)),NAMED_SENT (KNOWN (POBJECT n_previous))]',
        '$default_internal_valid(S_full,pdefaultnew,pctorcall)',
        'pctorcall_code = pctorcall[.SENT = [NAMED_SENT (KNOWN (PSTRING ptbytes_message)),NAMED_SENT (KNOWN (PINT 8)),NAMED_SENT (KNOWN (POBJECT n_previous))]]',
        *reject('code','S_full[.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall_code) :: ptask_full*]'),
        *reject('mode','S_full[.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall[.MODE = CTOR_METHOD]) :: ptask_full*]'),
        *reject('base','S_full[.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall[.BASE = "Error"]) :: ptask_full*]'),
        *reject('line','S_full[.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall[.LINE = $(pctorcall.LINE + 1)]) :: ptask_full*]'),
        *reject('index','S_full[.TODO = (DEFAULT_INTERNAL_CTOR_ARGS pdefaultnew pctorcall[.INDEX = 2]) :: ptask_full*]'),
        'S_missing = S_full[.TODO = ptask_full*]',
        '$heap_owners($heap_graph(S_missing),HOBJECT pdefaultnew.OBJECT) = 0',
        'S_done = $drive_steps(S_full,4096)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$internal_protocol_output(S_done.EVENTS) = $ptascii("outer/7/inner")',
        '~((HOBJECT pdefaultnew.OBJECT) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_previous) <- S_done.ALLOCATIONS)',
        r'S_done.CONSTCONTEXT = eps /\ S_done.PARAMETERBACKINGS = eps /\ S_done.HELD = eps',
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
    out = Path(tempfile.mkdtemp(prefix='internal-default-constructor-owner-', dir=ROOT / '.tools'))
    source = out / 'source.php'; source.write_bytes(OWNER_SOURCE)
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
