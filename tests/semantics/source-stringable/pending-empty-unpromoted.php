<?php
class EmptyPendingSource {
    public $label; public function __construct($label) { $this->label = $label; }
    public function __toString(): string {
        echo 'T:', $this->label, '|';
        unset($GLOBALS['operand']);
        return '';
    }
    public function __destruct() { echo 'D:', $this->label, '|'; throw new Exception($this->label); }
}
function caughtEmptySource($error) {
    echo get_class($error), ':', $error->getMessage(), ':';
    $previous = $error->getPrevious();
    echo $previous ? $previous->getMessage() : '-', '|';
}
$operand = new EmptyPendingSource('eval');
try { eval($operand); } catch (Throwable $error) { caughtEmptySource($error); }
$operand = new EmptyPendingSource('include');
try { include $operand; } catch (Throwable $error) { caughtEmptySource($error); }
$operand = new EmptyPendingSource('once');
try { require_once $operand; } catch (Throwable $error) { caughtEmptySource($error); }
echo 'END';
