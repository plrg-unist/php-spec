<?php
gc_disable();
$leaf = new stdClass;
$leaf2 = new stdClass;
$token = [];
$token[0] = $leaf;
$token[1] = $leaf2;
$collector = static function () use ($token) {
    $leafCopy = $token[0];
    $leafCopy2 = $token[1];
    echo 'P|', gc_collect_cycles(), '|';
    $roots0 = gc_status()['roots'];
    $copy = $token;
    unset($copy);
    $roots1 = gc_status()['roots'];
    unset($leafCopy);
    $roots2 = gc_status()['roots'];
    unset($leafCopy2);
    $roots3 = gc_status()['roots'];
    echo 'R|', $roots0, '|', $roots1, '|', $roots2, '|', $roots3, '|',
        ($token[0] !== null && $token[1] !== null ? 'live' : 'BAD');
};
$collector();
