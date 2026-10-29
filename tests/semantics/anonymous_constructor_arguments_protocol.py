#!/usr/bin/env python3
"""Source-reached anonymous NEW argument and constructor/no-constructor tasks."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/anonymous_constructor_arguments_cases.json'
CASES = {'anonymous-positional-typed', 'anonymous-named-reorder',
         'anonymous-no-constructor-arguments'}

PREFIX = r'''
dec $anon_arg_is_output(pevent) : bool
def $anon_arg_is_output(OUTPUT ptbytes) = true
def $anon_arg_is_output(pevent) = false -- otherwise
dec $anon_arg_output(pevent*) : ptbytes
def $anon_arg_output(eps) = eps
def $anon_arg_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $anon_arg_output(pevent*)
def $anon_arg_output(pevent :: pevent_tail*) = $anon_arg_output(pevent_tail*)
  -- if ~$anon_arg_is_output(pevent)
dec $anon_arg_front(pstate) : bool
def $anon_arg_front(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata_class) (SEQUENCE phpType7*) metadata)) :: ptask_tail*
  -- if phpType7* =/= eps
  -- if S.ORIGIN = (PORIGIN 0 pcpath)
def $anon_arg_front(S) = false -- otherwise
dec $anon_arg_seek(pstate,nat) : pstate
def $anon_arg_seek(S,n) = S -- if $anon_arg_front(S)
def $anon_arg_seek(S,0) = S -- if ~$anon_arg_front(S)
def $anon_arg_seek(S,n) = $anon_arg_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$anon_arg_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $anon_arg_seek(S,n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assertions(case, initial, filename, stdout):
    checks = [
        'program_source = ' + initial,
        'S_initial = $php_run(program_source,0,' + json.dumps(filename) + ')',
        '~S_initial.COMPILESTOP',
        'S_front_found = $anon_arg_seek(S_initial,4096)',
        r'S_front_found.COMPLETION = NORMAL \/ S_front_found.COMPLETION = BUDGET',
        'S_front = S_front_found[.COMPLETION = NORMAL]',
        '$anon_arg_front(S_front)',
        'S_front.ORIGIN = (PORIGIN 0 pcpath)',
        'S_front.TODO = (EVAL expression_new) :: ptask_tail*',
        '$anonymous_new_task_valid(S_front,expression_new)',
        '$anonymous_new_name(S_front,PORIGIN 0 pcpath) = (ptbytes_class)',
        '$call_descriptors_valid(S_front)',
        '$heap_valid($heap_graph(S_front))',
        'S_forged = S_front[.ORIGIN = (PORIGIN 0 (pcpath ++ [PCFIELD 1]))]',
        '~$anonymous_new_task_valid(S_forged,expression_new)',
        'S_selected_raw = $drive_steps(S_front,1)',
        r'S_selected_raw.COMPLETION = NORMAL \/ S_selected_raw.COMPLETION = BUDGET',
        'S_selected = S_selected_raw[.COMPLETION = NORMAL]',
        '$call_descriptors_valid(S_selected)',
        '$heap_valid($heap_graph(S_selected))',
    ]
    if case == 'anonymous-no-constructor-arguments':
        checks += [
            '~$new_has_ctor(S_front,ptbytes_class)',
            '$new_source_name(S_front,PORIGIN 0 pcpath) = (ptbytes_class)',
            'S_selected.TODO = (NOCTOR_ARGS pnoctorcall) :: ptask_selected*',
            'pnoctorcall.SITE = (PORIGIN 0 pcpath)',
            'pnoctorcall.CLASS = ptbytes_class',
            'pnoctorcall.INDEX = 0',
            '$call_task_valid(S_selected,NOCTOR_ARGS pnoctorcall)',
            'pnoctorcall_bad = pnoctorcall[.SITE = PORIGIN 0 (pcpath ++ [PCFIELD 1])]',
            '~$call_task_valid(S_selected,NOCTOR_ARGS pnoctorcall_bad)',
        ]
    else:
        checks += [
            '$new_has_ctor(S_front,ptbytes_class)',
            '$new_source_name(S_front,PORIGIN 0 pcpath) = (ptbytes_class)',
        ]
        if case == 'anonymous-positional-typed':
            checks += [
                'S_selected.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) phpType7* 0 eps (porigin_site) z_call) :: (CTOR_RESULT n_object) :: ptask_selected*',
            ]
        else:
            checks += [
                'S_selected.TODO = (NAMED_ARGS (METHOD_TARGET n_object porigin_method) phpType7* 0 {SLOTS eps, NAMED eps} (porigin_site) z_call) :: (CTOR_RESULT n_object) :: ptask_selected*',
            ]
        checks += [
            'porigin_site = PORIGIN 0 pcpath',
            'S_selected.OBJECTS[n_object] = INSTANCE porigin_class',
            '$effective_method(S_selected,porigin_class,$ptascii("__construct"),|S_selected.CLASSES|) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
            '$call_task_valid(S_selected,S_selected.TODO[0])',
            '$call_task_valid(S_selected,CTOR_RESULT n_object)',
            '(HOBJECT n_object) <- S_selected.ALLOCATIONS',
        ]
    checks += [
        'S_done = $drive_steps(S_selected,4096)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        '$anon_arg_output(S_done.EVENTS) = $base64(' + json.dumps(base64.b64encode(stdout).decode()) + ')',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=sorted(CASES), required=True)
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    catalogue = json.loads(CATALOGUE.read_text())
    row = next(row for row in catalogue['cases'] if row['id'] == args.case)
    out = Path(tempfile.mkdtemp(prefix='anonymous-arguments-' + args.case + '-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    watched = [ROOT / 'spec/semantics/383-anonymous-classes.watsup', CATALOGUE,
               ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'passed': False, 'case': args.case, 'source_sha256': sha(source),
              'inputs_before': before, 'raw': str(out)}
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
        filename = base64.b64encode(os.fsencode(source)).decode()
        checks = assertions(args.case, checked['fixture'], filename,
                            base64.b64decode(row['stdout_base64']))
        fixture = out / 'protocol.watsup'
        fixture.write_text(PREFIX + 'dec $body() : bool\ndef $body() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks) +
                           'dec $main() : bool\ndef $main() = $body()\n')
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       *[str(ROOT / module) for module in modules], str(fixture)],
                                      out / 'numeric', 120, ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True, assertions=len(checks), fixture_sha256=sha(fixture))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['inputs_after'] = {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_before'] == report['inputs_after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
