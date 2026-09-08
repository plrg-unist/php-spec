<?php
/* Empty statement keeps its own comment. */ ;
function /* function name */ commentFunction(
    /* parameter */ int /* variable */ $value = /* default */ 1
): /* return type */ int {
    $value = (/* nested operand */ $value) + /* right operand */ 1;
    if ($value) { echo /* echo operand */ $value; }
    /* elseif */ elseif (false) { }
    /* else */ else { }
    return /* return operand */ $value;
}
interface /* interface name */ CommentInterface { }
class /* class name */ CommentClass implements /* interface reference */ CommentInterface {
    public const /* constant */ FIRST = 1, /* next constant */ SECOND = 2;
    public int /* property */ $first = 1, /** second property */ $second = 2;
    public function /* method */ method(): void {
        self::/* static property */$first;
        $this->/* member */method();
        // trailing method comment
    }
    /**

       A doc comment with a deliberately blank first line.

    */
}
$anonymous = new /* anonymous class */ class { };
$result = (/* callable */ $callable)();
$value = (/* dereference base */ $array)[0];
/*
	Mixed tab indentation
    and space indentation remain distinct.
*/
echo 1;
/* Trailing file comment. */
