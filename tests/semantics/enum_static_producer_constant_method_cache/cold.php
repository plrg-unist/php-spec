<?php
namespace StaticProducerMethodCache146;
echo 'cold-scope:', self::class, ':', static::class, ':', isset($this) ? 'this' : 'no-this', '|';
const ColdCapture=Host::query(...);
echo 'cold-ready|';
