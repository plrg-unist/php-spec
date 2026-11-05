<?php
class GcWeakChainLate30 {
    public function __destruct() {
        echo 'D1|';
        $parent = new stdClass;
        $weak = WeakReference::create($parent);
        $same = WeakReference::create($parent);
        $chain = WeakReference::create($weak);
        echo $same === $weak ? 'same|' : 'BAD|';
        echo $chain->get() === $weak ? 'chain|' : 'BAD|';
        $retired = new stdClass;
        $dead = WeakReference::create($retired);
        unset($retired);
        echo $dead->get() === null ? 'dead|' : 'BAD|';
        $GLOBALS['chainParent30'] = $parent;
        $GLOBALS['chainWeak30'] = $weak;
        $GLOBALS['chainAlias30'] = $same;
        $GLOBALS['chainObserver30'] = $chain;
        $GLOBALS['chainDead30'] = $dead;
        echo 'D2|';
    }
}
ob_start(static function ($bytes, $phase) {
    register_shutdown_function(static function () {}, new GcWeakChainLate30);
    return 'F' . $bytes;
});
echo 'X|';
