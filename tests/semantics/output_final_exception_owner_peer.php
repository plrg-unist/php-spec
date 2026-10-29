<?php
class CursorTraceOwnerOB04 {
    public function __destruct() {
        $GLOBALS['cursor_stage'] = 'released';
        echo 'P|';
    }
}
class CursorRawObserverOB04 {
    public function __destruct() {
        echo 'A:', $GLOBALS['cursor_stage'], '|';
    }
}
function cursorOriginalOB04($payload) {
    return new Exception('cursor-primary');
}
class CursorFinalOwnerOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new CursorRawObserverOB04;
        $GLOBALS['cursor_stage'] = 'live';
        throw cursorOriginalOB04(new CursorTraceOwnerOB04);
    }
}
#[\Deprecated('before-owner-handler')]
function cursorSelectedOB04(Throwable $error) {
    echo 'BAD-BODY|';
}
function cursorNoticeOB04($level, $message, $file, $line) {
    echo 'D|';
    throw new Exception('owner-secondary');
}
set_error_handler('cursorNoticeOB04');
set_exception_handler('cursorSelectedOB04');
ob_start(null, 0);
echo 'B|';
ob_start(new CursorFinalOwnerOB04, 0);
echo 'T|';
