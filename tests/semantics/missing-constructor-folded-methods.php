<?php
function argument() { echo "ARG;"; }
class A {}
try { A::__CoNsTrUcT(argument()); }
catch (Error $ex) { echo "IDENTIFIER:", $ex->getMessage(), ";"; }
try { A::{"__CoNsTrUcT"}(argument()); }
catch (Error $ex) { echo "STRING:", $ex->getMessage(), ";"; }
try { A::{"__con"."struct"}(argument()); }
catch (Error $ex) { echo "CONCAT:", $ex->getMessage(), ";"; }
$method = "__CoNsTrUcT";
try { A::$method(argument()); }
catch (Error $ex) { echo "DYNAMIC:", $ex->getMessage(), ";"; }
$class = "A";
try { $class::__construct(argument()); }
catch (Error $ex) { echo "CLASSCV:", $ex->getMessage(), ";"; }
try { MissingClass::__construct(argument()); }
catch (Error $ex) { echo "CLASS:", $ex->getMessage(), ";"; }
try { A::missing(argument()); }
catch (Error $ex) { echo "METHOD:", $ex->getMessage(), ";"; }
