<?php
class EvalLifetimeSource {
    public $tag;
    public function __construct($tag) { $this->tag = $tag; $GLOBALS['alive'] = true; }
    public function __toString(): string {
        echo 'T:', $this->tag, '|';
        if ($this->tag === 'borrowed') { unset($GLOBALS['borrowedSource']); }
        return $this->tag === 'borrowed'
            ? 'function borrowedLifetimeUnit(int $arg = null) {} echo "BODY:B|"; return 31;'
            : 'function capturedLifetimeUnit(int $arg = null) {} echo "BODY:C|"; return 32;';
    }
    public function __destruct() { $GLOBALS['alive'] = false; echo 'D:', $this->tag, '|'; }
}
function lifetimeCompileWarning($level, $message, $file, $line) {
    echo 'N:', $GLOBALS['alive'] ? 'live|' : 'dead|';
    return true;
}
set_error_handler('lifetimeCompileWarning', E_DEPRECATED);
$borrowedSource = new EvalLifetimeSource('borrowed');
echo 'B|';
$result = eval($borrowedSource);
echo 'V:', $result, '|';
echo 'C|';
$result = eval(new EvalLifetimeSource('captured'));
echo 'V:', $result, '|';
restore_error_handler();
echo 'END';
