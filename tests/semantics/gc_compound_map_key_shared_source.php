<?php
class GcCompoundSharedValue33 {}
class GcCompoundSharedSetup33 {
    public function __destruct() {
        echo 'D1|';
        $outer = new WeakMap;
        $value = new GcCompoundSharedValue33;
        $plain = new stdClass;
        $inner = new WeakMap;
        $inner[$plain] = $value;
        $outer[$inner] = $value;
        $GLOBALS['compoundSharedOuter33'] = $outer;
        $GLOBALS['compoundSharedInner33'] = $inner;
        $GLOBALS['compoundSharedPlain33'] = $plain;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundSharedSetup33);
    return 'F' . $bytes;
});
echo 'X|';
