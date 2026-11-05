<?php
class GcCompoundWeakIncoming33 { public function __destruct() { echo 'INCOMING|'; } }
class GcCompoundWeakNotifySetup33 {
    public function __destruct() {
        echo 'D1|';
        $map = new WeakMap;
        $value = new GcCompoundWeakIncoming33;
        $target = new stdClass;
        $key = WeakReference::create($target);
        $map[$key] = $value;
        $GLOBALS['compoundWeakNotifyMap33'] = $map;
        $GLOBALS['compoundWeakNotifyTarget33'] = $target;
        $GLOBALS['compoundWeakNotifyKey33'] = $key;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcCompoundWeakNotifySetup33);
    return 'F' . $bytes;
});
echo 'X|';
