<?php
namespace Ns217Interface;
const DONOR = [1];
interface Base217 {
    #[\Deprecated]
    public const FIRST = 7, SECOND = \Ns217Interface\DONOR;
}
interface Child217 extends Base217 {}
class Implementer217 implements Child217 {}
function notice217($level, $message) {
    echo $message === 'Constant Ns217Interface\\Base217::FIRST is deprecated' ? 'F|' :
        ($message === 'Constant Ns217Interface\\Base217::SECOND is deprecated' ? 'S|' : 'BAD|');
    return true;
}
set_error_handler('Ns217Interface\\notice217');
echo Child217::FIRST, '|';
$first = Implementer217::SECOND;
$first[0] = 9;
echo $first[0], '|';
$second = Child217::SECOND;
echo $second[0], '|';
echo Implementer217::FIRST, '|';
restore_error_handler();
echo 'Z|';
