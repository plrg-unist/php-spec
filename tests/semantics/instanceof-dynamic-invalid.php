<?php
$invalid = [7];
$answer = 42;
echo "X:";
try { $answer = $undefinedLeft instanceof $invalid; }
catch (Error $caught) {
    echo "C|"; echo $answer; echo "|";
    echo $caught->getMessage(); echo "|";
}
$left = 7;
try { $answer = $left instanceof $invalid; }
catch (Error $caught) { echo "C|"; echo $answer; echo "|"; }
echo "E|";
