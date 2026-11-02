<?php
gc_disable();
$leaf = new stdClass;
$weak = WeakReference::create($leaf);
$token = [];
$token[0] = $leaf;
$token[1] = $leaf;
$collector = static function () use ($token) { return $token[0] === $token[1]; };
echo 'R|', gc_status()['roots'], '|';
unset($leaf);
echo gc_status()['roots'], '|';
unset($token);
echo gc_status()['roots'], '|';
echo 'C|', gc_collect_cycles(), '|', gc_status()['roots'], '|';
echo $collector() && $weak->get() !== null ? 'live|' : 'BAD|';
unset($collector);
echo $weak->get() === null ? 'dead' : 'BAD';
