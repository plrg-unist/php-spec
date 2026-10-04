<?php
class InterpolationOld {
    public function __toString(): string { echo 'O|'; return 'old'; }
}
class InterpolationNew {
    public function __toString(): string { echo 'N|'; return 'new'; }
}
class InterpolationBox { public mixed $piece; }
class InterpolationEarlier {
    public function __toString(): string {
        global $earlier, $later, $holder;
        $earlier = 17;
        $later = 'after';
        $holder->piece = new InterpolationNew;
        echo "C{$later}|";
        return 'first';
    }
}
$holder = new InterpolationBox;
$holder->piece = new InterpolationOld;
$later = 'before';
$earlier = new InterpolationEarlier;
$fast = "{$earlier}{$holder->piece}";
echo 'F[' . $fast . ']:' . $earlier . '|';
$holder->piece = new InterpolationOld;
$later = 'before';
$earlier = new InterpolationEarlier;
$rope = "P{$earlier}{$holder->piece}";
echo 'R[' . $rope . ']:' . $earlier . '|END';
