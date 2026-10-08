#!/usr/bin/env python3
"""Authentic second include rejects a reserved name during early binding."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'tests/semantics'
sys.path.insert(0, str(HERE))
import trait_public_object_demand_review_protocol as file_driver

CATALOGUE = HERE / 'trait_failed_name_cases.json'
HELPER = Path(__file__).with_name('trait_failed_name_early_review.watsup')
CHECKS = [
    'S_wait.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_wait)',
    'S_parse.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_parse)',
    '$class_stage(S)',
    'S.ORIGIN = (porigin_c)',
    'porigin_c = PORIGIN 0 pcpath_c',
    '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
    'pclassdesc_c.LINE = 5',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$failed_class_reserved(S, $ptascii("c")) = eps',
    'pdeclcause = $declaration_cause(S)',
    'PhpStep: S ~> S_after',
    'S_after.COMPLETION = STATICBYTES ptbytes_first 5',
    'S_after.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c pdeclcause]',
    '$failed_class_reserved(S_after, $ptascii("c")) = (pclassdesc_c)',
    'n_c = |S.OBJECTS|',
    '$constant_callable_record(S_after.CONSTANTCLOSURES, n_c) = (pconstantclosure_c)',
    '$trait_real_retired_receipt(S_after, pconstantclosure_c) = (pclassconstantdesc_y)',
    '$trait_real_birth_at(S_after.CLASSCONSTANTHISTORY, n_c) = ((pconstantclosure_c.SITE, ptraitcachecause_c))',
    'ptraitcachecause_c.PREFIX = |S.DECLARATIONS|',
    'S_wait_late = $review_failed_name_file_wait(S_after, 600)',
    'S_wait_late.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_wait_late)',
    'S_parse_late = $file_open_resume(S_wait_late, pfileopenresponse_new)',
    'S_parse_late.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_parse_late)',
    'S_parse_late.FILECONTEXTS = pfilecontext :: pfilecontext_tail*',
    'pfilecontext.PHASE = FILE_PARSE_WAIT',
    'pfilecontext.UNIT = (2)',
    'pfilecontext.OWNER = |S_parse_late.FRAMES|',
    '$origin_source(pfilecontext.SITE) = PORIGIN 0 pcpath_include',
    '$file_site_line(S_parse_late, pfilecontext.SITE) = 3',
    'pfilecontext.CALLER = $call_sourcefile(S_parse_late.FILES, porigin_c)',
    'pfilecontext.LEXICAL_CLASS = eps',
    'S_parse_late.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
    'S_parse_late.SHUTDOWN.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_first 5',
    '$eval_compile_fatal_current(S_parse_late) = eps',
    'S_parse_late.CURRENT = (pcallcontext_shutdown)',
    'pcallcontext_shutdown.LEXICAL_CLASS = eps',
    'pcallcontext_shutdown.CALLED_CLASS = eps',
    '$file_parse_response_valid(S_parse_late, psourceresponse_new)',
    '$review_failed_name_early_compile(S_parse_late, psourceresponse_new) = ((S_raw, P, pfilecontext, pfilecontext_tail*))',
    'S_raw.FILECONTEXTS = S_parse_late.FILECONTEXTS',
    'S_raw.CURRENT = S_parse_late.CURRENT',
    'S_raw.FRAMES = S_parse_late.FRAMES',
    'S_raw.COMPLETION = STATICBYTES ptbytes_new 2',
    'ptbytes_new = $ptascii("Cannot redeclare class C (previously declared in ") ++ $call_sourcefile(S.FILES, porigin_c) ++ [58] ++ $ntunsigned(pclassdesc_c.LINE) ++ [41]',
    'S_raw.ERRORORIGIN = (PORIGIN 2 eps)',
    'n_declarations = |S_raw.DECLARATIONS|',
    'S_raw.DECLARATIONS[$nabs($(n_declarations - 1))] = PDEXIT 2 (PCSLINK 0)',
    'P.PUBLICATIONS[0] = PPCP porigin_new n_diagnostics PPCLASS',
    'porigin_new = PORIGIN 2 pcpath_new',
    '$class_at(S_raw.CLASSES, porigin_new) = (pclassdesc_new)',
    'pclassdesc_new.NAME = $ptascii("c")',
    '$failed_class_file_stop(S_raw, pfilecontext, P)',
    '$file_compile_stop_trace(S_raw, pfilecontext, P) = [ptraceframe_include, ptraceframe_callback]',
    'ptraceframe_include.FILE = $call_sourcefile(S.FILES, porigin_c)',
    'ptraceframe_include.LINE = 3',
    'ptraceframe_include.FUNCTION = $ptascii("include")',
    'ptraceframe_include.CLASS = eps',
    'ptraceframe_include.TYPE = eps',
    'ptraceframe_include.ARGS = eps',
    '~ptraceframe_include.HASARGS',
    'ptraceframe_callback.FILE = eps',
    'ptraceframe_callback.LINE = $(-1)',
    'ptraceframe_callback.FUNCTION = $trace_context_function(S_parse_late, pcallcontext_shutdown)',
    'S_stop = $file_parse_resume(S_parse_late, psourceresponse_new)',
    'S_stop = $file_compile_result(S_raw, pfilecontext, pfilecontext_tail*, P)',
    'S_stop.COMPLETION = S_raw.COMPLETION',
    'S_stop.COMPILESTOP',
    'S_stop.TRACE = [ptraceframe_include, ptraceframe_callback]',
    'S_stop.FILECONTEXTS = pfilecontext_tail*',
    'S_stop.DECLARATIONS = S_raw.DECLARATIONS',
    '$class_named(S_stop.CLASSNAMES, $ptascii("c")) = eps',
    '$failed_class_reserved(S_stop, $ptascii("c")) = (pclassdesc_c)',
    '$failed_class_count(S_stop.DECLARATIONS, porigin_new) = 0',
    '$trait_real_retired_receipt(S_stop, pconstantclosure_c) = (pclassconstantdesc_y)',
    '$closure_scope_at(S_stop.CLOSURESCOPES, n_c) = eps',
    '~(HOBJECT n_c <- S_stop.ALLOCATIONS)',
    '~$constant_callable_value_valid(S_stop, n_c, pconstantclosure_c.SITE)',
    '$call_descriptors_valid(S_stop)',
    '$declaration_history_valid(S_stop)',
    '$class_constant_state_valid(S_stop)',
    '$heap_valid($heap_graph(S_stop))',
    '~$failed_class_file_stop(S_raw[.FILECONTEXTS = eps], pfilecontext, P)',
    'pfilecontext_owner = pfilecontext[.OWNER = $nabs($(pfilecontext.OWNER + 1))]',
    '~$failed_class_file_stop(S_raw[.FILECONTEXTS = pfilecontext_owner :: pfilecontext_tail*], pfilecontext_owner, P)',
    'pfilecontext_unit = pfilecontext[.UNIT = (1)]',
    '~$failed_class_file_stop(S_raw[.FILECONTEXTS = pfilecontext_unit :: pfilecontext_tail*], pfilecontext_unit, P)',
    'pfilecontext_site = pfilecontext[.SITE = porigin_c]',
    '~$failed_class_file_stop(S_raw[.FILECONTEXTS = pfilecontext_site :: pfilecontext_tail*], pfilecontext_site, P)',
    '~$failed_class_file_stop(S_raw[.COMPLETION = STATICBYTES ptbytes_new 3], pfilecontext, P)',
    '~$failed_class_file_stop(S_raw[.ERRORORIGIN = (PORIGIN 0 eps)], pfilecontext, P)',
    '~$failed_class_file_stop(S_raw, pfilecontext, P[.PUBLICATIONS = eps])',
    'S_no_checkpoint = S_raw[.DECLARATIONS = S_raw.DECLARATIONS[0:$nabs($(n_declarations - 1))] ++ [PDEXIT 2 PCSCOMPILER]]',
    '~$failed_class_file_stop(S_no_checkpoint, pfilecontext, P)',
    'n_tail = $nabs($(|S_stop.DECLARATIONS| - |S_after.DECLARATIONS|))',
    'pdeclaration_late* = S_stop.DECLARATIONS[|S_after.DECLARATIONS|:n_tail]',
    'S_wrong_owner = S_stop[.DECLARATIONS = S.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_new pdeclcause] ++ pdeclaration_late*]',
    '$failed_class_reserved(S_wrong_owner, $ptascii("c")) = eps',
    '$trait_real_retired_receipt(S_wrong_owner, pconstantclosure_c) = eps',
    '~$declaration_history_valid(S_wrong_owner)',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    row = next(row for row in json.loads(CATALOGUE.read_text())['cases'] if row['id'] == 'include-redeclare')
    out = Path(tempfile.mkdtemp(prefix='trait299-early-review-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_text(row['source'])
    children = [out / child['name'] for child in row['files']]
    for path, child in zip(children, row['files']):
        path.write_text(child['source'])
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())] + [HELPER]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/php.watsup', ROOT / 'spec/semantics/modules.json',
              ROOT / 'spec/schema.json', ROOT / 'frontend/worker.php',
              ROOT / '_build/default/adapter/main.exe', runner, ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', Path(__file__), Path(file_driver.__file__), CATALOGUE]
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    frontend = file_driver.Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                                  'extension=' + str(ROOT / '.tools/php-file.so'),
                                  str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = file_driver.Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        def packet(path, file=False):
            request = {'op': 'parse-file' if file else 'parse', 'source': base64.b64encode(path.read_bytes()).decode()}
            if file:
                filename = base64.b64encode(os.fsencode(path)).decode()
                request.update(id='0', mode='file', profile='cli-raw-85', requested=filename, resolved=filename, opened=filename)
            parsed = frontend.request(request)
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            return checked['fixture']
        main_ast = packet(source)
        first_ast, second_ast = [packet(path, True) for path in children]
    finally:
        frontend.close()
        adapter.close()
    seq = lambda value: '(' + str(list(value)) + ')'
    filename, dirname, first_name, second_name = map(os.fsencode, [source, out, *children])
    clauses = [
        'S_initial = $php_file_run(' + main_ast + ', 0, ' + seq(filename) + ', ' + seq(dirname) + ')',
        'S_wait = $review_failed_name_file_wait(S_initial, 600)',
        'S_parse = $file_open_resume(S_wait, FILE_OPENED 0 ' + seq(filename) + ' ' + seq(first_name) + ' ' + seq(first_name) + ' ' + seq(first_name) + ' ' + seq(children[0].read_bytes()) + ')',
        'S_running = $file_parse_resume(S_parse, SOURCE_ACCEPT 1 ' + seq(children[0].read_bytes()) + ' ' + first_ast + ')',
        'S = $seek_class(S_running[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
        'pfileopenresponse_new = FILE_OPENED 1 ' + seq(filename) + ' ' + seq(second_name) + ' ' + seq(second_name) + ' ' + seq(second_name) + ' ' + seq(children[1].read_bytes()),
        'psourceresponse_new = SOURCE_ACCEPT 2 ' + seq(children[1].read_bytes()) + ' ' + second_ast,
        *CHECKS,
    ]
    fixture = out / 'test.watsup'
    fixture.write_text(file_driver.PREFIX + 'dec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- ' + ('' if clause.startswith('PhpStep:') else 'if ') + clause + '\n' for clause in clauses))
    command = [str(runner), '--sl', *map(str, modules), str(fixture)]
    report = {'private_head': 'fde034abdaca1c5e470aaffd6c9f0e009b79ef45',
              'source': 'include-redeclare', 'command': command, 'cwd': str(ROOT), 'mode': 'SL',
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'timeout_seconds': 120, 'jobs': 1,
              'supplied_conditions': len(CHECKS), 'generated_setup_conditions': 7, 'inputs': before, 'exit': None}
    (out / 'numeric.command.json').write_text(json.dumps(report, indent=2) + '\n')
    if not args.prepare:
        environment = os.environ.copy()
        environment.update(LC_ALL='C', TZ='UTC')
        start = time.monotonic()
        try:
            result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, timeout=120)
            (out / 'stdout').write_text(result.stdout)
            (out / 'stderr').write_text(result.stderr)
            report.update(exit=result.returncode, pass_=result.returncode == 0 and result.stdout == 'true\n' and not result.stderr)
        except subprocess.TimeoutExpired as error:
            (out / 'stdout').write_bytes(error.stdout or b'')
            (out / 'stderr').write_bytes(error.stderr or b'')
            report.update(timed_out=True, pass_=False)
        report['elapsed_seconds'] = round(time.monotonic() - start, 3)
    report['inputs_stable'] = before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report.get('pass_', 'prepared'), flush=True)
    assert report['inputs_stable'] and (args.prepare or report['pass_'])


if __name__ == '__main__':
    main()
