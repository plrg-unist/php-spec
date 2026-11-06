<?php
#[Deprecated] const X = [];
#[Deprecated] const Y = [1];
$cached = Closure::bind(function(int $value = X) { echo 'BAD|'; }, null);
$nonempty = Closure::bind(function(int $value = Y) { echo 'BAD|'; }, null, null);
set_error_handler(function() { echo 'H|'; return true; });
try { $cached(); } catch (TypeError $e) { echo 'T|'; }
try { $cached(); } catch (TypeError $e) { echo 'T|'; }
try { $nonempty(); } catch (TypeError $e) { echo 'T|'; }
try { $nonempty(); } catch (TypeError $e) { echo 'T|'; }
