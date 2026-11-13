<?php
namespace Ns265ShortSetSingle;
class Selected265 {
    public int $tag = 17 {
        set => ($GLOBALS['called265single'] = true) ? 99 : $value;
    }
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 17 ? 'I|' : 'BAD|';
        $GLOBALS['member265single'] = 'B';
    }
}
function &selector265() {
    $receiver265 = new Selected265();
    echo 'C|';
    return $receiver265;
}
function member265() {
    echo 'M|';
    return $GLOBALS['member265single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns265ShortSetSingle\\Selected265::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member265single'] = 'A';
    return true;
});
$called265single = false;
$member265single = 'A';
echo 'B|', selector265()::{member265()}, '|', $called265single === false ? 'N|' : 'BAD|', 'Z|';
\restore_error_handler();
