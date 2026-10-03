#!/usr/bin/env python3
"""Source-derived raw INI/effective include-path guards in both file phases."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'interior-nul': (b'<?php ini_set(\'include_path\',"__SUB__\\0suffix");echo include \'one.php\';', b'\0suffix'),
    'nul-free': (b"<?php set_include_path('__SUB__');echo include 'one.php';", b''),
    'invoke-interior-nul': (b'<?php class I {function __invoke(){ini_set(\'include_path\',"__SUB__\\0suffix");echo include \'one.php\';}} (new I)();', b'\0suffix'),
    'ini-option-interior-nul': (b'<?php class O {function __toString():string {return \'include_path\';}} ini_set(new O,"__SUB__\\0suffix");echo include \'one.php\';', b'\0suffix'),
}
CHILD = b'<?php return 7;'
PREFIX = r'''
dec $file_prefix_live(pstate) : bool
def $file_prefix_live(S) = ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $file_prefix_live(S) = false -- otherwise
dec $file_prefix_resolve(pstate) : bool
def $file_prefix_resolve(S) = true
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = SOURCE_PENDING
  -- if S.FILECONTEXTS = pfilecontext :: eps
  -- if pfilecontext.PHASE = FILE_RESOLVE_WAIT
def $file_prefix_resolve(S) = false -- otherwise
dec $file_prefix_seek(pstate, nat) : pstate
def $file_prefix_seek(S,n) = S -- if $file_prefix_resolve(S)
def $file_prefix_seek(S,n) = $file_prefix_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $file_prefix_live(S)
  -- if ~$file_prefix_resolve(S)
  -- if $(n > 0)
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def seq(data):
    return '(' + str(list(data)) + ')'


def prepare(name, template, suffix, directory, invoke_frame=False):
    """Record parser/checker closures and write a fixture without executing it."""
    directory.mkdir()
    sub = directory / 'sub'
    sub.mkdir()
    effective = str(sub.resolve()).encode()
    raw = effective + suffix
    source = template.replace(b'__SUB__', effective)
    source_path = directory / 'main.php'
    child_path = sub / 'one.php'
    source_path.write_bytes(source)
    child_path.write_bytes(CHILD)
    main_bytes = str(source_path.resolve()).encode()
    child_bytes = str(child_path.resolve()).encode()
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], directory / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source)})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
        parsed_child = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
                                         'profile': 'cli-raw-85', 'requested': b64(b'one.php'),
                                         'resolved': b64(child_bytes), 'opened': b64(child_bytes),
                                         'source': b64(CHILD)})
        assert parsed_child['accepted'], parsed_child
        checked_child = adapter.request({'op': 'check', 'ast': parsed_child['ast'], 'fixture': True})
        assert checked_child['ok'], checked_child
    finally:
        frontend.close()
        adapter.close()
    start = '$php_file_run(' + checked['fixture'] + ', 0, $base64(' + json.dumps(b64(main_bytes)) + '), $base64(' + json.dumps(b64(str(ROOT.resolve()).encode())) + '))'
    opened = '(FILE_OPENED 0 ' + seq(main_bytes) + ' ' + seq(b'one.php') + ' ' + seq(child_bytes) + ' ' + seq(child_bytes) + ' ' + seq(CHILD) + ')'
    accepted = '(SOURCE_ACCEPT 1 ' + seq(CHILD) + ' ' + checked_child['fixture'] + ')'
    conditions = ['S_initial = ' + start,
                  '~S_initial.COMPILESTOP',
                  '$file_prefix_live(S_initial)',
                  '~$file_prefix_live(S_initial[.COMPILESTOP = true])',
                  '~$file_prefix_live(S_initial[.COMPLETION = UNSUPPORTED "guard"])',
                  '~$file_prefix_live(S_initial[.COMPLETION = PHPERROR eps 1])',
                  '~$file_prefix_live(S_initial[.COMPLETION = EXITED 0])',
                  '~$file_prefix_live(S_initial[.COMPLETION = SOURCE_PENDING])',
                  '~$file_prefix_resolve(S_initial[.COMPLETION = SOURCE_PENDING])',
                  'S_resolve = $file_prefix_seek(S_initial,1000)',
                  'S_resolve.COMPLETION = SOURCE_PENDING',
                  '$file_prefix_resolve(S_resolve)',
                  'S_resolve.FILECONTEXTS = pfilecontext_resolve :: eps',
                  'pfilecontext_resolve.PHASE = FILE_RESOLVE_WAIT',
                  'S_resolve.FILEINCLUDEPATH = (' + seq(raw) + ')',
                  'pfilecontext_resolve.INCLUDEPATH = ' + seq(effective),
                  '$file_pending_state_valid(S_resolve)',
                  '$file_context_phase_valid(S_resolve,pfilecontext_resolve)',
                  '$call_descriptors_valid(S_resolve)',
                  '$file_include_path(eps) = eps',
                  '$file_open_response_valid(S_resolve,' + opened + ')',
                  '~$file_open_response_valid(S_resolve,(FILE_OPENED 999 ' + seq(main_bytes) + ' ' + seq(b'one.php') + ' ' + seq(child_bytes) + ' ' + seq(child_bytes) + ' ' + seq(CHILD) + '))']
    if suffix:
        conditions += ['S_resolve.FILEINCLUDEPATH =/= (pfilecontext_resolve.INCLUDEPATH)',
                       '~$file_pending_state_valid(S_resolve[.FILECONTEXTS = pfilecontext_resolve[.INCLUDEPATH = ' + seq(raw) + '] :: eps])']
    for state, context in [('S_resolve', 'pfilecontext_resolve'), ('S_parse', 'pfilecontext_parse')]:
        if state == 'S_parse':
            conditions += ['S_parse = $file_open_resume(S_resolve,' + opened + ')',
                           'S_parse.COMPLETION = SOURCE_PENDING',
                           '~S_parse.COMPILESTOP',
                           '~$file_prefix_live(S_parse)',
                           '~$file_prefix_resolve(S_parse)',
                           'S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
                           'pfilecontext_parse.PHASE = FILE_PARSE_WAIT',
                           'S_parse.FILEINCLUDEPATH = (' + seq(raw) + ')',
                           'pfilecontext_parse.INCLUDEPATH = ' + seq(effective),
                           '$file_pending_state_valid(S_parse)',
                           '$file_context_phase_valid(S_parse,pfilecontext_parse)',
                           '$call_descriptors_valid(S_parse)']
        if invoke_frame:
            phase = 'resolve' if state == 'S_resolve' else 'parse'
            current = 'pcallcontext_' + phase
            receiver = 'n_receiver_' + phase
            method = 'pmethoddesc_' + phase
            called = 'porigin_called_' + phase
            conditions += [state + '.CURRENT = (' + current + ')',
                           current + '.RECEIVER = (' + receiver + ')',
                           '$object_invoke_method(' + state + ',' + receiver + ') = (' + method + ')',
                           current + '.FUNCTION = ' + method + '.FUNCTION.ORIGIN',
                           current + '.LEXICAL_CLASS = (' + method + '.OWNER)',
                           current + '.CALLED_CLASS = (' + called + ')',
                           current + '.INSTANCE = $target_instance($context_target(' + current + '))',
                           state + '.OBJECTS[' + receiver + '] = INSTANCE ' + called,
                           context + '.LEXICAL_CLASS = ' + current + '.LEXICAL_CLASS',
                           context + '.LEXICAL_CLASS =/= eps',
                           context + '.OWNER = |' + state + '.FRAMES|',
                           '$(' + context + '.OWNER > 0)',
                           '~$file_pending_state_valid(' + state + '[.FILECONTEXTS = ' + context + '[.OWNER = 0] :: eps])',
                           '~$file_context_phase_valid(' + state + '[.FILECONTEXTS = ' + context + '[.OWNER = 0] :: eps],' + context + '[.OWNER = 0])',
                           '~$file_pending_state_valid(' + state + '[.FILECONTEXTS = ' + context + '[.LEXICAL_CLASS = eps] :: eps])',
                           '~$call_descriptors_valid(' + state + '[.FILECONTEXTS = ' + context + '[.LEXICAL_CLASS = eps] :: eps])',
                           '~$call_descriptors_valid(' + state + '[.CURRENT = (' + current + '[.LEXICAL_CLASS = eps])])',
                           '~$call_descriptors_valid(' + state + '[.CURRENT = (' + current + '[.RECEIVER = eps])])']
        changed = state + '[.FILEINCLUDEPATH = (' + seq(effective + b'\0changed') + ')]'
        forged = state + '[.FILEINCLUDEPATH = (' + seq(b'/forged\0suffix') + ')]'
        conditions += ['$file_pending_state_valid(' + changed + ')',
                       '$file_context_phase_valid(' + changed + ',' + context + ')',
                       '$call_descriptors_valid(' + changed + ')',
                       '~$file_pending_state_valid(' + forged + ')',
                       '~$file_context_phase_valid(' + forged + ',' + context + ')',
                       '~$call_descriptors_valid(' + forged + ')',
                       '~$call_descriptors_valid(' + state + '[.FILECONTEXTS = ' + context + '[.INCLUDEPATH = ' + seq(b'/forged') + '] :: eps])',
                       '~$call_descriptors_valid(' + state + '[.FILESEQ = $(' + state + '.FILESEQ + 1)])',
                       '~$call_descriptors_valid(' + state + '[.TODO = eps])',
                       '~$call_descriptors_valid(' + state + '[.FILECONTEXTS = ' + context + '[.SITE = PORIGIN 999 eps] :: eps])',
                       '~$call_descriptors_valid(' + state + '[.FILECONTEXTS = ' + context + '[.OWNER = 999] :: eps])']
    conditions += ['$file_parse_response_valid(S_parse,' + accepted + ')',
                   '~$file_parse_response_valid(S_parse,(SOURCE_ACCEPT 999 ' + seq(CHILD) + ' ' + checked_child['fixture'] + '))',
                   'S_running = $file_parse_resume(S_parse,' + accepted + ')',
                   '~S_running.COMPILESTOP',
                   '$file_prefix_live(S_running)',
                   '$call_descriptors_valid(S_running)',
                   'S_done = $drive_steps(S_running,1000)',
                   'S_done.COMPLETION = NORMAL',
                   'S_done.FILEINCLUDEPATH = (' + seq(raw) + ')',
                   'S_done.FILECONTEXTS = eps',
                   'S_done.EVENTS = [OUTPUT ([55])]']
    fixture = directory / 'protocol.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions))
    return {'case': name, 'assertions': len(conditions), 'source_sha256': digest(source_path),
            'child_sha256': digest(child_path), 'fixture_sha256': digest(fixture)}


def main(cases=None):
    cases = CASES if cases is None else cases
    out = Path(tempfile.mkdtemp(prefix='ini-prefix-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', runner,
              ROOT / 'tests/semantics/numeric_runner.ml', ROOT / '_build/default/adapter/main.exe',
              ROOT / 'frontend/worker.php', ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
              ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php', ROOT / 'frontend/target.php',
              ROOT / 'frontend/SourcePrinter.php', ROOT / 'frontend/encoding.php', ROOT / 'frontend/wire.php',
              ROOT / 'frontend/wire.py', ROOT / 'spec/schema.json', ROOT / 'spec/php.watsup',
              ROOT / 'adapter/main.ml', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/recorded_worker.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_before = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'], cwd=ROOT, text=True).strip()
    rows = []
    for name, (template, suffix) in cases.items():
        directory = out / name
        row = prepare(name, template, suffix, directory, invoke_frame=name == 'invoke-interior-nul')
        command = [str(runner), *map(str, modules), str(directory / 'protocol.watsup')]
        (directory / 'command.json').write_text(json.dumps(command) + '\n')
        process = subprocess.run(command, capture_output=True, text=True, timeout=300)
        (directory / 'process.json').write_text(json.dumps({'status': 'exit', 'exit_status': process.returncode, 'timeout': 300}) + '\n')
        (directory / 'stdout').write_text(process.stdout)
        (directory / 'stderr').write_text(process.stderr)
        assert process.returncode == 0 and process.stdout == 'true\n' and not process.stderr, (name, process.stdout[-1000:], process.stderr[-2000:])
        rows.append(row)
        print(name, row['assertions'], flush=True)
    after = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'passed': True, 'cases': rows, 'inputs': before,
              'input_changes': [key for key in before if before[key] != after[key]],
              'vendor_tree': vendor_before, 'assertions': sum(row['assertions'] for row in rows)}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    assert not report['input_changes']
    assert vendor_before == subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'status', '--porcelain', '--', 'vendor/php-parser-source'], cwd=ROOT, text=True)


if __name__ == '__main__':
    main()
