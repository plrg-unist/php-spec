"""Native-first Deprecated exception-handler callbacks."""


def php(source):
    return ('<?php\n' + source.strip() + '\n').encode()


CASES = {
    'exception-named-warning-before-body': php(r'''
#[\Deprecated('named', '4'), \NoDiscard]
function old_handler(Throwable $error) {
    echo 'B:', $error === $GLOBALS['saved'], ':', $GLOBALS['warnings'] === 1,
        ':', get_exception_handler() === null, ';';
    return 7;
}
function notice($level, $message, $file, $line) {
    $GLOBALS['warnings']++;
    echo 'D:', $level === 16384, ':',
        $message === 'Function old_handler() is deprecated since 4, named', ':',
        $file === 'Unknown', ':', $line === 0, ';';
    return true;
}
$warnings = 0;
$saved = new Exception('original');
set_exception_handler('old_handler');
set_error_handler('notice');
throw $saved;
'''),
    'exception-method-default-deprecation': php(r'''
class LegacyExceptionHandler {
    #[\Deprecated('method', '5')]
    public function handle(Throwable $error) {
        echo 'B:', $error === $GLOBALS['saved'], ':',
            get_exception_handler() === null, ':', func_num_args() === 1, ';';
    }
}
$saved = new Exception('method');
$receiver = new LegacyExceptionHandler();
set_exception_handler([$receiver, 'handle']);
throw $saved;
'''),
    'exception-marked-body-throw-fatal': php(r'''
#[\Deprecated]
function throws_after_entry(Throwable $error) { echo 'B:', $error->getMessage() === 'original', ':', get_exception_handler() === null, ';'; throw new Exception('body'); }
function notice($level, $message, $file, $line) {
    echo 'D:', $level === 16384 && $message === 'Function throws_after_entry() is deprecated', ';';
    return true;
}
set_exception_handler('throws_after_entry');
set_error_handler('notice');
throw new Exception('original');
'''),
    'exception-unmarked-fresh-reference-control': php(r'''
function plain_terminal(&$error) {
    $GLOBALS['body']++;
    echo 'B:', $error === $GLOBALS['weak_original']->get(), ':', get_exception_handler() === null, ';';
    $fresh = new Exception('fresh');
    $GLOBALS['weak_fresh'] = WeakReference::create($fresh);
    $error = $fresh;
    echo 'F:', $error === $GLOBALS['weak_fresh']->get(), ';';
}
function notice($level, $message, $file, $line) {
    $GLOBALS['warnings']++;
    echo 'W:', $level === 2, ':',
        $message === 'plain_terminal(): Argument #1 ($error) must be passed by reference, value given',
        ':', $file === 'Unknown' && $line === 0, ';';
    return true;
}
function raise_original() {
    $error = new Exception('original');
    $GLOBALS['weak_original'] = WeakReference::create($error);
    throw $error;
}
function finish() {
    echo 'E:', $GLOBALS['warnings'] === 1, ':', $GLOBALS['body'] === 1, ':',
        $GLOBALS['weak_original']->get() === null, ':', $GLOBALS['weak_fresh']->get() === null, ';';
}
$warnings = 0; $body = 0;
register_shutdown_function('finish');
set_error_handler('notice');
set_exception_handler('plain_terminal');
raise_original();
'''),
}


EXPECTED_STDOUT = {
    'exception-named-warning-before-body': b'D:1:1:1:1;B:1:1:1;',
    'exception-method-default-deprecation': b'B:1:1:1;',
    'exception-marked-body-throw-fatal': b'D:1;B:1:1;',
    'exception-unmarked-fresh-reference-control': b'W:1:1:1;B:1:1;F:1;E:1:1:1:1;',
}

EXIT_CODES = {
    'exception-named-warning-before-body': 0,
    'exception-method-default-deprecation': 0,
    'exception-marked-body-throw-fatal': 255,
    'exception-unmarked-fresh-reference-control': 0,
}


def expected_stderr(name, source):
    if name == 'exception-method-default-deprecation':
        return b'Deprecated: Method LegacyExceptionHandler::handle() is deprecated since 5, method in Unknown on line 0\n'
    if name == 'exception-marked-body-throw-fatal':
        filename = bytes(source)
        return (b'Fatal error: Uncaught Exception: body in ' + filename + b':3\n'
                b'Stack trace:\n#0 [internal function]: throws_after_entry(Object(Exception))\n'
                b'#1 {main}\n  thrown in ' + filename + b' on line 3\n')
    return b''
