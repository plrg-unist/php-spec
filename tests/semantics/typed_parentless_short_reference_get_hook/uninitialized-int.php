<?php
namespace Ns296UninitializedShortReference;
class Box296 {
    public int $tag {
        &get =>
            $this->tag;
    }
    public function __destruct() { echo 'D|'; }
}
$box296 = new Box296();
echo (array)$box296 === [] ? 'U|' : 'BAD|';
try { $read296 = $box296->tag; } catch (\Error $e) { echo 'V|'; }
try { $tag296 =& $box296->tag; } catch (\Error $e) { echo 'E|'; }
$box296->tag = 43;
$tag296 =& $box296->tag;
echo $tag296 === 43 && $box296->tag === 43 ? 'G|' : 'BAD|';
unset($box296);
$tag296 = 'free';
echo $tag296 === 'free' ? 'R|' : 'BAD|';
unset($tag296);
echo 'Z|';
