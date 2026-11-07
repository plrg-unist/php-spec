<?php
namespace Ns233Host;
function member233(): string {
    echo 'M|';
    eval('namespace Ns233Late; class Target233 { #[\Deprecated] public const VALUE = 7; }');
    return 'VALUE';
}
function notice233($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns233Late\\Target233::VALUE is deprecated' ? 'H|' : 'BAD|';
    return true;
}
\set_error_handler('Ns233Host\\notice233');
echo 'B|';
$value233 = ('Ns233Late\\Tar' . 'get233')::{\Ns233Host\member233()};
echo 'O|', $value233, '|';
$again233 = \Ns233Late\Target233::VALUE;
echo 'W|', $again233, '|Z|';
