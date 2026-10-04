#!/usr/bin/env python3
"""Ordinary Throwable constructors suspend parsing without partial field writes."""
import argparse
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'ordinary-weak-null-new': b"<?php\nfunction h($level, $message, $file, $line) { echo 'H', func_num_args(), '|'; return true; }\nset_error_handler('h');\n$e = new Exception(null, null);\necho '[', $e->getMessage(), ']/', $e->getCode();\n",
    'ordinary-strict-null-inherited-method': b"<?php\ndeclare(strict_types=1);\nclass E extends Exception {}\nfunction h($level, $message, $file, $line) { echo 'H|'; return true; }\n$e = new E('old', 4);\nset_error_handler('h');\ntry { $e->__construct(null, 1); } catch (TypeError $x) { echo 'E1|', $x->getMessage(), '|'; }\ntry { $e->__construct('new', null); } catch (TypeError $x) { echo 'E2|', $x->getMessage(), '|'; }\necho $e->getMessage(), '/', $e->getCode();\n",
    'ordinary-stringable-lossy-new': b"<?php\nclass M { public function __toString() { echo 'T|'; return 'm'; } }\nfunction h($level, $message, $file, $line) { echo 'H', func_num_args(), '|'; return true; }\nset_error_handler('h');\n$e = new Exception(new M, 7.9);\necho $e->getMessage(), '/', $e->getCode();\n",
    'ordinary-warning-throw-method-atomic': b"<?php\nclass E extends Exception {}\nfunction h($level, $message, $file, $line) { echo 'H|'; throw new Exception('stop'); }\n$p = new Exception('previous');\n$e = new E('old', 4, $p);\nset_error_handler('h');\ntry { $e->__construct('new', 7.9); } catch (Exception $x) { echo 'E|', $x->getMessage(), '|'; }\necho $e->getMessage(), '/', $e->getCode(), '/', ($e->getPrevious() === $p ? 'same' : 'bad');\n",
    'ordinary-stringable-throw-method-atomic': b"<?php\nclass E extends Exception {}\nclass M { public function __toString() { echo 'T|'; throw new Exception('stop'); } }\n$e = new E('old', 4);\ntry { $e->__construct(new M, 7); } catch (Exception $x) { echo 'E|', $x->getMessage(), '|'; }\necho $e->getMessage(), '/', $e->getCode();\n",
    'ordinary-named-error-before-receive': b"<?php\nclass M { public function __toString() { echo 'T|'; return 'm'; } }\nfunction v($tag, $value) { echo $tag; return $value; }\nfunction h($level, $message, $file, $line) { echo 'H|'; return true; }\nset_error_handler('h');\ntry {\n    new Exception(message: v('M|', new M), missing: v('U|', 1), code: v('C|', 7.9));\n} catch (Error $x) { echo 'E|', $x->getMessage(); }\n",
    'ordinary-errorexception-formal-order': b"<?php\nclass M { public function __toString() { echo 'M|'; return 'm'; } }\nclass F { public function __toString() { echo 'F|'; return 'virtual.php'; } }\nfunction h($level, $message, $file, $line) { echo 'H', func_num_args(), '|'; return true; }\nset_error_handler('h');\n$e = new ErrorException(new M, 1.9, 2.9, new F, '4.9');\necho $e->getMessage(), '/', $e->getCode(), '/', $e->getSeverity(), '/', $e->getFile(), '/', $e->getLine();\n",
    'ordinary-string-rewrite-later-error-trace': b"<?php\nfunction h($level, $message, $file, $line) { echo 'H|'; return true; }\nfunction take() { new ErrorException(7, 1.9, 2, 'virtual.php', 'bad'); }\nset_error_handler('h');\ntry { take(); } catch (TypeError $x) {\n    $t = $x->getTrace();\n    $a = $t[0]['args'];\n    $n = 0; foreach ($a as $value) { $n = $n + 1; }\n    echo ($a[0] === '7' ? 'S' : 'bad'), '|', ($a[1] === 1.9 ? 'F' : 'bad'), '|';\n    echo $t[0]['function'], '|', $t[0]['class'], '|', $n, '|', $a[4];\n}\n",
    'ordinary-handler-throw-trace': b"<?php\nfunction h($level, $message, $file, $line) { throw new Exception('stop'); }\nfunction take() { new Exception(null, 7); }\nset_error_handler('h');\ntry { take(); } catch (Exception $x) {\n    $t = $x->getTrace();\n    $n = 0; foreach ($t[0]['args'] as $value) { $n = $n + 1; }\n    echo $t[0]['function'], '|', $n, '|', (isset($t[0]['file']) ? 'file' : 'none'), '|';\n    echo $t[1]['function'], '|', $t[1]['class'], '|', ($t[1]['args'][0] === null ? 'null' : 'bad'), '|', $t[1]['args'][1], '|', $t[2]['function'];\n}\n",
    'ordinary-stringable-throw-trace': b"<?php\nclass M { public function __toString() { throw new Exception('stop'); } }\nfunction take() { new Exception(new M, 7); }\ntry { take(); } catch (Exception $x) {\n    $t = $x->getTrace();\n    echo $t[0]['function'], '|', $t[0]['class'], '|', (isset($t[0]['file']) ? 'file' : 'none'), '|';\n    echo $t[1]['function'], '|', $t[1]['class'], '|', ($t[1]['args'][0] instanceof M ? 'M' : 'bad'), '|', $t[1]['args'][1], '|', $t[2]['function'];\n}\n",
    'ordinary-scoped-parent-private-handler': b"<?php\nclass E extends Exception {\n    private function h($level, $message, $file, $line) { echo get_called_class(), '/', ($this instanceof E ? 'R' : 'bad'), '|'; return true; }\n    public function run() {\n        set_error_handler([$this, 'h']);\n        parent::__construct(null, 4.9);\n        echo '[', $this->getMessage(), ']/', $this->getCode();\n    }\n}\n$e = new E('old', 3);\n$e->run();\n",
    'ordinary-handler-reentrant-default': b"<?php\nclass M { public function __toString() { echo 'T|'; return 'inner'; } }\nfunction f($e = new Exception(new M)) { echo 'F/', $e->getMessage(), '|'; }\nfunction h($level, $message, $file, $line) { echo 'H|'; f(); return true; }\nset_error_handler('h');\n$e = new Exception(null, 7.9);\necho '[', $e->getMessage(), ']/', $e->getCode();\n",
    'ordinary-owned-method-retirement': b"<?php\nclass M { public function __toString() { echo 'T|'; return 'new'; } }\nclass E extends Exception {\n    private function h($level, $message, $file, $line) {\n        echo 'H|';\n        unset($GLOBALS['receiver'], $GLOBALS['previous']);\n        return true;\n    }\n    public function run() {\n        set_error_handler([$this, 'h']);\n        $this->__construct(new M, 4.9, $GLOBALS['previous']);\n        echo $this->getMessage(), '/', $this->getCode(), '/', $this->getPrevious()->getMessage(), '|';\n    }\n}\n$previous = new Exception('p');\n$receiver = new E('old', 3);\n$receiver->run();\nrestore_error_handler();\necho (isset($receiver) ? 'live' : 'gone'), '/', (isset($previous) ? 'live' : 'gone');\n",
    'ordinary-strict-stringable-rejected': b"<?php\ndeclare(strict_types=1);\nclass M { public function __toString() { echo 'T|'; return 'm'; } }\nfunction h($level, $message, $file, $line) { echo 'H|'; return true; }\nset_error_handler('h');\ntry { new Exception(new M, 7.9); } catch (TypeError $x) { echo 'E|', $x->getMessage(); }\n",
    'ordinary-method-named-holes-trace': b"<?php\nclass E extends Exception {}\nfunction h($level, $message, $file, $line) { echo 'H', func_num_args(), '|'; return true; }\n$p = new Exception('p');\n$e = new E('old', 7, $p);\nset_error_handler('h');\n$e->__construct(code: null);\necho '[', $e->getMessage(), ']/', $e->getCode(), '/', ($e->getPrevious() === $p ? 'same' : 'bad'), '|';\ntry { $e->__construct(previous: 'bad'); } catch (TypeError $x) {\n    $t = $x->getTrace();\n    $a = $t[0]['args'];\n    $n = 0; foreach ($a as $value) { $n = $n + 1; }\n    echo $t[0]['function'], '/', $t[0]['class'], '/', $n, '/';\n    echo ($a[0] === '' ? 'empty' : 'bad'), '/', $a[1], '/', $a[2], '|';\n}\necho '[', $e->getMessage(), ']/', $e->getCode(), '/', ($e->getPrevious() === $p ? 'same' : 'bad');\n",
    'ordinary-inherited-builtin-stringable': b"<?php\nclass E extends Exception {}\nfunction h($level, $message, $file, $line) { echo 'H', func_num_args(), '|'; unset($GLOBALS['value']); return true; }\nset_error_handler('h');\n$value = new E('seed');\n$expected = (string) $value;\n$e = new Exception($value, 7.9);\necho ($e->getMessage() === $expected ? 'same' : 'bad'), '/', $e->getCode(), '/', (isset($value) ? 'live' : 'gone');\n",
    'ordinary-recursive-same-stringable-site': b"<?php\n$depth = 0;\nclass M {\n    public function __toString() {\n        global $depth;\n        if ($depth === 0) { $depth = 1; f($this); }\n        echo 'T|';\n        return 'm';\n    }\n}\nfunction h($level, $message, $file, $line) { echo 'H|'; return true; }\nfunction f($message) { $e = new Exception($message, 7.9); echo 'F/', $e->getMessage(), '|'; }\nset_error_handler('h');\n$message = new M;\nf($message);\n",
    'ordinary-template-reentrant-echo-composition': b"<?php\n$depth = 0;\nclass M {\n    public function __toString() {\n        global $depth;\n        if ($depth === 0) {\n            $depth = 1;\n            show($this);\n        }\n        echo 'T|';\n        return 'm';\n    }\n}\nclass E extends Exception {\n    public array $values = [E_STRICT];\n    public function __toString() {\n        echo 'E', $this->values[0], '|';\n        return $this->getMessage();\n    }\n}\nfunction h($severity, $message, $file, $line) {\n    if ($message === 'Constant E_STRICT is deprecated') {\n        echo 'D', func_num_args(), '|';\n    } else {\n        echo 'H', func_num_args(), '|';\n    }\n    return true;\n}\nfunction show($message) {\n    echo new E($message, 7.9), '|';\n}\nset_error_handler('h');\n$message = new M;\nshow($message);\n",
}
EXPECTED = {
    'ordinary-weak-null-new': b'H4|H4|[]/0',
    'ordinary-strict-null-inherited-method': b'E1|Exception::__construct(): Argument #1 ($message) must be of type string, null given|E2|Exception::__construct(): Argument #2 ($code) must be of type int, null given|old/4',
    'ordinary-stringable-lossy-new': b'T|H4|m/7',
    'ordinary-warning-throw-method-atomic': b'H|E|stop|old/4/same',
    'ordinary-stringable-throw-method-atomic': b'T|E|stop|old/4',
    'ordinary-named-error-before-receive': b'M|U|E|Unknown named parameter $missing',
    'ordinary-errorexception-formal-order': b'M|H4|H4|F|H4|m/1/2/virtual.php/4',
    'ordinary-string-rewrite-later-error-trace': b'H|S|F|__construct|ErrorException|5|bad',
    'ordinary-handler-throw-trace': b'h|4|none|__construct|Exception|null|7|take',
    'ordinary-stringable-throw-trace': b'__toString|M|none|__construct|Exception|M|7|take',
    'ordinary-scoped-parent-private-handler': b'E/R|E/R|[]/4',
    'ordinary-handler-reentrant-default': b'H|T|F/inner|H|T|F/inner|[]/7',
    'ordinary-owned-method-retirement': b'T|H|new/4/p|gone/gone',
    'ordinary-strict-stringable-rejected': b'E|Exception::__construct(): Argument #1 ($message) must be of type string, M given',
    'ordinary-method-named-holes-trace': b'H4|[]/7/same|__construct/Exception/3/empty/0/bad|[]/7/same',
    'ordinary-inherited-builtin-stringable': b'H4|same/7/gone',
    'ordinary-recursive-same-stringable-site': b'T|H|F/m|T|H|F/m|',
    'ordinary-template-reentrant-echo-composition': b'H4|T|H4|E2048|m|T|H4|E2048|m|',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='ordinary-constructors-', dir=ROOT / '.tools'))
    report = {'passed': False, 'completed': False, 'before': before,
              'profile': cross.invoke.types.PROFILE, 'selected': selected, 'records': []}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source = directory / 'source.php'; source.write_bytes(CASES[name])
            row = {'case': name, 'source_sha256': cross.invoke.sha(source), 'completed': False}
            report['records'].append(row)
            row['outcome'] = cross.source({'abrupt': False, 'expected_exit_status': 0,
                'expected_stdout': EXPECTED[name].decode()}, directory, source)
            row['completed'] = True
            print(name, row['outcome']['status'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
