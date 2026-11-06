<?php
#[Deprecated] const X = [];
function make188() { return function(int $value = X) { echo 'BAD|'; }; }
set_error_handler(function() { echo 'H|'; return true; });
$a = make188();
try { $a(); } catch (TypeError $e) { echo 'T|'; }
$b = make188();
try { $b(); } catch (TypeError $e) { echo 'T|'; }
$c = clone $a;
try { $c(); } catch (TypeError $e) { echo 'T|'; }
