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
        parse_code = b'declare(\n encoding=1\n);\necho ;'
        variants = [('eval', 'eval', parse_code), ('file', 'file', parse_code),
            ('legacy_compile_eval', 'eval', b'declare(encoding=true);'),
            ('legacy_compile_file', 'file', b'declare(encoding=true);')]
        for tag, mode, code in variants:
            unit = code if mode == 'eval' else b'<?php\n' + code
            child = out / (tag + '-unit.php')
            if mode == 'file': child.write_bytes(unit)
            operation = b'eval(' + literal(code) + b')' if mode == 'eval' else b'include ' + literal(os.fsencode(child.name))
            main = b'<?php $trash=new stdClass;unset($trash);echo "M|";try{' + operation + b';}catch(Throwable $e){echo "C|";}finally{echo "F|";}echo "A|";'
            path = out / (tag + '.php'); path.write_bytes(main)
            ast = frontend.request({'op': 'parse', 'source': b64(main)})['ast']
            checks.append('U_' + tag + ' = ' + adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture'])
            request = {'op': 'parse-' + mode, 'id': '1', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(unit)}
            if mode == 'file': request.update(requested=b64(os.fsencode(child.name)), resolved=b64(os.fsencode(child)), opened=b64(os.fsencode(child)))
            parsed = frontend.request(request)
            raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
            frontend.recorded_stderr.extend(raw)
            assert not parsed['accepted'] and CLI['dynamic_parser_stderr'](parsed, mode, raw)
            legacy = tag.startswith('legacy_'); kind = 'FAILED_COMPILE' if legacy else 'FAILED_PARSE'
            warning_line = None if legacy else (3 if mode == 'eval' else 4)
            assert parsed['category'] == ('parser_static_rejection' if legacy else 'parser_rejection')
            if not legacy:
                assert parsed['line'] == warning_line + 1 and parsed['headers'][0]['closeLine'] == warning_line
                responses[mode] = parsed
            value = response(parsed, tag)
            if legacy:
                checks.append('$eval_response_shape(' + value + ')')
                value = '(SOURCE_COMPILE_REJECT 1 ' + term(unit) + ' ' + term(base64.b64decode(parsed['message'])) + ' ' + str(parsed['line']) + ')'
            state = 'S_' + tag
            context = ('pevalcontext_' if mode == 'eval' else 'pfilecontext_') + tag
            startup = '{REPORTING ($ptascii("0")),INCLUDEPATH ($ptascii(".:"))}'
            if mode == 'eval':
                checks += [state + ' = $php_run(U_' + tag + ',1500,' + json.dumps(b64(os.fsencode(path))) + ')',
                    state + '.EVALCONTEXTS = [' + context + ']', context + '.UNIT = 1']
                resume, valid, continuation = '$eval_resume', '$eval_response_valid', '$eval_continue'
                masked_setup = [state + '_mask = $php_startup_run(U_' + tag + ',1500,'
                    + json.dumps(b64(os.fsencode(path))) + ',' + startup + ')']
            else:
                checks += [state + '_open = $php_file_run(U_' + tag + ',1500,' + term(os.fsencode(path)) + ',' + term(os.fsencode(out)) + ')',
                    state + '_open.COMPLETION = SOURCE_PENDING', state + '_open.FILECONTEXTS = [' + context + '_open]',
                    state + ' = $file_open_resume(' + state + '_open,FILE_OPENED ' + context + '_open.NONCE ' + context + '_open.CALLER ' + context + '_open.REQUESTED '
                    + term(os.fsencode(child)) + ' ' + term(os.fsencode(child)) + ' ' + term(unit) + ')',
                    state + '.FILECONTEXTS = [' + context + ']', context + '.UNIT = (1)']
                resume, valid, continuation = '$file_parse_resume', '$file_parse_response_valid', '$file_parse_continue'
                masked_setup = [state + '_mask_open = $php_file_startup_run(U_' + tag + ',1500,'
                    + term(os.fsencode(path)) + ',' + term(os.fsencode(out)) + ',' + startup + ')',
                    state + '_mask_open.COMPLETION = SOURCE_PENDING', state + '_mask_open.FILECONTEXTS = [' + context + '_mask_open]',
                    state + '_mask = $file_open_resume(' + state + '_mask_open,FILE_OPENED '
                    + context + '_mask_open.NONCE ' + context + '_mask_open.CALLER ' + context + '_mask_open.REQUESTED '
                    + term(os.fsencode(child)) + ' ' + term(os.fsencode(child)) + ' ' + term(unit) + ')']
            checks += [state + '.COMPLETION = SOURCE_PENDING', *public(state), valid + '(' + state + ',' + value + ')',
                state + '.DESTRUCTION.FREE = n_free_' + tag + ' :: n_free_tail_' + tag + '*',
                state + '_resumed = ' + resume + '(' + state + ',' + value + ')',
                state + '_resumed.COMPLETION = NORMAL', state + '_resumed.COMPILESTOP = false',
                state + '_resumed.SOURCES = ' + state + '.SOURCES', state + '_resumed.CODE = ' + state + '.CODE',
                state + '_resumed.EVALBINDINGS = ' + state + '.EVALBINDINGS', state + '_resumed.FILEBINDINGS = ' + state + '.FILEBINDINGS',
                state + '_resumed.EVALCONTEXTS = eps', state + '_resumed.FILECONTEXTS = eps',
                state + '_resumed.SERVICELEFT = eps', state + '_resumed.FAILEDSOURCES = [pfailedsource_' + tag + ']',
                'pfailedsource_' + tag + '.UNIT = 1', 'pfailedsource_' + tag + '.ISFILE = ' + str(mode == 'file').lower(),
                'pfailedsource_' + tag + '.BYTES = ' + term(unit), 'pfailedsource_' + tag + '.KIND = ' + kind,
                'pfailedsource_' + tag + '.LINE = ' + str(parsed['line']),
                'pfailedsource_' + tag + '.FILE = $call_sourcefile(' + state + '.FILES,PORIGIN 1 eps)',
                state + '_resumed.EVENTS = ' + state + '.EVENTS' + ('' if legacy else ' ++ [DIAGNOSTIC_SOURCE 1 "Warning" ($ptascii(' + json.dumps(MESSAGE) + ')) ' + str(warning_line) + ']'),
                '|' + state + '_resumed.DESTRUCTION.HANDLES| = |' + state + '_resumed.OBJECTS|',
                state + '_resumed.DESTRUCTION.HANDLES = ' + state + '.DESTRUCTION.HANDLES ++ [n_free_' + tag + ']',
                state + '_resumed.DESTRUCTION.FREE = n_free_tail_' + tag + '*',
                state + '_resumed.DESTRUCTION.NEXT = ' + state + '.DESTRUCTION.NEXT',
                *public(state + '_resumed'), '~' + valid + '(' + state + '_resumed,' + value + ')',
                state + '_replay = ' + resume + '(' + state + '_resumed,' + value + ')',
                state + '_replay = ' + state + '_resumed[.COMPLETION = UNSUPPORTED "invalid ' + ('eval' if mode == 'eval' else 'file') + ' parser response"]',
                *masked_setup, state + '_mask.COMPLETION = SOURCE_PENDING', *public(state + '_mask'),
                valid + '(' + state + '_mask,' + value + ')',
                state + '_masked = ' + resume + '(' + state + '_mask,' + value + ')',
                state + '_masked.COMPLETION = NORMAL',
                state + '_masked.EVENTS = ' + state + '.EVENTS', state + '_masked.FAILEDSOURCES = ' + state + '_resumed.FAILEDSOURCES',
                state + '_zero = ' + continuation + '(' + state + '[.SERVICELEFT = (0)],' + value + ')',
                state + '_zero.COMPLETION = BUDGET', state + '_zero.EVENTS = ' + state + '_resumed.EVENTS',
                state + '_zero.DESTRUCTION = ' + state + '_resumed.DESTRUCTION',
                state + '_zero.FAILEDSOURCES = ' + state + '_resumed.FAILEDSOURCES', *public(state + '_zero'),
                state + '_done = $drive_steps(' + state + '_zero[.COMPLETION = NORMAL],1500)',
                state + '_done.COMPLETION = NORMAL', state + '_done.TODO = eps',
                state + '_done.DESTRUCTION.HANDLES = ' + state + '_resumed.DESTRUCTION.HANDLES',
                '$test_outputs(' + state + '_done.EVENTS) = $ptascii("M|C|F|A|")', *public(state + '_done')]
            if not legacy:
                old = '(SOURCE_PARSE_REJECT 1 ' + term(unit) + ' ' + term(base64.b64decode(parsed['message'])) + ' ' + str(parsed['line']) + ')'
                checks += [state + '_legacy = ' + resume + '(' + state + ',' + old + ')',
                    state + '_legacy = ' + state + '_resumed[.EVENTS = ' + state + '.EVENTS]', *public(state + '_legacy'),
                    state + '_legacy_zero = ' + continuation + '(' + state + '[.SERVICELEFT = (0)],' + old + ')',
                    state + '_legacy_zero = ' + state + '_legacy[.COMPLETION = BUDGET]', *public(state + '_legacy_zero')]

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
        compile_result = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval', 'profile': 'cli-raw-85', 'source': b64(compile_code)})
        raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
        frontend.recorded_stderr.extend(raw)
        assert CLI['dynamic_parser_stderr'](compile_result, 'eval', raw)
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
        'startup_reporting_masks': [30719, 0], 'startup_include_path': '.:',
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
