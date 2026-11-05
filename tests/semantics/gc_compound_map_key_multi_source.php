<?php
class GcCompoundMultiValue33 {}
class GcCompoundMultiSetup33 {
    public function __destruct() {
        echo 'D1|';
        $outer = new WeakMap;
        $value = new GcCompoundMultiValue33;
        $plain = new stdClass;
        $second = new stdClass;
        $inner = new WeakMap;
        $inner[$plain] = $value;
        $inner[$second] = $value;
        $outer[$inner] = $value;
        $GLOBALS['compoundMultiOuter33'] = $outer;
        $GLOBALS['compoundMultiInner33'] = $inner;
        $GLOBALS['compoundMultiPlain33'] = $plain;
        $GLOBALS['compoundMultiSecond33'] = $second;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundMultiSetup33);
    return 'F' . $bytes;
});
echo 'X|';
