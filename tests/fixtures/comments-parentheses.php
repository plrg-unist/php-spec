<?php
$result = /* before parentheses */ ($left + $right);
$result = (/* inside outer parentheses */ (/* inside inner parentheses */ $left));
$result = $left /* before operator */ + $right;
emptyCall /* before empty argument list */ ();
$result /* before semicolon */;
