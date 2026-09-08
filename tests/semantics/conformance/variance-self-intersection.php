<?php
interface I {} interface J {}
class P implements I { function f(): I&J {} }
class C extends P { function f(): self {} }
