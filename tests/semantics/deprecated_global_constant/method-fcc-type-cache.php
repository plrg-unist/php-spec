<?php
#[Deprecated] const X = [];
class Receiver193 { function read(int $value = X) { echo 'BAD|'; } }
$receiver = new Receiver193(); $fn = Closure::fromCallable([$receiver, 'read']);
set_error_handler(function() { echo 'H|'; return true; });
try { $fn(); } catch (TypeError $e) { echo 'T|'; }
try { $fn(); } catch (TypeError $e) { echo 'T|'; }
$copy = clone $fn;
try { $copy(); } catch (TypeError $e) { echo 'T|'; }
try { $receiver->read(); } catch (TypeError $e) { echo 'T|'; }
