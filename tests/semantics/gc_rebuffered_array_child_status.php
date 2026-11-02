<?php
gc_disable();
$leaf = new stdClass;
$token = [];
$token[0] = $leaf;
$collector = static function () use ($token) {
    echo 'P|', gc_collect_cycles(), '|';
    $before = gc_status();
    $roots0 = $before['roots'];
    $copy = $token;
    unset($copy);
    $after = gc_status();
    $roots1 = $after['roots'];
    echo 'R|', $roots0, '|', $roots1, '|',
        ($token[0] !== null ? 'live' : 'BAD');
};
$collector();
