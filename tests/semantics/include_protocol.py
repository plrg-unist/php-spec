#!/usr/bin/env python3
"""Source-derived finite file pauses, bindings, markers and budget replay."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = b"<?php echo include 'one.php';"
CHILD = b'<?php return 7;'
BAD = b'<?php echo ;'
ONCE_SOURCE = b'<?php echo include_once __FILE__;'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def seq(data):
    return '(' + str(list(data)) + ')'


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree

def main():
    out = Path(tempfile.mkdtemp(prefix='include-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', runner,
              ROOT / 'tests/semantics/numeric_runner.ml',
              ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
              ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
              ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php',
              ROOT / 'frontend/target.php', ROOT / 'frontend/SourcePrinter.php',
              ROOT / 'frontend/encoding.php', ROOT / 'spec/schema.json',
              ROOT / 'spec/php.watsup', ROOT / 'adapter/main.ml', ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
              ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/static_types.py',
              ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py', ROOT / 'tests/validate.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    vendor_before = vendor_identity()
    source_path = out / 'main.php'
    child_path = out / 'one.php'
    bad_path = out / 'bad.php'
    once_path = out / 'once.php'
    source_path.write_bytes(SOURCE)
    child_path.write_bytes(CHILD)
    bad_path.write_bytes(BAD)
    once_path.write_bytes(ONCE_SOURCE)
    main_bytes = str(source_path.resolve()).encode()
    child_bytes = str(child_path.resolve()).encode()
    bad_bytes = str(bad_path.resolve()).encode()
    once_bytes = str(once_path.resolve()).encode()
    cwd_bytes = str(ROOT.resolve()).encode()
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(SOURCE)})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        parsed_file = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
                                        'profile': 'cli-raw-85', 'requested': b64(b'one.php'),
                                        'resolved': b64(child_bytes), 'opened': b64(child_bytes),
                                        'source': b64(CHILD)})
        assert parsed_file['accepted'], parsed_file
        checked_file = adapter.request({'op': 'check', 'ast': parsed_file['ast'], 'fixture': True})
        parsed_bad = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
                                       'profile': 'cli-raw-85', 'requested': b64(b'one.php'),
                                       'resolved': b64(bad_bytes), 'opened': b64(bad_bytes),
                                       'source': b64(BAD)})
        assert not parsed_bad['accepted'] and parsed_bad['category'] == 'parser_rejection', parsed_bad
        parsed_once = frontend.request({'op': 'parse', 'source': b64(ONCE_SOURCE)})
        assert parsed_once['accepted'], parsed_once
        checked_once = adapter.request({'op': 'check', 'ast': parsed_once['ast'], 'fixture': True})
    finally:
        frontend.close()
        adapter.close()
    start = '$php_file_run(' + checked['fixture'] + ', 300, $base64(' + json.dumps(b64(main_bytes)) + '), $base64(' + json.dumps(b64(cwd_bytes)) + '))'
    open_fact = '(FILE_OPENED 0 ' + seq(main_bytes) + ' ' + seq(b'one.php') + ' ' + seq(child_bytes) + ' ' + seq(child_bytes) + ' ' + seq(CHILD) + ')'
    accepted = '(SOURCE_ACCEPT 1 ' + seq(CHILD) + ' ' + checked_file['fixture'] + ')'
    open_bad = '(FILE_OPENED 0 ' + seq(main_bytes) + ' ' + seq(b'one.php') + ' ' + seq(bad_bytes) + ' ' + seq(bad_bytes) + ' ' + seq(BAD) + ')'
    rejected = '(SOURCE_PARSE_REJECT 1 ' + seq(BAD) + ' ' + seq(base64.b64decode(parsed_bad['message'])) + ' ' + str(parsed_bad['line']) + ')'
    once_start = '$php_file_run(' + checked_once['fixture'] + ', 300, $base64(' + json.dumps(b64(once_bytes)) + '), $base64(' + json.dumps(b64(cwd_bytes)) + '))'
    open_once = '(FILE_OPENED 0 ' + seq(once_bytes) + ' ' + seq(once_bytes) + ' ' + seq(once_bytes) + ' ' + seq(once_bytes) + ' ' + seq(ONCE_SOURCE) + ')'
    checks = [
        'S_initial = ' + start,
        'S_initial.COMPLETION = SOURCE_PENDING',
        'S_initial.FILECONTEXTS = pfilecontext_resolve :: eps',
        'pfilecontext_resolve.PHASE = FILE_RESOLVE_WAIT',
        'pfilecontext_resolve.UNIT = eps',
        'pfilecontext_resolve.RESOLVED = eps',
        'pfilecontext_resolve.OPENED = eps',
        'pfilecontext_resolve.BYTES = eps',
        'S_initial.FILESEQ = 1',
        'S_initial.FILES = [SOURCEFILE 0 ' + seq(main_bytes) + ']',
        '$call_descriptors_valid(S_initial)',
        '~$call_descriptors_valid(S_initial[.INCLUDEDOPENED = S_initial.INCLUDEDOPENED ++ [' + seq(b'/forged/file.php') + ']])',
        'S_initial.SERVICELEFT = (n_left)',
        '$(n_left > 1)',
        'n_low = $(301 - n_left)',
        'S_low = $php_file_run(' + checked['fixture'] + ', n_low, $base64(' + json.dumps(b64(main_bytes)) + '), $base64(' + json.dumps(b64(cwd_bytes)) + '))',
        'S_low.COMPLETION = SOURCE_PENDING',
        'S_low.SERVICELEFT = (1)',
        'S_low_parse = $file_open_continue(S_low, ' + open_fact + ')',
        'S_low_parse.COMPLETION = SOURCE_PENDING',
        'S_low_parse.SERVICELEFT = (1)',
        '$call_descriptors_valid(S_low_parse)',
        'S_low_done = $file_parse_continue(S_low_parse, ' + accepted + ')',
        'S_low_done.COMPLETION = BUDGET',
        '~$call_descriptors_valid(S_initial[.TODO = eps])',
        '~$call_descriptors_valid(S_initial[.TODO = (FILE_RESOLVE_AWAIT 0) :: S_initial.TODO])',
        '~$call_descriptors_valid(S_initial[.FILECONTEXTS = pfilecontext_resolve[.UNIT = (1)] :: eps])',
        '~$call_descriptors_valid(S_initial[.FILECONTEXTS = pfilecontext_resolve[.SITE = PORIGIN 999 eps] :: eps])',
        'S_parse = $file_open_resume(S_initial, ' + open_fact + ')',
        'S_parse.COMPLETION = SOURCE_PENDING',
        'S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
        'pfilecontext_parse.PHASE = FILE_PARSE_WAIT',
        'pfilecontext_parse.NONCE = 0',
        'pfilecontext_parse.UNIT = (1)',
        'S_parse.FILESEQ = 1',
        'S_parse.EVALBINDINGS = eps',
        'S_parse.FILEBINDINGS = eps',
        '$call_descriptors_valid(S_parse)',
        '~$call_descriptors_valid(S_parse[.TODO = eps])',
        '~$call_descriptors_valid(S_parse[.TODO = (FILE_PARSE_AWAIT 0) :: S_parse.TODO])',
        '~$call_descriptors_valid(S_parse[.FILECONTEXTS = pfilecontext_parse[.UNIT = eps] :: eps])',
        '~$call_descriptors_valid(S_parse[.FILECONTEXTS = pfilecontext_parse[.OPENED = eps] :: eps])',
        '~$file_parse_response_valid(S_parse, (SOURCE_ACCEPT 999 ' + seq(CHILD) + ' ' + checked_file['fixture'] + '))',
        'S_running = $file_parse_resume(S_parse, ' + accepted + ')',
        'S_running.COMPLETION = NORMAL',
        'S_running.FILECONTEXTS = pfilecontext_running :: eps',
        'pfilecontext_running.PHASE = FILE_UNIT_RUN',
        'S_running.FILEBINDINGS = [pfilebinding_running]',
        'pfilebinding_running.UNIT = 1',
        'S_running.EVALBINDINGS = eps',
        '$call_descriptors_valid(S_running)',
        '~$call_descriptors_valid(S_running[.FILEBINDINGS = eps])',
        '~$call_descriptors_valid(S_running[.FILEBINDINGS = [pfilebinding_running,pfilebinding_running]])',
        '~$call_descriptors_valid(S_running[.FILECONTEXTS = eps])',
        '~$call_descriptors_valid(S_running[.FILECONTEXTS = pfilecontext_running :: pfilecontext_running :: eps])',
        '~$call_descriptors_valid(S_running[.TODO = (FILE_END 1) :: S_running.TODO])',
        '~$call_descriptors_valid(S_running[.FILECONTEXTS = pfilecontext_running[.OWNER = $(pfilecontext_running.OWNER + 1)] :: eps])',
        '~$call_descriptors_valid(S_running[.FILECONTEXTS = pfilecontext_running[.TAIL = pfilecontext_running.TAIL ++ [DISCARD]] :: eps])',
        'S_done = $drive_steps(S_running, 100)',
        'S_done.COMPLETION = NORMAL',
        'S_done.FILECONTEXTS = eps',
        'S_done.FILEBINDINGS = [pfilebinding_running]',
        '$call_descriptors_valid(S_done)',
        'S_bad_parse = $file_open_resume(S_initial, ' + open_bad + ')',
        'S_bad_parse.COMPLETION = SOURCE_PENDING',
        'S_bad = $file_parse_resume(S_bad_parse, ' + rejected + ')',
        'S_bad.COMPLETION = NORMAL',
        'S_bad.FILECONTEXTS = eps',
        'S_bad.FILEBINDINGS = eps',
        'S_bad.FAILEDSOURCES = [pfailedsource]',
        'pfailedsource.ISFILE = true',
        'pfailedsource.FILE = ' + seq(bad_bytes),
        '$call_descriptors_valid(S_bad)',
        '~$call_descriptors_valid(S_bad[.INCLUDEDOPENED = S_bad.INCLUDEDOPENED ++ [' + seq(bad_bytes) + ']])',
        '~$call_descriptors_valid(S_bad[.FAILEDSOURCES = [pfailedsource[.ISFILE = false]]])',
        '~$call_descriptors_valid(S_bad[.FAILEDSOURCES = [pfailedsource[.FILE = ' + seq(child_bytes) + ']]])',
        'S_once_initial = ' + once_start,
        'S_once_initial.COMPLETION = SOURCE_PENDING',
        'S_once_skip = $file_open_resume(S_once_initial, ' + open_once + ')',
        'S_once_skip.COMPLETION = NORMAL',
        'S_once_skip.FILESEQ = 1',
        'S_once_skip.FILECONTEXTS = eps',
        'S_once_skip.FILES = [SOURCEFILE 0 ' + seq(once_bytes) + ']',
        'S_once_skip.FILEBINDINGS = eps',
        '$call_descriptors_valid(S_once_skip)',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- if ' + condition + '\n' for condition in checks))
    command = [str(runner), *map(str, modules), str(fixture)]
    (out / 'command.json').write_text(json.dumps(command) + '\n')
    result = subprocess.run(command, capture_output=True, timeout=300)
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    after = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    assert before == after
    assert vendor_before == vendor_identity()
    passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    (out / 'report.json').write_text(json.dumps({
        'result': 'pass' if passed else 'fail', 'assertions': len(checks),
        'inputs': before, 'vendor_parser_tree': vendor_before, 'source_sha256': digest(source_path),
        'child_sha256': digest(child_path), 'bad_sha256': digest(bad_path),
        'once_sha256': digest(once_path),
        'fixture_sha256': digest(fixture),
        'runner_exit_status': result.returncode,
        'scope': 'Source-derived two-phase file pause, unique binding, running marker and forged-state guards.'
    }, indent=2) + '\n')
    print('include-protocol', passed, len(checks), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
