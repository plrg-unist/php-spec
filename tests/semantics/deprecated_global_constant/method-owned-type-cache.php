<?php
#[Deprecated] const X = [];
class Base187 { public static function receive(int $value = X) { echo 'BAD|'; } }
class Child187 extends Base187 {}
set_error_handler(function($level, $message) { echo 'H|'; return true; });
try { Child187::receive(); } catch (TypeError $e) { echo 'T|'; }
try { Base187::receive(); } catch (TypeError $e) { echo 'T|'; }
