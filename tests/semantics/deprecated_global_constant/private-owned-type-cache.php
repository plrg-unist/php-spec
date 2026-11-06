<?php
#[Deprecated] const X = [];
#[Deprecated] const Y = [1];
class Scope190 {}
function private190($fn) {
    $scoped = $fn->bindTo(null, Scope190::class);
    return $scoped->bindTo(null, null);
}
$cached = private190(function(int $value = X) { echo 'BAD|'; });
$nonempty = private190(function(int $value = Y) { echo 'BAD|'; });
set_error_handler(function() { echo 'H|'; return true; });
try { $cached(); } catch (TypeError $e) { echo 'T|'; }
try { $cached(); } catch (TypeError $e) { echo 'T|'; }
$copy = clone $cached;
try { $copy(); } catch (TypeError $e) { echo 'T|'; }
try { $nonempty(); } catch (TypeError $e) { echo 'T|'; }
try { $nonempty(); } catch (TypeError $e) { echo 'T|'; }
