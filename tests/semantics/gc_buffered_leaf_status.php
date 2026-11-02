<?php
gc_disable();
$token = new stdClass;
$collector = static function () use ($token) { return $token; };
$status0 = gc_status();
$roots0 = $status0['roots'];
$status1 = gc_status();
$roots1 = $status1['roots'];
unset($token);
$status2 = gc_status();
$roots2 = $status2['roots'];
echo 'R|', $roots0, '|', $roots1, '|', $roots2, '|',
    ($collector() instanceof stdClass ? 'live' : 'BAD');
