<?php
function gc69TargetPeer() {}
class GC69ChildPeer {
    public function __destruct() {
        global $parentWatch;
        echo 'C|', (int) ($parentWatch->get() !== null), '|';
    }
}
class GC69ParentPeer {
    public $left;
    public $marker = 17;
    public $right;
    public function __destruct() {
        global $childWatch;
        echo 'P|', (int) ($childWatch->get() === $this->left), '|',
             (int) ($this->left === $this->right), '|',
             (int) ($this->marker === 17), '|';
    }
}
class GC69OldNamePeer {
    public function __destruct() {
        global $name, $parentWatch, $childWatch;
        $child = new GC69ChildPeer;
        $name = new GC69ParentPeer;
        $name->left = $child;
        $name->right = $child;
        $parentWatch = WeakReference::create($name);
        $childWatch = WeakReference::create($child);
        unset($child);
        echo 'O|';
    }
}
$name = new GC69OldNamePeer;
$ok = is_callable('gc69TargetPeer', false, $name);
echo 'N|', $ok, '|', $name, '|',
     (int) ($parentWatch->get() !== null), '|',
     (int) ($childWatch->get() !== null), '|';
$recovered = $parentWatch->get();
echo 'R|', (int) ($recovered->left === $recovered->right), '|',
     (int) ($recovered->marker === 17), '|';
unset($recovered, $name);
echo 'U|', (int) ($parentWatch->get() !== null), '|',
     (int) ($childWatch->get() !== null), '|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|', (int) ($parentWatch->get() !== null), '|',
     (int) ($childWatch->get() !== null), '|';
register_shutdown_function(function () {
    global $parentWatch, $childWatch;
    echo 'S|', (int) ($parentWatch->get() !== null), '|',
         (int) ($childWatch->get() !== null), '|';
});
echo 'E|';
