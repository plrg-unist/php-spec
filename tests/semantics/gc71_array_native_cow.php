<?php
function arrayCowTarget71() {}
class ArrayCowChild71 {
    public function __destruct() { echo 'D|'; }
}
class ArrayCowOldName71 {
    public function __destruct() {
        global $name, $kept, $watch;
        $child = new ArrayCowChild71;
        $name = [17, $child];
        $kept = $name;
        $watch = WeakReference::create($child);
        unset($child);
        echo 'O|';
    }
}
$kept = $watch = null;
$name = new ArrayCowOldName71;
echo 'B|';
$ok = is_callable('arrayCowTarget71', false, $name);
echo 'N|', $ok, '|', $name, '|', $watch->get() !== null, '|';
$kept[1] = 23;
echo 'W|', $kept[0], '|', $kept[1], '|', $watch->get() !== null, '|';
unset($kept, $name);
echo 'U|', $watch->get() !== null, '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', $watch->get() !== null, '|';
register_shutdown_function(function () {
    global $watch;
    echo 'S|', $watch->get() !== null, '|';
});
echo 'E|';
