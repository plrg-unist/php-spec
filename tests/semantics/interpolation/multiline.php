<?php
class TraceText { public function __toString() { $e = new Exception('trace'); echo $e->getTraceAsString(), '|'; return 'text'; } }
$t = new TraceText;
echo "begin
{$t}
end", '|';
echo "{$t}", '|END';
