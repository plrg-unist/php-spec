<?php
class CvReviewEmpty {
    public function __toString() { echo 'S|'; return ''; }
}
try { include ''; } catch (ValueError $e) { echo 'I:', $e->getMessage(), '|'; }
$nil = null;
try { require $nil; } catch (ValueError $e) { echo 'R:', $e->getMessage(), '|'; }
$false = false;
try { include $false; } catch (ValueError $e) { echo 'F:', $e->getMessage(), '|'; }
try { include new CvReviewEmpty; } catch (ValueError $e) { echo 'O:', $e->getMessage(), '|'; }
try { require new CvReviewEmpty; } catch (ValueError $e) { echo 'Q:', $e->getMessage(), '|'; }
echo 'END';
