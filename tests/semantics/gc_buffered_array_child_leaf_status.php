<?php
gc_disable();
$leaf = new stdClass;
$token = [];
$token[0] = $leaf;
$collector = static function () use ($token) {
    $leafCopy = $token[0];
    echo 'P|', gc_collect_cycles(), '|';
    $roots0 = gc_status()['roots'];
    $copy = $token;
    unset($copy);
    $roots1 = gc_status()['roots'];
    unset($leafCopy);
    $roots2 = gc_status()['roots'];
    echo 'R|', $roots0, '|', $roots1, '|', $roots2, '|',
        ($token[0] !== null ? 'live' : 'BAD');
};
$collector();
