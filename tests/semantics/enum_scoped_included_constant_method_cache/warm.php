<?php
namespace ScopedIncludedMethodCache144;
echo 'warm-scope:', self::class, ':', static::class, '|';
const WarmCapture=Host::query(...);
echo 'warm-ready|';
