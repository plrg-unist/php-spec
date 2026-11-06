<?php
namespace ScopedIncludedMethodCache144;
echo 'cold-scope:', self::class, ':', static::class, '|';
const ColdCapture=Host::query(...);
echo 'cold-ready|';
