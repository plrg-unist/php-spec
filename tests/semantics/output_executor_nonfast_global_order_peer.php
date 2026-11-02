<?php
class FirstGlobalOwnerOB05 {
    public function __destruct() {
        $GLOBALS['global_stage_ob05'] = 'first-entered';
        echo 'BAD-FIRST|';
    }
}
class SecondGlobalOwnerOB05 {
    public function __destruct() {
        $GLOBALS['global_stage_ob05'] = 'second-entered';
        echo 'BAD-SECOND|';
    }
}
class GlobalObserverOB05 {
    public function __destruct() {
        echo 'A:', $GLOBALS['global_stage_ob05'], '|';
    }
}
class GlobalFinalOB05 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new GlobalObserverOB05;
        $GLOBALS['global_stage_ob05'] = 'live';
        $GLOBALS['first_hold_ob05'] = null;
        $GLOBALS['second_hold_ob05'] = null;
        $GLOBALS['second_hold_ob05'] = new SecondGlobalOwnerOB05;
        $GLOBALS['first_hold_ob05'] = new FirstGlobalOwnerOB05;
        return $bytes;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new GlobalFinalOB05, 0);
echo 'T|';
