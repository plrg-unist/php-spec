<?php
function itemRefTarget72() {}
class ItemRefChild72 {
    public function __destruct() { echo 'D|'; }
}
class ItemRefOldName72 {
    public function __destruct() {
        global $name, $kept, $watch;
        $child = new ItemRefChild72;
        $name = [17, $child];
        $kept = $name;
        $watch = WeakReference::create($child);
        unset($child);
        echo 'O|';
    }
}
$kept = $watch = $ref = null;
$name = new ItemRefOldName72;
echo 'B|';
$ok = is_callable('itemRefTarget72', false, $name);
echo 'N|', (int) $ok, '|', $name, '|', (int) ($watch->get() !== null), '|';
$ref =& $kept[1];
echo 'R|';
$ref = 23;
echo 'W|', $kept[1], '|', (int) ($watch->get() !== null), '|';
unset($ref);
echo 'V|', $kept[1], '|';
unset($kept, $name);
echo 'U|', (int) ($watch->get() !== null), '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', (int) ($watch->get() !== null), '|';
register_shutdown_function(function () {
    global $watch;
    echo 'S|', (int) ($watch->get() !== null), '|';
});
echo 'E|';
