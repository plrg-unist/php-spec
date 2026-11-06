<?php
function singletonAliasTarget73() {}
class SingletonAliasChild73 {
    public function __destruct() { echo 'D|'; }
}
class SingletonAliasOldName73 {
    public function __destruct() {
        global $name, $kept, $watch, $slot;
        $slot = 17;
        $child = new SingletonAliasChild73;
        $name = [&$slot, $child];
        $kept = $name;
        $watch = WeakReference::create($child);
        unset($child);
        echo 'O|';
    }
}
$kept = $watch = $slot = null;
$name = new SingletonAliasOldName73;
echo 'B|';
$ok = is_callable('singletonAliasTarget73', false, $name);
echo 'N|', (int) $ok, '|', $name, '|';
unset($slot);
$kept[0] = 23;
echo 'W|', $kept[0], '|', (int) ($watch->get() !== null), '|';
unset($kept, $name);
echo 'U|', (int) ($watch->get() !== null), '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', (int) ($watch->get() !== null), '|';
register_shutdown_function(function () {
    global $watch;
    echo 'S|', (int) ($watch->get() !== null), '|';
});
echo 'E|';
