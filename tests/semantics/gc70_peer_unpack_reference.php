<?php
function gc70TargetPeer() {}
class GC70ParentPeer {
    public $quiet = 17;
    public function __destruct() { echo 'D|', $this->quiet, '|'; }
}
class GC70OldNamePeer {
    public function __destruct() {
        global $name, $watch;
        $name = new GC70ParentPeer;
        $watch = WeakReference::create($name);
        echo 'O|';
    }
}
$name = new GC70OldNamePeer;
$ok = is_callable('gc70TargetPeer', false, $name);
$parent = $watch->get();
$ref = 17;
$parent->quiet =& $ref;
unset($parent);
$array = [&$ref];
unset($ref);
echo 'B|', $ok, '|', $array[0], '|';
$copy = [...$array];
$copy[0] = 23;
echo 'A|', $array[0], '|', $copy[0], '|', $watch->get()->quiet, '|';
unset($copy, $array, $name);
echo 'E|';
