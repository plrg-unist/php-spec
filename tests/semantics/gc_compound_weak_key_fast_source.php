<?php
class GcCompoundWeakField33 { public function __destruct() { echo 'FIELD|'; } }
class GcCompoundWeakFastSetup33 {
    public function __destruct() {
        echo 'D1|';
        $map = new WeakMap;
        $field = new GcCompoundWeakField33;
        $target = new stdClass;
        $target->field = $field;
        $key = WeakReference::create($target);
        $map[$key] = 7;
        $GLOBALS['compoundWeakFastMap33'] = $map;
        $GLOBALS['compoundWeakFastTarget33'] = $target;
        $GLOBALS['compoundWeakFastKey33'] = $key;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundWeakFastSetup33);
    return 'F' . $bytes;
});
echo 'X|';
