<?php
class GC34Recreate { public function __construct(public stdClass $target, public WeakReference $watch) {} public function __destruct() { echo 'V|',(int)($this->watch->get() === null),'|'; $GLOBALS['newWR34'] = WeakReference::create($this->target); echo (int)($GLOBALS['newWR34']->get() === $this->target),'|'; } }
$t = new stdClass; $key = WeakReference::create($t); $watch = WeakReference::create($key); $map = new WeakMap; $map[$key] = new GC34Recreate($t, $watch); echo 'B|'; unset($key); echo 'A|',(int)($GLOBALS['newWR34']->get() === $t),'|',(int)($watch->get() === null),'|';
