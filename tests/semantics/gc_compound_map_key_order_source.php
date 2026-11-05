<?php
class GcCompoundMapOwn33 { public function __destruct() { echo 'OWN|'; } }
class GcCompoundMapIncoming33 { public function __destruct() { echo 'INCOMING|'; } }
class GcCompoundMapOrderSetup33 {
    public function __destruct() {
        echo 'D1|';
        $outer = new WeakMap;
        $incoming = new GcCompoundMapIncoming33;
        $own = new GcCompoundMapOwn33;
        $outgoingKey = new stdClass;
        $inner = new WeakMap;
        $inner[$outgoingKey] = $own;
        $outer[$inner] = $incoming;
        $GLOBALS['compoundOuterMap33'] = $outer;
        $GLOBALS['compoundInnerMap33'] = $inner;
        $GLOBALS['compoundOutgoingKey33'] = $outgoingKey;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundMapOrderSetup33);
    return 'F' . $bytes;
});
echo 'X|';
