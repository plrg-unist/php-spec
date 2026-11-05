#!/usr/bin/env python3
"""Independent constant-target rejection, earlier warnings and zero budget."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

from encoding_declare_protocol import MESSAGE, ParserWorker, public
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('constant_modifier_rejections')
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
literal = lambda data: b"'" + data.replace(b'\\', b'\\\\').replace(b"'", b"\\'") + b"'"
POSITIONS = ('beginLine', 'beginTokenPos', 'closeLine', 'closeTokenPos')
OUTPUTS = r'''
dec $test_constant_outputs(pevent*) : nat*
dec $test_constant_output(pevent) : nat*
def $test_constant_output(OUTPUT n*) = n*
def $test_constant_output(pevent) = eps -- otherwise
def $test_constant_outputs(eps) = eps
def $test_constant_outputs(pevent :: pevent_tail*) = $test_constant_output(pevent) ++ $test_constant_outputs(pevent_tail*)
'''


def prepare(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    cases = json.loads((SOURCE / 'cases.json').read_text()); checks = []
    try:
        for tag in ('constant',):
            name = 'attribute-before-abstract-constant-eval'; code = (SOURCE / name / 'unit.php').read_bytes(); case = cases[name]
            parsed = frontend.parse({'op': 'parse-eval', 'id': '1', 'mode': 'eval', 'profile': 'cli-raw-85', 'source': b64(code)})
            assert not parsed['accepted'] and parsed['category'] == 'parser_static_rejection' and parsed['line'] == case['line']
            assert base64.b64decode(parsed['message']) == case['message'].encode() and len(parsed['headers']) == 1
            headers = []
            for index, header in enumerate(parsed['headers']):
                suffix = tag + '_' + str(index)
                ast = {'version': 1, 'program': [{'node': 'Stmt_Declare', 'fields': [header['items'], None], 'meta': {}}]}
                fixture = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture']
                checks += ['U_' + suffix + ' = ' + fixture,
                    'U_' + suffix + ' = PROGRAM ([NStmtDeclare (SEQUENCE phpType49_' + suffix + '*) ABSENT eps])']
                headers.append('(PARSE_HEADER ' + ' '.join('(' + str(header[key]) + ')' for key in POSITIONS)
                    + ' (phpType49_' + suffix + '*))')
            value = '(SOURCE_REJECT_HEADERS 1 ' + term(code) + ' FAILED_COMPILE ' + term(case['message'].encode())
            value += ' ' + str(case['line']) + ' ([' + ','.join(headers) + ']))'
            main = (b'<?php set_error_handler(function(){echo "H|";return true;});'
                b'$trash=new stdClass;unset($trash);echo "M|";try{eval(' + literal(code)
                + b');}catch(Throwable $e){echo "C|";}finally{echo "F|";}echo "A|";')
            path = out / (tag + '-main.php'); path.write_bytes(main)
            ast = frontend.request({'op': 'parse', 'source': b64(main)})['ast']
            checks.append('U_' + tag + ' = ' + adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture'])
            for masked in (False, True):
                state = 'S_' + tag + ('_mask' if masked else '')
                initial = ('$php_startup_run(U_' + tag + ',2000,' + json.dumps(b64(os.fsencode(path)))
                    + ',{REPORTING ($ptascii("0")),INCLUDEPATH ($ptascii(".:"))})') if masked else (
                    '$php_run(U_' + tag + ',2000,' + json.dumps(b64(os.fsencode(path))) + ')')
                events = [] if masked else ['DIAGNOSTIC_SOURCE 1 "Warning" ($ptascii(' + json.dumps(MESSAGE) + ')) '
                    + str(line) for line in case['warning_lines']]
                checks += [state + ' = ' + initial, state + '.COMPLETION = SOURCE_PENDING',
                    state + '.EVALCONTEXTS = [pevalcontext_' + state + ']',
                    'pevalcontext_' + state + '.UNIT = 1', 'pevalcontext_' + state + '.BYTES = ' + term(code),
                    state + '.DESTRUCTION.FREE = n_free_' + state + ' :: n_free_tail_' + state + '*',
                    *public(state), '$eval_response_valid(' + state + ',' + value + ')',
                    state + '_resumed = $eval_resume(' + state + ',' + value + ')',
                    state + '_resumed.COMPLETION = NORMAL', state + '_resumed.EVALCONTEXTS = eps',
                    state + '_resumed.SOURCEPENDING = eps', state + '_resumed.FAILEDSOURCES = [pfailedsource_' + state + ']',
                    'pfailedsource_' + state + '.UNIT = 1', 'pfailedsource_' + state + '.KIND = FAILED_COMPILE',
                    'pfailedsource_' + state + '.BYTES = ' + term(code), 'pfailedsource_' + state + '.LINE = ' + str(case['line']),
                    'pfailedsource_' + state + '.FILE = $call_sourcefile(' + state + '.FILES,PORIGIN 1 eps)',
                    *[state + '_resumed.' + field + ' = ' + state + '.' + field for field in ('SOURCES', 'CODE', 'EVALBINDINGS', 'FILEBINDINGS', 'CLASSES', 'CLASSNAMES', 'FUNCTIONS', 'USERCONSTANTS')],
                    state + '_resumed.DECLARATIONS = ' + state + '.DECLARATIONS ++ [PDEXIT 1 PCSREJECT]',
                    state + '_resumed.EVENTS = ' + state + '.EVENTS ++ [' + ','.join(events) + ']',
                    state + '_resumed.DESTRUCTION.HANDLES = ' + state + '.DESTRUCTION.HANDLES ++ [n_free_' + state + ']',
                    state + '_resumed.DESTRUCTION.FREE = n_free_tail_' + state + '*',
                    state + '_resumed.DESTRUCTION.NEXT = ' + state + '.DESTRUCTION.NEXT', *public(state + '_resumed'),
                    state + '_zero = $eval_continue(' + state + '[.SERVICELEFT = (0)],' + value + ')',
                    state + '_zero = ' + state + '_resumed[.COMPLETION = BUDGET]', *public(state + '_zero'),
                    state + '_done = $drive_steps(' + state + '_zero[.COMPLETION = NORMAL],2000)',
                    state + '_done.COMPLETION = NORMAL', state + '_done.TODO = eps',
                    '$test_constant_outputs(' + state + '_done.EVENTS) = $ptascii("M|C|F|A|")', *public(state + '_done'),
                    '~$eval_response_valid(' + state + '_resumed,' + value + ')',
                    '$eval_resume(' + state + '_resumed,' + value + ') = ' + state + '_resumed[.COMPLETION = UNSUPPORTED "invalid eval parser response"]']
            checks += ['S_' + tag + '_mask_resumed.FAILEDSOURCES = S_' + tag + '_resumed.FAILEDSOURCES']
            for name, changed in [('unit', value.replace('SOURCE_REJECT_HEADERS 1 ', 'SOURCE_REJECT_HEADERS 2 ', 1)),
                                  ('bytes', value.replace(term(code), term(code + b' '), 1))]:
                checks += ['~$eval_response_valid(S_' + tag + ',' + changed + ')',
                    '$eval_resume(S_' + tag + ',' + changed + ') = S_' + tag + '[.COMPLETION = UNSUPPORTED "invalid eval parser response"]']
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text('var U : program\n' + OUTPUTS + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *modules, *(ROOT / name for name in ('spec/semantics/modules.json', 'spec/schema.json', 'spec/php.watsup',
        'adapter/main.ml', 'bin/php-semantics', 'native/php_file.c', 'frontend/worker.php', 'frontend/RejectedHeaderParser.php',
        'frontend/FileLexer.php', 'frontend/EvalLexer.php', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/profile.json', 'tests/semantics/encoding_declare_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/semantics/error_handler_run.py')),
        SOURCE / 'cases.json', SOURCE / 'attribute-before-abstract-constant-eval/unit.php']
    before = {str(path): sha(path) for path in paths}
    assert before[str(ROOT / '.tools/php/bin/php')] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'startup_reporting_masks': [30719, 0], 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
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
