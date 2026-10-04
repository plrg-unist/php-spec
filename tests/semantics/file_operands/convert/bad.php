<?php
class BadOperand {
    public function __toString(): string { echo "BAD|"; return []; }
}
try { require_once new BadOperand(); }
catch (TypeError $e) { echo $e->getMessage(), "|", $e->getTraceAsString(), "|"; }
try { include new stdClass(); }
catch (Error $e) { echo $e->getMessage(), "|"; }
echo "END";
