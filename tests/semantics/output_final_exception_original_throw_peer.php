<?php
class OriginalReleaseThrowOB04 {
    public function __destruct() {
        $GLOBALS['release_stage'] = 'throwing';
        echo 'P|';
        throw new Exception('original-release-secondary');
    }
}
class OriginalReleaseObserverOB04 {
    public function __destruct() {
        echo 'A:', $GLOBALS['release_stage'], '|';
    }
}
function originalReleaseErrorOB04($payload) {
    return new Exception('original-release-primary');
}
class OriginalReleaseFinalOB04 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new OriginalReleaseObserverOB04;
        $GLOBALS['release_stage'] = 'live';
        throw originalReleaseErrorOB04(new OriginalReleaseThrowOB04);
    }
}
function originalReleaseHandlerOB04(Throwable $error) {
    echo 'H|';
    return false;
}
set_exception_handler('originalReleaseHandlerOB04');
ob_start(null, 0);
echo 'B|';
ob_start(new OriginalReleaseFinalOB04, 0);
echo 'T|';
