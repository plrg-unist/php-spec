#!/usr/bin/env python3
"""Checked include-path mutation and compiler-stop interactions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time

import static_types as types
from compiler_method_modifier_guards import GuardWorker
import include_ini_prefix_protocol as files
import include_mutable_protocol as config

ROOT = Path(__file__).resolve().parents[2]
ENV = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
       'LC_ALL': 'C', 'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1', 'GIT_OPTIONAL_LOCKS': '0'}
FATAL_MAIN = b'''<?php
class O {function __toString():string {
    ini_set('include_path',"__SUB__\\0nested");
    include 'bad.php';
    return 'c';
}}
set_include_path(new O);
'''
FATAL_CHILD = b'''<?php
class A extends Exception { public function __wakeup() {} }
class B { public function __WAKEUP(): int {} }
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(directory, prefix, conditions):
    path = directory / 'protocol.watsup'
    path.write_text(prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- if ' + condition + '\n' for condition in conditions))
    return {'id': directory.name, 'fixture': str(path), 'conditions': len(conditions),
            'source': str(directory / 'main.php'), 'source_sha256': sha(directory / 'main.php'),
            'fixture_sha256': sha(path)}


def prepare_fatal(directory):
    directory.mkdir()
    sub = directory / 'sub'
    sub.mkdir()
    effective = os.fsencode(sub.resolve())
    raw = effective + b'\0nested'
    main, child = directory / 'main.php', sub / 'bad.php'
    main.write_bytes(FATAL_MAIN.replace(b'__SUB__', effective))
    child.write_bytes(FATAL_CHILD)
    frontend, adapter = None, None
    try:
        frontend = GuardWorker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = GuardWorker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': files.b64(main.read_bytes())})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
        parsed_child = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
                                         'profile': 'cli-raw-85', 'requested': files.b64(b'bad.php'),
                                         'resolved': files.b64(os.fsencode(child)),
                                         'opened': files.b64(os.fsencode(child)), 'source': files.b64(FATAL_CHILD)})
        assert parsed_child['accepted']
        checked_child = adapter.request({'op': 'check', 'ast': parsed_child['ast'], 'fixture': True})
        assert checked_child['ok']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    main_bytes, child_bytes, cwd = os.fsencode(main), os.fsencode(child), os.fsencode(ROOT)
    start = '$php_file_run(' + checked['fixture'] + ', 0, $base64(' + json.dumps(files.b64(main_bytes)) + '), $base64(' + json.dumps(files.b64(cwd)) + '))'
    opened = '(FILE_OPENED 0 ' + files.seq(main_bytes) + ' ' + files.seq(b'bad.php') + ' ' + files.seq(child_bytes) + ' ' + files.seq(child_bytes) + ' ' + files.seq(FATAL_CHILD) + ')'
    accepted = '(SOURCE_ACCEPT 1 ' + files.seq(FATAL_CHILD) + ' ' + checked_child['fixture'] + ')'
    conditions = [
        'S_initial = ' + start, '~S_initial.COMPILESTOP',
        'S_resolve = $file_prefix_seek(S_initial,1000)',
        'S_resolve.COMPLETION = SOURCE_PENDING',
        'S_resolve.FILECONTEXTS = pfilecontext_resolve :: eps',
        'pfilecontext_resolve.PHASE = FILE_RESOLVE_WAIT',
        'S_resolve.FILEINCLUDEPATH = (' + files.seq(raw) + ')',
        'pfilecontext_resolve.INCLUDEPATH = ' + files.seq(effective),
        '$file_pending_state_valid(S_resolve)', '$call_descriptors_valid(S_resolve)',
        '$file_open_response_valid(S_resolve,' + opened + ')',
        'S_parse = $file_open_resume(S_resolve,' + opened + ')',
        'S_parse.COMPLETION = SOURCE_PENDING',
        'S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
        'pfilecontext_parse.PHASE = FILE_PARSE_WAIT',
        'pfilecontext_parse.UNIT = (1)',
        'S_parse.FILEINCLUDEPATH = S_resolve.FILEINCLUDEPATH',
        '$file_pending_state_valid(S_parse)', '$call_descriptors_valid(S_parse)',
        'S_parse.CURRENT = (pcallcontext)', '$(|S_parse.FRAMES| > 0)',
        '$file_parse_response_valid(S_parse,' + accepted + ')',
        'S_fatal = $file_parse_resume(S_parse,' + accepted + ')',
        'S_fatal.COMPLETION = STATICBYTES ptbytes_fatal 3', 'S_fatal.COMPILESTOP',
        'S_fatal.FILEINCLUDEPATH = S_parse.FILEINCLUDEPATH',
        'S_fatal.FILECONTEXTS = eps', 'S_fatal.SERVICELEFT = eps',
        'S_fatal.TODO = pfilecontext_parse.TAIL',
        'S_fatal.FRAMES = S_parse.FRAMES', 'S_fatal.CURRENT = S_parse.CURRENT',
        'S_fatal.CLASSES = [pclassdesc_o,pclassdesc_a]',
        'pclassdesc_o.NAME = $ptascii("O")', 'pclassdesc_a.NAME = $ptascii("A")',
        'S_fatal.DECLARATIONS = [PDENTER 0 eps 30719,PDEXIT 0 PCSCOMPLETE,PDRCLASS pclassdesc_o.ORIGIN {UNIT 0,CALLS eps},PDENTER 1 (pfilecontext_parse.SITE) 30719,PDECLASS 1 pclassdesc_a.ORIGIN,PDEXIT 1 PCSCOMPILER]',
        'S_fatal.EVENTS = [DIAGNOSTIC "Deprecated" ptbytes_deprecated 2]',
        '$declaration_history_valid(S_fatal)',
        '~$declaration_history_valid(S_fatal[.COMPILESTOP = false])',
        '~$file_open_response_valid(S_fatal,' + opened + ')',
        '~$file_parse_response_valid(S_fatal,' + accepted + ')',
        '$drive_steps(S_fatal,1) = S_fatal', '$drive_steps(S_fatal,1000) = S_fatal']
    snapshot = {'version': 2, 'main': files.b64(main_bytes), 'cwd': files.b64(cwd),
                'include_path': files.b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': files.b64(main_bytes), 'requested': files.b64(b'bad.php'),
                     'cwd': files.b64(cwd), 'include_path': files.b64(effective),
                     'status': 'opened', 'resolved': files.b64(child_bytes),
                     'opened': files.b64(child_bytes), 'source': files.b64(FATAL_CHILD)}]}
    (directory / 'snapshot.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    return fixture(directory, files.PREFIX, conditions)


def prepare_config(directory, case):
    directory.mkdir()
    _, source, stage, checks = case
    (directory / 'main.php').write_bytes(source)
    frontend, adapter = None, None
    try:
        frontend = GuardWorker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = GuardWorker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': files.b64(source)})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    start = '$php_file_run(' + checked['fixture'] + ', 0, $base64(' + json.dumps(files.b64(os.fsencode(directory / 'main.php'))) + '), $base64(' + json.dumps(files.b64(os.fsencode(ROOT))) + '))'
    conditions = ['S_initial = ' + start, '~S_initial.COMPILESTOP',
                  '$ini_prefix_live(S_initial)',
                  'S = $ini_prefix_seek(S_initial[.COMPLETION = NORMAL],1000)[.COMPLETION = NORMAL]'] + checks
    return fixture(directory, config.PREFIX.replace('STAGE', stage), conditions)


def prepare(out):
    types.ENV = ENV
    files.Worker = GuardWorker
    rows = [prepare_fatal(out / 'conversion-file-compile-stop')]
    name = 'invoke-interior-nul'
    template, suffix = files.CASES[name]
    row = files.prepare(name, template, suffix, out / name, invoke_frame=True)
    rows.append({'id': name, 'fixture': str(out / name / 'protocol.watsup'),
                 'source': str(out / name / 'main.php'), 'conditions': row['assertions'], **row})
    cases = {case[0]: case for case in config.CASES}
    rows.append(prepare_config(out / 'nested-set-old-prefix', cases['ini-prefix-stringable-set-result']))
    scalar = cases['ini-prefix-leading-nul-result']
    source = b'''<?php function value(){ini_set('include_path',"a\\0b");return "\\0tail";}
echo ini_set('include_path',value())?'Y':'F';'''
    rows.append(prepare_config(out / 'empty-prefix-after-source-effect', (scalar[0], source, scalar[2], scalar[3])))
    (out / 'prepared.json').write_text(json.dumps(rows, indent=2) + '\n')
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    before = types.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='compiler-ini-publication-', dir=ROOT / '.tools'))
    rows = prepare(out)
    assert before == types.syntax_validation.implementation_fingerprint()
    print(out, flush=True)
    if args.prepare_only:
        return
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    results = []
    for row in rows:
        directory = Path(row['fixture']).parent
        assert sha(Path(row['fixture'])) == row['fixture_sha256']
        assert sha(Path(row['source'])) == row['source_sha256']
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, row['fixture']]
        launch = {'supplied_argv': command, 'cwd': str(ROOT), 'supplied_environment': ENV,
                  'timeout_seconds': 120, 'status': 'launching', 'started': time.time()}
        save = lambda: (directory / 'numeric.launch.json').write_text(json.dumps(launch, indent=2) + '\n')
        save()
        process, observed, error = None, None, None
        with (directory / 'stdout').open('wb') as stdout, (directory / 'stderr').open('wb') as stderr:
            try:
                process = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=stdout, stderr=stderr, start_new_session=True)
                launch.update(popen_args=process.args, pid=process.pid, pgid=os.getpgid(process.pid), status='running')
                save()
                observed = process.wait(timeout=120)
            except (subprocess.TimeoutExpired, OSError) as caught:
                error = type(caught).__name__ + ': ' + str(caught)
            finally:
                if process:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                try:
                    if process:
                        process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    error = (error or '') + '; cleanup timeout'
                launch.update(status='observed_exit' if observed is not None else 'unknown_failure',
                              observed_exit_status=observed, cleanup_exit_status=process.returncode if process else None,
                              error=error, ended=time.time())
                save()
        try:
            stable = before == types.syntax_validation.implementation_fingerprint()
            stable = stable and sha(Path(row['fixture'])) == row['fixture_sha256']
            stable = stable and sha(Path(row['source'])) == row['source_sha256']
        except Exception as caught:
            stable = False
            error = (error or '') + '; input guard: ' + str(caught)
        passed = observed == 0 and not error and stable and (directory / 'stdout').read_bytes() == b'true\n' and not (directory / 'stderr').read_bytes()
        results.append({**row, 'pass': passed, 'exit_status': observed, 'inputs_stable': stable, 'error': error})
        (out / 'report.json').write_text(json.dumps({'result': 'running' if passed else 'fail', 'fingerprint': before,
            'inputs_stable': all(r['inputs_stable'] for r in results),
            'records': results, 'conditional_unrun': [r['id'] for r in rows[len(results):]]}, indent=2) + '\n')
        if not passed:
            raise SystemExit(1)
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'records': results, 'fingerprint': before,
        'inputs_stable': all(r['inputs_stable'] for r in results),
        'conditional_unrun': [], 'overlapping_predicates': sum(r['conditions'] for r in rows)}, indent=2) + '\n')


if __name__ == '__main__':
    main()
