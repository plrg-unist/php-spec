"""Native-first selected callback witnesses for early Deprecated API calls."""


def php(body):
    return ('<?php\n' + body.strip() + '\n').encode()


CASES = {
    'assert-selected-before-byref-throw': php(r'''
#[\Deprecated('old', '1')]
function legacy_assert(&$file, $line, $code, $description = null) {
    $GLOBALS['old_body']++;
    echo 'BAD-OLD;';
}
function substitute_assert($file, $line, $code, $description = null) {
    $GLOBALS['new_body']++;
    echo 'BAD-NEW;';
}
function notice($level, $message, $file, $line) {
    if ($level === 16384) {
        $GLOBALS['deprecated']++;
        @assert_options(ASSERT_CALLBACK, 'substitute_assert');
        echo 'D:', $message === 'Function legacy_assert() is deprecated since 1, old', ':', $GLOBALS['new_body'] === 0, ';';
        return true;
    }
    if ($level === 2) {
        $GLOBALS['byref']++;
        echo 'W:', $message === 'legacy_assert(): Argument #1 ($file) must be passed by reference, value given', ':', $GLOBALS['deprecated'] === 1, ';';
        throw $GLOBALS['saved'];
    }
    return false;
}
$old_body = 0; $new_body = 0; $deprecated = 0; $byref = 0;
$saved = new Exception('stop');
@assert_options(ASSERT_EXCEPTION, 0);
@assert_options(ASSERT_WARNING, 0);
@assert_options(ASSERT_CALLBACK, 'legacy_assert');
set_error_handler('notice');
try { assert(false); } catch (Exception $caught) {
    echo 'C:', $caught === $saved, ':', $deprecated === 1, ':', $byref === 1, ':', $old_body === 0, ':', $new_body === 0, ';';
}
restore_error_handler();
@assert_options(ASSERT_CALLBACK, null);
'''),
    'assert-selected-receiver-after-registry-replacement': php(r'''
class LegacyReceiver {
    #[\Deprecated('old', '2')]
    public function run($file, $line, $code, $description = null) {
        $GLOBALS['old_body']++;
        echo 'B:', $GLOBALS['receiver'] === $this, ':', $GLOBALS['weak']->get() === $this, ';';
    }
    public function __destruct() { echo 'X;'; }
}
function substitute_receiver($file, $line, $code, $description = null) {
    $GLOBALS['new_body']++;
    echo 'BAD-NEW;';
}
function observe($level, $message, $file, $line) {
    if ($level === 16384) {
        @assert_options(ASSERT_CALLBACK, 'substitute_receiver');
        echo 'D:', $message === 'Method LegacyReceiver::run() is deprecated since 2, old', ':', $GLOBALS['weak']->get() === $GLOBALS['receiver'], ';';
        return true;
    }
    return false;
}
$old_body = 0; $new_body = 0;
$receiver = new LegacyReceiver();
$weak = WeakReference::create($receiver);
@assert_options(ASSERT_EXCEPTION, 0);
@assert_options(ASSERT_WARNING, 0);
@assert_options(ASSERT_CALLBACK, [$receiver, 'run']);
set_error_handler('observe');
assert(false);
restore_error_handler();
echo 'E:', $old_body === 1, ':', $new_body === 0, ':', $weak->get() === $receiver, ';';
$receiver = null;
echo 'Z:', $weak->get() === null, ';';
@assert_options(ASSERT_CALLBACK, null);
'''),
    'error-handler-deprecated-before-body': php(r'''
#[\Deprecated('old', '3')]
function legacy_error($level, $message, $file, $line) {
    $GLOBALS['body']++;
    echo 'B:', $level === 512, ':', $message === 'ping', ':', $file === __FILE__, ';';
    return true;
}
$body = 0;
set_error_handler('legacy_error');
trigger_error('ping', E_USER_WARNING);
restore_error_handler();
echo 'E:', $body === 1, ';';
'''),
    'error-handler-deprecated-before-default-byref': php(r'''
#[\Deprecated]
function legacy_byref_error(&$level, $message, $file, $line) {
    $GLOBALS['body']++;
    echo 'B:', $level === 512, ':', $message === 'ping', ';';
    return true;
}
$body = 0;
set_error_handler('legacy_byref_error');
trigger_error('ping', E_USER_WARNING);
restore_error_handler();
echo 'E:', $body === 1, ';';
'''),
}


# Frozen before the first native execution; source payloads above are unchanged.
EXPECTED_STDOUT = {
    'assert-selected-before-byref-throw': b'D:1:1;W:1:1;C:1:1:1:1:1;',
    'assert-selected-receiver-after-registry-replacement': b'D:1:1;B:1:1;E:1:1:1;X;Z:1;',
    'error-handler-deprecated-before-body': b'B:1:1:1;E:1;',
    'error-handler-deprecated-before-default-byref': b'B:1:1;E:1;',
}


def expected_stderr(name, path):
    path = bytes(path)
    location = b' in ' + path + b' on line 10\n'
    if name == 'error-handler-deprecated-before-body':
        return b'Deprecated: Function legacy_error() is deprecated since 3, old' + location
    if name == 'error-handler-deprecated-before-default-byref':
        return (b'Deprecated: Function legacy_byref_error() is deprecated' + location
                + b'Warning: legacy_byref_error(): Argument #1 ($level) must be passed by reference, value given' + location)
    return b''


EXIT_CODES = {name: 0 for name in CASES}
