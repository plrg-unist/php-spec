<?php
namespace Ns255NullableSingle;
class Selected255 {
    public ?string $tag;
    #[\Deprecated]
    public const A = 9, B = 10;
    public function __destruct() {
        echo 'D|', $this->tag === 'tag255' ? 'S|' : 'BAD|';
        $GLOBALS['member255single'] = 'B';
    }
}
function &selector255() {
    $receiver255 = new Selected255();
    $receiver255->tag = 'tag255';
    echo 'C|';
    return $receiver255;
}
function member255() {
    echo 'M|';
    return $GLOBALS['member255single'];
}
\set_error_handler(function ($level, $message) {
    echo $level === 16384 && $message === 'Constant Ns255NullableSingle\\Selected255::B is deprecated' ? 'H|' : 'BAD|';
    $GLOBALS['member255single'] = 'A';
    return true;
});
$member255single = 'A';
echo 'B|', selector255()::{member255()}, '|Z|';
\restore_error_handler();
