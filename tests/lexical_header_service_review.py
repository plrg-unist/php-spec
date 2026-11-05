#!/usr/bin/env python3
"""Independent lexical-prefix boundaries, EOF receipts and grammar cutoffs."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from encoding_declare_protocol import CLI, ParserWorker
from error_handler_run import recorded
import static_types as types

b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
CASES = {
    'immediate-bad': (b'declare(encoding=1)\x01', [1], 1),
    'multiple-faults': (b'declare(encoding=1);\n\x01\ndeclare(encoding=2);\n/* broken', [1], 1),
    'outer-nonliteral': (b'declare(encoding=true,Foo=function(){\ndeclare(encoding=2);\n/* broken', [2], 1),
    'nonliteral-cutoff': (b'declare(encoding=1,encoding=true);\n/* broken', [1], 1),
    'earlier-syntax': (b'echo ;declare(encoding=1);\x01', [], 0),
    'comment-control': (b'declare(encoding=1);/*\x01*/echo ;', [1], 1),
    'string-control': (b'declare(encoding=1);$x="\x01";echo ;', [1], 1),
    'crlf-comment': (b'declare(\r\nencoding=1\r\n);\r\n/* broken', [3], 1),
    'genuine-eof': (b'declare(encoding=1)', [1], 1),
}
PROBE = r'''<?php declare(strict_types=1);
require '@ROOT@/frontend/autoload.php';
require '@ROOT@/frontend/FileLexer.php';
require '@ROOT@/frontend/EvalLexer.php';
require '@ROOT@/frontend/RejectedHeaderParser.php';
final class ReviewReplayLexer extends PhpParser\Lexer {
    public function __construct(private array $tape, private array $errors) {}
    public function tokenize(string $code, ?PhpParser\ErrorHandler $handler = null): array {
        foreach ($this->errors as $error) $handler->handleError($error);
        return $this->tape;
    }
}
function replay(string $code, array $errors): array {
    $collector = new PhpParser\ErrorHandler\Collecting();
    $tokens = (new EvalLexer())->tokenize($code, $collector);
    $parser = new RejectedHeaderParser(new ReviewReplayLexer($tokens, $errors), PhpParser\PhpVersion::fromComponents(8, 5));
    $error = null;
    try { $parser->parse($code, new PhpParser\ErrorHandler\Collecting()); }
    catch (Throwable $exception) { $error = [get_class($exception), $exception->getMessage()]; }
    return [$parser, $error];
}
$records = [];
$code = 'declare(encoding=1);' . "\x01" . 'declare(encoding=2);' . "\x02";
$collector = new PhpParser\ErrorHandler\Collecting();
$tokens = (new EvalLexer())->tokenize($code, $collector);
$errors = $collector->getErrors();
assert(count($errors) === 2);
[$parser, $error] = replay($code, array_reverse($errors));
$boundary = $errors[0]->getAttributes()['startFilePos'];
$index = array_search($boundary, array_column($tokens, 'pos'), true);
$clipped = $parser->getTokens(); $last = $clipped[count($clipped)-1];
assert($parser->parsingStarted && count($parser->headers) === 1);
assert($parser->headers[0]['beginTokenPos'] === 0 && $parser->headers[0]['closeTokenPos'] === 5);
assert(count($clipped) === $index + 1 && $last->id === 0 && $last->pos === $boundary && $last->line === 1);
$records[] = ['id'=>'reversed-errors', 'boundary'=>$boundary, 'token'=>$index, 'headers'=>1];
foreach ([null, -1, '1', 1.5, 1, strlen($code)+3] as $position) {
    $attributes = $position === null ? [] : ['startFilePos'=>$position];
    [$parser, $error] = replay($code, [new PhpParser\Error('forged lexical fact', $attributes)]);
    assert($error !== null && $error[0] === RuntimeException::class);
    assert(!$parser->parsingStarted && $parser->headers === []);
    $records[] = ['id'=>'malformed-boundary', 'position'=>$position, 'error'=>$error];
}
[$parser, $error] = replay('echo ;declare(encoding=2);', []);
assert($error !== null && $error[0] === PhpParser\Error::class && $parser->headers === []);
$records[] = ['id'=>'grammar-before-later-header'];
$code = "\x01" . 'declare(encoding=2);';
$collector = new PhpParser\ErrorHandler\Collecting(); (new EvalLexer())->tokenize($code, $collector);
[$parser, $error] = replay($code, $collector->getErrors());
assert($parser->headers === [] && count($parser->getTokens()) === 1 && $parser->getTokens()[0]->pos === 0);
$records[] = ['id'=>'first-token-error'];
// Raw tokenization does not report these scanner/action errors. It must not
// fabricate a lexical boundary or certify a later completed header.
$code = 'declare(encoding=1);$x="\u{}";declare(encoding=2);';
$collector = new PhpParser\ErrorHandler\Collecting(); $tokens = (new EvalLexer())->tokenize($code, $collector);
assert($collector->getErrors() === [] && count($tokens) > 1);
$records[] = ['id'=>'raw-tokenizer-no-error-boundary', 'tokens'=>count($tokens)];
echo json_encode($records, JSON_THROW_ON_ERROR), "\n";
'''


def run(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for mode in ('eval', 'file'):
            for name, (code, lines, count) in CASES.items():
                if mode == 'file': code, lines = b'<?php\n' + code, [line + 1 for line in lines]
                request = {'op': 'parse-' + mode, 'id': '1', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(code)}
                if mode == 'file': request.update(requested=b64(b'lex.php'), resolved=b64(b'/review/lex.php'), opened=b64(b'/review/lex.php'))
                result = frontend.request(request)
                raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
                frontend.recorded_stderr.extend(raw)
                assert not result['accepted'] and not result['diagnostics'] and result['source'] == b64(code)
                assert len(result.get('headers', [])) == count
                assert CLI['rejected_encoding_warning_lines'](result) == lines
                assert [int(line.rsplit(b' ', 1)[1]) for line in raw.splitlines()] == lines
                assert CLI['dynamic_parser_stderr'](result, mode, raw)
                assert not CLI['dynamic_parser_stderr'](result, mode, raw + b'Unexpected\n')
                if name in ('immediate-bad', 'genuine-eof'):
                    header = result['headers'][0]
                    assert header['beginTokenPos'] == (0 if mode == 'eval' else 1)
                    assert header['closeTokenPos'] == (5 if mode == 'eval' else 6)
                if name == 'outer-nonliteral': assert result['headers'][0]['beginTokenPos'] > 0
                records.append({'id': name, 'mode': mode, 'warning_lines': lines,
                    'header_count': count, 'source_sha256': hashlib.sha256(code).hexdigest()})
            # This error is not reported by the raw lexer's Collecting handler.
            code = b'declare(encoding=1);$x="\\u{}";declare(encoding=2);'
            if mode == 'file': code = b'<?php\n' + code
            result = frontend.request({'op': 'parse-' + mode, **dict(request, source=b64(code))})
            raw = (frontend.output / 'stderr').read_bytes()[len(frontend.recorded_stderr):]
            frontend.recorded_stderr.extend(raw)
            assert not result['accepted'] and raw and not CLI['dynamic_parser_stderr'](result, mode, raw)
            records.append({'id': 'raw-tokenizer-mismatch', 'mode': mode, 'expected': 'explicit CLI refusal'})
    finally:
        frontend.close()
    probe = out / 'boundary.php'; probe.write_text(PROBE.replace('@ROOT@', str(ROOT)))
    process = recorded([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(probe)], out / 'boundary', 15)
    assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
    assert not (out / 'boundary.stderr').read_bytes()
    records.extend(json.loads((out / 'boundary.stdout').read_text()))
    return records, process


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), *(ROOT / name for name in ('frontend/worker.php', 'frontend/RejectedHeaderParser.php',
        'frontend/EvalLexer.php', 'frontend/FileLexer.php', 'frontend/encoding-literal.php', 'spec/schema.json',
        'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so', 'tests/semantics/profile.json',
        'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    assert before['.tools/php/bin/php'] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'source_agreement_credit': 0, 'passed': False}
    try:
        report['records'], report['boundary_process'] = run(out)
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['head_stable'] and report['inputs_stable']
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', len(report['records']))


if __name__ == '__main__': main()
