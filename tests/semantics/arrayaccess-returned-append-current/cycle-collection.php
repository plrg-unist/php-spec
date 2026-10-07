<?php
class LinkGC18 {
    public $next;
    public function __destruct() {
        echo "L;";
        $GLOBALS['aliasGC18'] = 25;
        $GLOBALS['rhsGC18'] =& $GLOBALS['newGC18'];
    }
}
class ChildGC18 implements ArrayAccess {
    public $next;
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed { echo "wrongGet;"; return null; }
    public function offsetSet($key, $value): void {
        echo "S:", (int) ($key === null), ":", $value, ";";
        $count = gc_collect_cycles();
        echo "K:", $count, ";H:", (int) ($GLOBALS['weakGC18']->get() === $this), ";";
    }
    public function offsetUnset($key): void { echo "wrongUnset;"; }
    public function __destruct() { echo "C;"; }
}
class OuterGC18 implements ArrayAccess {
    public function offsetExists($key): bool { return true; }
    public function offsetGet($key): mixed {
        echo "G;";
        $child = new ChildGC18();
        $child->next = $child;
        $GLOBALS['weakGC18'] = WeakReference::create($child);
        return $child;
    }
    public function offsetSet($key, $value): void { echo "wrongOuter;"; }
    public function offsetUnset($key): void {}
}
$rhsGC18 = 11;
$aliasGC18 =& $rhsGC18;
$newGC18 = 31;
$link = new LinkGC18();
$link->next = $link;
unset($link);
$outer = new OuterGC18();
$read = ($outer['root'][] = $rhsGC18);
echo "R:", $read, ";";
$count = gc_collect_cycles();
echo "N:", $count, ";E:", (int) ($weakGC18->get() === null), ":", $aliasGC18, ":", $rhsGC18, ";";
