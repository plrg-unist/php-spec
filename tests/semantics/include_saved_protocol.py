#!/usr/bin/env python3
"""File-to-eval-to-file nesting keeps the outer barrier in a saved frame."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
MAIN = b"<?php echo include 'one.php';"
OUTER = b'''<?php function f(){ return eval('return include "two.php";'); } return f();'''
EVAL_SOURCE = b'return include "two.php";'
INNER = b'<?php return 7;'
PREFIX = '''
dec $drop_file_end(ptask*, nat) : ptask*
def $drop_file_end(eps, n) = eps
def $drop_file_end((FILE_END n) :: ptask_tail*, n) = ptask_tail*
def $drop_file_end(ptask :: ptask_tail*, n) = ptask :: $drop_file_end(ptask_tail*, n)
  -- if ptask =/= FILE_END n
dec $drop_eval_end(ptask*, nat) : ptask*
def $drop_eval_end(eps, n) = eps
def $drop_eval_end((EVAL_END n) :: ptask_tail*, n) = ptask_tail*
def $drop_eval_end(ptask :: ptask_tail*, n) = ptask :: $drop_eval_end(ptask_tail*, n)
  -- if ptask =/= EVAL_END n
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def seq(data):
    return '(' + str(list(data)) + ')'


def fixture(worker, adapter, source):
    parsed = worker.request({'op': 'parse', 'source': b64(source)})
    assert parsed['accepted'], parsed
    return adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']


def file_fixture(worker, adapter, source, requested, opened, nonce):
    parsed = worker.request({'op': 'parse-file', 'id': str(nonce), 'mode': 'file',
                             'profile': 'cli-raw-85', 'requested': b64(requested),
                             'resolved': b64(opened), 'opened': b64(opened),
                             'source': b64(source)})
    assert parsed['accepted'], parsed
    return adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree

def main():
    out = Path(tempfile.mkdtemp(prefix='include-saved-protocol-', dir=ROOT / '.tools'))
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
    paths = [out / name for name in ('main.php', 'one.php', 'two.php')]
    for path, source in zip(paths, (MAIN, OUTER, INNER)):
        path.write_bytes(source)
    main_bytes, outer_bytes, inner_bytes = (str(path.resolve()).encode() for path in paths)
    cwd_bytes = str(ROOT.resolve()).encode()
    worker = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                     'extension=' + str(ROOT / '.tools/php-file.so'),
                     str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        main_ast = fixture(worker, adapter, MAIN)
        outer_ast = file_fixture(worker, adapter, OUTER, b'one.php', outer_bytes, 0)
        parsed_eval = worker.request({'op': 'parse-eval', 'id': '2', 'mode': 'eval',
                                      'profile': 'cli-raw-85', 'source': b64(EVAL_SOURCE)})
        assert parsed_eval['accepted'], parsed_eval
        eval_ast = adapter.request({'op': 'check', 'ast': parsed_eval['ast'], 'fixture': True})['fixture']
        inner_ast = file_fixture(worker, adapter, INNER, b'two.php', inner_bytes, 1)
    finally:
        worker.close()
        adapter.close()
    start = '$php_file_run(' + main_ast + ', 500, $base64(' + json.dumps(b64(main_bytes)) + '), $base64(' + json.dumps(b64(cwd_bytes)) + '))'
    open_outer = '(FILE_OPENED 0 ' + seq(main_bytes) + ' ' + seq(b'one.php') + ' ' + seq(outer_bytes) + ' ' + seq(outer_bytes) + ' ' + seq(OUTER) + ')'
    accept_outer = '(SOURCE_ACCEPT 1 ' + seq(OUTER) + ' ' + outer_ast + ')'
    accept_eval = '(SOURCE_ACCEPT 2 ' + seq(EVAL_SOURCE) + ' ' + eval_ast + ')'
    eval_filename = outer_bytes + b"(1) : eval()'d code"
    open_inner = '(FILE_OPENED 1 ' + seq(eval_filename) + ' ' + seq(b'two.php') + ' ' + seq(inner_bytes) + ' ' + seq(inner_bytes) + ' ' + seq(INNER) + ')'
    accept_inner = '(SOURCE_ACCEPT 3 ' + seq(INNER) + ' ' + inner_ast + ')'
    checks = [
        'S_initial = ' + start,
        'S_initial.COMPLETION = SOURCE_PENDING',
        'S_parse = $file_open_continue(S_initial, ' + open_outer + ')',
        'S_parse.COMPLETION = SOURCE_PENDING',
        'S_eval = $file_parse_continue(S_parse, ' + accept_outer + ')',
        'S_eval.COMPLETION = SOURCE_PENDING',
        'S_eval.EVALCONTEXTS = pevalcontext_pending :: eps',
        'pevalcontext_pending.PHASE = PARSER_WAIT',
        'S_inner_resolve = $eval_continue(S_eval, ' + accept_eval + ')',
        'S_inner_resolve.COMPLETION = SOURCE_PENDING',
        'S_inner_resolve.EVALCONTEXTS = pevalcontext_running :: eps',
        'pevalcontext_running.PHASE = UNIT_RUN',
        'pevalcontext_running.UNIT = 2',
        'S_inner_resolve.FILECONTEXTS = pfilecontext_inner :: pfilecontext_outer :: eps',
        'pfilecontext_inner.PHASE = FILE_RESOLVE_WAIT',
        'pfilecontext_outer.PHASE = FILE_UNIT_RUN',
        'pfilecontext_inner.NONCE = 1',
        'pfilecontext_outer.NONCE = 0',
        'pfilecontext_outer.UNIT = (1)',
        '$source_trace_at(S_inner_resolve, S_inner_resolve.EVALCONTEXTS, S_inner_resolve.FILECONTEXTS, |S_inner_resolve.FRAMES|) = [$eval_trace_frame(S_inner_resolve, pevalcontext_running)]',
        '$source_trace_at(S_inner_resolve, S_inner_resolve.EVALCONTEXTS, S_inner_resolve.FILECONTEXTS, 0) = [$file_trace_frame(S_inner_resolve, pfilecontext_outer)]',
        'S_inner_resolve.FILESEQ = 2',
        'S_inner_resolve.FRAMES = pframe :: pframe_tail*',
        '$file_marker_count(pframe.TODO, pfilecontext_outer) = 1',
        '$eval_marker_count(S_inner_resolve.TODO, 2) = 1',
        '$file_marker_count(S_inner_resolve.TODO, pfilecontext_inner) = 1',
        '$call_descriptors_valid(S_inner_resolve)',
        '~$call_descriptors_valid(S_inner_resolve[.FRAMES = pframe[.TODO = $drop_file_end(pframe.TODO, 1)] :: pframe_tail*])',
        '~$call_descriptors_valid(S_inner_resolve[.FRAMES = pframe[.TODO = (FILE_END 1) :: pframe.TODO] :: pframe_tail*])',
        '~$call_descriptors_valid(S_inner_resolve[.FRAMES = pframe[.TODO = (FILE_END 1) :: $drop_file_end(pframe.TODO, 1)] :: pframe_tail*])',
        '~$call_descriptors_valid(S_inner_resolve[.TODO = (FILE_END 1) :: $drop_eval_end(S_inner_resolve.TODO, 2)][.FRAMES = pframe[.TODO = (EVAL_END 2) :: $drop_file_end(pframe.TODO, 1)] :: pframe_tail*])',
        '~$call_descriptors_valid(S_inner_resolve[.FILECONTEXTS = pfilecontext_inner :: pfilecontext_outer[.OWNER = $(pfilecontext_outer.OWNER + 1)] :: eps])',
        'S_inner_parse = $file_open_continue(S_inner_resolve, ' + open_inner + ')',
        'S_inner_parse.COMPLETION = SOURCE_PENDING',
        'S_inner_parse.FILECONTEXTS = pfilecontext_parse :: pfilecontext_outer_again :: eps',
        'pfilecontext_parse.UNIT = (3)',
        '$source_trace_at(S_inner_parse, S_inner_parse.EVALCONTEXTS, S_inner_parse.FILECONTEXTS, |S_inner_parse.FRAMES|) = [$eval_trace_frame(S_inner_parse, pevalcontext_running)]',
        'S_inner_parse.FILESEQ = 2',
        '$call_descriptors_valid(S_inner_parse)',
        'S_done = $file_parse_continue(S_inner_parse, ' + accept_inner + ')',
        'S_done.COMPLETION = NORMAL',
        'S_done.FILECONTEXTS = eps',
        'S_done.FRAMES = eps',
        'S_done.FILEBINDINGS = [pfilebinding_outer,pfilebinding_inner]',
        'S_done.EVALBINDINGS = [pevalbinding]',
        '$call_descriptors_valid(S_done)',
    ]
    protocol = out / 'protocol.watsup'
    protocol.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- if ' + condition + '\n' for condition in checks))
    command = [str(runner), *map(str, modules), str(protocol)]
    (out / 'command.json').write_text(json.dumps(command) + '\n')
    result = subprocess.run(command, capture_output=True, timeout=300)
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    assert vendor_before == vendor_identity()
    passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    (out / 'report.json').write_text(json.dumps({
        'result': 'pass' if passed else 'fail', 'assertions': len(checks),
        'inputs': before, 'vendor_parser_tree': vendor_before, 'sources_sha256': {path.name: digest(path) for path in paths},
        'fixture_sha256': digest(protocol), 'runner_exit_status': result.returncode,
        'scope': 'File-to-eval-to-file pause with saved FILE_END and forged cross-kind marker swap.'
    }, indent=2) + '\n')
    print('include-saved-protocol', passed, len(checks), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
