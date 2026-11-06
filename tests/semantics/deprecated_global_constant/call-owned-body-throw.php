<?php
#[Deprecated] const X = [];
class Receiver191 {}
$receiver = new Receiver191();
$fn = function($value = X) { echo 'B|'; throw new Exception('body'); };
set_error_handler(function() { echo 'H|'; return true; });
try { $fn->call($receiver); } catch (Exception $e) { echo 'C|'; }
try { $fn->call($receiver); } catch (Exception $e) { echo 'C|'; }
