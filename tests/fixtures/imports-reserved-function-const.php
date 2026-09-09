<?php
namespace Plain;
use function Target\f as Self;
use const Target\C as Parent;
namespace Grouped;
use function Target\{f as Self, g as Parent};
use const Target\{C as Self, D as Parent};
namespace Mixed;
use Target\{function f as Self, const C as Parent};
