<?php
interface ArrayAPI214 {
    #[\Deprecated]
    public const EMPTY = [];
    #[\Deprecated]
    public const TREE = [[]];
}
interface DerivedArrayAPI214 extends ArrayAPI214 {}
class ImplementerArrayAPI214 implements DerivedArrayAPI214 {}
function noticeArrayAPI214($level, $message, $file, $line) {
    echo 'H|';
    if ($message === 'Constant ArrayAPI214::EMPTY is deprecated') {
        $copy = DerivedArrayAPI214::EMPTY;
        $copy[] = 9;
        echo $copy[0], '|';
    } else {
        $copy = ImplementerArrayAPI214::TREE;
        $copy[0][] = 9;
        echo $copy[0][0], '|';
    }
    return true;
}
set_error_handler('noticeArrayAPI214');
$empty = \constant('ImplementerArrayAPI214::EMPTY');
echo $empty === [] ? 'E|' : 'BAD|';
$empty[] = 7;
$again = \constant('DerivedArrayAPI214::EMPTY');
echo $again === [] ? 'E|' : 'BAD|';
$tree = \constant('DerivedArrayAPI214::TREE');
echo $tree[0] === [] ? 'E|' : 'BAD|';
$tree[0][] = 7;
echo $tree[0][0], '|';
$alias = \constant('ImplementerArrayAPI214::TREE');
echo $alias[0] === [] ? 'E|' : 'BAD|';
restore_error_handler();
echo 'Z|';
