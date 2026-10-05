#!/usr/bin/env python3
"""A real included trait keeps its incoming constant demand file and line."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/trait_data_public_object_initializer_file_review_cases.json'
HELPER = ROOT / 'tests/semantics/trait_public_object_initializer_review.watsup'
CASE = 'incoming-trait-constant-public-fcc-type-error-keeps-distinct-fetch-line'
PREFIX = '''dec $await(pstate, nat) : pstate
def $await(S, n) = S -- if S.COMPLETION = SOURCE_PENDING
def $await(S, n) = $await($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET -- if $(n > 0)
def $await(S, n) = S -- otherwise
dec $class_stage(pstate) : bool
def $class_stage(S) = true
  -- if S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin_c)
  -- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c)
  -- if pclassdesc_c.NAME = $ptascii("C")
def $class_stage(S) = false -- otherwise
dec $seek_class(pstate, nat) : pstate
def $seek_class(S, n) = S -- if $class_stage(S)
def $seek_class(S, n) = $seek_class($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$class_stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek_class(S, n) = S -- otherwise
'''

CHECKS = [
    'S_wait.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_wait)',
    'S_parse.COMPLETION = SOURCE_PENDING',
    '$call_descriptors_valid(S_parse)',
    '$class_stage(S)',
    'S.CURRENT = eps',
    'S.FRAMES = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    'S.ORIGIN = (porigin_c)',
    '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
    'pclassdesc_c.LINE = 5',
    '$class_named(S.CLASSNAMES, $ptascii("t")) = (porigin_t)',
    '$class_at(S.CLASSES, porigin_t) = (pclassdesc_t)',
    'porigin_t = PORIGIN 1 pcpath_t',
    'pclassdesc_t.KIND = "trait"',
    '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
    '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
    '$class_constant_desc(pclassdesc_p.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_p',
    'pclassconstantdesc_y.LINE = 2',
    '~pclassconstantdesc_y.FOLDED',
    '$trait_cache_object_source(S, pclassconstantdesc_y)',
    '$class_constant_desc(pclassdesc_t.CONSTANTS, $ptascii("X")) = (pclassconstantdesc_t)',
    'pclassconstantdesc_t.OWNER = porigin_t',
    'pclassconstantdesc_t.INITIALIZER = PORIGIN 1 pcpath_root',
    'porigin_root = pclassconstantdesc_t.INITIALIZER',
    '$origin_node(S.SOURCES, porigin_root) = (expression_root)',
    '$expression_line(expression_root) = 9',
    '$class_constant_desc(pclassdesc_c.CONSTANTS, $ptascii("X")) = (pclassconstantdesc_c)',
    'pclassconstantdesc_c.OWNER = porigin_c',
    '$review_trait_object_seed(S, pclassdesc_c, porigin_root) = (F_seed)',
    '$trait_recording(F_seed, pcpath_root)',
    'F_seed.EXTERNAL = (S)',
    'F_seed.RECORD = (pfrecorder)',
    'pfrecorder.CLASS = porigin_c',
    'pfrecorder.ROOT = porigin_root',
    'pfrecorder.TABLE = pclassdesc_c.CONSTANTS',
    '~$trait_recording(F_seed[.RECORD = (pfrecorder[.CLASS = PORIGIN 999 eps])], pcpath_root)',
    '~$trait_recording(F_seed[.SOURCE = $pcsource(999, F_seed.SOURCE.AST)], pcpath_root)',
    '$review_trait_object_start(F_seed, pcpath_root, pclassconstantdesc_y, 9) = ((S_start, ptraitcachecause))',
    'ptraitcachecause.CLASS = porigin_c',
    'ptraitcachecause.ROOT = porigin_root',
    'ptraitcachecause.TABLE = pclassdesc_c.CONSTANTS',
    'ptraitcachecause.LOOKUPS = [porigin_root]',
    'ptraitcachecause.PREFIX = |S.DECLARATIONS|',
    'ptraitcachecause.USERPREFIX = |S.USERCONSTANTS|',
    '$review_trait_object_error(F_seed, S_start, ptraitcachecause, 300) = ((F_seen, S_before, S_raw))',
    'S_before.TODO = (CLASS_CONST_BIND pclassconstantdesc_y.ORIGIN) :: ptask_bind_tail*',
    '$trait_cache_object_type_error(S_before)',
    'S_before.CONSTCONTEXT = (pconstantcontext_y)',
    'pconstantcontext_y.ORIGIN = pclassconstantdesc_y.ORIGIN',
    'pconstantcontext_y.LINE = 9',
    'S_raw.COMPLETION = THROWN "TypeError" ($ptascii("Cannot assign Closure to class constant P::Y of type int")) 9',
    'S_raw.ORIGIN = (porigin_root)',
    'S_raw.CONSTCONTEXT = eps',
    'S_raw.CLASSCONSTANTINIT = eps',
    'F_seen.RECORDED = [pfdiagnostic]',
    'pfdiagnostic.OWNER = porigin_p',
    'pfdiagnostic.LEVEL = 8192',
    'pfdiagnostic.LINE = 2',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause) = ((porigin_c, 9, ptraceframe_override*))',
    'ptraceframe_override* = [ptraceframe_demand]',
    'ptraceframe_demand.FUNCTION = $ptascii("[constant expression]")',
    'ptraceframe_demand.FILE = $call_sourcefile(S.FILES, porigin_c)',
    'ptraceframe_demand.LINE = 5',
    'S_baseline = $throwable_transition(S_before, S_raw)',
    'S_baseline.COMPLETION = THROWING n_throw_baseline',
    '$throwable_field(S_baseline, n_throw_baseline, "file") = PSTRING $call_sourcefile(S.FILES, porigin_t)',
    '$throwable_field(S_baseline, n_throw_baseline, "line") = PINT 9',
    '$eval_exception_trace($throwable_continuation(S_before, S_raw)) = eps',
    '$trait_cache_object_exception(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause) = (S_throw, ptraceframe_override*)',
    'S_throw.COMPLETION = THROWING n_throw',
    'S_throw.OBJECTS[n_throw] = THROWABLE pthrowable',
    'pthrowable.FILEORIGIN = (porigin_c)',
    '$throwable_field(S_throw, n_throw, "file") = PSTRING $call_sourcefile(S.FILES, porigin_c)',
    '$throwable_field(S_throw, n_throw, "line") = PINT 9',
    '$trait_cache_object_demand(F_seen[.RECORD = eps], pcpath_root, S_before, S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen[.RECORD = (pfrecorder[.CLASS = porigin_p])], pcpath_root, S_before, S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen[.RECORD = (pfrecorder[.ROOT = porigin_c])], pcpath_root, S_before, S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen[.LOOKUPS = [porigin_root]], pcpath_root, S_before, S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.CLASS = porigin_p]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.ROOT = porigin_c]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.LOOKUPS = [pclassconstantdesc_y.INITIALIZER]]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.PREFIX = 0]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw, ptraitcachecause[.USERPREFIX = $(ptraitcachecause.USERPREFIX + 1)]) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.SOURCES = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CODE = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.FILES = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CLASSES = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CLASSNAMES = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.DECLARATIONS = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.TODO = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CONSTCONTEXT = eps], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CLASSCONSTANTINIT = eps], S_raw, ptraitcachecause) = eps',
    'S_before.CLASSCONSTANTINIT = [pclassconstantcontext_y]',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CLASSCONSTANTINIT = [pclassconstantcontext_y[.ORIGIN = (porigin_c)]]], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.CLASSCONSTANTINIT = [pclassconstantcontext_y[.LINE = 2]]], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before[.RESULT = KNOWN (PINT 1)], S_raw, ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw[.ORIGIN = (porigin_c)], ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw[.COMPLETION = THROWN "TypeError" ($ptascii("Cannot assign Closure to class constant P::Y of type int")) 2], ptraitcachecause) = eps',
    '$trait_cache_object_demand(F_seen, pcpath_root, S_before, S_raw[.COMPLETION = THROWN "Error" ($ptascii("Cannot assign Closure to class constant P::Y of type int")) 9], ptraitcachecause) = eps',
    'F_error = $trait_cache_object_resume(F_seen, pcpath_root, pclassconstantdesc_y, 9, S_before, S_raw, ptraitcachecause)',
    '$trait_fold_error(F_error) = (ptraitdataerror)',
    'ptraitdataerror.KIND = "TypeError"',
    'ptraitdataerror.LINE = 9',
    'ptraitdataerror.MESSAGE = $ptascii("Cannot assign Closure to class constant P::Y of type int")',
    'ptraitdataerror.OWNER = porigin_c',
    'ptraitdataerror.TRACE = [ptraceframe]',
    'ptraceframe.FUNCTION = $ptascii("[constant expression]")',
    'ptraceframe.LINE = 5',
    'ptraceframe.FILE = $call_sourcefile(S.FILES, porigin_c)',
    'ptraceframe.CLASS = eps',
    'ptraceframe.ARGS = eps',
    'F_error.MEMORY.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
    'F_error.MEMORY.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
    'F_error.MEMORY.ALLOCATIONS = S.ALLOCATIONS',
    'F_error.MEMORY.OBJECTPROPS = S.OBJECTPROPS',
    'F_error.MEMORY.HELD = F_seen.MEMORY.HELD',
    '~$trait_recording(F_seen[.MEMORY = F_seen.MEMORY[.SOURCES = eps]], pcpath_root)',
    '$trait_member_fold(S, pclassdesc_c, porigin_root) = (F_fold)',
    '$trait_fold_error(F_fold) = (ptraitdataerror)',
    'PhpStep: S ~> S_failed',
    'S_failed.COMPLETION = REQUESTFATAL ($ptascii("CompileError")) ptbytes_fatal 5',
    'S_failed.ERRORORIGIN = (porigin_c)',
    '$class_named(S_failed.CLASSNAMES, $ptascii("c")) = eps',
    '$call_descriptors_valid(S_failed)',
    '$declaration_history_valid(S_failed)',
    '$class_constant_state_valid(S_failed)',
    '$heap_valid($heap_graph(S_failed))',
    'S_done = $drive(S_failed, 3000)',
    'S_done.COMPLETION = S_failed.COMPLETION',
    'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
    '$review_trait_initializer_output(S_done.EVENTS) = $ptascii("PRE;S;")',
    '$class_named(S_done.CLASSNAMES, $ptascii("c")) = eps',
    '$call_descriptors_valid(S_done)',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', DUNEJOBS='1')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    row = next(row for row in json.loads(CATALOGUE.read_text())['cases'] if row['id'] == CASE)
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    child = row['files'][0]
    assert hashlib.sha256(child['source'].encode()).hexdigest() == child['source_sha256']
    out = Path(tempfile.mkdtemp(prefix='trait266-demand-protocol-', dir=ROOT / '.tools'))
    path, child_path = out / 'source.php', out / child['name']
    path.write_text(row['source'])
    child_path.write_text(child['source'])
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    modules.append(HELPER)
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/php.watsup', ROOT / 'spec/semantics/modules.json',
              ROOT / 'spec/schema.json', ROOT / 'frontend/worker.php',
              ROOT / '_build/default/adapter/main.exe', runner, ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', Path(__file__), CATALOGUE]
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    encoded = lambda value: base64.b64encode(value).decode()
    try:
        def packet(source, file=False):
            request = {'op': 'parse-file' if file else 'parse', 'source': encoded(source)}
            if file:
                request.update(id='0', mode='file', profile='cli-raw-85',
                               requested=encoded(os.fsencode(child_path)),
                               resolved=encoded(os.fsencode(child_path)), opened=encoded(os.fsencode(child_path)))
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            return checked['fixture']
        main_ast = packet(path.read_bytes())
        child_ast = packet(child_path.read_bytes(), True)
    finally:
        frontend.close()
        adapter.close()
    seq = lambda value: '(' + str(list(value)) + ')'
    filename, dirname, childname = map(os.fsencode, (path, out, child_path))
    clauses = [
        'S_initial = $php_file_run(' + main_ast + ', 0, ' + seq(filename) + ', ' + seq(dirname) + ')',
        'S_wait = $await(S_initial[.COMPLETION = NORMAL], 500)',
        'S_parse = $file_open_resume(S_wait, FILE_OPENED 0 ' + seq(filename) + ' ' + seq(childname) + ' ' + seq(childname) + ' ' + seq(childname) + ' ' + seq(child_path.read_bytes()) + ')',
        'S_running = $file_parse_resume(S_parse, SOURCE_ACCEPT 1 ' + seq(child_path.read_bytes()) + ' ' + child_ast + ')',
        'S = $seek_class(S_running[.COMPLETION = NORMAL], 1000)',
        *CHECKS,
    ]
    fixture = out / 'test.watsup'
    fixture.write_text(PREFIX + 'dec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- ' + ('' if c.startswith('PhpStep:') else 'if ') + c + '\n' for c in clauses))
    command = [str(runner), *map(str, modules), str(fixture)]
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'mode': 'prepare' if args.prepare else 'check', 'source': CASE, 'command': command,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'DUNEJOBS': '1', 'PHP_SPEC_SCRIPT_ENCODING': None},
              'caps_seconds': 300, 'jobs': 1, 'supplied_conditions': len(CHECKS),
              'generated_setup_conditions': 5, 'inputs': before}
    if not args.prepare:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=300)
        (out / 'stdout').write_text(result.stdout)
        (out / 'stderr').write_text(result.stderr)
        report.update(exit=result.returncode, pass_=result.returncode == 0 and result.stdout == 'true\n' and not result.stderr)
    report['inputs_stable'] = before == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report.get('pass_', 'prepared'), flush=True)
    assert report['inputs_stable'] and (args.prepare or report['pass_'])


if __name__ == '__main__':
    main()
