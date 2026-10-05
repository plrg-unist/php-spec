#!/usr/bin/env python3
"""Parameter-default NEW autoload source controls."""
import argparse
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'default-autoload-before-nested-argument': b"<?php\nclass DefaultArgumentMarker {\n    public function __construct() { echo 'V|'; }\n}\nfunction publish_default_target() {\n    class DefaultAutoloadTarget {\n        public function __construct($value) { echo 'C|'; }\n    }\n}\nfunction receive_default($value = new DefaultAutoloadTarget(new DefaultArgumentMarker)) {\n    echo 'F', $value::class;\n}\nspl_autoload_register(function ($name) {\n    echo 'L', $name, '|';\n    publish_default_target();\n});\nreceive_default();\n",
    'default-autoload-throw-before-argument': b"<?php\nclass ThrowArgumentMarker {\n    public function __construct() { echo 'V|'; }\n}\nfunction receive_throw_default($value = new ThrowAutoloadTarget(new ThrowArgumentMarker)) {\n    echo 'F';\n}\nspl_autoload_register(function ($name) {\n    echo 'L', $name, '|';\n    throw new Exception('stop');\n});\ntry { receive_throw_default(); }\ncatch (Exception $error) { echo 'E|', $error->getMessage(); }\n",
    'default-autoload-miss-before-argument': b"<?php\nclass MissingArgumentMarker {\n    public function __construct() { echo 'V|'; }\n}\nfunction receive_missing_default($value = new MissingAutoloadTarget(new MissingArgumentMarker)) {\n    echo 'F';\n}\nspl_autoload_register(function ($name) { echo 'L', $name, '|'; });\ntry { receive_missing_default(); }\ncatch (Error $error) { echo 'E|', $error->getMessage(); }\n",
    'default-autoload-same-key-recursion': b"<?php\nclass RecursiveArgumentMarker {\n    public function __construct() { echo 'V|'; }\n}\nfunction publish_recursive_default() {\n    class RecursiveDefaultTarget {\n        public function __construct($value = null) { echo 'C|'; }\n    }\n}\nfunction outer_recursive_default($value = new RecursiveDefaultTarget(new RecursiveArgumentMarker)) {\n    echo 'F', $value::class;\n}\nfunction nested_recursive_default($value = new RecursiveDefaultTarget) { echo 'N'; }\nspl_autoload_register(function ($name) {\n    echo 'L', $name, '|';\n    try { nested_recursive_default(); }\n    catch (Error $error) { echo 'R|', $error->getMessage(), '|'; }\n    publish_recursive_default();\n});\nouter_recursive_default();\n",
    'default-autoload-declaration-strictness': b'<?php\nfunction publish_strict_default() { class StrictDefaultTarget {} }\nspl_autoload_register(function (bool $name) { echo \'B|\'; publish_strict_default(); });\neval(\'declare(strict_types=1); function strict_default_receive($value = new StrictDefaultTarget) { echo "F"; }\');\ntry { strict_default_receive(); }\ncatch (TypeError $error) { echo \'E\'; }\n',
    'default-autoload-private-constructor-order': b"<?php\nclass AccessArgumentMarker {\n    public function __construct() { echo 'V|'; }\n}\nfunction publish_private_default_target() {\n    class PrivateDefaultAutoloadTarget {\n        private function __construct($value) { echo 'C|'; }\n    }\n}\nfunction receive_private_default($value = new PrivateDefaultAutoloadTarget(new AccessArgumentMarker)) {\n    echo 'F';\n}\nspl_autoload_register(function ($name) { echo 'L|'; publish_private_default_target(); });\ntry { receive_private_default(); }\ncatch (Error $error) { echo 'E|', $error->getMessage(); }\n",
    'default-autoload-multiline-loader-trace': b"<?php\nfunction default_loader_trace($name) {\n    throw new Exception('stop');\n}\nfunction traced_default_receive(\n    $value =\n        new TraceDefaultTarget(\n            1\n        )\n) { echo 'F'; }\nspl_autoload_register('default_loader_trace');\ntry { traced_default_receive(); }\ncatch (Exception $error) {\n    $trace = $error->getTrace();\n    echo $trace[0]['function'], '|', isset($trace[0]['line']) ? $trace[0]['line'] : 'internal', '|';\n    echo $trace[1]['function'], '|', isset($trace[1]['line']) ? $trace[1]['line'] : 'internal';\n}\n",
    'default-autoload-named-no-constructor': b"<?php\nclass NamedDefaultArgumentMarker {\n    public function __construct($value) { echo 'V', $value, '|'; }\n}\nspl_autoload_register(static function ($name) {\n    echo 'L|';\n    if ($name === 'NamedDefaultNoConstructor') {\n        class NamedDefaultNoConstructor {}\n    }\n});\nfunction named_default_no_constructor($value = new NamedDefaultNoConstructor(first: new NamedDefaultArgumentMarker(1), second: new NamedDefaultArgumentMarker(2))) {\n    echo 'F', get_class($value);\n}\nnamed_default_no_constructor();\n",
    'default-autoload-receiving-closure-core': b"<?php\nclass DefaultAutoloadOwner {\n    public function make() {\n        return function ($value = new RetirementDefaultTarget()) {\n            echo 'F', self::class, '/', get_called_class(), '|';\n        };\n    }\n}\nclass DefaultAutoloadChild extends DefaultAutoloadOwner {}\n$factory = new DefaultAutoloadChild();\n$receive = $factory->make();\nspl_autoload_register(static function ($name) {\n    unset($GLOBALS['receive'], $GLOBALS['factory']);\n    echo 'L', isset($GLOBALS['receive']) || isset($GLOBALS['factory']) ? 'bound' : 'gone', '|';\n    if ($name === 'RetirementDefaultTarget') {\n        class RetirementDefaultTarget {\n            public function __construct() { echo 'C|'; }\n        }\n    }\n});\n$receive();\necho 'R', isset($GLOBALS['receive']) || isset($GLOBALS['factory']) ? 'bound' : 'gone';\n",
    'default-autoload-generator-composition': b"<?php\nclass GeneratorDefaultArgument {\n    public function __construct() { echo 'V|'; }\n}\nfunction publish_generator_default_target() {\n    class GeneratorAutoloadDefaultTarget {\n        public function __construct($value) { echo 'C|'; }\n    }\n}\nspl_autoload_register(static function ($name) {\n    echo 'L|';\n    if ($name === 'GeneratorAutoloadDefaultTarget') {\n        publish_generator_default_target();\n    }\n});\nfunction generator_with_autoload_default($value = new GeneratorAutoloadDefaultTarget(new GeneratorDefaultArgument())) {\n    echo 'B|';\n    yield $value;\n}\n$generator = generator_with_autoload_default();\necho 'G|';\nforeach ($generator as $object) {\n    echo 'Y|', get_class($object), '|';\n}\nunset($generator, $object);\necho 'R';\n",
}
EXPECTED = {
    'default-autoload-before-nested-argument': b'LDefaultAutoloadTarget|V|C|FDefaultAutoloadTarget',
    'default-autoload-throw-before-argument': b'LThrowAutoloadTarget|E|stop',
    'default-autoload-miss-before-argument': b'LMissingAutoloadTarget|E|Class "MissingAutoloadTarget" not found',
    'default-autoload-same-key-recursion': b'LRecursiveDefaultTarget|R|Class "RecursiveDefaultTarget" not found|V|C|FRecursiveDefaultTarget',
    'default-autoload-declaration-strictness': b'E',
    'default-autoload-private-constructor-order': b'L|V|E|Call to private PrivateDefaultAutoloadTarget::__construct() from global scope',
    'default-autoload-multiline-loader-trace': b'default_loader_trace|6|traced_default_receive|12',
    'default-autoload-named-no-constructor': b'L|V1|V2|FNamedDefaultNoConstructor',
    'default-autoload-receiving-closure-core': b'Lgone|C|FDefaultAutoloadOwner/DefaultAutoloadChild|Rgone',
    'default-autoload-generator-composition': b'L|V|C|G|B|Y|GeneratorAutoloadDefaultTarget|R',
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
    out = Path(tempfile.mkdtemp(prefix='default-new-autoload-sources-', dir=ROOT / '.tools'))
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
