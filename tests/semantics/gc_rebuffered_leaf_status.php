<?php
gc_disable();
$token = new stdClass;
$collector = static function () use ($token) {
    echo 'P|', gc_collect_cycles(), '|';
    $before = gc_status();
    $roots0 = $before['roots'];
    $copy = $token;
    unset($copy);
    $after = gc_status();
    $roots1 = $after['roots'];
    echo 'R|', $roots0, '|', $roots1, '|',
        ($token instanceof stdClass ? 'live' : 'BAD');
};
unset($token);
$collector();
