# Strict declaration compilation

Compiler92 handles source `declare(strict_types=0|1);` through the existing lexical
environment and parser-literal helper. A1 declaration sets the environment flag;
a later0 does not clear it. Unit and function CODE store the resulting STRICT
flag. Runtime93 must pair declaration work with source-derived code integrity
before source execution is admitted. Typed calls and returns remain later work.

Checks follow pinned PHP8.5.10 `zend_compile_declare`: parser-literal form, placement
in the original top file list, absence of a block body, then integer0/1 value.
Preceding Nop and Declare statements are allowed. Nested declarations fail the
file-list membership check. Directive names are case-insensitive. Errors use the
first declaration item's line, including failures in a later item.92 does not
clone constant folding or type normalization. Other directive semantics remain
explicit Unsupported after their common literal check.

The minimal compiler910/e7227852 differs from accepted defaults909/e25eb2b9 in92,
its registry entry, pcode.STRICT and the unit/function projections. Portable tests
produce912/d4f327b5 with all910 bytes/modes unchanged. The maintained compiler gate
checks37 exact native phases/lines, two other-directive boundaries and47 actual
strictness projections, preserving raw subprocess bytes and recorded worker
packets/stderr/closure. Separate source projections cover nested functions and
namespace contexts. No ENDLINE or return-root metadata from the earlier typed
prototype is included.

The preparation archives retain39 matching native/current909 compiler originals,
prior metadata/strict prototypes and their failed attempts. A separate seven-case
builtin supplement preserves strict/weak native/runtime/compiler boundaries.
Registered builtin bodies already remain Unsupported in80;87 only models compiler
facts. Thus these cases do not claim builtin execution agreement. The portable
test archive explicitly depends on the main preparation archive for the unchanged
910 source/tool inputs. Runtime/source/state/protocol acceptance is recorded
separately from this compiler evidence.

The frozen pairing917/309b046c preserves all six copied compiler/test files
byte-for-byte and by mode; its ordered module registry adds runtime93. The
[compiler pairing report](../../coverage/semantics/strict-declaration-compiler-pairing.json)
records that bridge and all three archive identities. Their historical preparation
scope and failed attempts remain intact.

The paired source/runtime implementation is committed as `c81fb14e`.
