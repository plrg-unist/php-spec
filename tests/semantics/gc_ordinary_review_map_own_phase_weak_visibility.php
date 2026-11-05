<?php
class GC34OwnView { public function __construct(public WeakReference $weak) {} public function __destruct() { echo 'OWN|',(int)($this->weak->get() !== null),'|'; } }
class GC34IncomingView { public function __destruct() { echo 'IN|'; } }
$map = new WeakMap; $watch = WeakReference::create($map); $key = new stdClass; $outer = new WeakMap; $outer[$map] = new GC34IncomingView; $map[$key] = new GC34OwnView($watch); echo 'B|'; unset($map); echo 'A|',(int)($watch->get() === null),'|',count($outer),'|';
