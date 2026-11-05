<?php
class GcNotifyAliasValue32 {}
class GcNotifyAliasLate32 {
    public function __destruct() {
        echo "D1|";
        $map = new WeakMap;
        $key = new stdClass;
        $value = new GcNotifyAliasValue32;
        $map[$key] = $value;
        foreach ($map as $loopKey => &$alias) {}
        $GLOBALS['notifyAliasMap32'] = $map;
        $GLOBALS['notifyAliasKey32'] = $key;
        $GLOBALS['notifyAlias32'] =& $alias;
        echo $alias === $value ? "same|" : "BAD|";
        echo "D2|";
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcNotifyAliasLate32);
    return "F" . $bytes;
});
echo "X|";
