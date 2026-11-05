<?php
class GcCompoundCrossValue33 {}
class GcCompoundCrossSetup33 {
    public function __destruct() {
        echo 'D1|';
        $outer = new WeakMap;
        $other = new WeakMap;
        $value = new GcCompoundCrossValue33;
        $plain = new stdClass;
        $second = new stdClass;
        $inner = new WeakMap;
        $inner[$plain] = $value;
        $inner[$second] = $value;
        $other[$inner] = $value;
        $outer[$inner] = $value;
        $GLOBALS['compoundCrossOuter33'] = $outer;
        $GLOBALS['compoundCrossOther33'] = $other;
        $GLOBALS['compoundCrossInner33'] = $inner;
        $GLOBALS['compoundCrossPlain33'] = $plain;
        $GLOBALS['compoundCrossSecond33'] = $second;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundCrossSetup33);
    return 'F' . $bytes;
});
echo 'X|';
