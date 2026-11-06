<?php
#[Deprecated] const X = [1];
function receive186(int $value = X, $later = 0) { echo 'BAD|'; }
set_error_handler(function() { echo 'H|'; return true; });
try { receive186(); } catch (TypeError $error) {
    $trace = $error->getTrace(); $args = $trace[0]['args'];
    echo isset($args[0]) ? 'BAD|' : 'none|';
}
try { receive186(later: 5); } catch (TypeError $error) {
    $trace = $error->getTrace(); $args = $trace[0]['args'];
    echo $args[0][0], '|', $args[1], '|';
}
