#!/usr/bin/env python3
"""Checked header-prefix tables and reached failed include_once/reparse state."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from encoding_declare_protocol import CLI, MESSAGE, PREFIX, ParserWorker, public
from error_handler_run import recorded
from recorded_worker import Worker
from rejected_encoding_sources import CASES, HASHES, ORACLE, SOURCE, expected
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
POSITIONS = ('beginLine', 'beginTokenPos', 'closeLine', 'closeTokenPos')
EXTRA = r'''
dec $test_rejected_warning_unit(pevent) : nat?
def $test_rejected_warning_unit(DIAGNOSTIC_SOURCE n "Warning" n_message* z) = (n)
def $test_rejected_warning_unit(pevent) = eps -- otherwise
dec $test_rejected_warnings(pevent*) : nat*
def $test_rejected_warnings(eps) = eps
def $test_rejected_warnings(pevent :: pevent_tail*) = n :: $test_rejected_warnings(pevent_tail*)
  -- if $test_rejected_warning_unit(pevent) = (n)
def $test_rejected_warnings(pevent :: pevent_tail*) = $test_rejected_warnings(pevent_tail*)
  -- if $test_rejected_warning_unit(pevent) = eps
'''


def prepare(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks, responses = [], {}
    try:
        for name, case in CASES.items():
            if case['status'] == 'unsupported': continue
            path = SOURCE / name / 'unit.php'; code = path.read_bytes(); tag = name.replace('-', '_')
            request = {'op': 'parse-' + case['mode'], 'id': '1', 'mode': case['mode'],
                'profile': 'cli-raw-85', 'source': b64(code)}
            if case['mode'] == 'file':
                request.update(requested=b64(bytes(path)), resolved=b64(bytes(path)), opened=b64(bytes(path)))
            parsed = frontend.request(request)
            raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
            frontend.recorded_stderr.extend(raw)
            assert not parsed['accepted'] and CLI['dynamic_parser_stderr'](parsed, case['mode'], raw)
            lines = ([1] if name in ('eval-suppressed', 'eval-mask-zero', 'include-once-retry') else case['warning_lines'])
            assert CLI['rejected_encoding_warning_lines'](parsed) == lines
            headers = []
            for index, header in enumerate(parsed.get('headers', [])):
                suffix = tag + '_' + str(index)
                ast = {'version': 1, 'program': [{'node': 'Stmt_Declare', 'fields': [header['items'], None], 'meta': {}}]}
                fixture = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture']
                checks += ['U_' + suffix + ' = ' + fixture,
                    'U_' + suffix + ' = PROGRAM ([NStmtDeclare (SEQUENCE phpType49_' + suffix + '*) ABSENT eps])']
                headers.append('(PARSE_HEADER ' + ' '.join('(' + str(header[key]) + ')' for key in POSITIONS)
                    + ' (phpType49_' + suffix + '*))')
            header_term = '[' + ','.join(headers) + ']'
            stop = '(' + str(case['line']) + ')' if case['kind'] == 'CompileError' and case['message'] == 'Encoding must be a literal' else 'eps'
            kind = 'FAILED_PARSE' if parsed['category'] == 'parser_rejection' else 'FAILED_COMPILE'
            value = ('SOURCE_REJECT_HEADERS 1 ' + term(code) + ' ' + kind + ' '
                + term(base64.b64decode(parsed['message'])) + ' ' + str(parsed['line']) + ' (' + header_term + ')')
            checks += ['$rejected_headers_valid(' + header_term + ',-1,1)',
                '$rejected_header_prefix(' + header_term + ') = (' + str(lines) + ',z_stop_' + tag + '?)',
                'z_stop_' + tag + '? = ' + stop,
                '$eval_response_shape(' + value + ')']
            responses[name] = value

        path = SOURCE / 'include-once-retry/main.php'; child = path.with_name('unit.php'); code = child.read_bytes()
        parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())})
        fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
        response = responses['include-once-retry']
        opened = lambda context: ('FILE_OPENED ' + context + '.NONCE ' + context + '.CALLER ' + context
            + '.REQUESTED ' + term(bytes(child)) + ' ' + term(bytes(child)) + ' ' + term(code))
        checks += ['U_main = ' + fixture,
            'S_open = $php_file_run(U_main,3000,' + term(bytes(path)) + ',' + term(bytes(ROOT)) + ')',
            'S_open.COMPLETION = SOURCE_PENDING', 'S_open.FILECONTEXTS = [pfilecontext_first]',
            'pfilecontext_first.PHASE = FILE_RESOLVE_WAIT', 'S_open.FILESEQ = 1',
            'S_parse = $file_open_resume(S_open,' + opened('pfilecontext_first') + ')',
            'S_parse.COMPLETION = SOURCE_PENDING', 'S_parse.FILECONTEXTS = [pfilecontext_parse]',
            'pfilecontext_parse.UNIT = (1)', 'S_parse.INCLUDEDOPENED = [' + term(bytes(child)) + ']',
            '$file_parse_response_valid(S_parse,' + response + ')',
            'S_throw = $file_parse_resume(S_parse,' + response + ')',
            'S_throw.COMPLETION = NORMAL', 'S_throw.ERRORHANDLER = S_parse.ERRORHANDLER',
            'S_throw.SOURCES = S_parse.SOURCES', 'S_throw.CODE = S_parse.CODE',
            'S_throw.FAILEDSOURCES = [pfailedsource_first]', 'pfailedsource_first.UNIT = 1',
            '$test_rejected_warnings(S_throw.EVENTS) = [1]', *public('S_throw'),
            'S_second = $drive_steps(S_throw,3000)', 'S_second.COMPLETION = SOURCE_PENDING',
            'S_second.FILECONTEXTS = [pfilecontext_second]', 'pfilecontext_second.PHASE = FILE_RESOLVE_WAIT',
            'pfilecontext_second.UNIT = eps', 'S_second.FILESEQ = 2', '|S_second.FILES| = 2',
            'S_skip = $file_open_resume(S_second,' + opened('pfilecontext_second') + ')',
            'S_skip.COMPLETION = NORMAL', 'S_skip.RESULT = KNOWN (PBOOL true)',
            'S_skip.FILES = S_second.FILES', 'S_skip.SOURCES = S_second.SOURCES',
            'S_skip.FAILEDSOURCES = S_second.FAILEDSOURCES', 'S_skip.EVENTS = S_second.EVENTS',
            'S_skip.FILECONTEXTS = eps', *public('S_skip'),
            'S_third = $drive_steps(S_skip,3000)', 'S_third.COMPLETION = SOURCE_PENDING',
            'S_third.FILECONTEXTS = [pfilecontext_third]', 'pfilecontext_third.PHASE = FILE_RESOLVE_WAIT',
            'S_third.FILESEQ = 3', '|S_third.FILES| = 2', '$test_rejected_warnings(S_third.EVENTS) = [1]',
            'S_reparse = $file_open_resume(S_third,' + opened('pfilecontext_third') + ')',
            'S_reparse.COMPLETION = SOURCE_PENDING', 'S_reparse.FILECONTEXTS = [pfilecontext_reparse]',
            'pfilecontext_reparse.UNIT = (2)', '|S_reparse.FILES| = 3',
            '~$file_parse_response_valid(S_reparse,' + response + ')',
            '$file_parse_response_valid(S_reparse,' + response.replace('SOURCE_REJECT_HEADERS 1 ', 'SOURCE_REJECT_HEADERS 2 ', 1) + ')',
            'S_done = $file_parse_continue(S_reparse,' + response.replace('SOURCE_REJECT_HEADERS 1 ', 'SOURCE_REJECT_HEADERS 2 ', 1) + ')',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps', 'S_done.FILECONTEXTS = eps',
            'S_done.SOURCES = S_parse.SOURCES', 'S_done.FILEBINDINGS = eps', 'S_done.EVALBINDINGS = eps',
            'S_done.INCLUDEDOPENED = S_parse.INCLUDEDOPENED', '$test_rejected_warnings(S_done.EVENTS) = [1,2]',
            'S_done.FAILEDSOURCES = pfailedsource_second :: pfailedsource_first :: eps',
            'pfailedsource_second.UNIT = 2', 'pfailedsource_second.BYTES = pfailedsource_first.BYTES',
            'pfailedsource_second.FILE = pfailedsource_first.FILE',
            '$test_outputs(S_done.EVENTS) = ' + term(expected('include-once-retry')[0]), *public('S_done')]
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\n' + PREFIX + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *modules, SOURCE / 'hashes.json', *(SOURCE / name for name in HASHES),
        *(ROOT / name for name in ('spec/semantics/modules.json', 'spec/schema.json', 'adapter/main.ml', 'bin/php-semantics',
          'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php',
          '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/profile.json',
          'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/rejected_encoding_sources.py',
          'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/recorded_worker.py',
          'tests/semantics/static_types.py', 'tests/semantics/error_handler_run.py'))]
    inputs = {str(path): sha(path) for path in paths}; head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    report = {'head': head, 'inputs': inputs, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and (out / 'check.stdout').read_bytes() == b'true\n' and not (out / 'check.stderr').read_bytes())
    finally:
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        report['inputs_stable'] = inputs == {str(path): sha(path) for path in paths}
        report['passed'] = report['passed'] and report['head_stable'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__':
    main()
