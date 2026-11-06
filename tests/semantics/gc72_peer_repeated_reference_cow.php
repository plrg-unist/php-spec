<?php
function gc72TargetPeer() {}
class GC72ChildPeer {
    public function __destruct() { echo 'D|'; }
}
class GC72OldNamePeer {
    public function __destruct() {
        global $name, $kept, $watch;
        $child = new GC72ChildPeer;
        $watch = WeakReference::create($child);
        $kept = [$child, 17, $child];
        $name = $kept;
        unset($child);
        echo 'O|';
    }
}
$name = new GC72OldNamePeer;
$ok = is_callable('gc72TargetPeer', false, $name);
echo 'B|', $ok, '|', $name, '|', (int) ($watch->get() !== null), '|';
$ref =& $kept[0];
echo 'A|', (int) ($ref === $kept[2]), '|',
     (int) ($watch->get() === $ref), '|';
$ref = 29;
echo 'R|', $ref, '|', (int) ($watch->get() !== null), '|';
$kept[2] = 31;
echo 'W|', $kept[2], '|', (int) ($watch->get() !== null), '|';
unset($ref);
echo 'C|', $kept[0], '|', (int) ($watch->get() !== null), '|';
unset($kept, $name);
echo 'U|', (int) ($watch->get() !== null), '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', (int) ($watch->get() !== null), '|';
register_shutdown_function(function () {
    global $watch;
    echo 'S|', (int) ($watch->get() !== null), '|';
});
echo 'E|';
