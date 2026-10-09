<?php
function argument() { echo "ARG;"; }
class A {}
echo "PRE;";
try { A::__construct(argument()); }
catch (Error $ex) { echo "LITERAL:", $ex->getMessage(), ";"; }
$method = "__construct";
try { A::$method(argument()); }
catch (Error $ex) { echo "DYNAMIC:", $ex->getMessage(), ";"; }
echo "POST;";
