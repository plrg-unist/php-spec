<?php
class PrecisionKeyOwner {
    private static function secret() { echo self::class, ':', static::class, '|'; }
    public const array VALUE = [
        (12.3456789 . 'P') . E_STRICT => self::secret(...),
        ((22.3456789 + 0) . 'R') . E_STRICT => self::secret(...),
    ];
}
trait PrecisionKeyData { public static array $value = PrecisionKeyOwner::VALUE; }
function precisionKeyNotice($level, $message, $file, $line) {
    echo 'H:', ini_get('precision'), '|';
    return true;
}
set_error_handler('precisionKeyNotice');
ini_set('precision', '1tail');
echo 'PRE|';
class PrecisionKeyUser {
    use PrecisionKeyData;
    public static array $value = PrecisionKeyOwner::VALUE;
}
$array = PrecisionKeyOwner::VALUE;
foreach ($array as $key => $callable) { echo 'K:', $key, '|'; }
$parsed = '12.346P2048';
echo PrecisionKeyUser::$value[$parsed] === $array[$parsed] ? 'Y|' : 'N|';
($array[$parsed])();
PrecisionKeyUser::$value[$parsed] = null;
(PrecisionKeyOwner::VALUE[$parsed])();
echo isset(PrecisionKeyUser::$value[$parsed]) ? 'Y|' : 'N|';
echo 'R:', ini_get('precision'), '|END';
