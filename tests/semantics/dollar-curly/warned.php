<?php
function published_curly_258() { echo 'f'; }
class CurlyPublished258 {
    public static function token() { echo 'c'; }
    public static function dormant($name, $value) {
        return "${value}${$name}";
    }
}
echo 'BODY|';
