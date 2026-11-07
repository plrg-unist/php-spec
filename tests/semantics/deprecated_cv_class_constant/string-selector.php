<?php
namespace Ns221Select;
class Base221 {
    #[\Deprecated]
    public const C = 7;
}
class Child221 extends Base221 {}
class Other221 extends Base221 {
    #[\Deprecated]
    public const C = 9;
}
function notice221($level, $message) {
    echo $message, '|', $level, '|';
    $GLOBALS['selector221'] = 'Ns221Select\\Other221';
    return true;
}
\set_error_handler('Ns221Select\\notice221');
$selector221 = 'nS221SeLeCt\\cHiLd221';
echo $selector221::C, '|';
echo $selector221::C, '|';
echo Base221::C, '|Z|';
