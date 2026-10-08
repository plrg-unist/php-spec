#!/usr/bin/env python3
"""Fresh included REAL birth retains physical notice and incoming typed demand."""
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

CATALOGUE = HERE / 'trait_data_failed_real_review_cases.json'
HELPERS = [HERE / 'trait_public_object_initializer_review.watsup',
           HERE / 'trait_unpublished_real.watsup', HERE / 'trait_failed_real.watsup',
           HERE / 'trait_failed_real_crossfile_review.watsup']
CASE = 'crossfile-c-real-type'
CHECKS = [
    'S_wait.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_wait)',
    'S_parse.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_parse)',
    '$class_stage(S)',
    'S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*',
    r'S.CURRENT = eps /\ S.FRAMES = eps',
    'S.ORIGIN = (porigin_c)',
    '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
    'porigin_c = PORIGIN 0 pcpath_c',
    'pclassdesc_c.LINE = 6',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("t")) = (porigin_t)',
    '$class_at(S.CLASSES, porigin_t) = (pclassdesc_t)',
    'porigin_t = PORIGIN 1 pcpath_t',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    'S_seed = S[.TODO = ptask_tail*]',
    '$class_constant_desc(pclassdesc_t.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_t_y)',
    'S_partial = $trait_data_constant_one(S_seed, pclassdesc_c, pclassdesc_t, pclassconstantdesc_t_y, eps)',
    'S_partial.COMPLETION = NORMAL',
    '$class_at(S_partial.CLASSES, porigin_c) = (pclassdesc_partial)',
    '$class_constant_desc(pclassdesc_partial.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_c',
    'pclassconstantdesc_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c pclassconstantdesc_t_y.ORIGIN',
    'pclassconstantdesc_y.INITIALIZER = pclassconstantdesc_t_y.INITIALIZER',
    '$class_constant_desc(pclassdesc_t.CONSTANTS, $ptascii("K")) = (pclassconstantdesc_k)',
    'porigin_root = pclassconstantdesc_k.INITIALIZER',
    'porigin_root = PORIGIN 1 pcpath_root',
    '$origin_node(S.SOURCES, porigin_root) = (expression_root)',
    '$expression_line(expression_root) = 9',
    '$review_trait_object_seed(S_partial, pclassdesc_partial, porigin_root) = (F_seed)',
    '$review_trait_real_start(F_seed, pcpath_root, pclassconstantdesc_y, 9) = ((S_start, ptraitcachecause))',
    'ptraitcachecause.TABLE = pclassdesc_partial.CONSTANTS',
    'ptraitcachecause.LOOKUPS = [porigin_root]',
    '$trait_real_active(S_start, ptraitcachecause)',
    'n_c = |S_start.OBJECTS|',
    'S_birth = $review_trait_real_birth(S_start, ptraitcachecause, n_c, 300)',
    '$constant_callable_record(S_birth.CONSTANTCLOSURES, n_c) = (pconstantclosure_c)',
    '$trait_real_birth_at(S_birth.CLASSCONSTANTHISTORY, n_c) = ((pconstantclosure_c.SITE, ptraitcachecause))',
    '$constant_callable_record_valid(S_birth, pconstantclosure_c)',
    '$review_trait_real_notice(S_birth, ptraitcachecause, 300) = ((S_notice, S_notice_next))',
    'S_notice.ORIGIN = (porigin_notice)',
    '$origin_source(porigin_notice) = PORIGIN 1 pcpath_notice',
    'S_notice_next.EVENTS = [DIAGNOSTIC_SOURCE 1 "Deprecated" ptbytes_notice 3]',
    '$trait_cache_object_events(porigin_c, porigin_notice, S_notice_next.EVENTS) = ([pfdiagnostic_notice])',
    'pfdiagnostic_notice.OWNER = porigin_c',
    'pfdiagnostic_notice.SITE = porigin_notice',
    r'pfdiagnostic_notice.LEVEL = 8192 /\ pfdiagnostic_notice.LINE = 3',
    '$trait_cache_object_events(porigin_c, porigin_notice, [DIAGNOSTIC_SOURCE 999 "Deprecated" ptbytes_notice 3]) = eps',
    '$review_trait_object_error(F_seed, S_start, ptraitcachecause, 300) = ((F_seen, S_before, S_raw))',
    'F_seen.RECORDED = [pfdiagnostic_notice]',
    'S_before.TODO = (CLASS_CONST_BIND pclassconstantdesc_y.ORIGIN) :: ptask_bind_tail*',
    '$trait_cache_object_type_error(S_before)',
    '$trait_real_active(S_before, ptraitcachecause)',
    '$trait_cache_object_error_allowed(S_before, ptraitcachecause)',
    'S_before.CLASSCONSTANTINIT = [pclassconstantcontext]',
    r'pclassconstantcontext.ORIGIN = (porigin_root) /\ pclassconstantcontext.LINE = 9',
    'S_raw.COMPLETION = THROWN "TypeError" ($ptascii("Cannot assign Closure to class constant C::Y of type int")) 9',
    r'S_raw.CLASSCONSTANTINIT = eps /\ S_raw.CONSTCONTEXT = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause) = ((porigin_c, 9, [ptraceframe]))',
    'ptraceframe.FILE = $call_sourcefile(S.FILES, porigin_c)',
    r'ptraceframe.FUNCTION = $ptascii("[constant expression]") /\ ptraceframe.LINE = 6',
    '$trait_cache_object_exception(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause) = (S_throw, [ptraceframe])',
    'S_throw.COMPLETION = THROWING n_throw',
    '$throwable_field(S_throw, n_throw, "file") = PSTRING $call_sourcefile(S.FILES, porigin_c)',
    '$throwable_field(S_throw, n_throw, "line") = PINT 9',
    '$trait_cache_object_demand(F_seen[.RECORD = eps], pcpath_root, S_before, S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.ROOT = porigin_c]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.TABLE = eps]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.LOOKUPS = eps]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.PREFIX = $(ptraitcachecause.PREFIX + 1)]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.SOURCES = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.FILES = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.TODO = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CLASSCONSTANTINIT = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CLASSCONSTANTINIT = [pclassconstantcontext[.LINE = 3]]], S_raw, ptraitcachecause) = eps',
    'F_error = $trait_cache_object_resume(F_seen, pcpath_root, pclassconstantdesc_y, 9, S_before, S_raw, ptraitcachecause)',
    '$trait_fold_error(F_error) = (ptraitdataerror)',
    r'ptraitdataerror.OWNER = porigin_c /\ ptraitdataerror.LINE = 9',
    'ptraitdataerror.TRACE = [ptraceframe]',
    'S_link = $review_trait_real_failed_link(S_seed, pclassdesc_c)',
    '$trait_failed_cache_ready(S_seed, S_link)',
    'S_link.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_fatal 6',
    'PhpStep: S ~> S_failed',
    'S_failed.COMPLETION = S_link.COMPLETION',
    'S_failed.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
    '$constant_callable_record(S_failed.CONSTANTCLOSURES, n_c) = (pconstantclosure_c)',
    '$trait_real_retired_receipt(S_failed, pconstantclosure_c) = (pclassconstantdesc_y)',
    '~((HOBJECT n_c) <- S_failed.ALLOCATIONS)',
    '$closure_scope_at(S_failed.CLOSURESCOPES, n_c) = eps',
    '$call_descriptors_valid(S_failed)',
    '$declaration_history_valid(S_failed)',
    '$class_constant_state_valid(S_failed)',
    '$heap_valid($heap_graph(S_failed))',
    'S_done = $drive(S_failed, 3000)',
    r'S_done.COMPLETION = S_failed.COMPLETION /\ S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
    '$review_trait_initializer_output(S_done.EVENTS) = $ptascii("PRE;S;")',
    '$constant_callable_record_valid(S_done, pconstantclosure_c)',
    '$call_descriptors_valid(S_done)',
    '$declaration_history_valid(S_done)',
    '$class_constant_state_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    env = os.environ.copy()
    env.update(LC_ALL='C', TZ='UTC', DUNEJOBS='1')
    env.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row = next(row for row in json.loads(CATALOGUE.read_text())['cases'] if row['id'] == CASE)
    child = row['files'][0]
    out = Path(tempfile.mkdtemp(prefix='trait297-crossfile-review-', dir=ROOT / '.tools'))
    source, child_path = out / 'source.php', out / child['name']
    source.write_text(row['source'])
    child_path.write_text(child['source'])
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())] + HELPERS
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/php.watsup', ROOT / 'spec/semantics/modules.json',
              ROOT / 'spec/schema.json', ROOT / 'frontend/worker.php',
              ROOT / '_build/default/adapter/main.exe', runner, ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', Path(__file__), Path(file_driver.__file__), CATALOGUE]
    fingerprints = lambda: {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    before = fingerprints()
    frontend = file_driver.Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                                  'extension=' + str(ROOT / '.tools/php-file.so'),
                                  str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = file_driver.Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        def packet(data, file=False):
            request = {'op': 'parse-file' if file else 'parse', 'source': base64.b64encode(data).decode()}
            if file:
                filename = base64.b64encode(os.fsencode(child_path)).decode()
                request.update(id='0', mode='file', profile='cli-raw-85', requested=filename, resolved=filename, opened=filename)
            parsed = frontend.request(request)
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
            return checked['fixture']
        main_ast = packet(source.read_bytes())
        child_ast = packet(child_path.read_bytes(), True)
    finally:
        frontend.close()
        adapter.close()
    seq = lambda value: '(' + str(list(value)) + ')'
    filename, dirname, childname = map(os.fsencode, (source, out, child_path))
    clauses = [
        'S_initial = $php_file_run(' + main_ast + ', 0, ' + seq(filename) + ', ' + seq(dirname) + ')',
        'S_wait = $await(S_initial[.COMPLETION = NORMAL], 500)',
        'S_parse = $file_open_resume(S_wait, FILE_OPENED 0 ' + seq(filename) + ' ' + seq(childname) + ' ' + seq(childname) + ' ' + seq(childname) + ' ' + seq(child_path.read_bytes()) + ')',
        'S_running = $file_parse_resume(S_parse, SOURCE_ACCEPT 1 ' + seq(child_path.read_bytes()) + ' ' + child_ast + ')',
        'S = $seek_class(S_running[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]',
        *CHECKS,
    ]
    fixture = out / 'test.watsup'
    fixture.write_text(file_driver.PREFIX + 'dec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- ' + ('' if c.startswith('PhpStep:') else 'if ') + c + '\n' for c in clauses))
    command = [str(runner), '--sl', *map(str, modules), str(fixture)]
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source': CASE, 'command': command, 'cwd': str(ROOT), 'mode': 'SL',
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'DUNEJOBS': '1', 'PHP_SPEC_SCRIPT_ENCODING': None},
              'timeout_seconds': 120, 'jobs': 1, 'supplied_conditions': len(CHECKS),
              'generated_setup_conditions': 5, 'inputs': before, 'exit': None}
    (out / 'numeric.command.json').write_text(json.dumps(report, indent=2) + '\n')
    if not args.prepare:
        start = time.monotonic()
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
            (out / 'stdout').write_text(result.stdout)
            (out / 'stderr').write_text(result.stderr)
            report.update(exit=result.returncode, pass_=result.returncode == 0 and result.stdout == 'true\n' and not result.stderr)
        except subprocess.TimeoutExpired as error:
            (out / 'stdout').write_bytes(error.stdout or b'')
            (out / 'stderr').write_bytes(error.stderr or b'')
            report.update(timed_out=True, pass_=False)
        report['elapsed_seconds'] = round(time.monotonic() - start, 3)
    report['inputs_stable'] = before == fingerprints()
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report.get('pass_', 'prepared'), flush=True)
    assert report['inputs_stable'] and (args.prepare or report['pass_'])


if __name__ == '__main__':
    main()
