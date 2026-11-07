<?php
class GC78ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
class GC78OldAuthor {
    public function __destruct() {
        global $name, $kept;
        $kept = [17, new GC78ChildAuthor];
        $name = $kept;
        echo 'O|';
    }
}
function gc78AvailableAuthor() {}
$kept = null;
$name = new GC78OldAuthor;
echo 'B|';
$ok = is_callable('gc78AvailableAuthor', false, $name);
echo 'N|', (int) $ok, '|', $name, '|';
$view = $kept;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$kept[0] = 23;
echo 'W|', $view[0], '|', $kept[0], '|';
unset($kept);
echo 'K|';
unset($view, $name);
echo 'V|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
