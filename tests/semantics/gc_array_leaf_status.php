<?php
gc_disable();
$token = [];
$token[0] = 11;
$collector = static function () use ($token) { return $token[0]; };
echo 'P|', gc_collect_cycles(), '|';
$before = gc_status();
$roots0 = $before['roots'];
$copy = $token;
unset($copy);
$after = gc_status();
$roots1 = $after['roots'];
echo 'R|', $roots0, '|', $roots1, '|',
    ($collector() === 11 ? 'live' : 'BAD');
