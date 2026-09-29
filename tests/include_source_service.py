#!/usr/bin/env python3
"""File-mode source service admits only checked, identified parse facts."""
import base64
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'frontend'))
import wire


def encoded(value):
    return base64.b64encode(value).decode()


def request(identifier, source):
    return {'op': 'parse-file', 'id': identifier, 'mode': 'file',
            'profile': 'cli-raw-85', 'requested': encoded(b'fixture.php'),
            'resolved': encoded(b'/snapshot/fixture.php'),
            'opened': encoded(b'/snapshot/canonical.php'),
            'source': encoded(source)}


class Worker:
    def __init__(self, setting=None):
        command = [str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                   setting or 'precision=14', '-d',
                   'extension=' + str(ROOT / '.tools/php-file.so'),
                   str(ROOT / 'frontend/worker.php')]
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True)

    def call(self, packet):
        self.process.stdin.write(wire.dumps(packet) + '\n')
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        assert line, self.process.stderr.read()
        return wire.loads(line)

    def close(self):
        self.process.stdin.close()
        assert self.process.wait(timeout=5) == 0, self.process.stderr.read()


def main():
    worker = Worker()
    try:
        accepted = (
            b'<?php /*\xff*/ echo 1;',
            b'plain text<?php echo 2; ?>tail',
            b'<?php function file_only_declaration() {}',
        )
        for number, source in enumerate(accepted):
            packet = request(str(number), source)
            response = worker.call(packet)
            assert response['ok'] and response['accepted'] and not response['diagnostics'], response
            for key in ('id', 'mode', 'profile', 'requested', 'resolved', 'opened', 'source'):
                assert response[key] == packet[key]
            assert response['ast']['version'] == 1
            assert 'token_comments' not in response
        assert worker.call({'op': 'parse-file', **request('3', b'<?php echo file_only_declaration();')})['accepted']

        for identifier, source, category, line, message in (
            ('4', b'<?php\necho ;', 'parser_rejection', 2, b'syntax error, unexpected token ";"'),
            ('5', b'<?php\nclass A { final abstract private function f(); }',
             'parser_static_rejection', 2, b'Cannot use the final modifier on an abstract method'),
        ):
            packet = request(identifier, source)
            response = worker.call(packet)
            assert response['ok'] and response['accepted'] is False and not response['diagnostics'], response
            assert response['category'] == category and response['line'] == line
            assert base64.b64decode(response['message']) == message
            for key in ('id', 'mode', 'profile', 'requested', 'resolved', 'opened', 'source'):
                assert response[key] == packet[key]

        for field, value in (('id', '00'), ('mode', 'eval'), ('profile', 'other'),
                             ('requested', '!!!'), ('resolved', ''), ('opened', ''),
                             ('source', '!!!')):
            packet = request('6', b'<?php echo 3;')
            packet[field] = value
            assert worker.call(packet)['ok'] is False
        packet = request('6', b'<?php echo 3;')
        packet['extra'] = True
        assert worker.call(packet)['ok'] is False
        assert worker.call(request('7', b'<?php echo 3;'))['accepted']
        # Zend accepts these structural ASTs and defers the fatal diagnostic
        # to compilation. The checked file-mode retry admits only their nodes.
        namespace_shapes = (
            (b'<?php echo 1; namespace N;', ['Stmt_Echo', 'Stmt_Namespace']),
            (b'<?php namespace N; namespace M {}', ['Stmt_Namespace', 'Stmt_Namespace']),
            (b'<?php namespace N {} echo 1;', ['Stmt_Namespace', 'Stmt_Echo']),
            (b'<?php namespace N { namespace M {} }', ['Stmt_Namespace']),
        )
        for number, (source, expected_nodes) in enumerate(namespace_shapes, 8):
            response = worker.call(request(str(number), source))
            assert response['ok'] and response['accepted'], response
            assert [node['node'] for node in response['ast']['program']] == expected_nodes
    finally:
        worker.close()

    for setting in ('zend.multibyte=1', 'precision=15', 'short_open_tag=0'):
        unsupported = Worker(setting)
        try:
            response = unsupported.call(request('12', b'<?php echo 1;'))
            assert response['ok'] is False and response['category'] == 'helper_unsupported'
        finally:
            unsupported.close()
    print(json.dumps({'result': 'pass', 'accepted': len(accepted) + 1 + len(namespace_shapes),
                      'native_rejections': 2, 'request_negatives': 8,
                      'unsupported_profiles': 3, 'namespace_recoveries': len(namespace_shapes),
                      'native_execution': 'none'}))


if __name__ == '__main__':
    main()
