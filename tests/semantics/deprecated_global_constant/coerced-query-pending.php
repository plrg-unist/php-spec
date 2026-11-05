<?php
#[Deprecated('old',since:'8.5')]
const X=7;
class Q{function __toString(){return "X";}}echo constant(new Q);
