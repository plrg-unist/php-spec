<?php
interface I {} interface J {}
class P implements I,J { function f(): (I&J)|null {} }
class C extends P { function f(): static {} }
