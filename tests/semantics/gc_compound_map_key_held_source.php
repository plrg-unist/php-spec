<?php
class GcCompoundMapHeldOwn33 { public function __destruct() { echo 'OWN|'; } }
class GcCompoundMapHeldIncoming33 { public function __destruct() { echo 'INCOMING|'; } }
class GcCompoundMapHeldSetup33 {
    public function __destruct() {
        echo 'D1|';
        $outer = new WeakMap;
        $incoming = new GcCompoundMapHeldIncoming33;
        $own = new GcCompoundMapHeldOwn33;
        $outgoingKey = new stdClass;
        $inner = new WeakMap;
        $inner[$outgoingKey] = $own;
        $outer[$inner] = $incoming;
        $GLOBALS['compoundOuterMap33'] = $outer;
        $GLOBALS['compoundInnerMap33'] = $inner;
        $GLOBALS['compoundOutgoingKey33'] = $outgoingKey;
        $GLOBALS['compoundHeldOwn33'] = $own;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundMapHeldSetup33);
    return 'F' . $bytes;
});
echo 'X|';
