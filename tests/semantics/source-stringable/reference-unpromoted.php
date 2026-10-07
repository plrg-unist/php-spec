<?php
$alive = false;
class ReferenceSource {
    public $tag; public $rewrite; public function __construct($tag, $rewrite) { $this->tag = $tag; $this->rewrite = $rewrite; $GLOBALS['alive'] = true; }
    public function __toString(): string {
        echo 'T:', $this->tag, '|';
        if ($this->rewrite) { $GLOBALS['operand'] = null; }
        else { unset($GLOBALS['operand']); }
        return 'function reference_' . $this->tag . '(string $arg = null) {} echo "BODY:' . $this->tag . '|"; return 71;';
    }
    public function __destruct() { $GLOBALS['alive'] = false; echo 'D:', $this->tag, '|'; }
}
function &sourceReference() { global $operand; return $operand; }
set_error_handler(function($severity, $message) { echo $GLOBALS['alive'] ? 'N:live|' : 'N:dead|'; return true; });
$operand = new ReferenceSource('held', false);
$value = eval(sourceReference());
echo 'V:', $value, '|';
$operand = new ReferenceSource('rewrite', true);
$value = eval(sourceReference());
echo 'V:', $value, '|';
restore_error_handler();
echo 'END';
