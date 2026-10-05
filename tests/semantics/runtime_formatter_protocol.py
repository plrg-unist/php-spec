#!/usr/bin/env python3
"""Source-derived deferred runtime links, recorded primary and owner retirement."""
import argparse
import hashlib
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import iterator_declaration_notices as catalogue
import user_iterator as source

ROOT = Path(__file__).resolve().parents[2]
TRAIT_ERROR = ROOT / 'tests/semantics/trait_data_collision_held_primary_review_cases.json'
CASES = {
    'runtime-eval': 'runtime-fatal-formatter-eval',
    'runtime-constant': 'runtime-fatal-formatter-constant',
    'runtime-include': 'runtime-fatal-formatter-include',
    'runtime-trait-error': 'held-eval-primary-precedes-new-trait-collision-error',
}
PREFIX = r'''dec $await(pstate,nat) : pstate
def $await(S,n) = S -- if S.COMPLETION = SOURCE_PENDING
def $await(S,n) = $await($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $await(S,n) = S -- otherwise
dec $stage(pstate) : bool
def $stage(S) = true
  -- if S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN 2 pcpath)
  -- if $origin_node(S.SOURCES,PORIGIN 2 pcpath) = (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)
__RUNTIME_CONTEXT__
def $stage(S) = false -- otherwise
dec $seek(pstate,nat) : pstate
def $seek(S,n) = S -- if $stage(S)
def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek(S,n) = S -- otherwise
dec $failed_match(pdeclaration,porigin) : bool
def $failed_match(PDRCLASSFATAL porigin pdeclcause,porigin) = true
def $failed_match(pdeclaration,porigin) = false -- otherwise
dec $replace_failure(pdeclaration*,porigin,pdeclaration*) : pdeclaration*
def $replace_failure(eps,porigin,pdeclaration_new*) = eps
def $replace_failure((PDRCLASSFATAL porigin pdeclcause) :: pdeclaration_tail*,porigin,pdeclaration_new*) = pdeclaration_new* ++ pdeclaration_tail*
def $replace_failure(pdeclaration :: pdeclaration_tail*,porigin,pdeclaration_new*) = pdeclaration :: $replace_failure(pdeclaration_tail*,porigin,pdeclaration_new*)
  -- if ~$failed_match(pdeclaration,porigin)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['fixtures', 'prepare', 'check'], default='check')
    parser.add_argument('--select', default=','.join(CASES))
    args = parser.parse_args()
    root = ROOT
    names = args.select.split(',')
    assert names and len(set(names)) == len(names) and all(name in CASES for name in names)
    out = Path(tempfile.mkdtemp(prefix='runtime-formatter-protocol-', dir=root / '.tools'))
    print(out, flush=True)
    profile = json.loads((root / 'tests/semantics/profile.json').read_text())
    flags = ['-n'] + [item for key, value in profile.items() for item in ('-d', key + '=' + value)]
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    os.environ.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    modules = [root / name for name in json.loads((root / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, root / 'spec/semantics/modules.json', Path(__file__),
              root / 'tests/semantics/iterator_declaration_notices.py', root / 'tests/semantics/profile.json',
              root / '_build/default/adapter/main.exe', root / 'tests/semantics/_build/default/numeric_runner.exe', source.driver.types.PHP]
    if 'runtime-trait-error' in names:
        inputs.append(TRAIT_ERROR)
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    report = {'result': 'fail', 'mode': args.mode, 'inputs': before, 'root': str(root), 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
              'generator': str(Path(__file__)), 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': None},
              'profile': profile, 'caps_seconds': {'native': 10, 'numeric': 300, 'jobs': 1}, 'cases': {}}
    frontend = adapter = None
    protocols = []
    try:
        report['runtime'] = source.runtime(out)
        frontend = Worker([str(root / '.tools/php/bin/php'), *flags, '-d', 'extension=' + str(root / '.tools/php-file.so'),
                           str(root / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(root / '_build/default/adapter/main.exe'), str(root)], out / 'adapter')

        def packet(code, unit=None):
            request = {'op': 'parse' if unit is None else 'parse-eval', 'source': base64.b64encode(code).decode()}
            if unit is not None:
                request.update(id=str(unit), mode='eval', profile='cli-raw-85')
            parsed = frontend.request(request)
            assert parsed.get('accepted'), parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            return checked['fixture']

        seq = lambda data: str(list(data))
        for name in names:
            directory = out / name
            directory.mkdir()
            if name == 'runtime-trait-error':
                row = next(row for row in json.loads(TRAIT_ERROR.read_text())['cases'] if row['id'] == CASES[name])
                case = {'source': row['source'].encode()}
                assert hashlib.sha256(case['source']).hexdigest() == row['source_sha256']
            else:
                case = catalogue.CASES[CASES[name]]
            path = directory / 'source.php'
            path.write_bytes(case['source'])
            text = path.read_text()
            outer = text.split("try{eval('", 1)[1].split("');}catch", 1)[0]
            is_file = name == 'runtime-include'
            inner = case['unit'] if is_file else text.split('echo "F";eval(\'', 1)[1].split('\');return "formatted";', 1)[0].encode()
            assert '\\' not in outer and "'" not in outer
            if not is_file:
                assert b'\\' not in inner and b"'" not in inner
            if is_file:
                (directory / 'child.php').write_bytes(inner)
            native = source.process([str(source.driver.types.PHP), '-n', *source.driver.types.FLAGS, str(path)], directory / 'native', 10, directory)
            assert native.returncode == 255 and native.stdout == b'HF'
            assert native.stderr.count(b'Return type of B::current()') == 2
            assert b'Declaration of B::next($x): void' in native.stderr and b'InnerBad' not in native.stderr
            main_fixture = packet(path.read_bytes())
            outer_fixture = packet(outer.encode(), 1)
            inner_fixture = packet(inner, None if is_file else 2)
            response1 = 'SOURCE_ACCEPT 1 (' + seq(outer.encode()) + ') ' + outer_fixture
            response2 = 'SOURCE_ACCEPT 2 (' + seq(inner) + ') ' + inner_fixture
            conditions = [
                'S_initial = $php_file_run(' + main_fixture + ',0,' + seq(os.fsencode(path)) + ',' + seq(os.fsencode(directory)) + ')',
                'S_wait = $await(S_initial[.COMPLETION = NORMAL],600)', 'S_wait.COMPLETION = SOURCE_PENDING',
                'S_compiled = $eval_resume(S_wait,' + response1 + ')', 'S_compiled.COMPLETION = NORMAL',
                'S_inner_wait = $await(S_compiled,800)', 'S_inner_wait.COMPLETION = SOURCE_PENDING',
                '$eval_compile_fatal_current(S_inner_wait) = (pevalcompilefatal)',
                'pevalcompilefatal.CURSOR.PLAN.UNIT = 1', 'pevalcompilefatal.CURSOR.PENDING = THROWING n_root',
            ]
            if is_file:
                child = directory / 'child.php'
                conditions += [
                    'S_inner_wait.FILECONTEXTS = [pfilecontext_wait]', 'pfilecontext_wait.PHASE = FILE_RESOLVE_WAIT',
                    'pfilecontext_wait.REQUESTED = ' + seq(os.fsencode(child)),
                    'S_parse = $file_open_resume(S_inner_wait,FILE_OPENED pfilecontext_wait.NONCE pfilecontext_wait.CALLER pfilecontext_wait.REQUESTED (' + seq(os.fsencode(child)) + ') (' + seq(os.fsencode(child)) + ') (' + seq(inner) + '))',
                    'S_parse.COMPLETION = SOURCE_PENDING', 'S_parse.FILECONTEXTS = [pfilecontext_parse]',
                    'pfilecontext_parse.PHASE = FILE_PARSE_WAIT', 'pfilecontext_parse.UNIT = (2)',
                    'S_loaded = $file_parse_resume(S_parse,' + response2 + ')',
                ]
                context_stage = '  -- if S.FILECONTEXTS = [pfilecontext]\n  -- if pfilecontext.PHASE = FILE_UNIT_RUN\n  -- if pfilecontext.UNIT = (2)'
            else:
                conditions += ['S_inner_wait.EVALCONTEXTS = pevalcontext_parse :: pevalcontext_outer :: eps',
                               'pevalcontext_parse.PHASE = PARSER_WAIT', 'pevalcontext_parse.UNIT = 2',
                               'S_loaded = $eval_resume(S_inner_wait,' + response2 + ')']
                context_stage = '  -- if $eval_context_at(S.EVALCONTEXTS,2) = (pevalcontext)\n  -- if pevalcontext.PHASE = UNIT_RUN'
            conditions += [
                'S_loaded.COMPLETION = NORMAL', 'S_before = $seek(S_loaded,300)', '$stage(S_before)',
                r'S_before.COMPLETION = NORMAL \/ S_before.COMPLETION = BUDGET',
                'S = S_before[.COMPLETION = NORMAL]', 'S.ORIGIN = (porigin_class)',
                '$class_at(S.CLASSES,porigin_class) = (pclassdesc)',
                '$declaration_open(S.DECLARATIONS) = eps', '~$declaration_early(S.DECLARATIONS,porigin_class,PPCLASS)',
                '$eval_context_at(S.EVALCONTEXTS,1) = (pevalcontext_outer)', 'pevalcontext_outer.PHASE = EVAL_COMPILE',
                '$eval_compile_fatal_current(S) = (pevalcompilefatal)', '$eval_compile_fatal_valid(S,pevalcompilefatal)',
                '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
                'pdeclcause = $declaration_cause(S)', 'pdeclcause.UNIT = 2', 'pdeclcause.CALLS =/= eps',
                '$declaration_cause_valid(S,porigin_class,pdeclcause)',
                'PhpStep: S ~> S_report',
                'S_report.COMPLETION = REQUESTFATAL ptbytes_class ptbytes_message z_fatal',
                '$shutdown_compiler_snapshot(pevalcompilefatal.COMPLETION) = (S_report.COMPLETION)',
                'S_report.ORIGIN = (porigin_class)', 'S_report.ERRORORIGIN = pevalcompilefatal.ORIGIN',
                '~S_report.COMPILESTOP', 'S_report.TODO = eps', 'S_report.SERVICELEFT = eps',
                'S_report.EVALCONTEXTS = [pevalcontext_outer]', 'S_report.FILECONTEXTS = eps',
                '$call_descriptors_valid(S_report)', '$heap_valid($heap_graph(S_report))',
                '$eval_compile_owners_valid(S_report)', '$eval_state_valid(S_report)',
                '$eval_compile_cursors(S_report) = [pevalcompilefatal.CURSOR]',
                '$runtime_class_rollback(S,S_report)',
                'S_report.DECLARATIONS = S.DECLARATIONS ++ [PDRCLASSFATAL porigin_class pdeclcause]',
                '$runtime_class_report_origin(S_report) = (porigin_class)', '$runtime_class_report_valid(S_report)',
                'S_report.TRACE = [ptraceframe_inner,ptraceframe_formatter]',
                'ptraceframe_inner.FUNCTION = $ptascii("' + ('include' if is_file else 'eval') + '")',
                'ptraceframe_inner.LINE = 3', 'ptraceframe_formatter.FUNCTION = $ptascii("__toString")',
                'ptraceframe_formatter.LINE = 6', 'ptraceframe_inner.FILE = ' + seq(os.fsencode(path)),
                '$class_named(S_report.CLASSNAMES,$ptascii("a")) =/= eps',
                '$class_named(S_report.CLASSNAMES,$ptascii("b")) = eps',
                '$class_named(S_report.CLASSNAMES,$ptascii("innerbad")) = eps',
            ]
            if name == 'runtime-trait-error':
                conditions += [
                    'pclassdesc.NAME = $ptascii("InnerBad")',
                    '$class_named(S.CLASSNAMES,$ptascii("t")) = (porigin_trait)',
                    '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
                    'pclassdesc_trait.KIND = "trait"',
                    'porigin_trait = PORIGIN 2 pcpath_trait',
                    '$ppproperty_desc_at(pclassdesc_trait.PROPERTIES,$ptascii("x")) = (ppropertydesc_trait)',
                    'ppropertydesc_trait.DEFAULT = PROP_DEFERRED porigin_default',
                    '$trait_member_fold(S,pclassdesc,porigin_default) = (F_error)',
                    '$trait_fold_error(F_error) = (ptraitdataerror)',
                    'ptraitdataerror.KIND = "Error"',
                    'ptraitdataerror.MESSAGE = $ptascii("Undefined constant self::MISSING")',
                    '$trait_collision_held(S)',
                    'S_failed = $activate_class_body(S,pclassdesc)',
                    'S_failed.COMPLETION = STATICBYTES ptbytes_inner z_inner',
                    'S_failed.ERRORORIGIN = (PORIGIN 2 eps)',
                    'S_failed.EVENTS = S.EVENTS',
                    'S_failed.OBJECTS = S.OBJECTS',
                    'S_failed.ALLOCATIONS = S.ALLOCATIONS',
                    'S_failed.RESULT = S.RESULT',
                    '$runtime_class_rollback(S,S_failed)',
                    '$runtime_class_recorded_fatal(S,S_failed,pclassdesc)',
                    '~$runtime_class_recorded_fatal(S,S_failed[.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_inner z_inner],pclassdesc)',
                    '~$runtime_class_recorded_fatal(S[.ORIGIN = (porigin_trait)],S_failed,pclassdesc)',
                    '~$runtime_class_recorded_fatal(S,S_failed[.CLASSNAMES = S.CLASSNAMES ++ [($ptascii("innerbad"),porigin_class)]],pclassdesc)',
                    '~$runtime_class_recorded_fatal(S[.TODO = eps][.FRAMES = eps],S_failed,pclassdesc)',
                    'S_report.OBJECTS = S.OBJECTS',
                    'S_report.OBJECTPROPS = S.OBJECTPROPS',
                    'S_report.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
                    '$declaration_history_valid(S_report)',
                    '$declaration_entry_check(S_report) = S_report',
                    '$class_named(S_report.CLASSNAMES,$ptascii("t")) = (porigin_trait)',
                ]
            if name == 'runtime-constant':
                conditions += ['$class_named(S_report.CLASSNAMES,$ptascii("inneri")) = (porigin_interface)',
                               '$declaration_entry_check(S_report[.DECLARATIONS = $replace_failure(S_report.DECLARATIONS,porigin_class,[PDRCLASSFATAL porigin_interface pdeclcause])]).COMPLETION = UNSUPPORTED "invalid declaration publication history"']
            if not is_file:
                for replacement in ['eps', '[PDRCLASS porigin_class pdeclcause]',
                                    '[PDRCLASSFATAL porigin_class {UNIT 1, CALLS pdeclcause.CALLS}]',
                                    '[PDRCLASSFATAL porigin_class {UNIT pdeclcause.UNIT, CALLS eps}]']:
                    conditions += ['$declaration_entry_check(S_report[.DECLARATIONS = $replace_failure(S_report.DECLARATIONS,porigin_class,' + replacement + ')]).COMPLETION = UNSUPPORTED "invalid declaration publication history"']
            conditions += [
                'S_unwind = $start_error_unwind(S_report)', 'S_unwind.TODO = [ERROR_UNWIND S_report.COMPLETION]',
                '$eval_state_valid(S_unwind)', '$eval_compile_owners_valid(S_unwind)', '$heap_valid($heap_graph(S_unwind))',
                'S_restored = $drive_steps(S_unwind,1)', 'S_restored.TODO = [ERROR_UNWIND S_report.COMPLETION]',
                'S_restored.FRAMES = eps', 'S_restored.CURRENT = eps', 'S_restored.EVALCONTEXTS = eps', 'S_restored.FILECONTEXTS = eps',
                '$eval_compile_cursors(S_restored) = eps', '$eval_compile_owners_valid(S_restored)',
                '$eval_state_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
                '~$eval_state_valid(S_restored[.EVALCONTEXTS = [pevalcontext_outer]])',
            ]
            if is_file:
                conditions += ['S.FILECONTEXTS = [pfilecontext_live]',
                               '~$eval_state_valid(S_report[.FILECONTEXTS = [pfilecontext_live]])']
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX.replace('__RUNTIME_CONTEXT__', context_stage) + '\ndec $body() : bool\ndef $body() = true\n' +
                               ''.join('  -- ' + (item if item.startswith('PhpStep:') else 'if ' + item) + '\n' for item in conditions) + '\ndec $main() : bool\ndef $main() = ' + ('true' if args.mode == 'prepare' else '$body()') + '\n')
            report['cases'][name] = {'source': str(path), 'source_case': CASES[name], 'native_command': [str(source.driver.types.PHP), '-n', *source.driver.types.FLAGS, str(path)], 'native_exit': native.returncode,
                                     'main_fixture': main_fixture, 'units': [{'id': 1, 'code': outer, 'fixture': outer_fixture},
                                                                          {'id': 2, 'code': inner.decode(), 'fixture': inner_fixture}],
                                     'conditions': conditions, 'fixture': str(fixture), 'runtime_mode': 'SL'}
            if args.mode != 'fixtures':
                command = [str(root / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)]
                report['cases'][name]['numeric_command'] = command
                result = source.driver.process(command, directory / 'numeric', 300, root)
                assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            protocols.append({'id': name, 'source_case': CASES[name], 'fixture': str(fixture),
                              'predicates': len(conditions), 'evaluated': args.mode == 'check', 'runtime_mode': 'SL'})
            print(name, args.mode, len(conditions), 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter:
            adapter.close()
        if frontend:
            frontend.close()
        report['protocols'] = protocols
        report['stable_inputs'] = before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
