#!/usr/bin/env python3
"""Independent rejected-main terminal state, warning order and refusal premises."""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
from main_rejected_source_review import SOURCE, file_packet
from encoding_declare_protocol import MESSAGE, ParserWorker, public
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
POSITIONS = ('beginLine', 'beginTokenPos', 'closeLine', 'closeTokenPos')
REFUSAL = '$initial_state(UNSUPPORTED "invalid rejected main source or startup facts")'


def prepare(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks, originals = [], {}

    def response(value, tag, unit=0, legacy=False):
        source, message = (term(base64.b64decode(value[key])) for key in ('source', 'message'))
        kind = 'FAILED_PARSE' if value['category'] == 'parser_rejection' else 'FAILED_COMPILE'
        if legacy:
            return '(' + ('SOURCE_PARSE_REJECT' if kind == 'FAILED_PARSE' else 'SOURCE_COMPILE_REJECT') + ' ' + str(unit) + ' ' + source + ' ' + message + ' ' + str(value['line']) + ')'
        headers = []
        for index, header in enumerate(value['headers']):
            suffix = tag + '_' + str(index)
            ast = {'version': 1, 'program': [{'node': 'Stmt_Declare', 'fields': [header['items'], None], 'meta': {}}]}
            fixture = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture']
            checks.extend(['U_' + suffix + ' = ' + fixture,
                'U_' + suffix + ' = PROGRAM ([NStmtDeclare (SEQUENCE phpType49_' + suffix + '*) ABSENT eps])'])
            headers.append('(PARSE_HEADER ' + ' '.join('(' + str(header[key]) + ')' for key in POSITIONS)
                           + ' (phpType49_' + suffix + '*))')
        return '(SOURCE_REJECT_HEADERS ' + str(unit) + ' ' + source + ' ' + kind + ' ' + message + ' ' + str(value['line']) + ' ([' + ','.join(headers) + ']))'

    def entry(source, value, filename, startup='eps', display='false,eps', precision='14', assertions='1', cwd='eps'):
        return ('$php_rejected_main_run(' + term(source) + ',' + value + ',' + term(os.fsencode(filename)) + ','
                + startup + ',' + display + ',$ptascii(' + json.dumps(precision) + '),$ptascii('
                + json.dumps(assertions) + '),eps,' + cwd + ')')

    try:
        cases = [('parse', SOURCE, [3, 4, 4], 5, 'ParseError'),
                 ('compile', b'<?php\ndeclare(encoding=true,Foo=function(){\n declare(encoding=2);\n});', [3], 4, 'CompileError')]
        for tag, source, lines, line, kind in cases:
            filename = out / (tag + ' \u03bb main.php'); filename.write_bytes(source)
            parsed = file_packet(frontend, source, filename)
            assert parsed['line'] == line and parsed['category'] == ('parser_rejection' if tag == 'parse' else 'parser_static_rejection')
            value = response(parsed, tag); originals[tag] = (source, filename, parsed, value)
            message = term(base64.b64decode(parsed['message']))
            warning = lambda number: 'DIAGNOSTIC_SOURCE 0 "Warning" ($ptascii(' + json.dumps(MESSAGE) + ')) ' + str(number)
            warnings = [warning(number) for number in lines]
            terminal = 'DIAGNOSTIC_SOURCE 0 ' + json.dumps('Parse error' if tag == 'parse' else 'Fatal error') + ' ' + message + ' ' + str(line)
            events = warnings + [terminal]
            state = 'S_' + tag
            checks += [state + ' = ' + entry(source, value, filename),
                state + '.COMPLETION = REQUESTFATAL ($ptascii(' + json.dumps(kind) + ')) ' + message + ' ' + str(line),
                state + '.EXITSTATUS = 255', state + '.FILES = [SOURCEFILE 0 ' + term(os.fsencode(filename)) + ']',
                state + '.EVENTS = [' + ','.join(events) + ']', state + '.COMPILESTOP = false',
                state + '.ORIGIN = eps', state + '.SOURCEPENDING = eps', state + '.SERVICELEFT = eps',
                state + '.ERRORHANDLER.CALLBACK = eps', state + '.EXCEPTIONHANDLER = eps',
                state + '.SHUTDOWN.ENTRIES = eps', state + '.DESTRUCTION.HANDLES = eps',
                *[state + '.' + field + ' = eps' for field in ('SOURCES', 'CODE', 'DECLARATIONS', 'POOLS', 'FUNCTIONS',
                    'CLASSES', 'USERCONSTANTS', 'OBJECTS', 'ARRAYS', 'STORE', 'ALLOCATIONS', 'TODO', 'FRAMES',
                    'EVALCONTEXTS', 'FILECONTEXTS', 'EVALBINDINGS', 'FILEBINDINGS', 'FAILEDSOURCES')], *public(state)]
            for reporting in (0, 4, 64, 128):
                masked = state + '_mask' + str(reporting)
                startup = '({REPORTING ($ptascii(' + json.dumps(str(reporting)) + ')),INCLUDEPATH ($ptascii(".:"))})'
                selected = (warnings if reporting & 128 else []) + ([terminal] if reporting & (4 if tag == 'parse' else 64) else [])
                checks += [masked + ' = ' + entry(source, value, filename, startup=startup),
                    masked + '.EVENTS = [' + ','.join(selected) + ']', masked + '.COMPLETION = ' + state + '.COMPLETION',
                    masked + '.EXITSTATUS = 255', masked + '.REPORTING = ' + str(reporting), '$call_descriptors_valid(' + masked + ')']
            for display in ('0', '1'):
                shown = state + '_display' + display
                selected = ['DISPLAY_STDOUT (' + event + ')' for event in events] if display == '1' else []
                checks += [shown + ' = ' + entry(source, value, filename, display='true,($ptascii(' + json.dumps(display) + '))'),
                    shown + '.EVENTS = [' + ','.join(selected) + ']', shown + '.COMPLETION = ' + state + '.COMPLETION',
                    shown + '.EXITSTATUS = 255', '$display_state_mode(' + shown + ') = ' + display]
            legacy = response(parsed, tag, legacy=True)
            checks += [state + '_legacy = ' + entry(source, legacy, filename), state + '_legacy = ' + state + '[.EVENTS = [' + terminal + ']]']
            if tag == 'parse':
                checks += [state + '_cwd = ' + entry(source, value, filename, cwd='(' + term(os.fsencode(out)) + ')'),
                    state + '_cwd.FILECWD = (' + term(os.fsencode(out)) + ')', state + '_cwd.INCLUDEDOPENED = [' + term(os.fsencode(filename)) + ']',
                    state + '_cwd.SOURCES = eps', state + '_cwd.EVENTS = ' + state + '.EVENTS', *public(state + '_cwd')]

        source, filename, original, value = originals['parse']
        checks += [entry(source, response(original, 'wrong_unit', unit=1), filename) + ' = ' + REFUSAL,
            entry(source + b' ', value, filename) + ' = ' + REFUSAL,
            entry(source, '(SOURCE_ACCEPT 0 ' + term(source) + ' (PROGRAM eps))', filename) + ' = ' + REFUSAL,
            entry(source, '(SOURCE_PARSE_REJECT 0 ' + term(source) + ' eps 1)', filename) + ' = ' + REFUSAL,
            entry(source, '(SOURCE_PARSE_REJECT 0 ' + term(source) + ' ($ptascii("bad")) 0)', filename) + ' = ' + REFUSAL,
            entry(source, value, filename, precision='-2') + ' = ' + REFUSAL,
            entry(source, value, filename, assertions='2') + ' = ' + REFUSAL]
        mutations = []
        for name in ('duplicate-header', 'duplicate-item', 'reversed-item', 'missing-position'):
            changed = copy.deepcopy(original); header = changed['headers'][0]
            if name == 'duplicate-header': changed['headers'].append(copy.deepcopy(header))
            elif name == 'duplicate-item': header['items'].append(copy.deepcopy(header['items'][0]))
            elif name == 'reversed-item': header['items'][0]['meta']['startTokenPos'] = {'int': str(header['closeTokenPos'])}
            else: del header['items'][0]['meta']['endLine']
            mutations.append((name, source, filename, changed))
        source, filename, original, value = originals['compile']
        for key, changed_value in [('category', 'parser_rejection'), ('message', b64(b'other')), ('line', 3)]:
            changed = dict(original, **{key: changed_value}); mutations.append(('stop-' + key, source, filename, changed))
        for name, source, filename, changed in mutations:
            checks.append(entry(source, response(changed, 'bad_' + name.replace('-', '_')), filename) + ' = ' + REFUSAL)
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *modules, *(ROOT / name for name in ('tests/main_rejected_source_review.py', 'adapter/main.ml',
        'bin/php-semantics', 'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php', '.tools/php/bin/php',
        '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe',
        'tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py',
        'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/error_handler_run.py'))]
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
        report['inputs_stable'] = before == {str(path): sha(path) for path in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
