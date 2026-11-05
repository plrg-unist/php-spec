#!/usr/bin/env python3
"""Independent raw eval tapes, scanner restoration and rejected service identity."""
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
EMBEDDED = b'{$a[(function(){\n declare(encoding=2);\n return 0;\n})()]}'
CASES = {
    'plain': (b'declare(encoding=1);\n$x="\\u{}";declare(encoding=2);', [1], 1),
    'large': (b'declare(encoding=1);\n$x="\\u{110000}";declare(encoding=2);', [1], 1),
    'inner': (b'declare(encoding=true,Foo=function(){\n declare(encoding=2);\n $x="\\u{}";\n});declare(encoding=3);', [2], 1),
    'double-embedded': (b'declare(encoding=1);\n$x="' + EMBEDDED + b'\\u{}";declare(encoding=3);', [1, 3], 2),
    'heredoc-embedded': (b'declare(encoding=1);\n$x=<<<TXT\n' + EMBEDDED + b'\\u{}\nTXT;declare(encoding=3);', [1, 4], 2),
    'backtick-embedded': (b'declare(encoding=1);\n$x=`' + EMBEDDED + b'\\u{}`;declare(encoding=3);', [1, 3], 2),
    'earlier-syntax': (b'echo ;declare(encoding=1);$x="\\u{}";', [], 0),
    'earlier-nonliteral': (b'declare(encoding=1,encoding=true);$x="\\u{}";', [1], 1),
    'single-control': (b'declare(encoding=1);$x=\'\\u{}\';declare(encoding=2);echo ;', [1, 1], 2),
    'nowdoc-control': (b'declare(encoding=1);$x=<<<\'TXT\'\n\\u{}\nTXT;declare(encoding=2);echo ;', [1, 3], 2),
}
PROBE = r'''<?php declare(strict_types=1);
require '@ROOT@/frontend/autoload.php';
require '@ROOT@/frontend/FileLexer.php';
require '@ROOT@/frontend/EvalLexer.php';
require '@ROOT@/frontend/RejectedHeaderParser.php';
function lineAt(string $source, int $position): int {
    return 1 + preg_match_all('/\r\n|\r|\n/', substr($source, 0, $position));
}
function parsed(string $source): array {
    try { return ['accepted', php_spec_parse_eval($source)]; }
    catch (Throwable $error) { return [get_class($error), $error->getMessage(), $error->getLine()]; }
}
function tokenFacts(array $tokens): array {
    return array_map(static fn($token): array => [$token->id,base64_encode($token->text),$token->line,$token->pos], $tokens);
}
$before = [parsed('return 1;'), parsed("\necho ;")];
$records = [];
$cases = json_decode(file_get_contents($argv[1]), true, flags: JSON_THROW_ON_ERROR);
foreach ($cases as $case) {
    $source = base64_decode($case['source'], true);
    assert(!str_contains($source, "\0"));
    $acceptedBefore = tokenFacts((new EvalLexer())->tokenize('return "A";'));
    $tokens = php_spec_lex_eval($source); $position = 0; $tape = '';
    foreach ($tokens as $token) {
        assert(array_is_list($token) && count($token) === 4);
        [$id,$text,$line,$offset] = $token;
        assert(is_int($id) && $id > 0 && is_string($text) && $text !== '');
        assert(is_int($line) && is_int($offset) && $offset === $position);
        assert($line === lineAt($source, $offset));
        assert(substr($source, $offset, strlen($text)) === $text);
        $tape .= $text; $position += strlen($text);
    }
    assert($tape === substr($source, 0, $position));
    if ($case['complete']) assert($tape === $source);
    else assert(strlen($tape) < strlen($source));
    $collector = new PhpParser\ErrorHandler\Collecting();
    $checked = (new RejectedEvalLexer())->tokenize($source, $collector);
    $end = $checked[count($checked)-1];
    assert($end->id === 0 && $end->pos === $position && $end->line === lineAt($source, $position));
    assert(count($checked) === count($tokens)+1);
    assert(tokenFacts((new EvalLexer())->tokenize('return "A";')) === $acceptedBefore);
    assert([parsed('return 1;'),parsed("\necho ;")] === $before);
    $records[] = ['id'=>$case['id'], 'tokens'=>count($tokens), 'prefix_bytes'=>$position,
        'source_bytes'=>strlen($source), 'eof_line'=>$end->line];
}
$source = 'declare(encoding=1);$x="\u{}";declare(encoding=2);';
$collector = new PhpParser\ErrorHandler\Collecting();
$old = (new EvalLexer())->tokenize($source, $collector);
assert($collector->getErrors() === []);
$fresh = (new RejectedEvalLexer())->tokenize($source, new PhpParser\ErrorHandler\Collecting());
assert(count(array_filter($old,static fn($token): bool=>$token->id===T_DECLARE)) === 2);
assert(count(array_filter($fresh,static fn($token): bool=>$token->id===T_DECLARE)) === 1);
$records[] = ['id'=>'accepted-tokenizer-preserved', 'old_tokens'=>count($old), 'rejected_tokens'=>count($fresh)];
echo json_encode($records, JSON_THROW_ON_ERROR), "\n";
'''
MULTIBYTE = r'''<?php declare(strict_types=1);
$records = [];
foreach (['php_spec_parse_eval','php_spec_lex_eval'] as $function) {
    foreach (['','return 1;'] as $source) {
        try { $function($source); throw new RuntimeException('profile was accepted'); }
        catch (ValueError $error) {
            assert($error->getMessage() === 'Eval parser requires the raw source profile');
            $records[] = ['function'=>$function,'empty'=>$source==='','class'=>get_class($error)];
        }
    }
}
echo json_encode($records, JSON_THROW_ON_ERROR), "\n";
'''


def run(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for mode in ('eval', 'file'):
            for name, (source, lines, count) in CASES.items():
                if mode == 'file': source, lines = b'<?php\n' + source, [line + 1 for line in lines]
                packet = {'op': 'parse-' + mode, 'id': '7', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(source)}
                if mode == 'file': packet.update(requested=b64(b'unit.php'), resolved=b64(b'/review/unit.php'), opened=b64(b'/review/unit.php'))
                result = frontend.parse(packet)
                assert not result['accepted'] and not result['diagnostics']
                assert all(result[key] == value for key, value in packet.items() if key != 'op')
                assert len(result.get('headers', [])) == count and CLI['rejected_encoding_warning_lines'](result) == lines
                if name not in ('inner', 'earlier-syntax', 'earlier-nonliteral'):
                    assert result['headers'][0]['beginTokenPos'] == (0 if mode == 'eval' else 1)
                    assert result['headers'][0]['closeTokenPos'] == (5 if mode == 'eval' else 6)
                if name == 'inner': assert result['headers'][0]['beginTokenPos'] > 0
                records.append({'id': name, 'mode': mode, 'warning_lines': lines, 'headers': count,
                    'source_sha256': hashlib.sha256(source).hexdigest()})
    finally:
        frontend.close()
    raw = [('empty', b''), ('crlf', b'$x=1;\r\nreturn 2;'), ('tags', b'?>HTML\n<?php return 1;'),
        ('hash', b'#! comment\nreturn 1;'), ('bom', b'\xef\xbb\xbf$x=1;'),
        ('halt', b'__halt_compiler();unscanned "\\u{}"'), ('single', b'$x=\'\\u{}\';'),
        ('nowdoc', b'$x=<<<\'TXT\'\n\\u{}\nTXT;'), ('maximum', b'$x="\\u{10FFFF}";'),
        ('surrogate', b'$x="\\u{D800}";')]
    payload = [{'id': name, 'source': b64(source), 'complete': True} for name, source in raw]
    payload += [{'id': name, 'source': b64(CASES[name][0]), 'complete': False}
                for name in ('plain', 'large', 'double-embedded', 'heredoc-embedded', 'backtick-embedded')]
    (out / 'tapes.json').write_text(json.dumps(payload) + '\n')
    processes = []
    for name, source, extra in [('tapes', PROBE.replace('@ROOT@', str(ROOT)), [str(out / 'tapes.json')]),
                               ('multibyte', MULTIBYTE, [])]:
        path = out / (name + '.php'); path.write_text(source)
        flags = ['-d', 'zend.multibyte=1'] if name == 'multibyte' else []
        process = recorded([str(types.PHP), '-n', *types.FLAGS, *flags, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(path), *extra], out / name, 15)
        assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
        assert not (out / (name + '.stderr')).read_bytes()
        records.extend(json.loads((out / (name + '.stdout')).read_text())); processes.append(process)
    return records, processes


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), *(ROOT / name for name in ('native/php_file.c', 'frontend/worker.php', 'frontend/RejectedHeaderParser.php',
        'frontend/EvalLexer.php', 'frontend/FileLexer.php', 'frontend/encoding-literal.php', 'spec/schema.json',
        'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so', 'tests/semantics/profile.json',
        'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    assert before['.tools/php/bin/php'] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE, 'multibyte_refusal_profile': {'zend.multibyte': '1'},
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'source_agreement_credit': 0, 'passed': False}
    try:
        report['records'], report['processes'] = run(out)
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['head_stable'] and report['inputs_stable']
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', len(report['records']))


if __name__ == '__main__': main()
