# YIELD key warnings

Module321 continues an ordinary missing key-CV read after copying the known
YIELD value into its Generator. The cache owns that value before a warning
handler runs. Reference writes in the handler cannot replace the cached value;
array writes retain copied-container behavior. The missing read still yields
null as its key, and null does not advance the implicit integer index.

The source-authenticated continuation records only Generator identity, yield
origin and opcode line. It adds no value owner. Public admission permits one
actual bare or warning-handler carrier for the partial value-only cache. A bare
carrier requires the original key VARIABLE or frozen null result and null BASE.
Handler return values retain the generic207 admission rules. Genuine reached
controls test forged inputs, bases, lines, preinstalled keys and duplicate,
hidden or missing carriers while preserving the heap.
Two genuine running Generators can share identical cache payloads; the node
guard authenticates each object separately. The lost outer-carrier control
distinguishes payload-hook borrowing from the exact object guard. It does not
claim whole-public admission on a historical candidate without that guard.

The warning line is the emitted YIELD opcode line, which can differ from the key
AST line in multiline source. VALUE warnings still precede KEY warnings. A
throwing VALUE handler suppresses the later key read.

A direct API resumer closes the Generator and transfers the same Throwable to
its real caller, skipping its own catch/finally. The closed record retains cached
value, null key and Closure before frame retirement. When the actual immediate
resumer is289's child-resume/yield-from-result pair, the same Throwable instead
enters the child's own exception search; its catch/finally precedes the parent's.
A live parked parent alone does not select this branch. This shared warning
helper also covers the accepted311 VALUE-warning ingress.

Cached storage release uses303's existing ordered close walk. An uncalled cached
destructor can enter257 only through a genuine top operation/frame carrier and
an exact path of release markers to its exit. Local and caller pending exceptions
merge before entry; replacement exceptions update the same Generator releases
and caller exit. The head owner moves once into the ordinary destructor loop.
Other close stages and releases without this carrier keep their explicit boundary.

Source authority is vendored PHP8.5.10 `Zend/zend_vm_def.h::ZEND_YIELD` and
`Zend/zend_generators.c` (`zend_generator_resume`, `zend_generator_dtor_storage`,
`zend_generator_free_storage`, `zend_generator_get_gc`), with emitted line order
from `Zend/zend_compile.c::zend_compile_yield`.

Maintained checks are:

```sh
python3 tests/semantics/yield_key_warning_prepare.py --mode full
python3 tests/semantics/yield_key_warning_review.py --mode full
python3 tests/semantics/yield_key_warning_protocol.py --mode check --sl
python3 tests/semantics/yield_key_release_protocol.py --mode check --sl
python3 tests/semantics/yield_key_identity_review.py --mode full
python3 tests/semantics/yield_key_identity_protocol.py --mode check --sl
```

Historical311 warning and Unsupported observations retain their own cuts. The
byte-identical missing-key original is now maintained as a normal321 source;
its earlier Unsupported record receives no agreement credit. Broader operand
producers, reference yields, handler suspension with saved Generator resumers,
other close-stage destructors, cyclic/request/terminal cleanup and wider
Generator/Fiber lifetimes remain required. Paused generic returns are excluded.
This slice does not establish complete Generator or core semantics.

The reviewed295-module cut passes strict compilation,27 exact normal
source observations and eight genuine reached groups with658 physical
setup-inclusive premises. These include23 new originals, one promoted historical
Unsupported original and three affected earlier normal originals. The ledger
keeps the c102 warning and7edf cleanup cuts separate, including the first three
successful records of a packet whose fourth source initially failed. The required
older close Unsupported and original fixture failures earn zero agreement.
[Results and recovery](../../coverage/semantics/yield-key-warning-review.json)
record the unchanged inputs and bounded control claims. Module321 is integrated
over actual `642659405`/304 at `309c9b25f`/305: strict compilation passes with
9,833,849 bytes of complete output. Independent review preserves current
receive/source/ARG319/collector fields and exact accepted Generator rules; this
composition adds zero source observations or reached premises.
