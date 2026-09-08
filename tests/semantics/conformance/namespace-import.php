<?php
namespace A; function f(){echo "A";} namespace B; use function A\f as g; function f(){echo "B";}g();f();
