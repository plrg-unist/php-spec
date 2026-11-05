<?php
class GcMapPayload31 {}
class GcMapAliasLate31 {
    public function __destruct() {
        echo 'D1|';
        $key = new stdClass;
        $value = new GcMapPayload31;
        $map = new WeakMap;
        $map[$key] = $value;
        foreach ($map as $loopKey => &$alias) {}
        $GLOBALS['mapKey31'] = $key;
        $GLOBALS['mapAlias31'] =& $alias;
        $GLOBALS['map31'] = $map;
        $GLOBALS['emptyMap31'] = new WeakMap;
        echo $alias === $value ? 'alias|' : 'BAD|';
        unset($value);
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcMapAliasLate31);
    return 'F' . $bytes;
});
echo 'X|';
