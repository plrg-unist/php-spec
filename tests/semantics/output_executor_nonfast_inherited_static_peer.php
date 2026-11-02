<?php
class FirstInheritedStaticOwnerOB05 {
    public function __destruct() {
        $GLOBALS['inherited_static_stage_ob05'] = 'first-entered';
        echo 'BAD-FIRST|';
    }
}
class SecondInheritedStaticOwnerOB05 {
    public function __destruct() {
        $GLOBALS['inherited_static_stage_ob05'] = 'second-entered';
        echo 'BAD-SECOND|';
    }
}
class ParentStaticHoldOB05 {
    public static function hold() {
        static $held = null;
        $held = new FirstInheritedStaticOwnerOB05;
    }
}
class MiddleStaticHoldOB05 {
    public static function hold() {
        static $held = null;
        $held = new SecondInheritedStaticOwnerOB05;
    }
}
class InheritedStaticObserverOB05 {
    public function __destruct() {
        echo 'A:', $GLOBALS['inherited_static_stage_ob05'], '|';
    }
}
class InheritedStaticFinalOB05 {
    public $after = null;
    public function __invoke(string $bytes, int $phase): string {
        $this->after = new InheritedStaticObserverOB05;
        $GLOBALS['inherited_static_stage_ob05'] = 'live';
        ParentStaticHoldOB05::hold();
        MiddleStaticHoldOB05::hold();
        return $bytes;
    }
}
class LastStaticChildOB05 extends ParentStaticHoldOB05 {}
ob_start(null, 0);
echo 'B|';
ob_start(new InheritedStaticFinalOB05, 0);
echo 'T|';
