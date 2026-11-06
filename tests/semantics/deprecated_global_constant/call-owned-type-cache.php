<?php
#[Deprecated] const X = [];
class Receiver191 {}
$receiver = new Receiver191();
$fn = function(int $value = X) { echo 'BAD|'; };
set_error_handler(function() { echo 'H|'; return true; });
try { $fn->call($receiver); } catch (TypeError $e) { echo 'T|'; }
try { $fn->call($receiver); } catch (TypeError $e) { echo 'T|'; }
try { $fn(); } catch (TypeError $e) { echo 'T|'; }
try { $fn(); } catch (TypeError $e) { echo 'T|'; }
