<?php
#[Deprecated] const X = [];
class Receiver192 {}
$original = function($value = X) { echo 'B|'; throw new Exception('body'); };
$fn = $original->bindTo(new Receiver192(), Receiver192::class); $original = null;
set_error_handler(function() { echo 'H|'; return true; });
try { $fn(); } catch (Exception $e) { echo 'C|'; }
try { $fn(); } catch (Exception $e) { echo 'C|'; }
$copy = clone $fn; $fn = null;
try { $copy(); } catch (Exception $e) { echo 'C|'; }
