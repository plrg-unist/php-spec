<?php
function lostRcTarget() {}
class LostRcChild {
    public function __destruct() { echo 'D|'; }
}
class OldQueryName {
    public function __destruct() {
        global $name, $watch;
        $name = new LostRcChild;
        $watch = WeakReference::create($name);
        echo 'O|';
    }
}
$watch = null;
$name = new OldQueryName;
$ok = is_callable('lostRcTarget', false, $name);
echo 'N|', $ok, '|', $name, '|', $watch->get() !== null, '|';
unset($name);
echo 'U|', $watch->get() !== null, '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', $watch->get() !== null, '|';
register_shutdown_function(function () {
    global $watch;
    echo 'S|', $watch->get() !== null, '|';
});
echo 'E|';
