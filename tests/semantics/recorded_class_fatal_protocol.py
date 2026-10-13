#!/usr/bin/env python3
"""A real deferred class binding draining its retained compiler-fatal record."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_redeclare_fatal_protocol as source
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

fatal, retirement = source.fatal, source.retirement
ROOT, inputs, types = source.ROOT, source.inputs, source.types
seq, byte_expr, b64 = source.seq, source.byte_expr, source.b64
CASES = {
    'file-record': ('static-native-v37', 'file-fatal-shutdown-class-redeclaration'),
    'eval-ordinary': ('static-native-v37', 'eval-fatal-shutdown-class-redeclaration'),
}
PREFIX = source.PREFIX + r'''
dec $test_class_stage(pstate) : bool
def $test_class_stage(S) = true
  -- if S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*
def $test_class_stage(S) = false -- otherwise
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_class_seek(pstate, nat) : pstate
def $test_class_seek(S, 0) = S
def $test_class_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_class_stage(S) \/ S.COMPLETION = SOURCE_PENDING
def $test_class_seek(S, n) = $test_class_seek($drive_steps($test_running(S), 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_class_stage(S) /\ S.COMPLETION =/= SOURCE_PENDING
dec $test_one(pstate) : pstate
def $test_one(S) = S_next -- PhpStep: S ~> S_next
dec $test_stderr_item(pevent) : nat
def $test_stderr_item(STDERR n*) = 1
def $test_stderr_item(pevent) = 0 -- otherwise
dec $test_stderr_count(pevent*) : nat
def $test_stderr_count(eps) = 0
def $test_stderr_count(pevent :: pevent_tail*) = $($test_stderr_item(pevent) + $test_stderr_count(pevent_tail*))
'''


def prepare(out, sources, stage):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')

        def checked(data, mode, unit=0, path=None):
            request = {'op': 'parse', 'source': b64(data)} if mode == 'main' else {
                'op': 'parse-file' if mode == 'file' else 'parse-eval', 'id': str(unit), 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(data)}
            if mode == 'file':
                request.update({key: b64(os.fsencode(path)) for key in ['requested', 'resolved', 'opened']})
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            return parsed['ast'], adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']

        case, native = fatal.native_record(sources, *CASES[stage])
        main_ast, main = checked((case / 'main.php').read_bytes(), 'main')
        if stage == 'eval-ordinary':
            outer, = [node for _, node, ancestors in retirement.nodes(main_ast['program'])
                if node['node'] == 'Expr_Eval' and 'Stmt_Function' not in ancestors]
            first_bytes = base64.b64decode(outer['fields'][0]['fields'][0]['bytes'])
            first_ast, first = checked(first_bytes, 'eval', 1)
            inner, = [node for _, node, _ in retirement.nodes(first_ast['program']) if node['node'] == 'Expr_Eval']
            second_bytes = base64.b64decode(inner['fields'][0]['fields'][0]['bytes'])
            _, second = checked(second_bytes, 'eval', 2)
            response_1 = 'SOURCE_ACCEPT 1 ' + seq(first_bytes) + ' ' + first
            response_2 = 'SOURCE_ACCEPT 2 ' + seq(second_bytes) + ' ' + second
            checks = ['S_wait_1 = $php_file_run(' + main + ',2000,' + byte_expr(os.fsencode(case / 'main.php')) + ',' + byte_expr(os.fsencode(case)) + ')',
                'S_wait_1.COMPLETION = SOURCE_PENDING', '$eval_response_valid(S_wait_1,' + response_1 + ')',
                'S_ready_1 = $eval_resume(S_wait_1,' + response_1 + ')',
                'S_wait_2 = $drive_steps(S_ready_1,2000)', 'S_wait_2.COMPLETION = SOURCE_PENDING',
                '$eval_response_valid(S_wait_2,' + response_2 + ')', 'S_compiled_2 = $eval_resume(S_wait_2,' + response_2 + ')',
                '$recorded_compile_fatal(S_compiled_2.COMPLETION)', 'S_compiled_2.RECORDEDCOMPILEERROR = eps',
                'S_final = $drive_steps(S_compiled_2,2000)', 'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE',
                'S_final.EXITSTATUS = 255', 'S_final.RECORDEDCOMPILEERROR = eps',
                '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')', '$test_stderr_count(S_final.EVENTS) = 2',
                'S_final.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_new]',
                'pdestructioncleanup_new.SOURCE = DESTRUCTOR_FATAL pdestructionfatal',
                '$recorded_class_snapshot(pdestructionfatal)', '~$recorded_runtime_snapshot_required(pdestructionfatal)',
                'S_history = $eager_fatal_history(S_final,pdestructionfatal)',
                'S_history.DECLARATIONS = pdestructionfatal.DECLARATIONS', 'S_history.RECORDEDCOMPILEERROR = eps',
                '$recorded_history_index(S_final,S_history.DECLARATIONS) = eps',
                'S_history.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*',
                'S_history.ORIGIN = (porigin_decl)', '$class_at(S_history.CLASSES,porigin_decl) = (pclassdesc)',
                'pclassdesc.NAME = $ptascii("G")', '~$recorded_class_pending(S_history,pclassdesc)',
                '$eager_fatal_source_valid(S_history,pdestructionfatal.COMPLETION)',
                '$eager_fatal_valid(S_final,pdestructioncleanup_new,pdestructionfatal)', *fatal.public('S_final')]
            (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
            (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            return
        # Pick an authentic echo in the same shutdown function as the declaration.
        shutdown = next(node for _, node, _ in retirement.nodes(main_ast['program'])
            if node['node'] == 'Stmt_Function' and node['fields'][2]['fields'][0]['bytes'] == b64(b'source_shutdown'))
        shutdown_path = next(path for path, node, _ in retirement.nodes(main_ast['program']) if node is shutdown)
        echo_path = next(path for path, node, _ in retirement.nodes(main_ast['program'])
            if node['node'] == 'Stmt_Echo' and path[:len(shutdown_path)] == shutdown_path)
        echo = 'PORIGIN 0 (' + '[' + ', '.join(echo_path) + ']' + ')'
        checks = ['S_open_1 = $php_file_run(' + main + ',2000,' + byte_expr(os.fsencode(case / 'main.php')) + ',' + byte_expr(os.fsencode(case)) + ')']
        for unit, filename in [(1, 'unit.php'), (2, 'inner.php')]:
            data = (case / filename).read_bytes()
            _, fixture = checked(data, 'file', unit, case / filename)
            opened, parsed, compiled = 'S_open_' + str(unit), 'S_parse_' + str(unit), 'S_compiled_' + str(unit)
            context = 'pfilecontext_open_' + str(unit)
            if unit == 2:
                checks += [opened + ' = $drive_steps(S_compiled_1,2000)']
            response = 'FILE_OPENED ' + context + '.NONCE ' + context + '.CALLER ' + context + '.REQUESTED ' + seq(os.fsencode(case / filename)) + ' ' + seq(os.fsencode(case / filename)) + ' ' + seq(data)
            accepted = 'SOURCE_ACCEPT ' + str(unit) + ' ' + seq(data) + ' ' + fixture
            checks += [opened + '.COMPLETION = SOURCE_PENDING', opened + '.FILECONTEXTS = ' + context + ' :: pfilecontext_tail_' + str(unit) + '*',
                '$file_open_response_valid(' + opened + ',' + response + ')', parsed + ' = $file_open_resume(' + opened + ',' + response + ')',
                '$file_parse_response_valid(' + parsed + ',' + accepted + ')', compiled + ' = $file_parse_resume(' + parsed + ',' + accepted + ')']
        checks += ['$recorded_compile_fatal(S_compiled_2.COMPLETION)',
            *fatal.reached('S', '$test_class_seek(S_compiled_2,1800)'),
            'S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*',
            'S.ORIGIN = (porigin_decl)', '$class_at(S.CLASSES,porigin_decl) = (pclassdesc_decl)',
            'pclassdesc_decl.NAME = $ptascii("G")', 'pclassdesc_decl.LINE = 9',
            'pclassdesc_decl.KIND = "class"', '~$class_internal(pclassdesc_decl.NAME)',
            '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_decl.NAME)) = (porigin_old)',
            '$class_at(S.CLASSES,porigin_old) = (pclassdesc_old)',
            'porigin_old =/= porigin_decl', 'pclassdesc_old.LINE = 3',
            '$origin_node(S.SOURCES,porigin_decl) = (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)',
            '~$declaration_early(S.DECLARATIONS,porigin_decl,PPCLASS)',
            'S_binding = $activate_class_base_body(S[.TODO = ptask_tail*],pclassdesc_decl)',
            '$recorded_compile_fatal(S_binding.COMPLETION)', 'S_binding.DECLARATIONS = S.DECLARATIONS',
            'S_binding.CALLABLES = S.CALLABLES', 'S_binding.CLASSNAMES = S.CLASSNAMES',
            'S.RECORDEDCOMPILEERROR = (n_record)',
            '$recorded_compile_at(S.DECLARATIONS,(n_record)) = ((pcompletion_cached,porigin_cached?))',
            '$recorded_compile_fatal(pcompletion_cached)', 'porigin_cached? = (PORIGIN 2 eps)',
            'pcompletion_cached =/= S_binding.COMPLETION', 'porigin_cached? =/= S_binding.ERRORORIGIN',
            '$recorded_class_pending(S,pclassdesc_decl)', '$recorded_class_site(S,porigin_decl)',
            '~$recorded_runtime_site(S,porigin_decl)',
            'pdeclcause = $declaration_cause(S)', '$declaration_cause_valid(S,' + echo + ',pdeclcause)',
            '~$recorded_class_site(S,' + echo + ')',
            '$test_outputs(S.EVENTS) = $ptascii("B|S|alive|")', '$test_stderr_count(S.EVENTS) = 1', *fatal.public('S'),
            '~$recorded_class_pending(S[.RECORDEDCOMPILEERROR = eps],pclassdesc_decl)',
            'S_raw = $test_one(S)', 'S_raw.COMPLETION = pcompletion_cached', 'S_raw.ERRORORIGIN = porigin_cached?',
            'S_raw.RECORDEDCOMPILEERROR = eps', 'S_raw.TODO = eps', 'S_raw.CURRENT = S.CURRENT', 'S_raw.FRAMES = S.FRAMES',
            'S_raw.ERRORHANDLER = S.ERRORHANDLER', 'S_raw.EVENTS = S.EVENTS', 'S_raw.CALLABLES = S.CALLABLES',
            'S_raw.CLASSNAMES = S.CLASSNAMES',
            'S_raw.TRACE = S_binding.TRACE', 'S_raw.ERRORFATALTRACE = S_binding.ERRORFATALTRACE',
            'S_raw.DECLARATIONS = S.DECLARATIONS ++ [PDRECORDEDFATAL porigin_decl pdeclcause n_record]',
            'S_raw.TRACE = ptraceframe :: ptraceframe_tail*', 'ptraceframe.FILE = eps',
            'ptraceframe.FUNCTION = $ptascii("source_shutdown")',
            'S_final = $drive_steps(S,2000)', 'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE', 'S_final.EXITSTATUS = 255',
            'S_final.RECORDEDCOMPILEERROR = eps', 'S_final.DECLARATIONS = S_raw.DECLARATIONS',
            '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')', '$test_stderr_count(S_final.EVENTS) = 2',
            'S_final.STATICS = [pstaticcell]', 'S_final.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
            '$weakref_find(S_final,S_final.ALLOCATIONS,n_object) = (n_weak)', '$weakref_get(S_final,n_weak) = POBJECT n_object',
            'n_object <- S_final.DESTRUCTION.CALLED', 'S_final.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_new]',
            'pdestructioncleanup_old.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_old', 'pdestructioncleanup_new.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_new',
            'pdestructionfatal_old.COMPILESTOP', '~pdestructionfatal_new.COMPILESTOP',
            'pdestructionfatal_new.FRAME.TODO = S.TODO', 'pdestructionfatal_new.FRAME.ORIGIN = S.ORIGIN',
            'pdestructionfatal_new.COMPLETION = pcompletion_cached', 'pdestructionfatal_new.ERRORORIGIN = porigin_cached?',
            'pdestructionfatal_new.TRACE = S_raw.TRACE', 'pdestructionfatal_new.DECLARATIONS = S_final.DECLARATIONS',
            '$recorded_runtime_snapshot_required(pdestructionfatal_new)',
            '$eager_fatal_valid(S_final,pdestructioncleanup_old,pdestructionfatal_old)',
            '$eager_fatal_valid(S_final,pdestructioncleanup_new,pdestructionfatal_new)', *fatal.public('S_final'),
            'S_history = $eager_fatal_history(S_final,pdestructionfatal_new)', 'S_history.DECLARATIONS = S.DECLARATIONS',
            'S_history.RECORDEDCOMPILEERROR = (n_record)', '$recorded_runtime_snapshot_valid(S_final,S_history,pdestructionfatal_new)',
            'S_replayed = $recorded_class_step(S_history,pclassdesc_decl)', 'S_replayed.DECLARATIONS = S_final.DECLARATIONS',
            'S_replayed.COMPLETION = pcompletion_cached', 'S_replayed.ERRORORIGIN = porigin_cached?', 'S_replayed.TRACE = S_raw.TRACE',
            '~$call_descriptors_valid(S_final[.RECORDEDCOMPILEERROR = (n_record)])',
            'pdestructionfatal_stale = pdestructionfatal_new[.DECLARATIONS = S.DECLARATIONS]',
            'pdestructioncleanup_stale = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_stale]',
            '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_new,pdestructioncleanup_stale]])',
            '$shutdown_compiler_snapshot(S_binding.COMPLETION) = (pcompletion_fresh)',
            'pdestructionfatal_fresh = pdestructionfatal_stale[.COMPLETION = S_binding.COMPLETION][.ERRORORIGIN = S_binding.ERRORORIGIN][.FROZEN = pcompletion_fresh][.TRACE = S_binding.TRACE][.ERRORTRACE = S_binding.ERRORFATALTRACE]',
            'pdestructioncleanup_fresh = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_fresh]',
            '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_new,pdestructioncleanup_fresh]])']
        for label, change in [
            ('origin', '.ERRORORIGIN = (PORIGIN 0 eps)'),
            ('tuple', '.COMPLETION = S_binding.COMPLETION][.FROZEN = pcompletion_fresh')]:
            checks += ['pdestructionfatal_' + label + ' = pdestructionfatal_new[' + change + ']',
                'pdestructioncleanup_' + label + ' = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_' + label + ']',
                '~$call_descriptors_valid(S_final[.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_' + label + ']])']
        for label, site, index in [('site', '(' + echo + ')', 'n_record'), ('index', 'porigin_decl', '(|S.DECLARATIONS|)')]:
            checks += ['pdeclaration_' + label + '* = S.DECLARATIONS ++ [PDRECORDEDFATAL ' + site + ' pdeclcause ' + index + ']',
                'pdestructionfatal_' + label + ' = pdestructionfatal_new[.DECLARATIONS = pdeclaration_' + label + '*]',
                'pdestructioncleanup_' + label + ' = pdestructioncleanup_new[.SOURCE = DESTRUCTOR_FATAL pdestructionfatal_' + label + ']',
                '~$call_descriptors_valid(S_final[.DECLARATIONS = pdeclaration_' + label + '*][.DESTRUCTION.ABANDONED = [pdestructioncleanup_old,pdestructioncleanup_' + label + ']])']
        (out / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + item + '\n' for item in checks))
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--attempt', type=int, default=1)
    parser.add_argument('--stage', choices=CASES, default='file-record')
    args = parser.parse_args()
    out, sources = args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0
    case = sources.joinpath(*CASES[args.stage])
    paths = [Path(__file__), Path(source.__file__), Path(fatal.__file__), Path(retirement.__file__),
        ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml', case.parent / 'run.py', case.parent / 'report.json',
        *sorted(case.glob('*.php')), *[case / 'native' / name for name in ['stdout', 'stderr', 'process.json', 'command.json']]]
    if args.phase == 'check':
        paths += [out / 'protocol.watsup', out / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'stage': args.stage, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, args.stage)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(out / 'protocol.watsup')], out / label, 90, ROOT)
            passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['result'] = 'pass' if passed else 'fail'
            report['runtime_assertions'] = len(json.loads((out / 'assertions.json').read_text())) if passed else 0
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            report['runtime_assertions'] = 0
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
