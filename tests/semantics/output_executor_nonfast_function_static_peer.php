<?php
class FirstStaticOwnerOB05 {
    public function __destruct() {
        $GLOBALS['static_stage_ob05'] = 'first-entered';
        echo 'BAD-FIRST|';
    }
}
class SecondStaticOwnerOB05 {
    public function __destruct() {
        $GLOBALS['static_stage_ob05'] = 'second-entered';
        echo 'BAD-SECOND|';
    }
}
function firstStaticHoldOB05() {
    static $held = null;
    $held = new FirstStaticOwnerOB05;
}
function secondStaticHoldOB05() {
    static $held = null;
    $held = new SecondStaticOwnerOB05;
}
class StaticObserverOB05 {
    public function __destruct() {
        echo 'A:', $GLOBALS['static_stage_ob05'], '|';
    }
}
class StaticFinalOB05 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new StaticObserverOB05;
        $GLOBALS['static_stage_ob05'] = 'live';
        secondStaticHoldOB05();
        firstStaticHoldOB05();
        return $bytes;
    }
}
ob_start(null, 0);
echo 'B|';
ob_start(new StaticFinalOB05, 0);
echo 'T|';
