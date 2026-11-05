#!/usr/bin/env python3
"""Independent failed-source warning identity, budget and receipt refusals."""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

from encoding_declare_protocol import CLI, MESSAGE, PREFIX, ParserWorker, public
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
literal = lambda data: b"'" + data.replace(b'\\', b'\\\\').replace(b"'", b"\\'") + b"'"
POSITIONS = ('beginLine', 'beginTokenPos', 'closeLine', 'closeTokenPos')


def prepare(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks, responses = [], {}

    def response(value, tag, unit=1):
        headers = []
        for index, header in enumerate(value['headers']):
            suffix = tag + '_' + str(index)
            ast = {'version': 1, 'program': [{'node': 'Stmt_Declare', 'fields': [header['items'], None], 'meta': {}}]}
            fixture = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture']
            checks.extend(['U_' + suffix + ' = ' + fixture,
                'U_' + suffix + ' = PROGRAM ([NStmtDeclare (SEQUENCE phpType49_' + suffix + '*) ABSENT eps])'])
            headers.append('(PARSE_HEADER ' + ' '.join('(' + str(header[key]) + ')' for key in POSITIONS)
                           + ' (phpType49_' + suffix + '*))')
        kind = 'FAILED_PARSE' if value['category'] == 'parser_rejection' else 'FAILED_COMPILE'
        return ('(SOURCE_REJECT_HEADERS ' + str(unit) + ' ' + term(base64.b64decode(value['source'])) + ' ' + kind
                + ' ' + term(base64.b64decode(value['message'])) + ' ' + str(value['line']) + ' ([' + ','.join(headers) + ']))')

    try:
        code = b'declare(\n encoding=1\n);\necho ;'
        for mode in ('eval', 'file'):
            unit = code if mode == 'eval' else b'<?php\n' + code
            child = out / 'unit.php'
            if mode == 'file': child.write_bytes(unit)
            operation = b'eval(' + literal(code) + b')' if mode == 'eval' else b'include "unit.php"'
            main = b'<?php echo "M|";try{' + operation + b';}catch(ParseError $e){echo "C|";}finally{echo "F|";}echo "A|";'
            path = out / (mode + '.php'); path.write_bytes(main)
            ast = frontend.request({'op': 'parse', 'source': b64(main)})['ast']
            checks.append('U_' + mode + ' = ' + adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture'])
            request = {'op': 'parse-' + mode, 'id': '1', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(unit)}
            if mode == 'file': request.update(requested=b64(b'unit.php'), resolved=b64(os.fsencode(child)), opened=b64(os.fsencode(child)))
            parsed = frontend.request(request)
            raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
            frontend.recorded_stderr.extend(raw)
            assert not parsed['accepted'] and CLI['dynamic_parser_stderr'](parsed, mode, raw)
            warning_line = 3 if mode == 'eval' else 4
            assert parsed['line'] == warning_line + 1 and parsed['headers'][0]['closeLine'] == warning_line
            value = response(parsed, mode); responses[mode] = parsed
            state = 'S_' + mode
            if mode == 'eval':
                checks += [state + ' = $php_run(U_eval,1500,' + json.dumps(b64(os.fsencode(path))) + ')',
                    state + '.EVALCONTEXTS = [pevalcontext]', 'pevalcontext.UNIT = 1']
                resume, valid, continuation = '$eval_resume', '$eval_response_valid', '$eval_continue'
            else:
                checks += ['S_file_open = $php_file_run(U_file,1500,' + term(os.fsencode(path)) + ',' + term(os.fsencode(out)) + ')',
                    'S_file_open.COMPLETION = SOURCE_PENDING', 'S_file_open.FILECONTEXTS = [pfilecontext_open]',
                    state + ' = $file_open_resume(S_file_open,FILE_OPENED pfilecontext_open.NONCE pfilecontext_open.CALLER pfilecontext_open.REQUESTED '
                    + term(os.fsencode(child)) + ' ' + term(os.fsencode(child)) + ' ' + term(unit) + ')',
                    state + '.FILECONTEXTS = [pfilecontext]', 'pfilecontext.UNIT = (1)']
                resume, valid, continuation = '$file_parse_resume', '$file_parse_response_valid', '$file_parse_continue'
            checks += [state + '.COMPLETION = SOURCE_PENDING', *public(state), valid + '(' + state + ',' + value + ')',
                state + '_resumed = ' + resume + '(' + state + ',' + value + ')',
                state + '_resumed.COMPLETION = NORMAL', state + '_resumed.COMPILESTOP = false',
                state + '_resumed.SOURCES = ' + state + '.SOURCES', state + '_resumed.CODE = ' + state + '.CODE',
                state + '_resumed.EVALBINDINGS = ' + state + '.EVALBINDINGS', state + '_resumed.FILEBINDINGS = ' + state + '.FILEBINDINGS',
                state + '_resumed.EVALCONTEXTS = eps', state + '_resumed.FILECONTEXTS = eps',
                state + '_resumed.SERVICELEFT = eps', state + '_resumed.FAILEDSOURCES = [pfailedsource_' + mode + ']',
                'pfailedsource_' + mode + '.UNIT = 1', 'pfailedsource_' + mode + '.ISFILE = ' + str(mode == 'file').lower(),
                'pfailedsource_' + mode + '.BYTES = ' + term(unit), 'pfailedsource_' + mode + '.KIND = FAILED_PARSE',
                'pfailedsource_' + mode + '.LINE = ' + str(warning_line + 1),
                'pfailedsource_' + mode + '.FILE = $call_sourcefile(' + state + '.FILES,PORIGIN 1 eps)',
                state + '_resumed.EVENTS = ' + state + '.EVENTS ++ [DIAGNOSTIC_SOURCE 1 "Warning" ($ptascii(' + json.dumps(MESSAGE) + ')) ' + str(warning_line) + ']',
                *public(state + '_resumed'), '~' + valid + '(' + state + '_resumed,' + value + ')',
                state + '_replay = ' + resume + '(' + state + '_resumed,' + value + ')',
                state + '_replay = ' + state + '_resumed[.COMPLETION = UNSUPPORTED "invalid ' + ('eval' if mode == 'eval' else 'file') + ' parser response"]',
                state + '_masked = ' + resume + '(' + state + '[.REPORTING = 0],' + value + ')',
                state + '_masked.EVENTS = ' + state + '.EVENTS', state + '_masked.FAILEDSOURCES = ' + state + '_resumed.FAILEDSOURCES',
                state + '_zero = ' + continuation + '(' + state + '[.SERVICELEFT = (0)],' + value + ')',
                state + '_zero.COMPLETION = BUDGET', state + '_zero.EVENTS = ' + state + '_resumed.EVENTS',
                state + '_zero.FAILEDSOURCES = ' + state + '_resumed.FAILEDSOURCES', *public(state + '_zero'),
                state + '_done = $drive_steps(' + state + '_zero[.COMPLETION = NORMAL],1500)',
                state + '_done.COMPLETION = NORMAL', state + '_done.TODO = eps',
                '$test_outputs(' + state + '_done.EVENTS) = $ptascii("M|C|F|A|")', *public(state + '_done')]

        original = responses['eval']; mutations = []
        for key, value in [('beginLine', 0), ('beginTokenPos', -1), ('closeLine', 1), ('closeTokenPos', 0)]:
            changed = copy.deepcopy(original); changed['headers'][0][key] = value
            mutations.append((key, changed))
        for name in ('empty', 'duplicate-header', 'duplicate-item', 'missing-position', 'name-after-value', 'value-before-name'):
            changed = copy.deepcopy(original); header = changed['headers'][0]; item = header['items'][0]
            if name == 'empty': header['items'] = []
            elif name == 'duplicate-header': changed['headers'].append(copy.deepcopy(header))
            elif name == 'duplicate-item': header['items'].append(copy.deepcopy(item))
            elif name == 'missing-position': del item['meta']['startTokenPos']
            elif name == 'name-after-value': item['fields'][0]['meta'] = copy.deepcopy(item['fields'][1]['meta'])
            else: item['fields'][1]['meta'] = copy.deepcopy(item['fields'][0]['meta'])
            mutations.append((name, changed))
        for name, changed in mutations:
            tag = 'bad_' + name.replace('-', '_'); value = response(changed, tag)
            assert CLI['rejected_encoding_warning_lines'](changed) is None
            checks += ['~$eval_response_shape(' + value + ')', '~$eval_response_valid(S_eval,' + value + ')',
                'S_' + tag + ' = $eval_resume(S_eval,' + value + ')',
                'S_' + tag + ' = S_eval[.COMPLETION = UNSUPPORTED "invalid eval parser response"]']
        compile_code = b'declare(encoding=1,encoding=true);'
        compile_result = frontend.parse({'op': 'parse-eval', 'id': '1', 'mode': 'eval', 'profile': 'cli-raw-85', 'source': b64(compile_code)})
        assert compile_result['category'] == 'parser_static_rejection'
        checks.append('$eval_response_shape(' + response(compile_result, 'compile') + ')')
        for key, value in [('category', 'parser_rejection'), ('message', b64(b'other')), ('line', 2)]:
            changed = dict(compile_result, **{key: value})
            assert CLI['rejected_encoding_warning_lines'](changed) is None
            checks.append('~$eval_response_shape(' + response(changed, 'bad_compile_' + key) + ')')
        # Duplicate metadata cannot be represented by the JSON metadata object.
        checks += ['phpType49_eval_0* = [(NDeclareItem phpType11_eval expression_eval metadata_eval)]',
            'phpType49_duplicate_meta = NDeclareItem phpType11_eval expression_eval ((MstartLine 2) :: metadata_eval)',
            '~$rejected_header_items([phpType49_duplicate_meta],1,3,0,7)']
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\n' + PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *modules, *(ROOT / name for name in ('spec/semantics/modules.json', 'spec/schema.json',
        'adapter/main.ml', 'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php',
        'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/profile.json', 'tests/semantics/encoding_declare_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/semantics/error_handler_run.py'))]
    before = {str(path): sha(path) for path in paths}
    assert before[str(ROOT / '.tools/php/bin/php')] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path): sha(Path(path)) for path in before}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
