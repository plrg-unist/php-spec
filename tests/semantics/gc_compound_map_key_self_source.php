<?php
class GcCompoundSelfValue33 {}
class GcCompoundSelfSetup33 {
    public function __destruct() {
        echo 'D1|';
        $map = new WeakMap;
        $map[$map] = new GcCompoundSelfValue33;
        $GLOBALS['compoundSelfMap33'] = $map;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundSelfSetup33);
    return 'F' . $bytes;
});
echo 'X|';
