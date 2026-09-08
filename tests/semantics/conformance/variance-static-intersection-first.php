<?php
interface I {} interface J {}
class P implements I { function f(): I&J {} }
class C extends P { function f(): static { return new C; } }
echo (new C)->f() instanceof J ? "J" : "notJ";
