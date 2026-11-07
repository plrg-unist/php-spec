<?php
class BaseAPI213 {
    #[\Deprecated]
    public const VALUE = 7;
}
class ChildAPI213 extends BaseAPI213 {}
interface InterfaceAPI213 {
    #[\Deprecated]
    public const VALUE = 8;
}
interface DerivedAPI213 extends InterfaceAPI213 {}
class ImplementerAPI213 implements DerivedAPI213 {}
function noticeAPI213($level, $message, $file, $line) {
    echo 'H|', $message, '|', $line, '|';
    echo $file === __FILE__ ? 'F|' : 'BAD|';
    echo $level, '|';
    return true;
}
set_error_handler('noticeAPI213');
echo \defined('BaseAPI213::VALUE'), '|';
echo \constant('BaseAPI213::VALUE'), '|';
echo \constant('ChildAPI213::VALUE'), '|';
echo \constant('InterfaceAPI213::VALUE'), '|';
echo \constant('DerivedAPI213::VALUE'), '|';
echo \constant('ImplementerAPI213::VALUE'), '|';
restore_error_handler();
echo 'Z|';
