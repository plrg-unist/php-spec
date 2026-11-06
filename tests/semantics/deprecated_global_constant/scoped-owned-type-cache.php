<?php
#[Deprecated] const X = [];
class Receiver192 {}
$original = function(int $value = X) { echo 'BAD|'; };
$fn = $original->bindTo(new Receiver192(), Receiver192::class); $original = null;
set_error_handler(function() { echo 'H|'; return true; });
try { $fn(); } catch (TypeError $e) { echo 'T|'; }
try { $fn(); } catch (TypeError $e) { echo 'T|'; }
$copy = clone $fn; $fn = null;
try { $copy(); } catch (TypeError $e) { echo 'T|'; }
