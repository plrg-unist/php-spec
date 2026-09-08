<?php
enum E { case A; case B; public function f(): string { return $this->name; } }
enum S: string implements I { case A = 'a'; use T; }
function f((A&B)|C $a, D|(E&F) $b, null|false|true $c): never { throw new E; }
function g(A&B $a): ?C {}
