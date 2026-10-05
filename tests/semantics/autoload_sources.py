#!/usr/bin/env python3
"""Autoload registry, live lookup queue and source callback controls."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'autoload-named-before-arguments': b"<?php\nfunction argument_value() { echo 'V|'; return 7; }\n$loader = function($name) {\n    echo 'L', $name, '|';\n    class AutoloadTarget { public function __construct($v) { echo 'C', $v, '|'; } }\n};\nspl_autoload_register($loader);\n$value = new AutoloadTarget(argument_value());\necho 'F', $value::class;\n",
    'autoload-dynamic-capture-casing': b"<?php\n$name = '\\\\mIxEdLoAd';\n$loader = function($class) use (&$name) {\n    echo 'L', $class, '|';\n    $name = 'OtherLoaded';\n    class MixedLoad {}\n    class OtherLoaded {}\n};\nspl_autoload_register($loader);\n$value = new $name;\necho 'F', $value::class, '/', $name;\n",
    'autoload-namespace-alias': b"<?php\nnamespace Remote {\n    function load($name) {\n        echo 'L', $name, '|';\n        if ($name === 'Remote\\\\Type') { class Type {} }\n    }\n}\nnamespace N {\n    use Remote\\Type as Imported;\n    \\spl_autoload_register('Remote\\\\load');\n    $value = new Imported;\n    $dynamic = 'Imported';\n    try { new $dynamic; } catch (\\Error $e) { echo 'E|', $e->getMessage(), '|'; }\n    echo 'F', $value::class;\n}\n",
    'autoload-prepend-duplicate-unregister': b"<?php\n$a = function($name) { echo 'A|'; class QueueTarget {} };\n$b = function($name) { echo 'B|'; };\n$c = function($name) { echo 'C|'; };\nspl_autoload_register($a);\nspl_autoload_register($b);\nspl_autoload_register($c, true, true);\nspl_autoload_register($a, true, true);\nforeach (spl_autoload_functions() as $v) {\n    echo $v === $a ? 'A' : ($v === $b ? 'B' : 'C');\n}\necho '|', spl_autoload_unregister($b) ? '1' : '0', spl_autoload_unregister($b) ? '1' : '0', '|';\n$value = new QueueTarget;\necho 'F', $value::class;\n",
    'autoload-live-remove-append': b"<?php\n$b = function($name) { echo 'B|'; };\n$c = function($name) { echo 'C|'; };\n$d = function($name) { echo 'D|'; class MutationTarget {} };\n$a = function($name) use ($b, $d) {\n    echo 'A|';\n    spl_autoload_unregister($b);\n    spl_autoload_register($d);\n};\nspl_autoload_register($a);\nspl_autoload_register($b);\nspl_autoload_register($c);\n$value = new MutationTarget;\necho 'F';\n",
    'autoload-live-prepend-cursor': b"<?php\n$ran = false;\n$d = function($name) { echo 'D|'; class InsertedTarget {} };\n$a = function($name) use (&$ran, $d) {\n    echo 'A|';\n    if (!$ran) { $ran = true; spl_autoload_register($d, true, true); }\n};\n$b = function($name) { echo 'B|'; };\nspl_autoload_register($a);\nspl_autoload_register($b);\ntry { new InsertedTarget; } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\n$value = new InsertedTarget;\necho 'F';\n",
    'autoload-same-name-recursion': b"<?php\n$loader = function($name) {\n    echo 'L', $name, '|';\n    try { new recursivetarget; } catch (Error $e) { echo 'R|', $e->getMessage(), '|'; }\n    class RecursiveTarget {}\n};\nspl_autoload_register($loader);\n$value = new RecursiveTarget;\necho 'F', $value::class;\n",
    'autoload-nested-parent-link': b"<?php\n$loader = function($name) {\n    echo 'L', $name, '|';\n    if ($name === 'AutoloadChild') { class AutoloadChild extends AutoloadParent {} }\n    if ($name === 'AutoloadParent') { class AutoloadParent {} }\n};\nspl_autoload_register($loader);\n$value = new AutoloadChild;\necho 'F', $value::class, '/', $value instanceof AutoloadParent ? 'P' : 'N';\n",
    'autoload-exception-stops-queue': b"<?php\nfunction argument_value() { echo 'V|'; return 7; }\n$a = function($name) { echo 'A|'; throw new Exception('stop'); };\n$b = function($name) { echo 'B|'; class StoppedTarget {} };\nspl_autoload_register($a);\nspl_autoload_register($b);\ntry { new StoppedTarget(argument_value()); } catch (Exception $e) { echo 'E', $e->getMessage(); }\n",
    'autoload-published-class-throw-retry': b"<?php\nfunction argument_value($v) { echo 'V', $v, '|'; return $v; }\n$loader = function($name) {\n    echo 'L|';\n    class PublishedTarget { public function __construct($v) { echo 'C', $v, '|'; } }\n    throw new Exception('after');\n};\nspl_autoload_register($loader);\ntry { new PublishedTarget(argument_value(1)); } catch (Exception $e) { echo 'E', $e->getMessage(), '|'; }\n$value = new PublishedTarget(argument_value(2));\necho 'F';\n",
    'autoload-explicit-call-lookup-distinction': b"<?php\nclass ExistingTarget {}\n$loader = function($name) { echo '[', $name, ']|'; };\nspl_autoload_register($loader);\nspl_autoload_call('\\\\ExistingTarget');\nspl_autoload_call('Bad!');\n$bad = 'Bad!';\ntry { new $bad; } catch (Error $e) { echo 'E|', $e->getMessage(); }\n",
    'autoload-cold-class-before-arguments': b"<?php\nset_error_handler(function($n, $m) { echo 'D', func_num_args(), '|'; return true; });\nfunction argument_value() { echo 'V|'; return 1; }\n$loader = function($name) {\n    echo 'L|';\n    class ColdTarget {\n        public const X = E_STRICT;\n        public $p = 7;\n        public function __construct($v) { echo 'C', self::X, '/', $this->p, '|'; }\n    }\n};\nspl_autoload_register($loader);\n$value = new ColdTarget(argument_value());\necho 'F';\n",
    'autoload-registration-notice': b"<?php\nset_error_handler(function($n, $m) { echo 'N', $n, '/', func_num_args(), '|'; return true; });\n$loader = function($name) { class FalseFlagTarget {} };\necho spl_autoload_register($loader, false) ? '1|' : '0|';\n$value = new FalseFlagTarget;\necho 'F';\n",
    'autoload-registration-notice-throws-commit': b"<?php\nset_error_handler(function($n, $m) { echo 'N|'; throw new Exception('stop'); });\n$loader = function($name) { echo 'L|'; class CommitTarget {} };\ntry { spl_autoload_register($loader, false); } catch (Exception $e) { echo 'E', $e->getMessage(), '|'; }\nrestore_error_handler();\n$value = new CommitTarget;\necho 'F';\n",
    'autoload-unregister-notice-throws-keeps-queue': b"<?php\n$loader = function($name) { echo 'L|'; class KeptTarget {} };\nspl_autoload_register($loader);\nset_error_handler(function($n, $m) { echo 'D|'; throw new Exception('stop'); });\ntry { spl_autoload_unregister('spl_autoload_call'); } catch (Exception $e) { echo 'E', $e->getMessage(), '|'; }\nrestore_error_handler();\n$value = new KeptTarget;\necho 'F';\n",
    'autoload-invalid-callback-before-notice': b"<?php\nset_error_handler(function($n, $m) { echo 'W|'; return true; });\ntry { spl_autoload_register('missing_callback', false); } catch (TypeError $e) { echo 'E', $e::class, '|'; }\n$empty = true;\nforeach (spl_autoload_functions() as $v) { $empty = false; }\necho $empty ? 'empty' : 'present';\n",
    'autoload-language-tests-do-not-load': b"<?php\n$loader = function($name) { echo 'L', $name, '|'; };\nspl_autoload_register($loader);\nfunction receive(AbsentType $value) {}\ntry { receive(new stdClass); } catch (TypeError $e) { echo 'T|'; }\n$value = new stdClass;\necho $value instanceof AbsentType ? '1|' : '0|';\ntry { throw new Exception; } catch (AbsentCatch $e) { echo 'wrong'; } catch (Exception $e) { echo 'E'; }\n",
    'autoload-captured-private-method-core': b"<?php\nfunction publish_private_target() { class PrivateTarget {} }\nclass LoaderOwner {\n    public static function register() { spl_autoload_register(self::load(...)); }\n    private static function load($name) {\n        echo 'L', self::class, '/', get_called_class(), '|';\n        publish_private_target();\n    }\n}\nclass LoaderChild extends LoaderOwner {}\nLoaderChild::register();\n$value = new PrivateTarget;\necho 'F', $value::class;\n",
    'autoload-required-reference-loader': b"<?php\nset_error_handler(function($level, $message) { echo 'W', $level, '/', func_num_args(), '|'; return true; });\nfunction reference_loader(&$name) { echo 'L', $name, '|'; $name = 'ChangedTarget'; class ReferenceTarget {} }\nspl_autoload_register('reference_loader');\n$value = new ReferenceTarget;\necho 'F', $value::class;\n",
    'autoload-reference-warning-throw': b"<?php\nset_error_handler(function($level, $message) { echo 'W|'; throw new Exception('stop'); });\nfunction reference_loader(&$name) { echo 'L|'; class ReferenceTarget {} }\nspl_autoload_register('reference_loader');\ntry { new ReferenceTarget; } catch (Exception $e) { echo 'E', $e->getMessage(); }\n",
    'autoload-registration-captured-receiver': b"<?php\nfunction publish_receiver_target() { class ReceiverTarget {} }\nclass ReceiverLoader { public function load($name) { echo 'M|'; publish_receiver_target(); } }\n$receiver = new ReceiverLoader;\n$callback = [$receiver, 'load'];\nset_error_handler(function($level, $message) { unset($GLOBALS['receiver'], $GLOBALS['callback']); echo 'N|'; throw new Exception('stop'); });\ntry { spl_autoload_register($callback, false); } catch (Exception $e) { echo 'E', $e->getMessage(), '|'; }\nrestore_error_handler();\n$functions = spl_autoload_functions();\necho isset($receiver) ? 'live' : 'retired', '/', $functions[0][0]::class, '|';\n$value = new ReceiverTarget;\necho 'F';\n",
    'autoload-current-unregister-core': b"<?php\n$a = function($name) use (&$a) { echo 'A|'; spl_autoload_unregister($a); };\n$b = function($name) { echo 'B|'; class RemovedCurrentTarget {} };\nspl_autoload_register($a);\nspl_autoload_register($b);\ntry { new RemovedCurrentTarget; } catch (Error $e) { echo 'E|', $e->getMessage(), '|'; }\n$value = new RemovedCurrentTarget;\necho 'F';\n",
    'autoload-lookup-explicit-trace-lines': b"<?php\nfunction trace_loader($name) { throw new Exception('stop'); }\nspl_autoload_register('trace_loader');\nfunction factory() { return new TraceTarget; }\ntry { factory(); } catch (Exception $e) {\n    $t = $e->getTrace();\n    echo $t[0]['function'], '/', isset($t[0]['file']) ? 'F' : 'I', '/', $t[0]['line'], '/', $t[0]['args'][0], '|';\n    echo $t[1]['function'], '/', $t[1]['line'], '|';\n}\ntry { spl_autoload_call('TraceExplicit'); } catch (Exception $e) {\n    $t = $e->getTrace();\n    echo $t[0]['function'], '/', isset($t[0]['file']) ? 'F' : 'I', '/', isset($t[0]['line']) ? $t[0]['line'] : '-', '/', $t[0]['args'][0], '|';\n    echo $t[1]['function'], '/', $t[1]['line'];\n}\n",
    'autoload-default-registry-without-search': b"<?php\necho spl_autoload_register() ? '1' : '0', '|';\n$functions = spl_autoload_functions();\necho $functions[0], '|';\necho spl_autoload_register(callback: null, prepend: true) ? '1' : '0', '/', isset(spl_autoload_functions()[1]) ? 'two' : 'one', '|';\necho spl_autoload_unregister($functions[0]) ? '1' : '0', '/', isset(spl_autoload_functions()[0]) ? 'live' : 'empty';\n",
    'autoload-lookup-explicit-strictness': b"<?php\ndeclare(strict_types=1);\nfunction bool_loader(bool $name) { echo 'T', $name ? '1' : '0', '|'; class WeakCallbackTarget {} }\nspl_autoload_register(callback: 'bool_loader', prepend: true, throw: true);\ntry { new WeakCallbackTarget; } catch (TypeError $e) { echo 'E|'; }\nspl_autoload_call('WeakCallbackTarget');\n$value = new WeakCallbackTarget;\necho 'F';\n",
    'autoload-invokable-registry-core': b"<?php\nfunction publish_invokable_target() { class InvokableTarget {} }\nclass InvokableLoader { public function __invoke($name) { echo 'I|'; publish_invokable_target(); } }\n$receiver = new InvokableLoader;\nspl_autoload_register($receiver);\n$functions = spl_autoload_functions();\necho $functions[0] === $receiver ? 'same' : 'other', '|';\necho spl_autoload_register($functions[0]) ? '1' : '0', '/', isset(spl_autoload_functions()[1]) ? 'two' : 'one', '|';\nunset($receiver);\n$value = new InvokableTarget;\necho 'F|', spl_autoload_unregister(callback: $functions[0]) ? '1' : '0', '/', isset(spl_autoload_functions()[0]) ? 'live' : 'empty';\n",
    'autoload-unregister-all-returns': b"<?php\nfunction absent_loader($name) { echo 'L|'; }\nspl_autoload_register('absent_loader');\nset_error_handler(function($level, $message) { echo 'D', $level, '/', func_num_args(), '|'; return true; });\necho spl_autoload_unregister('spl_autoload_call') ? '1' : '0', '|';\nrestore_error_handler();\necho isset(spl_autoload_functions()[0]) ? 'live' : 'empty';\n",
    'autoload-invokable-array-distinct-cache': b"<?php\nclass Loader { public function __invoke($name) { echo 'L|'; } }\n$loader = new Loader;\nspl_autoload_register($loader);\nspl_autoload_register([$loader, '__invoke']);\n$functions = spl_autoload_functions();\necho $functions[0] === $loader ? 'object' : 'other', '/', $functions[1][0] === $loader ? 'array' : 'other', '|';\necho spl_autoload_unregister($loader) ? '1' : '0', '|';\n$remaining = spl_autoload_functions();\necho $remaining[0][0] === $loader ? 'array' : 'other', '|';\necho spl_autoload_unregister([$loader, '__invoke']) ? '1' : '0', '/', isset(spl_autoload_functions()[0]) ? 'live' : 'empty';\n",
    'autoload-forbidden-notice-priority-core': b"<?php\nset_error_handler(function($level, $message) { echo 'N|'; throw new Exception('old'); });\ntry { spl_autoload_register('spl_autoload_call', false); } catch (Throwable $e) { echo $e::class, '/', $e->getMessage(), '/', $e->getPrevious() === null ? 'no' : 'yes', '|'; }\nset_error_handler(function($level, $message) { echo 'N2|'; return true; });\ntry { spl_autoload_register('spl_autoload_call', false); } catch (ValueError $e) { echo 'V/', $e->getPrevious() === null ? 'no' : 'yes', '|'; }\nrestore_error_handler();\necho isset(spl_autoload_functions()[0]) ? 'live' : 'empty';\n",
    'autoload-live-compaction-cursor': b"<?php\nfunction load_a($name) { echo 'A|'; }\nfunction load_b($name) { echo 'B|'; }\nfunction load_c($name) { echo 'C|'; spl_autoload_unregister('load_a'); spl_autoload_unregister('load_b'); spl_autoload_register('load_i'); }\nfunction load_d($name) { echo 'D|'; }\nfunction load_e($name) { echo 'E|'; }\nfunction load_f($name) { echo 'F|'; }\nfunction load_g($name) { echo 'G|'; }\nfunction load_h($name) { echo 'H|'; }\nfunction load_i($name) { echo 'I|'; class CompactedTarget {} }\nforeach (['load_a', 'load_b', 'load_c', 'load_d', 'load_e', 'load_f', 'load_g', 'load_h'] as $loader) { spl_autoload_register($loader); }\n$value = new CompactedTarget;\necho 'Z';\n",
    'autoload-explicit-user-stringable': b"<?php\nclass NameString { public function __toString() { echo 'T|'; return 'ExplicitTarget'; } }\nspl_autoload_register(function($name) { echo 'L', $name, '|'; class ExplicitTarget {} });\nspl_autoload_call(new NameString);\n$value = new ExplicitTarget;\necho 'F';\n",
    'autoload-explicit-stringable-throw': b"<?php\nclass NameString { public function __toString() { echo 'T|'; throw new Exception('stop'); } }\nspl_autoload_register(function($name) { echo 'L|'; });\ntry { spl_autoload_call(new NameString); } catch (Exception $e) { echo 'E', $e->getMessage(); }\n",
    'autoload-explicit-inherited-builtin-stringable': b"<?php\nclass StringException extends Exception {}\nspl_autoload_register(function($name) { echo $name[0], $name[1], $name[2], $name[3], $name[4], $name[5], $name[6], $name[7], $name[8], $name[9], $name[10], $name[11], $name[12], $name[13], $name[14], $name[15], $name[16], $name[17], $name[18], $name[19], $name[20], '|'; });\nspl_autoload_call(new StringException('boom'));\necho 'F';\n",
    'autoload-private-fcc-retirement': b"<?php\nfunction publish_private_retired() { class PrivateRetiredTarget {} }\nclass RetiredOwner {\n    public static function make() { return self::load(...); }\n    private static function load($name) {\n        spl_autoload_unregister($GLOBALS['loader']);\n        unset($GLOBALS['loader']);\n        echo 'L', self::class, '/', get_called_class(), '|';\n        publish_private_retired();\n    }\n}\nclass RetiredChild extends RetiredOwner {}\n$loader = RetiredChild::make();\nspl_autoload_register($loader);\n$value = new PrivateRetiredTarget;\necho isset($loader) ? 'live' : 'retired', '/', $value::class;\n",
    'autoload-dynamic-two-leading-known': b"<?php\nclass SlashKnown {}\nspl_autoload_register(function($name) { echo 'L[', $name, ']|'; });\n$name = '\\\\\\\\SlashKnown';\ntry { $value = new $name; } catch (Error $e) { echo 'E|', $e->getMessage(); }\n",
    'autoload-dynamic-two-leading-missing': b"<?php\nspl_autoload_register(function($name) { echo 'L[', $name, ']|'; class SlashMissing {} });\n$name = '\\\\\\\\SlashMissing';\ntry { $value = new $name; } catch (Error $e) { echo 'E|', $e->getMessage(); }\n",
    'autoload-global-constant-inherited-eval': b'<?php\nfunction publish_constant_autoload_target() {\n    class ConstantAutoloadTarget {\n        public function __construct($value) { echo \'C\', $value, \'|\'; }\n    }\n}\nfunction constant_autoload_argument() { echo \'V|\'; return 7; }\nclass ConstantLoaderOwner {\n    private const TOKEN = \'secret\';\n    public function install() {\n        eval(\'const CONST_AUTOLOADER = static function ($name) { echo "L", self::class, "/", get_called_class(), ":", self::TOKEN, "|"; publish_constant_autoload_target(); };\');\n    }\n}\nclass ConstantLoaderChild extends ConstantLoaderOwner {}\n$receiver = new ConstantLoaderChild;\n$receiver->install();\n$loader = CONST_AUTOLOADER;\nspl_autoload_register($loader);\nunset($receiver, $loader);\n$value = new ConstantAutoloadTarget(constant_autoload_argument());\necho \'F\', $value::class;\n',
}
EXPECTED = {
    'autoload-named-before-arguments': b'LAutoloadTarget|V|C7|FAutoloadTarget',
    'autoload-dynamic-capture-casing': b'LmIxEdLoAd|FMixedLoad/OtherLoaded',
    'autoload-namespace-alias': b'LRemote\\Type|LImported|E|Class "Imported" not found|FRemote\\Type',
    'autoload-prepend-duplicate-unregister': b'CAB|10|C|A|FQueueTarget',
    'autoload-live-remove-append': b'A|C|D|F',
    'autoload-live-prepend-cursor': b'A|A|B|E|Class "InsertedTarget" not found|D|F',
    'autoload-same-name-recursion': b'LRecursiveTarget|R|Class "recursivetarget" not found|FRecursiveTarget',
    'autoload-nested-parent-link': b'LAutoloadChild|LAutoloadParent|FAutoloadChild/P',
    'autoload-exception-stops-queue': b'A|Estop',
    'autoload-published-class-throw-retry': b'L|Eafter|V2|C2|F',
    'autoload-explicit-call-lookup-distinction': b'[\\ExistingTarget]|[Bad!]|E|Class "Bad!" not found',
    'autoload-cold-class-before-arguments': b'L|D4|V|C2048/7|F',
    'autoload-registration-notice': b'N8/4|1|F',
    'autoload-registration-notice-throws-commit': b'N|Estop|L|F',
    'autoload-unregister-notice-throws-keeps-queue': b'D|Estop|L|F',
    'autoload-invalid-callback-before-notice': b'ETypeError|empty',
    'autoload-language-tests-do-not-load': b'T|0|E',
    'autoload-captured-private-method-core': b'LLoaderOwner/LoaderChild|FPrivateTarget',
    'autoload-required-reference-loader': b'W2/4|LReferenceTarget|FReferenceTarget',
    'autoload-reference-warning-throw': b'W|Estop',
    'autoload-registration-captured-receiver': b'N|Estop|retired/ReceiverLoader|M|F',
    'autoload-current-unregister-core': b'A|E|Class "RemovedCurrentTarget" not found|B|F',
    'autoload-lookup-explicit-trace-lines': b'trace_loader/F/4/TraceTarget|factory/5|trace_loader/I/-/TraceExplicit|spl_autoload_call/10',
    'autoload-default-registry-without-search': b'1|spl_autoload|1/one|1/empty',
    'autoload-lookup-explicit-strictness': b'E|T1|F',
    'autoload-invokable-registry-core': b'same|1/one|I|F|1/empty',
    'autoload-unregister-all-returns': b'D8192/4|1|empty',
    'autoload-invokable-array-distinct-cache': b'object/array|1|array|1/empty',
    'autoload-forbidden-notice-priority-core': b'N|Exception/old/no|N2|V/no|empty',
    'autoload-live-compaction-cursor': b'A|B|C|F|G|H|I|Z',
    'autoload-explicit-user-stringable': b'T|LExplicitTarget|F',
    'autoload-explicit-stringable-throw': b'T|Estop',
    'autoload-explicit-inherited-builtin-stringable': b'StringException: boom|F',
    'autoload-private-fcc-retirement': b'LRetiredOwner/RetiredChild|retired/PrivateRetiredTarget',
    'autoload-dynamic-two-leading-known': b'L[\\SlashKnown]|E|Class "\\\\SlashKnown" not found',
    'autoload-dynamic-two-leading-missing': b'L[\\SlashMissing]|E|Class "\\\\SlashMissing" not found',
    'autoload-global-constant-inherited-eval': b'LConstantLoaderOwner/ConstantLoaderOwner:secret|V|C7|FConstantAutoloadTarget',
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
    out = Path(tempfile.mkdtemp(prefix='autoload-sources-', dir=ROOT / '.tools'))
    report = {'passed': False, 'completed': False, 'before': before,
              'profile': cross.invoke.types.PROFILE, 'selected': selected, 'records': []}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source = directory / 'source.php'; source.write_bytes(CASES[name])
            row = {'case': name, 'source_sha256': cross.invoke.sha(source), 'completed': False}
            report['records'].append(row)
            row['outcome'] = cross.source(
                {'abrupt': False, 'expected_exit_status': 0, 'expected_stdout': EXPECTED[name].decode()}, directory, source)
            assert cross.snapshot(args.freeze) == before
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
