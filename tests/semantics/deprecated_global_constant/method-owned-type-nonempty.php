<?php
#[Deprecated] const X = [1];
class Receiver187 { public function receive(int $value = X) { echo 'BAD|'; } }
$receiver = new Receiver187();
set_error_handler(function($level, $message) { echo 'H|'; return true; });
try { $receiver->receive(); } catch (TypeError $e) { echo 'T|'; }
try { $receiver->receive(); } catch (TypeError $e) { echo 'T|'; }
