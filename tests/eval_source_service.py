#!/usr/bin/env python3
"""Checked eval parser service and its pending-response protocol boundary."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'frontend'))
import wire


class Worker:
    def __init__(self, command):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def call(self, request):
        self.process.stdin.write(wire.dumps(request) + '\n')
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        assert line, self.process.stderr.read()
        return wire.loads(line)

    def close(self):
        self.process.stdin.close()
        assert self.process.wait(timeout=5) == 0, self.process.stderr.read()


def encoded(source):
    return base64.b64encode(source).decode()


def pending(identifier, source):
    return {'id': identifier, 'mode': 'eval', 'profile': 'cli-raw-85', 'source': encoded(source)}


def parser_response(result):
    assert result['ok'] and not result['diagnostics']
    keys = ('id', 'mode', 'profile', 'source', 'accepted')
    if result['accepted']:
        keys += ('ast',)
    else:
        keys += ('category', 'message', 'line')
    return {key: result[key] for key in keys}


def meta(node, name):
    return int(node['meta'][name]['int'])


def main():
    php = str(ROOT / '.tools/php/bin/php')
    frontend = Worker([php, '-n', '-d', 'precision=14', '-d', 'extension=' +
                       str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    cases = [b'echo 1;', b'?>T<?php echo 2;', b'', b'<?php echo 1;',
             b'/** doc */ echo 1;', b'echo 1; //tail', b'echo 1;\necho 2;',
             b'/*\xff*/ echo 1;', b'\xef\xbb\xbfecho 1;', b'\x00echo 1;',
             b'function x( {']
    try:
        results = []
        for number, source in enumerate(cases):
            identity = pending(str(number), source)
            parsed = frontend.call({'op': 'parse-eval', **identity})
            response = parser_response(parsed)
            checked = adapter.call({'op': 'check_source_service', 'pending': identity,
                                    'response': response})
            assert checked['ok'] and checked['accepted'] == parsed['accepted']
            if parsed['accepted']:
                assert checked['ast'] == parsed['ast']
            else:
                assert checked['category'] == 'parser_rejection' and checked['line'] >= 1
            results.append(parsed)

        first = results[0]['ast']['program'][0]
        assert first['node'] == 'Stmt_Echo' and meta(first, 'startFilePos') == 0
        assert meta(first, 'startTokenPos') == 0
        assert [node['node'] for node in results[1]['ast']['program']] == ['Stmt_InlineHTML', 'Stmt_Echo']
        assert meta(results[1]['ast']['program'][0], 'startFilePos') == 2
        assert results[2]['ast']['program'] == []
        assert not results[3]['accepted']
        doc = results[4]['ast']['program'][0]
        assert meta(doc, 'startFilePos') == 11 and meta(doc, 'startTokenPos') == 2
        assert doc['meta']['comments'][0]['comment'][3:5] == ['0', '0']
        trailing = results[5]['ast']['program'][1]
        assert trailing['node'] == 'Stmt_Nop' and meta(trailing, 'startTokenPos') == 6
        assert trailing['meta']['comments'][0]['comment'][3:5] == ['8', '5']
        assert meta(results[6]['ast']['program'][1], 'startLine') == 2
        assert results[7]['accepted'] and all(not result['accepted'] for result in results[8:])

        # Zend's after-open-tag parser supplies rejection evidence. Its message
        # and line are kept distinct from PHP-Parser diagnostics and execution.
        for number, (source, line) in enumerate(((b'echo ;', 1), (b'echo 1;\necho ;', 2)), 11):
            identity = pending(str(number), source)
            parsed = frontend.call({'op': 'parse-eval', **identity})
            assert parsed['ok'] and parsed['accepted'] is False
            assert parsed['category'] == 'parser_rejection' and parsed['line'] == line
            assert base64.b64decode(parsed['message']) == b'syntax error, unexpected token ";"'
            checked = adapter.call({'op': 'check_source_service', 'pending': identity,
                                    'response': parser_response(parsed)})
            assert checked['ok'] and checked['accepted'] is False

        static_sources = ((b'class A { final abstract private function f(); }', 1),
                          (b'class A {\nfinal abstract private function f(); }', 2))
        for number, (source, line) in enumerate(static_sources, 13):
            identity = pending(str(number), source)
            static = frontend.call({'op': 'parse-eval', **identity})
            assert static['ok'] and static['accepted'] is False
            assert static['category'] == 'parser_static_rejection' and static['line'] == line
            assert base64.b64decode(static['message']) == b'Cannot use the final modifier on an abstract method'
            checked = adapter.call({'op': 'check_source_service', 'pending': identity,
                                    'response': parser_response(static)})
            assert checked['ok'] and checked['accepted'] is False
            assert checked['category'] == static['category'] and checked['line'] == line
            assert checked['message'] == static['message'] and checked['source'] == identity['source']
        namespace_sources = (
            (b'echo 1; namespace N;', ['Stmt_Echo', 'Stmt_Namespace']),
            (b'namespace N; namespace M {}', ['Stmt_Namespace', 'Stmt_Namespace']),
            (b'namespace N {} echo 1;', ['Stmt_Namespace', 'Stmt_Echo']),
            (b'namespace N { namespace M {} }', ['Stmt_Namespace']),
            (b'namespace N { namespace M { namespace O {} } }', ['Stmt_Namespace']),
        )
        for number, (source, nodes) in enumerate(namespace_sources, 16):
            identity = pending(str(number), source)
            parsed = frontend.call({'op': 'parse-eval', **identity})
            assert parsed['ok'] and parsed['accepted'] is True
            assert [node['node'] for node in parsed['ast']['program']] == nodes
            checked = adapter.call({'op': 'check_source_service', 'pending': identity,
                                    'response': parser_response(parsed)})
            assert checked['ok'] and checked['accepted'] is True
            assert checked['ast'] == parsed['ast']
        recovered = frontend.call({'op': 'parse-eval', **pending('15', b'echo 4;')})
        assert recovered['ok'] and recovered['accepted'] is True

        native_only = subprocess.run([php, '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                                      '-r', 'if (!php_spec_parse_eval("function php_spec_probe() {} class PhpSpecProbe {}")) exit(1); '
                                            'if (function_exists("php_spec_probe") || class_exists("PhpSpecProbe", false)) exit(2); '
                                            'echo "parse-only";'], capture_output=True)
        assert native_only.returncode == 0 and native_only.stdout == b'parse-only', native_only.stderr

        file_source = encoded(b'<?php echo 3;')
        after_eval = frontend.call({'op': 'parse', 'source': file_source})
        fresh = Worker([php, '-n', '-d', 'precision=14', '-d', 'extension=' +
                        str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')])
        try:
            assert after_eval == fresh.call({'op': 'parse', 'source': file_source})
        finally:
            fresh.close()

        good = parser_response(results[0])
        for field, value in [('id', '99'), ('mode', 'file'), ('profile', 'other'),
                             ('source', encoded(b'echo 2;'))]:
            bad = copy.deepcopy(good)
            bad[field] = value
            assert not adapter.call({'op': 'check_source_service', 'pending': pending('0', cases[0]),
                                     'response': bad})['ok']
        for mutation in (lambda x: x.update(extra=True), lambda x: x.pop('ast'),
                         lambda x: x['ast']['program'][0].update(node='NotAConstructor')):
            bad = copy.deepcopy(good)
            mutation(bad)
            assert not adapter.call({'op': 'check_source_service', 'pending': pending('0', cases[0]),
                                     'response': bad})['ok']
        bad = parser_response(results[3])
        bad['accepted'] = True
        assert not adapter.call({'op': 'check_source_service', 'pending': pending('3', cases[3]),
                                 'response': bad})['ok']

        static_response = parser_response(static)
        for field, value in [('category', 'compile_error'), ('line', 0),
                             ('source', encoded(b'echo 1;')), ('message', '!!!'), ('extra', True)]:
            bad = copy.deepcopy(static_response)
            bad[field] = value
            assert not adapter.call({'op': 'check_source_service', 'pending': pending('14', static_sources[1][0]),
                                     'response': bad})['ok']

        for field, value in [('id', '00'), ('source', 'ZWNobyAxOw=')]:
            bad_pending = pending('0', cases[0])
            bad_pending[field] = value
            assert not adapter.call({'op': 'check_source_service', 'pending': bad_pending,
                                     'response': good})['ok']
        bad_pending = pending('0', cases[0])
        bad_pending['extra'] = True
        assert not adapter.call({'op': 'check_source_service', 'pending': bad_pending,
                                 'response': good})['ok']

        for setting in ('zend.multibyte=1', 'precision=15', 'short_open_tag=0'):
            unsupported = Worker([php, '-n', '-d', setting, '-d',
                                  'extension=' + str(ROOT / '.tools/php-file.so'),
                                  str(ROOT / 'frontend/worker.php')])
            try:
                result = unsupported.call({'op': 'parse-eval', **pending('10', b'echo 1;')})
                assert result['ok'] is False and result['category'] == 'helper_unsupported'
            finally:
                unsupported.close()
        print(json.dumps({'result': 'pass', 'eval_cases': len(cases), 'namespace_recoveries': len(namespace_sources),
                          'native_rejections': 2,
                          'native_static_rejections': 2, 'protocol_negatives': 16,
                          'native_declarations': 'not installed',
                          'file_parse_after_eval': 'unchanged', 'unsupported_profile': 'distinct'}))
    finally:
        frontend.close()
        adapter.close()


if __name__ == '__main__':
    main()
