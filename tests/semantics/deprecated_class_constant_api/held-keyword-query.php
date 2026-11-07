<?php
class KeywordApi213 {
    #[\Deprecated] public const C = 7;
    public static function read() { return \constant('self::C'); }
}
echo KeywordApi213::read(), '|';
