#!/usr/bin/env python3
"""Independent source-reached exception callback guards and ownership checks."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('exception_handler_review_cases.json').read_text())}
VALID = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
         '$call_descriptors_valid(S)', '$class_state_valid(S)',
         '$heap_valid($heap_graph(S))']
DONE = ['S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))']
CURRENT = ['S.CURRENT = (pcallcontext)', 'S.FRAMES = pframe :: pframe_tail*',
           'pframe.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_saved*',
           '$exception_context_valid(S, pcallcontext)',
           'pexceptioncall.TARGET = (pcallcontext.TARGET)',
           'pcallcontext.CALLSITE = eps', 'pcallcontext.LINE = $(-1)',
           'pcallcontext.ARGC = 1', 'pframe.CONTEXT = eps',
           'pframe.LOCALS = eps', 'pframe.ORIGIN = eps']
STAGE_CURRENT = ('S.CURRENT = (pcallcontext) -- if '
                 '$exception_context_kind(S, pcallcontext)')

CASES = {
    'pending-raw-registry': {
        'source': '<?php class C{static function h($e){}}'
                  'set_exception_handler([new C,"h"]);throw new Exception;',
        'stage': 'S.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: ptask_tail*',
        'checks': [
            'S.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: ptask_tail*',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.EXCEPTIONHANDLER = eps',
            'S.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue?)*',
            'pexceptioncall.CALLBACK = PARRAY n_raw',
            'pexceptioncall.RAW = (S.ARRAYS[n_raw])',
            'pexceptioncall.TARGET = eps', 'pexceptioncall.SENT = eps',
            '$task_nodes(EXCEPTION_HANDLER_INVOKE pexceptioncall) = [HOBJECT pexceptioncall.OBJECT]',
            '$call_task_valid(S, EXCEPTION_HANDLER_INVOKE pexceptioncall)',
            '~$call_task_valid(S, EXCEPTION_HANDLER_INVOKE pexceptioncall[.OBJECT = |S.OBJECTS|])',
            '~$call_task_valid(S, EXCEPTION_HANDLER_INVOKE pexceptioncall[.RAW = ($array_empty())])',
            '~$call_task_valid(S[.EXCEPTIONHANDLERS = eps], EXCEPTION_HANDLER_INVOKE pexceptioncall)',
            '~$call_task_valid(S[.EXCEPTIONHANDLER = (pexceptioncall.CALLBACK)], EXCEPTION_HANDLER_INVOKE pexceptioncall)',
            *VALID,
            'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
        ],
    },
    'zero-formals-original-extra': {
        'source': SOURCES['handler-zero-formals-extra-arg'],
        'stage': 'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* -- if ' + STAGE_CURRENT,
        'checks': [
            *CURRENT, 'pcallcontext.EXTRA = [KNOWN (POBJECT pexceptioncall.OBJECT)]',
            'pexceptioncall.SENT = (KNOWN (POBJECT pexceptioncall.OBJECT))',
            '~$exception_result_valid(S, pexceptioncall[.SENT = (KNOWN PNULL)])',
            '~$exception_context_valid(S, pcallcontext[.EXTRA = [KNOWN PNULL]])',
            '~$exception_context_valid(S, pcallcontext[.ARGC = 0])',
            '~$exception_context_valid(S, pcallcontext[.LINE = 0])',
            '~$exception_context_valid(S, pcallcontext[.CALLSITE = (pcallcontext.FUNCTION)])',
            '~$exception_context_valid(S[.FRAMES = eps], pcallcontext)',
            '~$exception_context_valid(S[.FRAMES = [pframe[.ORIGIN = (pcallcontext.FUNCTION)]]], pcallcontext)',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
        ],
    },
    'saved-private-caller': {
        'source': SOURCES['saved-caller-scope'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_SET_EXCEPTION_HANDLER '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if ~$exception_context_kind(S, pcallcontext) '
                  '-- if S.FRAMES = [pframe_saved, pframe_global] '
                  '-- if pframe_global.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_saved*'),
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'S.FRAMES = [pframe_saved, pframe_global]',
            'pframe_saved.CONTEXT = (pcallcontext_handler)',
            'pframe_global.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_saved*',
            'pcallcontext.LEXICAL_CLASS = eps',
            'pcallcontext_handler.LEXICAL_CLASS = (porigin_class)',
            '$exception_context_valid(S, pcallcontext_handler)',
            '~$exception_context_valid(S, pcallcontext)',
            '$call_saved_context_valid(S, pframe_saved)',
            '~$exception_context_valid(S, pcallcontext_handler[.ARGC = 2])',
            '~$exception_context_valid(S[.FRAMES = [pframe_saved, pframe_global[.CONTEXT = (pcallcontext)]]], pcallcontext_handler)',
            '~$exception_context_valid(S[.FRAMES = [pframe_saved, pframe_global[.TODO = eps]]], pcallcontext_handler)',
            '$error_handler_resolution(S, PSTRING $ptascii("C::h")) = HANDLERINVALID n_reason*',
            *VALID, 'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL', *DONE,
        ],
    },
    'retired-static-selector': {
        'source': '<?php class C{static function h($e){global $raw;restore_exception_handler();'
                  'restore_exception_handler();$raw[0]="C";echo func_num_args();}}'
                  '$raw=[new C,"h"];set_exception_handler($raw);throw new Exception;',
        'stage': 'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* -- if ' + STAGE_CURRENT,
        'checks': [
            *CURRENT, 'pexceptioncall.CALLBACK = PARRAY n_raw',
            'pexceptioncall.RAW = (parray)',
            'parray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_selector)), ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("h")))]',
            '~((HOBJECT n_selector) <- S.ALLOCATIONS)',
            'S.ARRAYS[n_raw].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING $ptascii("C"))), ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("h")))]',
            'pcallcontext.RECEIVER = eps', '$target_nodes(pcallcontext.TARGET) = eps',
            '$task_nodes(EXCEPTION_HANDLER_RESULT pexceptioncall) = [HOBJECT pexceptioncall.OBJECT]',
            'S.EXCEPTIONHANDLER = eps', 'S.EXCEPTIONHANDLERS = eps',
            '$exception_result_valid(S, pexceptioncall)',
            '~$exception_result_valid(S, pexceptioncall[.RAW = ($array_empty())])',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
        ],
    },
    'byref-rebound-retired-send-cell': {
        'source': '<?php function h(&$e){$e=null;}set_exception_handler("h");throw new Exception;',
        'stage': 'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*',
        'checks': [
            'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pexceptioncall.SENT = (REFERENCE n_cell)',
            'S.STORE[n_cell] = DEFINED PNULL', '~((HCELL n_cell) <- S.ALLOCATIONS)',
            '$exception_result_valid(S, pexceptioncall)',
            '$task_nodes(EXCEPTION_HANDLER_RESULT pexceptioncall) = [HOBJECT pexceptioncall.OBJECT]',
            '~$exception_result_valid(S, pexceptioncall[.SENT = (REFERENCE $(|S.STORE|))])',
            *VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S.TODO', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
            '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
        ],
    },
    'ignored-reference-return': {
        'source': '<?php function &h($e){$r=false;return $r;}set_exception_handler("h");throw new Exception;',
        'stage': 'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*',
        'checks': [
            'S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*',
            'S.RESULT = REFERENCE n_cell', 'S.STORE[n_cell] = DEFINED (PBOOL false)',
            '(HCELL n_cell) <- S.ALLOCATIONS',
            '$call_reference_operand_valid(S, S.RESULT)',
            '$exception_return_operand(S.RESULT)',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            'S_done.RESULT = KNOWN PNULL', '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
            '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
        ],
    },
    'warning-nested-throw-resumes-selected': {
        'source': SOURCES['byref-warning-installs-throws'],
        'stage': 'S.TODO = (EXCEPTION_HANDLER_ENTER pexceptioncall) :: ptask_tail*',
        'checks': [
            'S.TODO = (EXCEPTION_HANDLER_ENTER pexceptioncall) :: ptask_tail*',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pexceptioncall.CALLBACK = PSTRING $ptascii("h")',
            'pexceptioncall.TARGET = (pcalltarget)', 'pexceptioncall.SENT = eps',
            '$target_function(S, pcalltarget) = (pfunction)',
            'S.ORIGIN = (pfunction.ORIGIN)',
            '$throwable_field(S, pexceptioncall.OBJECT, "message") = PSTRING $ptascii("outer")',
            'S.EXCEPTIONHANDLER = (PSTRING $ptascii("other"))',
            '$call_task_valid(S, EXCEPTION_HANDLER_ENTER pexceptioncall)',
            '~$call_task_valid(S, EXCEPTION_HANDLER_ENTER pexceptioncall[.SENT = (KNOWN PNULL)])',
            *VALID, 'S_one = $drive(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.CURRENT = (pcallcontext)', '$exception_context_valid(S_one, pcallcontext)',
            'pcallcontext.TARGET = pcalltarget', 'pcallcontext.ARGC = 1',
            'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
        ],
    },
    'throw-retains-original-in-trace': {
        'source': SOURCES['handler-throws'], 'stage': STAGE_CURRENT,
        'checks': [
            *CURRENT, *VALID, 'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = UNCAUGHT n_new', *DONE,
            'n_new =/= pexceptioncall.OBJECT',
            '(HOBJECT n_new) <- S_done.ALLOCATIONS',
            '$throwable_field(S_done, n_new, "trace") = PARRAY n_trace',
            '$entry_lookup(S_done.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_handler))',
            '$trace_array_field(S_done, n_handler, $ptascii("args")) = PARRAY n_arguments',
            'S_done.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT pexceptioncall.OBJECT))]',
            '$heap_owners($heap_graph(S_done), HOBJECT pexceptioncall.OBJECT) = 1',
        ],
    },
    'exit-retires-original': {
        'source': SOURCES['handler-exit'], 'stage': STAGE_CURRENT,
        'checks': [
            *CURRENT, *VALID, 'S_done = $drive(S, 1500)',
            'S_done.COMPLETION = EXITED 7', *DONE,
            '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
        ],
    },
}
def run(selected):
    assert not selected or set(selected) <= CASES.keys(), 'unknown state case'
    cases = {name: case for name, case in CASES.items() if not selected or name in selected}
    out = Path(tempfile.mkdtemp(prefix='exceptions-state-review-', dir=ROOT / '.tools'))
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    records = []
    print(out, flush=True)
    for name, case in cases.items():
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(case['source'])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], name
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], name
        finally:
            frontend.close()
            adapter.close()
        fixture = directory / 'test.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\ndef $stage(S) = true -- if ' + case['stage'] + '\n'
            'def $stage(S) = false -- otherwise\ndec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1))) '
            '-- if ~$stage(S) -- if $(n > 0) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, '
            + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 2000)[.COMPLETION = NORMAL]\n'
            '  -- if ' + case['stage'] + '\n'
            + ''.join('  -- ' + ('' if clause.startswith('PhpStep:') else 'if ') + clause + '\n'
                      for clause in case['checks']))
        process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                            *modules, fixture], directory, 'model', environment, 120)
        passed = not process['timeout'] and process['exit'] == 0 and (
            directory / 'model.stdout').read_bytes() == b'true\n' and not (
            directory / 'model.stderr').read_bytes()
        records.append({'id': name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'assertions': len(case['checks']) + 3, 'process': process, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            print((directory / 'model.stderr').read_text()[-2500:], flush=True)
            break
    report = {'revision': revision, 'selection': list(cases), 'records': records,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
              'passed': len(records) == len(cases) and all(row['passed'] for row in records)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
