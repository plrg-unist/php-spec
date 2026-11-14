#!/usr/bin/env python3
"""Check marked current CV reads after the initial undefined-CV Warning."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from string_offset_current_marked_cv_review import render
from string_offset_current_marked_cv_cases import CASES
from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--peer', action='store_true', help='check the independent reference-rebinding source')
    kinds = parser.add_mutually_exclusive_group()
    kinds.add_argument('--strings', action='store_true', help='check marked INTERNED/REQUEST string carriers')
    kinds.add_argument('--arrays', action='store_true', help='check the marked current ARRAY domain')
    kinds.add_argument('--variable-base', action='store_true', help='check the selected interned CV-base header')
    kinds.add_argument('--undefined-throw', action='store_true', help='check diagnostics after an undefined-key handler throws')
    kinds.add_argument('--variable-throw', action='store_true', help='check a saved VARIABLE base after an undefined-key handler throws')
    kinds.add_argument('--request-base', action='store_true', help='check an outside ordinary keeper of a selected REQUEST base')
    kinds.add_argument('--request-throw', action='store_true', help='check a retained REQUEST base after the first undefined-key handler throws')
    kinds.add_argument('--request-release', action='store_true', help='check last-owner REQUEST release after Undefined or CAST')
    kinds.add_argument('--request-release-registered', action='store_true', help='check last-owner release with the literal handler still registered')
    kinds.add_argument('--request-release-prior', action='store_true', help='check last-owner release through a nonowning prior callback stack')
    kinds.add_argument('--request-release-distinct', action='store_true', help='check release beside live independent REQUEST headers')
    kinds.add_argument('--request-release-key', action='store_true', help='check NULL release before current-key conversion')
    kinds.add_argument('--request-release-callback', action='store_true', help='check nonowning REQUEST callback headers')
    kinds.add_argument('--request-callback-owner', action='store_true', help='check selected REQUEST callback owners')
    kinds.add_argument('--request-callback-cast-owner', action='store_true', help='check selected REQUEST callback owners after an ordinary CAST')
    kinds.add_argument('--request-callback-known-key', action='store_true', help='check callback owners with immutable primitive keys')
    kinds.add_argument('--request-known-key-release', action='store_true', help='check last-owner CAST release with immutable primitive keys')
    kinds.add_argument('--request-variable-key-release', action='store_true', help='check last-owner CAST release with captured variable keys')
    kinds.add_argument('--request-callback-rebound-key', action='store_true', help='check retained callback headers after key-reference rebinding')
    kinds.add_argument('--request-callback-referenced-key', action='store_true', help='check the prior callback owner and an initial key wrapper with --peer')
    kinds.add_argument('--request-callback-late-reference', action='store_true', help='check a plain key after the callback creates a surviving reference alias')
    kinds.add_argument('--request-callback-scalar-key', action='store_true', help='check three quiet scalar retargets through initial wrappers or plain CVs')
    kinds.add_argument('--request-callback-ordinary-key', action='store_true', help='check ordinary current key cells after global unset and assignment')
    kinds.add_argument('--request-callback-text-key', action='store_true', help='check late interned text in current or initial-wrapper key cells')
    kinds.add_argument('--request-callback-old-key', action='store_true', help='check a live initial wrapper with an absent or unchanged current name')
    kinds.add_argument('--request-callback-plain-key', action='store_true', help='check a plain CV with an absent name or same-slot text')
    kinds.add_argument('--request-callback-request-key', action='store_true', help='check selected late REQUEST text in a current CV or initial wrapper')
    kinds.add_argument('--request-callback-marked-request-key', action='store_true', help='check a captured plain CV with a later-marked REQUEST current key')
    kinds.add_argument('--request-callback-marked-interned-key', action='store_true', help='check late marked INTERNED text after captured plain CV history')
    kinds.add_argument('--request-callback-raw-message-key', action='store_true', help='check raw Warning message keys in late current reference cells')
    kinds.add_argument('--request-callback-ordinary-raw-key', action='store_true', help='check raw Warning message keys in ordinary current cells')
    kinds.add_argument('--request-callback-reference-raw-key', action='store_true', help='check raw Warning message payloads in captured initial key wrappers')
    kinds.add_argument('--request-callback-raw-key-cell-owner', action='store_true', help='check real base cells after raw-key callback-owner loss')
    kinds.add_argument('--request-callback-marked-raw-key-cell-owner', action='store_true', help='check later-marked raw keys with real base-cell providers')
    kinds.add_argument('--request-callback-reference-raw-key-cell-owner', action='store_true', help='check initial raw key wrappers with real base-cell providers')
    kinds.add_argument('--literal-callback-raw-key', action='store_true', help='check late raw keys with source-authenticated literal string bases')
    kinds.add_argument('--initial-raw-leading-key', action='store_true', help='check frozen leading offsets from initial raw CV strings')
    kinds.add_argument('--variable-base-initial-raw-leading-key', action='store_true', help='check selected ordinary CV bases with initial raw leading keys')
    kinds.add_argument('--reference-base-initial-raw-leading-key', action='store_true', help='check selected initial-reference CV bases with raw leading keys')
    kinds.add_argument('--conditional-base-initial-raw-leading-key', action='store_true', help='check quiet Boolean ternary bases with raw leading keys')
    kinds.add_argument('--shorthand-base-initial-raw-leading-key', action='store_true', help='check literal-string shorthand bases with raw leading keys')
    kinds.add_argument('--string-conditional-base-initial-raw-leading-key', action='store_true', help='check raw-string full ternary bases with raw leading keys')
    kinds.add_argument('--coalesce-base-initial-raw-leading-key', action='store_true', help='check literal coalesce bases with raw leading keys')
    kinds.add_argument('--raw-truth-shorthand-base-initial-raw-leading-key', action='store_true', help='check certified falsey scalar shorthand bases with raw leading keys')
    kinds.add_argument('--folded-boolean-not-truth-base-initial-raw-leading-key', action='store_true', help='check folded non-FLOAT NOT tree literal bases with raw leading keys')
    kinds.add_argument('--raw-truth-conditional-base-initial-raw-leading-key', action='store_true', help='check certified scalar full ternary bases with raw leading keys')
    kinds.add_argument('--integer-division-truth-base-initial-raw-leading-key', action='store_true', help='check exact integer-division full ternary bases with raw leading keys')
    kinds.add_argument('--integer-binary-truth-base-initial-raw-leading-key', action='store_true', help='check quiet integer-binary full ternary bases with raw leading keys')
    kinds.add_argument('--integer-bitnot-truth-base-initial-raw-leading-key', action='store_true', help='check quiet integer-bitnot full ternary bases with raw leading keys')
    kinds.add_argument('--integer-conditional-base-initial-raw-leading-key', action='store_true', help='check integer-conditioned full ternary bases with raw leading keys')
    kinds.add_argument('--float-unary-truth-base-initial-raw-leading-key', action='store_true', help='check finite FLOAT-sign full ternary bases with raw leading keys')
    kinds.add_argument('--float-arithmetic-truth-base-initial-raw-leading-key', action='store_true', help='check finite FLOAT-arithmetic full ternary bases with raw leading keys')
    kinds.add_argument('--numeric-arithmetic-truth-base-initial-raw-leading-key', action='store_true', help='check finite FLOAT-arithmetic full ternary bases with raw leading keys')
    kinds.add_argument('--numeric-unary-truth-base-initial-raw-leading-key', action='store_true', help='check finite numeric FLOAT-sign full ternary bases with raw leading keys')
    kinds.add_argument('--numeric-string-unary-truth-base-initial-raw-leading-key', action='store_true', help='check finite quiet numeric-string FLOAT-sign full ternary bases with raw leading keys')
    kinds.add_argument('--coercive-arithmetic-truth-base-initial-raw-leading-key', action='store_true', help='check finite quiet scalar FLOAT-arithmetic full ternary bases with raw leading keys')
    kinds.add_argument('--coercive-integer-arithmetic-truth-base-initial-raw-leading-key', action='store_true', help='check quiet scalar integer-result arithmetic full ternary bases with raw leading keys')
    kinds.add_argument('--coercive-integer-unary-truth-base-initial-raw-leading-key', action='store_true', help='check quiet signs over certified integer-result arithmetic full ternary bases with raw leading keys')
    kinds.add_argument('--coercive-integer-bitnot-truth-base-initial-raw-leading-key', action='store_true', help='check quiet complements over certified integer-result arithmetic full ternary bases with raw leading keys')
    kinds.add_argument('--boolean-null-unary-truth-base-initial-raw-leading-key', action='store_true', help='check quiet Boolean/null signs full ternary bases with raw leading keys')
    kinds.add_argument('--coercive-integer-binary-truth-base-initial-raw-leading-key', action='store_true', help='check quiet scalar-coercive integer binary operators full ternary bases with raw leading keys')
    kinds.add_argument('--folded-scalar-comparison-truth-base-initial-raw-leading-key', action='store_true', help='check quiet folded scalar-comparison full ternary bases with raw leading keys')
    kinds.add_argument('--folded-scalar-boolean-truth-base-initial-raw-leading-key', action='store_true', help='check quiet finite-FLOAT comparisons and scalar XOR full ternary bases with raw leading keys')
    kinds.add_argument('--float-conditional-base-initial-raw-leading-key', action='store_true', help='check finite float-conditioned full ternary bases with raw leading keys')
    kinds.add_argument('--null-conditional-base-initial-raw-leading-key', action='store_true', help='check literal null-conditioned full ternary bases with raw leading keys')
    kinds.add_argument('--null-shorthand-base-initial-raw-leading-key', action='store_true', help='check literal null shorthand bases with raw leading keys')
    kinds.add_argument('--false-shorthand-base-initial-raw-leading-key', action='store_true', help='check literal false shorthand bases with raw leading keys')
    kinds.add_argument('--integer-zero-shorthand-base-initial-raw-leading-key', action='store_true', help='check literal integer-zero shorthand bases with raw leading keys')
    kinds.add_argument('--float-zero-shorthand-base-initial-raw-leading-key', action='store_true', help='check literal positive-zero float shorthand bases with raw leading keys')
    kinds.add_argument('--negative-zero-shorthand-base-initial-raw-leading-key', action='store_true', help='check unary-minus float-zero shorthand bases with raw leading keys')
    kinds.add_argument('--unary-plus-zero-shorthand-base-initial-raw-leading-key', action='store_true', help='check unary-plus float-zero shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-true-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot true shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-integer-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot nonzero integer shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-integer-unary-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot nonzero integer unary-chain shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-true-unary-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot quiet literal-true unary-chain shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-integer-arithmetic-unary-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot quiet integer ADD/SUBTRACT/MULTIPLY unary-chain shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-integer-arithmetic-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot certified direct integer arithmetic shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-float-shorthand-base-initial-raw-leading-key', action='store_true', help='check emitted BooleanNot finite raw FLOAT shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-numeric-string-unary-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot quiet integer numeric-string unary-chain shorthand bases with raw leading keys')
    kinds.add_argument('--boolean-not-string-shorthand-base-initial-raw-leading-key', action='store_true', help='check BooleanNot truthy raw string shorthand bases with raw leading keys')
    args = parser.parse_args()
    if args.request_callback_referenced_key and not args.peer:
        parser.error('--request-callback-referenced-key requires --peer')
    cases = CASES
    selected_render = render
    if args.strings:
        from string_offset_current_marked_string_cv_cases import CASES as string_cases
        from string_offset_current_marked_string_cv_review import render as render_strings
        cases = string_cases
        selected_render = render_strings
    elif args.arrays:
        from string_offset_current_marked_array_cv_cases import CASES as array_cases
        from string_offset_current_marked_array_cv_review import render as render_arrays
        cases = array_cases
        selected_render = render_arrays
    elif args.variable_base:
        from string_offset_variable_base_cv_cases import CASES as base_cases
        from string_offset_variable_base_cv_review import render as render_base
        cases = base_cases
        selected_render = render_base
    elif args.undefined_throw:
        from string_offset_undefined_throw_cases import CASES as throw_cases
        from string_offset_undefined_throw_review import render as render_throw
        cases = throw_cases
        selected_render = render_throw
    elif args.variable_throw:
        from string_offset_variable_throw_cases import CASES as throw_cases
        from string_offset_variable_throw_review import render as render_throw
        cases = throw_cases
        selected_render = render_throw
    elif args.request_base:
        from string_offset_request_base_cv_cases import CASES as request_cases
        from string_offset_request_base_cv_review import render as render_request
        cases = request_cases
        selected_render = render_request
    elif args.request_throw:
        from string_offset_request_throw_cases import CASES as throw_cases
        from string_offset_request_throw_review import render as render_throw
        cases = throw_cases
        selected_render = render_throw
    elif args.request_release:
        from string_offset_request_release_cv_cases import CASES as release_cases
        from string_offset_request_release_cv_review import render as render_release
        cases = release_cases
        selected_render = render_release
    elif args.request_release_registered:
        from string_offset_request_release_registered_cv_cases import CASES as registered_cases
        from string_offset_request_release_registered_cv_review import render as render_registered
        cases = registered_cases
        selected_render = render_registered
    elif args.request_release_prior:
        from string_offset_request_release_prior_cv_cases import CASES as prior_cases
        from string_offset_request_release_prior_cv_review import render as render_prior
        cases = prior_cases
        selected_render = render_prior
    elif args.request_release_distinct:
        from string_offset_request_release_distinct_cv_cases import CASES as distinct_cases
        from string_offset_request_release_distinct_cv_review import render as render_distinct
        cases = distinct_cases
        selected_render = render_distinct
    elif args.request_release_key:
        from string_offset_request_release_key_cv_cases import CASES as key_cases
        from string_offset_request_release_key_cv_review import render as render_key
        cases = key_cases
        selected_render = render_key
    elif args.request_release_callback:
        from string_offset_request_release_callback_cv_cases import CASES as callback_cases
        from string_offset_request_release_callback_cv_review import render as render_callback
        cases = callback_cases
        selected_render = render_callback
    elif args.request_callback_owner:
        from string_offset_request_callback_owner_cv_cases import CASES as owner_cases
        from string_offset_request_callback_owner_cv_review import render as render_owner
        cases = owner_cases
        selected_render = render_owner
    elif args.request_callback_cast_owner:
        from string_offset_request_callback_cast_owner_cases import CASES as cast_owner_cases
        from string_offset_request_callback_cast_owner_review import render as render_cast_owner
        cases = cast_owner_cases
        selected_render = render_cast_owner
    elif args.request_callback_known_key:
        from string_offset_request_callback_known_key_cases import CASES as known_key_cases
        from string_offset_request_callback_known_key_review import render as render_known_key
        cases = known_key_cases
        selected_render = render_known_key
    elif args.request_known_key_release:
        from string_offset_request_known_key_release_cases import CASES as known_key_release_cases
        from string_offset_request_known_key_release_review import render as render_known_key_release
        cases = known_key_release_cases
        selected_render = render_known_key_release
    elif args.request_variable_key_release:
        from string_offset_request_variable_key_release_cases import CASES as variable_key_release_cases
        from string_offset_request_variable_key_release_review import render as render_variable_key_release
        cases = variable_key_release_cases
        selected_render = render_variable_key_release
    elif args.request_callback_rebound_key:
        from string_offset_request_callback_rebound_key_cases import CASES as rebound_key_cases
        from string_offset_request_callback_rebound_key_review import render as render_rebound_key
        cases = rebound_key_cases
        selected_render = render_rebound_key
    elif args.request_callback_referenced_key:
        from string_offset_request_callback_referenced_key_cases import CASES as referenced_key_cases
        cases = referenced_key_cases
    elif args.request_callback_late_reference:
        from string_offset_request_callback_late_reference_cases import CASES as late_reference_cases
        from string_offset_request_callback_late_reference_review import render as render_late_reference
        cases = late_reference_cases
        selected_render = render_late_reference
    elif args.request_callback_scalar_key:
        from string_offset_request_callback_scalar_key_cases import CASES as scalar_key_cases
        from string_offset_request_callback_scalar_key_review import render as render_scalar_key
        cases = scalar_key_cases[3:] if args.peer else scalar_key_cases[:3]
        selected_render = render_scalar_key
    elif args.request_callback_ordinary_key:
        from string_offset_request_callback_ordinary_key_cases import CASES as ordinary_key_cases
        from string_offset_request_callback_ordinary_key_review import render as render_ordinary_key
        cases = ordinary_key_cases
        selected_render = render_ordinary_key
    elif args.request_callback_text_key:
        from string_offset_request_callback_text_key_cases import CASES as text_key_cases
        from string_offset_request_callback_text_key_review import render as render_text_key
        cases = text_key_cases
        selected_render = render_text_key
    elif args.request_callback_old_key:
        from string_offset_request_callback_old_key_cases import CASES as old_key_cases
        from string_offset_request_callback_old_key_review import render as render_old_key
        cases = old_key_cases
        selected_render = render_old_key
    elif args.request_callback_plain_key:
        from string_offset_request_callback_plain_key_cases import CASES as plain_key_cases
        from string_offset_request_callback_plain_key_review import render as render_plain_key
        cases = plain_key_cases
        selected_render = render_plain_key
    elif args.request_callback_request_key:
        from string_offset_request_callback_request_key_cases import CASES as request_key_cases
        from string_offset_request_callback_request_key_review import render as render_request_key
        cases = request_key_cases
        selected_render = render_request_key
    elif args.request_callback_marked_request_key:
        from string_offset_request_callback_marked_request_key_cases import CASES as marked_request_key_cases
        from string_offset_request_callback_marked_request_key_review import render as render_marked_request_key
        cases = marked_request_key_cases
        selected_render = render_marked_request_key
    elif args.request_callback_marked_interned_key:
        from string_offset_request_callback_marked_interned_key_cases import CASES as marked_interned_key_cases
        from string_offset_request_callback_marked_interned_key_review import render as render_marked_interned_key
        cases = marked_interned_key_cases
        selected_render = render_marked_interned_key
    elif args.request_callback_raw_message_key:
        from string_offset_request_callback_raw_message_key_cases import CASES as raw_message_key_cases
        from string_offset_request_callback_raw_message_key_review import render as render_raw_message_key
        cases = raw_message_key_cases
        selected_render = render_raw_message_key
    elif args.request_callback_ordinary_raw_key:
        from string_offset_request_callback_ordinary_raw_key_cases import CASES as ordinary_raw_key_cases
        from string_offset_request_callback_ordinary_raw_key_review import render as render_ordinary_raw_key
        cases = ordinary_raw_key_cases
        selected_render = render_ordinary_raw_key
    elif args.request_callback_reference_raw_key:
        from string_offset_request_callback_reference_raw_key_cases import CASES as reference_raw_key_cases
        from string_offset_request_callback_reference_raw_key_review import render as render_reference_raw_key
        cases = reference_raw_key_cases
        selected_render = render_reference_raw_key
    elif args.request_callback_raw_key_cell_owner:
        from string_offset_request_callback_raw_key_cell_owner_cases import CASES as cell_owner_cases
        from string_offset_request_callback_raw_key_cell_owner_review import render as render_cell_owner
        cases = cell_owner_cases
        selected_render = render_cell_owner
    elif args.request_callback_marked_raw_key_cell_owner:
        from string_offset_request_callback_marked_raw_key_cell_owner_cases import CASES as marked_cell_owner_cases
        from string_offset_request_callback_marked_raw_key_cell_owner_review import render as render_marked_cell_owner
        cases = marked_cell_owner_cases
        selected_render = render_marked_cell_owner
    elif args.request_callback_reference_raw_key_cell_owner:
        from string_offset_request_callback_reference_raw_key_cell_owner_cases import CASES as reference_cell_owner_cases
        from string_offset_request_callback_reference_raw_key_cell_owner_review import render as render_reference_cell_owner
        cases = reference_cell_owner_cases
        selected_render = render_reference_cell_owner
    elif args.literal_callback_raw_key:
        from string_offset_literal_callback_raw_key_cases import CASES as literal_raw_key_cases
        from string_offset_literal_callback_raw_key_review import render as render_literal_raw_key
        cases = literal_raw_key_cases
        selected_render = render_literal_raw_key
    elif args.initial_raw_leading_key:
        from string_offset_initial_raw_leading_key_cases import CASES as initial_raw_key_cases
        from string_offset_initial_raw_leading_key_review import render as render_initial_raw_key
        cases = initial_raw_key_cases
        selected_render = render_initial_raw_key
    elif args.variable_base_initial_raw_leading_key:
        from string_offset_variable_base_initial_raw_leading_key_cases import CASES as variable_raw_key_cases
        from string_offset_variable_base_initial_raw_leading_key_review import render as render_variable_raw_key
        cases = variable_raw_key_cases
        selected_render = render_variable_raw_key
    elif args.reference_base_initial_raw_leading_key:
        from string_offset_reference_base_initial_raw_leading_key_cases import CASES as reference_raw_key_cases
        from string_offset_reference_base_initial_raw_leading_key_review import render as render_reference_raw_key
        cases = reference_raw_key_cases
        selected_render = render_reference_raw_key
    elif args.raw_truth_shorthand_base_initial_raw_leading_key:
        from string_offset_raw_truth_shorthand_base_initial_raw_leading_key_cases import CASES as raw_shorthand_cases
        from string_offset_raw_truth_shorthand_base_initial_raw_leading_key_review import render as render_raw_shorthand
        cases = raw_shorthand_cases
        selected_render = render_raw_shorthand
    elif args.folded_boolean_not_truth_base_initial_raw_leading_key:
        from string_offset_folded_boolean_not_truth_base_initial_raw_leading_key_cases import CASES as folded_not_cases
        from string_offset_folded_boolean_not_truth_base_initial_raw_leading_key_review import render as render_folded_not
        cases = folded_not_cases
        selected_render = render_folded_not
    elif args.raw_truth_conditional_base_initial_raw_leading_key:
        from string_offset_raw_truth_conditional_base_initial_raw_leading_key_cases import CASES as truth_cases
        from string_offset_raw_truth_conditional_base_initial_raw_leading_key_review import render as render_truth
        cases = truth_cases
        selected_render = render_truth
    elif args.integer_division_truth_base_initial_raw_leading_key:
        from string_offset_integer_division_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_integer_division_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.integer_binary_truth_base_initial_raw_leading_key:
        from string_offset_integer_binary_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_integer_binary_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.integer_bitnot_truth_base_initial_raw_leading_key:
        from string_offset_integer_bitnot_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_integer_bitnot_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.integer_conditional_base_initial_raw_leading_key:
        from string_offset_integer_conditional_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_integer_conditional_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.float_unary_truth_base_initial_raw_leading_key:
        from string_offset_float_unary_truth_base_initial_raw_leading_key_cases import CASES as float_conditional_raw_key_cases
        from string_offset_float_unary_truth_base_initial_raw_leading_key_review import render as render_float_conditional_raw_key
        cases = float_conditional_raw_key_cases
        selected_render = render_float_conditional_raw_key
    elif args.float_arithmetic_truth_base_initial_raw_leading_key:
        from string_offset_float_arithmetic_truth_base_initial_raw_leading_key_cases import CASES as float_conditional_raw_key_cases
        from string_offset_float_arithmetic_truth_base_initial_raw_leading_key_review import render as render_float_conditional_raw_key
        cases = float_conditional_raw_key_cases
        selected_render = render_float_conditional_raw_key
    elif args.numeric_arithmetic_truth_base_initial_raw_leading_key:
        from string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_cases import CASES as float_conditional_raw_key_cases
        from string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_review import render as render_float_conditional_raw_key
        cases = float_conditional_raw_key_cases
        selected_render = render_float_conditional_raw_key
    elif args.numeric_unary_truth_base_initial_raw_leading_key:
        from string_offset_numeric_unary_truth_base_initial_raw_leading_key_cases import CASES as float_conditional_raw_key_cases
        from string_offset_numeric_unary_truth_base_initial_raw_leading_key_review import render as render_float_conditional_raw_key
        cases = float_conditional_raw_key_cases
        selected_render = render_float_conditional_raw_key
    elif args.numeric_string_unary_truth_base_initial_raw_leading_key:
        from string_offset_numeric_string_unary_truth_base_initial_raw_leading_key_cases import CASES as float_conditional_raw_key_cases
        from string_offset_numeric_string_unary_truth_base_initial_raw_leading_key_review import render as render_float_conditional_raw_key
        cases = float_conditional_raw_key_cases
        selected_render = render_float_conditional_raw_key
    elif args.folded_scalar_boolean_truth_base_initial_raw_leading_key:
        from string_offset_folded_scalar_boolean_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_folded_scalar_boolean_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.folded_scalar_comparison_truth_base_initial_raw_leading_key:
        from string_offset_folded_scalar_comparison_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_folded_scalar_comparison_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.coercive_integer_binary_truth_base_initial_raw_leading_key:
        from string_offset_coercive_integer_binary_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_coercive_integer_binary_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.boolean_null_unary_truth_base_initial_raw_leading_key:
        from string_offset_boolean_null_unary_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_boolean_null_unary_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.coercive_integer_bitnot_truth_base_initial_raw_leading_key:
        from string_offset_coercive_integer_bitnot_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_coercive_integer_bitnot_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.coercive_integer_unary_truth_base_initial_raw_leading_key:
        from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.coercive_integer_arithmetic_truth_base_initial_raw_leading_key:
        from string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_cases import CASES as integer_conditional_raw_key_cases
        from string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_review import render as render_integer_conditional_raw_key
        cases = integer_conditional_raw_key_cases
        selected_render = render_integer_conditional_raw_key
    elif args.coercive_arithmetic_truth_base_initial_raw_leading_key:
        from string_offset_coercive_arithmetic_truth_base_initial_raw_leading_key_cases import CASES as float_conditional_raw_key_cases
        from string_offset_coercive_arithmetic_truth_base_initial_raw_leading_key_review import render as render_float_conditional_raw_key
        cases = float_conditional_raw_key_cases
        selected_render = render_float_conditional_raw_key
    elif args.float_conditional_base_initial_raw_leading_key:
        from string_offset_float_conditional_base_initial_raw_leading_key_cases import CASES as float_conditional_raw_key_cases
        from string_offset_float_conditional_base_initial_raw_leading_key_review import render as render_float_conditional_raw_key
        cases = float_conditional_raw_key_cases
        selected_render = render_float_conditional_raw_key
    elif args.null_conditional_base_initial_raw_leading_key:
        from string_offset_null_conditional_base_initial_raw_leading_key_cases import CASES as null_conditional_raw_key_cases
        from string_offset_null_conditional_base_initial_raw_leading_key_review import render as render_null_conditional_raw_key
        cases = null_conditional_raw_key_cases
        selected_render = render_null_conditional_raw_key
    elif args.null_shorthand_base_initial_raw_leading_key:
        from string_offset_null_shorthand_base_initial_raw_leading_key_cases import CASES as null_shorthand_raw_key_cases
        from string_offset_null_shorthand_base_initial_raw_leading_key_review import render as render_null_shorthand_raw_key
        cases = null_shorthand_raw_key_cases
        selected_render = render_null_shorthand_raw_key
    elif args.false_shorthand_base_initial_raw_leading_key:
        from string_offset_false_shorthand_base_initial_raw_leading_key_cases import CASES as false_shorthand_raw_key_cases
        from string_offset_false_shorthand_base_initial_raw_leading_key_review import render as render_false_shorthand_raw_key
        cases = false_shorthand_raw_key_cases
        selected_render = render_false_shorthand_raw_key
    elif args.integer_zero_shorthand_base_initial_raw_leading_key:
        from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_cases import CASES as integer_zero_shorthand_raw_key_cases
        from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_review import render as render_integer_zero_shorthand_raw_key
        cases = integer_zero_shorthand_raw_key_cases
        selected_render = render_integer_zero_shorthand_raw_key
    elif args.float_zero_shorthand_base_initial_raw_leading_key:
        from string_offset_float_zero_shorthand_base_initial_raw_leading_key_cases import CASES as float_zero_shorthand_raw_key_cases
        from string_offset_float_zero_shorthand_base_initial_raw_leading_key_review import render as render_float_zero_shorthand_raw_key
        cases = float_zero_shorthand_raw_key_cases
        selected_render = render_float_zero_shorthand_raw_key
    elif args.negative_zero_shorthand_base_initial_raw_leading_key:
        from string_offset_negative_zero_shorthand_base_initial_raw_leading_key_cases import CASES as negative_zero_shorthand_raw_key_cases
        from string_offset_negative_zero_shorthand_base_initial_raw_leading_key_review import render as render_negative_zero_shorthand_raw_key
        cases = negative_zero_shorthand_raw_key_cases
        selected_render = render_negative_zero_shorthand_raw_key
    elif args.unary_plus_zero_shorthand_base_initial_raw_leading_key:
        from string_offset_unary_plus_zero_shorthand_base_initial_raw_leading_key_cases import CASES as unary_plus_zero_shorthand_raw_key_cases
        from string_offset_unary_plus_zero_shorthand_base_initial_raw_leading_key_review import render as render_unary_plus_zero_shorthand_raw_key
        cases = unary_plus_zero_shorthand_raw_key_cases
        selected_render = render_unary_plus_zero_shorthand_raw_key
    elif args.boolean_not_true_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_true_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_true_shorthand_raw_key_cases
        from string_offset_boolean_not_true_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_true_shorthand_raw_key
        cases = boolean_not_true_shorthand_raw_key_cases
        selected_render = render_boolean_not_true_shorthand_raw_key
    elif args.boolean_not_integer_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_integer_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_integer_shorthand_raw_key_cases
        from string_offset_boolean_not_integer_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_integer_shorthand_raw_key
        cases = boolean_not_integer_shorthand_raw_key_cases
        selected_render = render_boolean_not_integer_shorthand_raw_key
    elif args.boolean_not_integer_unary_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_integer_unary_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_integer_unary_shorthand_raw_key_cases
        from string_offset_boolean_not_integer_unary_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_integer_unary_shorthand_raw_key
        cases = boolean_not_integer_unary_shorthand_raw_key_cases
        selected_render = render_boolean_not_integer_unary_shorthand_raw_key
    elif args.boolean_not_true_unary_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_true_unary_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_true_unary_shorthand_raw_key_cases
        from string_offset_boolean_not_true_unary_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_true_unary_shorthand_raw_key
        cases = boolean_not_true_unary_shorthand_raw_key_cases
        selected_render = render_boolean_not_true_unary_shorthand_raw_key
    elif args.boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_integer_arithmetic_unary_shorthand_raw_key_cases
        from string_offset_boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_integer_arithmetic_unary_shorthand_raw_key
        cases = boolean_not_integer_arithmetic_unary_shorthand_raw_key_cases
        selected_render = render_boolean_not_integer_arithmetic_unary_shorthand_raw_key
    elif args.boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_integer_arithmetic_shorthand_raw_key_cases
        from string_offset_boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_integer_arithmetic_shorthand_raw_key
        cases = boolean_not_integer_arithmetic_shorthand_raw_key_cases
        selected_render = render_boolean_not_integer_arithmetic_shorthand_raw_key
    elif args.boolean_not_float_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_float_shorthand_base_initial_raw_leading_key_cases import CASES as float_cases
        from string_offset_boolean_not_float_shorthand_base_initial_raw_leading_key_review import render as render_float
        cases = float_cases
        selected_render = render_float
    elif args.boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_numeric_string_unary_shorthand_raw_key_cases
        from string_offset_boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_numeric_string_unary_shorthand_raw_key
        cases = boolean_not_numeric_string_unary_shorthand_raw_key_cases
        selected_render = render_boolean_not_numeric_string_unary_shorthand_raw_key
    elif args.boolean_not_string_shorthand_base_initial_raw_leading_key:
        from string_offset_boolean_not_string_shorthand_base_initial_raw_leading_key_cases import CASES as boolean_not_string_shorthand_raw_key_cases
        from string_offset_boolean_not_string_shorthand_base_initial_raw_leading_key_review import render as render_boolean_not_string_shorthand_raw_key
        cases = boolean_not_string_shorthand_raw_key_cases
        selected_render = render_boolean_not_string_shorthand_raw_key
    elif args.coalesce_base_initial_raw_leading_key:
        from string_offset_coalesce_base_initial_raw_leading_key_cases import CASES as coalesce_raw_key_cases
        from string_offset_coalesce_base_initial_raw_leading_key_review import render as render_coalesce_raw_key
        cases = coalesce_raw_key_cases
        selected_render = render_coalesce_raw_key
    elif args.string_conditional_base_initial_raw_leading_key:
        from string_offset_string_conditional_base_initial_raw_leading_key_cases import CASES as string_conditional_raw_key_cases
        from string_offset_string_conditional_base_initial_raw_leading_key_review import render as render_string_conditional_raw_key
        cases = string_conditional_raw_key_cases
        selected_render = render_string_conditional_raw_key
    elif args.shorthand_base_initial_raw_leading_key:
        from string_offset_shorthand_base_initial_raw_leading_key_cases import CASES as shorthand_raw_key_cases
        from string_offset_shorthand_base_initial_raw_leading_key_review import render as render_shorthand_raw_key
        cases = shorthand_raw_key_cases
        selected_render = render_shorthand_raw_key
    elif args.conditional_base_initial_raw_leading_key:
        from string_offset_conditional_base_initial_raw_leading_key_cases import CASES as conditional_raw_key_cases
        from string_offset_conditional_base_initial_raw_leading_key_review import render as render_conditional_raw_key
        cases = conditional_raw_key_cases
        selected_render = render_conditional_raw_key
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'original.php'
    selected_case = cases[0 if args.request_callback_scalar_key else int(args.peer)]
    source.write_text(selected_case['source'])
    scalar_sources = []
    if args.request_callback_scalar_key:
        for case, name in zip(cases[1:], ('null-key.php','float-key.php'), strict=True):
            extra_source = out / name
            extra_source.write_text(case['source'])
            scalar_sources.append(extra_source)
    control_source = None
    if args.undefined_throw and args.peer:
        control_source = out / 'literal-key-control.php'
        assert cases[1]['source'].count('"abc"[$key]') == 1
        control_source.write_text(cases[1]['source'].replace('"abc"[$key]', '"abc"[true]'))
    elif args.request_callback_rebound_key:
        from string_offset_request_callback_rebound_key_cases import CONTROL
        control_source = out / 'initial-reference-control.php'
        control_source.write_text(CONTROL['source'])
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), source]
    watched += scalar_sources
    if control_source is not None:
        watched.append(control_source)
    watched += [ROOT / name for name in (
        'spec/semantics/modules.json', 'tests/semantics/string_offset_current_marked_cv_review.py',
        'tests/semantics/string_offset_current_marked_cv_cases.py',
        'tests/semantics/string_offset_undefined_cv_review.py',
        'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/numeric_runner.ml',
        'tests/semantics/_build/default/numeric_runner.exe', 'frontend/worker.php', '.tools/php/bin/php',
        '.tools/php-file.so', '_build/default/adapter/main.exe', '.tools/spectec/bin/p4spectec')]
    if args.strings:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_current_marked_string_cv_cases.py',
            'tests/semantics/string_offset_current_marked_string_cv_review.py')]
    elif args.arrays:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_current_marked_array_cv_cases.py',
            'tests/semantics/string_offset_current_marked_array_cv_review.py')]
    elif args.variable_base:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_variable_base_cv_cases.py',
            'tests/semantics/string_offset_variable_base_cv_review.py')]
    elif args.undefined_throw:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_undefined_throw_cases.py',
            'tests/semantics/string_offset_undefined_throw_review.py',
            'tests/semantics/string_offset_undefined_throw_peer_review.py')]
    elif args.variable_throw:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_variable_throw_cases.py',
            'tests/semantics/string_offset_variable_throw_review.py',
            'tests/semantics/string_offset_undefined_throw_peer_review.py')]
    elif args.request_base:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_base_cv_cases.py',
            'tests/semantics/string_offset_request_base_cv_review.py')]
    elif args.request_throw:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_throw_cases.py',
            'tests/semantics/string_offset_request_throw_review.py',
            'tests/semantics/string_offset_undefined_throw_peer_review.py')]
    elif args.request_release:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_cv_cases.py',
            'tests/semantics/string_offset_request_release_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_registered:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_registered_cv_cases.py',
            'tests/semantics/string_offset_request_release_registered_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_prior:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_prior_cv_cases.py',
            'tests/semantics/string_offset_request_release_prior_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_distinct:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_distinct_cv_cases.py',
            'tests/semantics/string_offset_request_release_distinct_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_key_cv_cases.py',
            'tests/semantics/string_offset_request_release_key_cv_review.py',
            'tests/semantics/string_offset_request_release_distinct_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_release_callback:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_release_callback_cv_cases.py',
            'tests/semantics/string_offset_request_release_callback_cv_review.py',
            'tests/semantics/string_offset_request_release_key_cv_review.py',
            'tests/semantics/string_offset_request_release_distinct_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_callback_owner:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_owner_cv_cases.py',
            'tests/semantics/string_offset_request_callback_owner_cv_review.py',
            'tests/semantics/string_offset_request_base_cv_peer_review.py')]
    elif args.request_callback_cast_owner:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_cast_owner_cases.py',
            'tests/semantics/string_offset_request_callback_cast_owner_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_callback_known_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_known_key_cases.py',
            'tests/semantics/string_offset_request_callback_known_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_known_key_release:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_known_key_release_cases.py',
            'tests/semantics/string_offset_request_known_key_release_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_variable_key_release:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_variable_key_release_cases.py',
            'tests/semantics/string_offset_request_variable_key_release_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_callback_rebound_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_rebound_key_cases.py',
            'tests/semantics/string_offset_request_callback_rebound_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_callback_referenced_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_referenced_key_cases.py',
            'tests/semantics/string_offset_request_callback_rebound_key_cases.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_callback_late_reference:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_late_reference_cases.py',
            'tests/semantics/string_offset_request_callback_late_reference_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_callback_scalar_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_scalar_key_cases.py',
            'tests/semantics/string_offset_request_callback_scalar_key_review.py',
            'tests/semantics/string_offset_request_callback_referenced_key_cases.py',
            'tests/semantics/string_offset_request_callback_rebound_key_cases.py',
            'tests/semantics/string_offset_request_callback_late_reference_cases.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    elif args.request_callback_ordinary_key or args.request_callback_text_key or args.request_callback_old_key or args.request_callback_plain_key or args.request_callback_request_key or args.request_callback_marked_request_key or args.request_callback_marked_interned_key or args.request_callback_raw_message_key or args.request_callback_ordinary_raw_key or args.request_callback_reference_raw_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_ordinary_key_cases.py',
            'tests/semantics/string_offset_request_callback_ordinary_key_review.py',
            'tests/semantics/string_offset_request_callback_late_reference_cases.py',
            'tests/semantics/string_offset_request_callback_referenced_key_cases.py',
            'tests/semantics/string_offset_request_callback_rebound_key_cases.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
        if args.request_callback_text_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_text_key_cases.py',
                'tests/semantics/string_offset_request_callback_text_key_review.py')]
        if args.request_callback_old_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_old_key_cases.py',
                'tests/semantics/string_offset_request_callback_old_key_review.py',
                'tests/semantics/string_offset_request_callback_text_key_cases.py')]
        if args.request_callback_plain_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_plain_key_cases.py',
                'tests/semantics/string_offset_request_callback_plain_key_review.py')]
        if args.request_callback_reference_raw_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_reference_raw_key_cases.py',
                'tests/semantics/string_offset_request_callback_reference_raw_key_review.py',
                'tests/semantics/string_offset_request_callback_old_key_cases.py',
                'tests/semantics/string_offset_request_callback_text_key_cases.py')]
        if args.request_callback_ordinary_raw_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_ordinary_raw_key_cases.py',
                'tests/semantics/string_offset_request_callback_ordinary_raw_key_review.py',
                'tests/semantics/string_offset_request_callback_plain_key_cases.py')]
        if args.request_callback_raw_message_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_raw_message_key_cases.py',
                'tests/semantics/string_offset_request_callback_raw_message_key_review.py',
                'tests/semantics/string_offset_request_callback_plain_key_cases.py')]
        if args.request_callback_marked_interned_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_marked_interned_key_cases.py',
                'tests/semantics/string_offset_request_callback_marked_interned_key_review.py',
                'tests/semantics/string_offset_request_callback_plain_key_cases.py')]
        if args.request_callback_marked_request_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_marked_request_key_cases.py',
                'tests/semantics/string_offset_request_callback_marked_request_key_review.py',
                'tests/semantics/string_offset_request_callback_request_key_cases.py',
                'tests/semantics/string_offset_request_callback_plain_key_cases.py',
                'tests/semantics/string_offset_request_callback_old_key_cases.py',
                'tests/semantics/string_offset_request_callback_text_key_cases.py')]
        if args.request_callback_request_key:
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_request_key_cases.py',
                'tests/semantics/string_offset_request_callback_request_key_review.py',
                'tests/semantics/string_offset_request_callback_plain_key_cases.py',
                'tests/semantics/string_offset_request_callback_old_key_cases.py',
                'tests/semantics/string_offset_request_callback_text_key_cases.py')]
    if args.request_callback_raw_key_cell_owner:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_raw_key_cell_owner_cases.py',
            'tests/semantics/string_offset_request_callback_raw_key_cell_owner_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.request_callback_marked_raw_key_cell_owner:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_raw_key_cell_owner_cases.py',
            'tests/semantics/string_offset_request_callback_marked_raw_key_cell_owner_cases.py',
            'tests/semantics/string_offset_request_callback_marked_raw_key_cell_owner_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.request_callback_reference_raw_key_cell_owner:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_request_callback_reference_raw_key_cell_owner_cases.py',
            'tests/semantics/string_offset_request_callback_reference_raw_key_cell_owner_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.literal_callback_raw_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_literal_callback_raw_key_cases.py',
            'tests/semantics/string_offset_literal_callback_raw_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.variable_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_variable_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_variable_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.reference_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_reference_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_reference_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.conditional_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_conditional_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.string_conditional_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_string_conditional_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_string_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.coalesce_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_coalesce_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_coalesce_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.raw_truth_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_raw_truth_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_raw_truth_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_zero_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.folded_boolean_not_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_folded_boolean_not_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_folded_boolean_not_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.raw_truth_conditional_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_raw_truth_conditional_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_raw_truth_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.integer_division_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_integer_division_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_integer_division_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.integer_binary_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_integer_binary_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_integer_binary_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.integer_bitnot_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_integer_bitnot_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_integer_bitnot_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.integer_conditional_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.float_unary_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_float_unary_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_float_unary_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.float_arithmetic_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_float_arithmetic_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_float_arithmetic_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.numeric_arithmetic_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.numeric_unary_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_numeric_unary_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_numeric_unary_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.numeric_string_unary_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_numeric_string_unary_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_numeric_string_unary_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.folded_scalar_boolean_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_folded_scalar_boolean_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_folded_scalar_boolean_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py',
            'tests/semantics/string_offset_undefined_cv_review.py',
            'tests/semantics/string_offset_folded_scalar_comparison_truth_base_initial_raw_leading_key_peer_review.py')]
    if args.folded_scalar_comparison_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_folded_scalar_comparison_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_folded_scalar_comparison_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py',
            'tests/semantics/string_offset_undefined_cv_review.py')]
    if args.coercive_integer_binary_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_coercive_integer_binary_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_coercive_integer_binary_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py',
            'tests/semantics/string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_peer_review.py')]
    if args.boolean_null_unary_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_null_unary_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_null_unary_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    if args.coercive_integer_bitnot_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_coercive_integer_bitnot_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_coercive_integer_bitnot_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py',
            'tests/semantics/string_offset_retained_carrier_cases.py')]
    if args.coercive_integer_unary_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.coercive_integer_arithmetic_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.coercive_arithmetic_truth_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_coercive_arithmetic_truth_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_coercive_arithmetic_truth_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.float_conditional_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.null_conditional_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_null_conditional_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_null_conditional_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.null_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_null_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_null_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.false_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_false_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_false_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.integer_zero_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_integer_zero_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_integer_zero_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.float_zero_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_float_zero_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_float_zero_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.negative_zero_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_negative_zero_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_negative_zero_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.unary_plus_zero_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_unary_plus_zero_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_unary_plus_zero_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_true_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_true_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_true_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_integer_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_integer_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_integer_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_integer_unary_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_integer_unary_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_integer_unary_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_true_unary_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_true_unary_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_true_unary_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_float_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_float_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_float_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.boolean_not_string_shorthand_base_initial_raw_leading_key:
        watched += [ROOT / name for name in (
            'tests/semantics/string_offset_boolean_not_string_shorthand_base_initial_raw_leading_key_cases.py',
            'tests/semantics/string_offset_boolean_not_string_shorthand_base_initial_raw_leading_key_review.py',
            'tests/semantics/string_offset_retained_carrier_protocol.py')]
    if args.peer:
        if args.strings:
            from string_offset_current_marked_string_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_current_marked_string_cv_peer_review.py')
        elif args.arrays:
            from string_offset_current_marked_array_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_current_marked_array_cv_peer_review.py')
        elif args.variable_base:
            from string_offset_variable_base_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_variable_base_cv_peer_review.py')
        elif args.undefined_throw:
            from string_offset_undefined_throw_peer_review import render as render_peer
        elif args.variable_throw:
            from string_offset_variable_throw_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_variable_throw_peer_review.py')
        elif args.request_base:
            from string_offset_request_base_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_base_cv_peer_review.py')
        elif args.request_throw:
            from string_offset_request_throw_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_throw_peer_review.py')
        elif args.request_release:
            from string_offset_request_release_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_release_cv_peer_review.py')
        elif args.request_release_registered:
            from string_offset_request_release_registered_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_release_registered_cv_peer_review.py')
        elif args.request_release_prior:
            from string_offset_request_release_prior_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')
        elif args.request_release_distinct:
            from string_offset_request_release_distinct_cv_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_release_distinct_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_release_key:
            from string_offset_request_release_key_cv_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_release_key_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_distinct_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_release_callback:
            from string_offset_request_release_callback_cv_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_release_callback_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_key_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_distinct_cv_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_callback_owner:
            from string_offset_request_callback_owner_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_owner_cv_peer_review.py')
        elif args.request_callback_cast_owner:
            from string_offset_request_callback_cast_owner_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_cast_owner_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_callback_known_key:
            from string_offset_request_callback_known_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_known_key_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_known_key_release:
            from string_offset_request_known_key_release_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_known_key_release_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_variable_key_release:
            from string_offset_request_variable_key_release_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_variable_key_release_peer_review.py',
                'tests/semantics/string_offset_request_release_prior_cv_peer_review.py')]
        elif args.request_callback_rebound_key:
            from string_offset_request_callback_rebound_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_rebound_key_peer_review.py')
        elif args.request_callback_referenced_key:
            from string_offset_request_callback_referenced_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_referenced_key_peer_review.py')
        elif args.request_callback_late_reference:
            from string_offset_request_callback_late_reference_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_late_reference_peer_review.py')
        elif args.request_callback_scalar_key:
            from string_offset_request_callback_scalar_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_scalar_key_peer_review.py')
        elif args.request_callback_ordinary_key:
            from string_offset_request_callback_ordinary_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_ordinary_key_peer_review.py')
        elif args.request_callback_text_key:
            from string_offset_request_callback_text_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_request_callback_text_key_peer_review.py',
                'tests/semantics/string_offset_request_callback_ordinary_key_peer_review.py')]
        elif args.request_callback_old_key:
            from string_offset_request_callback_old_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_old_key_peer_review.py')
        elif args.request_callback_plain_key:
            from string_offset_request_callback_plain_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_plain_key_peer_review.py')
        elif args.request_callback_request_key:
            from string_offset_request_callback_request_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_request_key_peer_review.py')
        elif args.request_callback_marked_request_key:
            from string_offset_request_callback_marked_request_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_marked_request_key_peer_review.py')
        elif args.request_callback_marked_interned_key:
            from string_offset_request_callback_marked_interned_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_marked_interned_key_peer_review.py')
        elif args.request_callback_reference_raw_key:
            from string_offset_request_callback_reference_raw_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_reference_raw_key_peer_review.py')
        elif args.request_callback_ordinary_raw_key:
            from string_offset_request_callback_ordinary_raw_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_ordinary_raw_key_peer_review.py')
        elif args.request_callback_raw_message_key:
            from string_offset_request_callback_raw_message_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_raw_message_key_peer_review.py')
        elif args.request_callback_raw_key_cell_owner:
            from string_offset_request_callback_raw_key_cell_owner_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_raw_key_cell_owner_peer_review.py')
        elif args.request_callback_marked_raw_key_cell_owner:
            from string_offset_request_callback_marked_raw_key_cell_owner_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_marked_raw_key_cell_owner_peer_review.py')
        elif args.request_callback_reference_raw_key_cell_owner:
            from string_offset_request_callback_reference_raw_key_cell_owner_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_request_callback_reference_raw_key_cell_owner_peer_review.py')
        elif args.literal_callback_raw_key:
            from string_offset_literal_callback_raw_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_literal_callback_raw_key_peer_review.py')
        elif args.initial_raw_leading_key:
            from string_offset_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_initial_raw_leading_key_peer_review.py')
        elif args.variable_base_initial_raw_leading_key:
            from string_offset_variable_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_variable_base_initial_raw_leading_key_peer_review.py')
        elif args.reference_base_initial_raw_leading_key:
            from string_offset_reference_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_reference_base_initial_raw_leading_key_peer_review.py')
        elif args.conditional_base_initial_raw_leading_key:
            from string_offset_conditional_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_conditional_base_initial_raw_leading_key_peer_review.py')
        elif args.shorthand_base_initial_raw_leading_key:
            from string_offset_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.string_conditional_base_initial_raw_leading_key:
            from string_offset_string_conditional_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_string_conditional_base_initial_raw_leading_key_peer_review.py')
        elif args.coalesce_base_initial_raw_leading_key:
            from string_offset_coalesce_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_coalesce_base_initial_raw_leading_key_peer_review.py')
        elif args.raw_truth_shorthand_base_initial_raw_leading_key:
            from string_offset_raw_truth_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_raw_truth_shorthand_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_zero_shorthand_base_initial_raw_leading_key_peer_review.py')]
        elif args.folded_boolean_not_truth_base_initial_raw_leading_key:
            from string_offset_folded_boolean_not_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_folded_boolean_not_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.raw_truth_conditional_base_initial_raw_leading_key:
            from string_offset_raw_truth_conditional_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_raw_truth_conditional_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.integer_division_truth_base_initial_raw_leading_key:
            from string_offset_integer_division_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_integer_division_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.integer_binary_truth_base_initial_raw_leading_key:
            from string_offset_integer_binary_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_integer_binary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.integer_bitnot_truth_base_initial_raw_leading_key:
            from string_offset_integer_bitnot_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_integer_bitnot_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.integer_conditional_base_initial_raw_leading_key:
            from string_offset_integer_conditional_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')
        elif args.float_unary_truth_base_initial_raw_leading_key:
            from string_offset_float_unary_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_float_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.float_arithmetic_truth_base_initial_raw_leading_key:
            from string_offset_float_arithmetic_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_float_arithmetic_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.numeric_arithmetic_truth_base_initial_raw_leading_key:
            from string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.numeric_unary_truth_base_initial_raw_leading_key:
            from string_offset_numeric_unary_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_numeric_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.numeric_string_unary_truth_base_initial_raw_leading_key:
            from string_offset_numeric_string_unary_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_numeric_string_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_numeric_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.folded_scalar_boolean_truth_base_initial_raw_leading_key:
            from string_offset_folded_scalar_boolean_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_folded_scalar_boolean_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.folded_scalar_comparison_truth_base_initial_raw_leading_key:
            from string_offset_folded_scalar_comparison_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_folded_scalar_comparison_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.coercive_integer_binary_truth_base_initial_raw_leading_key:
            from string_offset_coercive_integer_binary_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_coercive_integer_binary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.boolean_null_unary_truth_base_initial_raw_leading_key:
            from string_offset_boolean_null_unary_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_boolean_null_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.coercive_integer_bitnot_truth_base_initial_raw_leading_key:
            from string_offset_coercive_integer_bitnot_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_coercive_integer_bitnot_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.coercive_integer_unary_truth_base_initial_raw_leading_key:
            from string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_coercive_integer_unary_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.coercive_integer_arithmetic_truth_base_initial_raw_leading_key:
            from string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_coercive_integer_arithmetic_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_integer_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.coercive_arithmetic_truth_base_initial_raw_leading_key:
            from string_offset_coercive_arithmetic_truth_base_initial_raw_leading_key_peer_review import render as render_peer
            watched += [ROOT / name for name in (
                'tests/semantics/string_offset_coercive_arithmetic_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_numeric_arithmetic_truth_base_initial_raw_leading_key_peer_review.py',
                'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_peer_review.py')]
        elif args.float_conditional_base_initial_raw_leading_key:
            from string_offset_float_conditional_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_float_conditional_base_initial_raw_leading_key_peer_review.py')
        elif args.null_conditional_base_initial_raw_leading_key:
            from string_offset_null_conditional_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_null_conditional_base_initial_raw_leading_key_peer_review.py')
        elif args.null_shorthand_base_initial_raw_leading_key:
            from string_offset_null_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_null_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.false_shorthand_base_initial_raw_leading_key:
            from string_offset_false_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_false_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.integer_zero_shorthand_base_initial_raw_leading_key:
            from string_offset_integer_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_integer_zero_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.float_zero_shorthand_base_initial_raw_leading_key:
            from string_offset_float_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_float_zero_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.negative_zero_shorthand_base_initial_raw_leading_key:
            from string_offset_negative_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_negative_zero_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.unary_plus_zero_shorthand_base_initial_raw_leading_key:
            from string_offset_unary_plus_zero_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_unary_plus_zero_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_true_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_true_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_true_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_integer_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_integer_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_integer_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_integer_unary_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_integer_unary_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_integer_unary_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_true_unary_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_true_unary_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_true_unary_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_float_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_float_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_float_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key_peer_review.py')
        elif args.boolean_not_string_shorthand_base_initial_raw_leading_key:
            from string_offset_boolean_not_string_shorthand_base_initial_raw_leading_key_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_boolean_not_string_shorthand_base_initial_raw_leading_key_peer_review.py')
        else:
            from string_offset_current_marked_cv_peer_review import render as render_peer
            watched.append(ROOT / 'tests/semantics/string_offset_current_marked_cv_peer_review.py')
        selected_render = render_peer
    before = {str(path): digest(path) for path in watched}
    report = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'case_id': selected_case['id'], 'strings': args.strings, 'arrays': args.arrays,
        'variable_base': args.variable_base,
        'undefined_throw': args.undefined_throw,
        'variable_throw': args.variable_throw,
        'request_base': args.request_base,
        'request_throw': args.request_throw,
        'request_release': args.request_release,
        'request_release_registered': args.request_release_registered,
        'request_release_prior': args.request_release_prior,
        'request_release_distinct': args.request_release_distinct,
        'request_release_key': args.request_release_key,
        'request_release_callback': args.request_release_callback,
        'request_callback_owner': args.request_callback_owner,
        'request_callback_cast_owner': args.request_callback_cast_owner,
        'request_callback_known_key': args.request_callback_known_key,
        'request_known_key_release': args.request_known_key_release,
        'request_variable_key_release': args.request_variable_key_release,
        'request_callback_rebound_key': args.request_callback_rebound_key,
        'request_callback_referenced_key': args.request_callback_referenced_key,
        'request_callback_late_reference': args.request_callback_late_reference,
        'request_callback_scalar_key': args.request_callback_scalar_key,
        'request_callback_ordinary_key': args.request_callback_ordinary_key,
        'request_callback_text_key': args.request_callback_text_key,
        'request_callback_old_key': args.request_callback_old_key,
        'request_callback_plain_key': args.request_callback_plain_key,
        'request_callback_request_key': args.request_callback_request_key,
        'request_callback_marked_request_key': args.request_callback_marked_request_key,
        'request_callback_marked_interned_key': args.request_callback_marked_interned_key,
        'request_callback_raw_message_key': args.request_callback_raw_message_key,
        'request_callback_ordinary_raw_key': args.request_callback_ordinary_raw_key,
        'request_callback_reference_raw_key': args.request_callback_reference_raw_key,
        'request_callback_raw_key_cell_owner': args.request_callback_raw_key_cell_owner,
        'request_callback_marked_raw_key_cell_owner': args.request_callback_marked_raw_key_cell_owner,
        'request_callback_reference_raw_key_cell_owner': args.request_callback_reference_raw_key_cell_owner,
        'literal_callback_raw_key': args.literal_callback_raw_key,
        'initial_raw_leading_key': args.initial_raw_leading_key,
        'variable_base_initial_raw_leading_key': args.variable_base_initial_raw_leading_key,
        'reference_base_initial_raw_leading_key': args.reference_base_initial_raw_leading_key,
        'conditional_base_initial_raw_leading_key': args.conditional_base_initial_raw_leading_key,
        'shorthand_base_initial_raw_leading_key': args.shorthand_base_initial_raw_leading_key,
        'string_conditional_base_initial_raw_leading_key': args.string_conditional_base_initial_raw_leading_key,
        'coalesce_base_initial_raw_leading_key': args.coalesce_base_initial_raw_leading_key,
        'raw_truth_shorthand_base_initial_raw_leading_key': args.raw_truth_shorthand_base_initial_raw_leading_key,
        'folded_boolean_not_truth_base_initial_raw_leading_key': args.folded_boolean_not_truth_base_initial_raw_leading_key,
        'raw_truth_conditional_base_initial_raw_leading_key': args.raw_truth_conditional_base_initial_raw_leading_key,
        'integer_division_truth_base_initial_raw_leading_key': args.integer_division_truth_base_initial_raw_leading_key,
        'integer_binary_truth_base_initial_raw_leading_key': args.integer_binary_truth_base_initial_raw_leading_key,
        'integer_bitnot_truth_base_initial_raw_leading_key': args.integer_bitnot_truth_base_initial_raw_leading_key,
        'integer_conditional_base_initial_raw_leading_key': args.integer_conditional_base_initial_raw_leading_key,
        'float_unary_truth_base_initial_raw_leading_key': args.float_unary_truth_base_initial_raw_leading_key,
        'float_arithmetic_truth_base_initial_raw_leading_key': args.float_arithmetic_truth_base_initial_raw_leading_key,
        'numeric_arithmetic_truth_base_initial_raw_leading_key': args.numeric_arithmetic_truth_base_initial_raw_leading_key,
        'numeric_unary_truth_base_initial_raw_leading_key': args.numeric_unary_truth_base_initial_raw_leading_key,
        'numeric_string_unary_truth_base_initial_raw_leading_key': args.numeric_string_unary_truth_base_initial_raw_leading_key,
        'coercive_arithmetic_truth_base_initial_raw_leading_key': args.coercive_arithmetic_truth_base_initial_raw_leading_key,
        'coercive_integer_arithmetic_truth_base_initial_raw_leading_key': args.coercive_integer_arithmetic_truth_base_initial_raw_leading_key,
        'coercive_integer_unary_truth_base_initial_raw_leading_key': args.coercive_integer_unary_truth_base_initial_raw_leading_key,
        'coercive_integer_bitnot_truth_base_initial_raw_leading_key': args.coercive_integer_bitnot_truth_base_initial_raw_leading_key,
        'boolean_null_unary_truth_base_initial_raw_leading_key': args.boolean_null_unary_truth_base_initial_raw_leading_key,
        'coercive_integer_binary_truth_base_initial_raw_leading_key': args.coercive_integer_binary_truth_base_initial_raw_leading_key,
        'folded_scalar_comparison_truth_base_initial_raw_leading_key': args.folded_scalar_comparison_truth_base_initial_raw_leading_key,
        'folded_scalar_boolean_truth_base_initial_raw_leading_key': args.folded_scalar_boolean_truth_base_initial_raw_leading_key,
        'float_conditional_base_initial_raw_leading_key': args.float_conditional_base_initial_raw_leading_key,
        'null_conditional_base_initial_raw_leading_key': args.null_conditional_base_initial_raw_leading_key,
        'null_shorthand_base_initial_raw_leading_key': args.null_shorthand_base_initial_raw_leading_key,
        'false_shorthand_base_initial_raw_leading_key': args.false_shorthand_base_initial_raw_leading_key,
        'integer_zero_shorthand_base_initial_raw_leading_key': args.integer_zero_shorthand_base_initial_raw_leading_key,
        'float_zero_shorthand_base_initial_raw_leading_key': args.float_zero_shorthand_base_initial_raw_leading_key,
        'negative_zero_shorthand_base_initial_raw_leading_key': args.negative_zero_shorthand_base_initial_raw_leading_key,
        'unary_plus_zero_shorthand_base_initial_raw_leading_key': args.unary_plus_zero_shorthand_base_initial_raw_leading_key,
        'boolean_not_true_shorthand_base_initial_raw_leading_key': args.boolean_not_true_shorthand_base_initial_raw_leading_key,
        'boolean_not_integer_shorthand_base_initial_raw_leading_key': args.boolean_not_integer_shorthand_base_initial_raw_leading_key,
        'boolean_not_integer_unary_shorthand_base_initial_raw_leading_key': args.boolean_not_integer_unary_shorthand_base_initial_raw_leading_key,
        'boolean_not_true_unary_shorthand_base_initial_raw_leading_key': args.boolean_not_true_unary_shorthand_base_initial_raw_leading_key,
        'boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key': args.boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key,
        'boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key': args.boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key,
        'boolean_not_float_shorthand_base_initial_raw_leading_key': args.boolean_not_float_shorthand_base_initial_raw_leading_key,
        'boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key': args.boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key,
        'boolean_not_string_shorthand_base_initial_raw_leading_key': args.boolean_not_string_shorthand_base_initial_raw_leading_key,
        'inputs': before, 'mode': 'production SL fixture' if (args.request_release_prior or args.request_release_distinct or args.request_release_key or args.request_release_callback or args.request_callback_owner or args.request_callback_cast_owner or args.request_callback_known_key or args.request_known_key_release or args.request_variable_key_release or args.request_callback_rebound_key or args.request_callback_referenced_key or args.request_callback_late_reference or args.request_callback_scalar_key or args.request_callback_ordinary_key or args.request_callback_text_key or args.request_callback_old_key or args.request_callback_plain_key or args.request_callback_request_key or args.request_callback_marked_request_key or args.request_callback_marked_interned_key or args.request_callback_raw_message_key or args.request_callback_ordinary_raw_key or args.request_callback_reference_raw_key or args.request_callback_raw_key_cell_owner or args.request_callback_marked_raw_key_cell_owner or args.request_callback_reference_raw_key_cell_owner or args.literal_callback_raw_key or args.initial_raw_leading_key or args.variable_base_initial_raw_leading_key or args.reference_base_initial_raw_leading_key or args.conditional_base_initial_raw_leading_key or args.shorthand_base_initial_raw_leading_key or args.string_conditional_base_initial_raw_leading_key or args.coalesce_base_initial_raw_leading_key or args.raw_truth_shorthand_base_initial_raw_leading_key or args.folded_boolean_not_truth_base_initial_raw_leading_key or args.raw_truth_conditional_base_initial_raw_leading_key or args.integer_division_truth_base_initial_raw_leading_key or args.integer_binary_truth_base_initial_raw_leading_key or args.integer_bitnot_truth_base_initial_raw_leading_key or args.integer_conditional_base_initial_raw_leading_key or args.float_unary_truth_base_initial_raw_leading_key or args.float_arithmetic_truth_base_initial_raw_leading_key or args.numeric_arithmetic_truth_base_initial_raw_leading_key or args.numeric_unary_truth_base_initial_raw_leading_key or args.numeric_string_unary_truth_base_initial_raw_leading_key or args.coercive_arithmetic_truth_base_initial_raw_leading_key or args.coercive_integer_arithmetic_truth_base_initial_raw_leading_key or args.coercive_integer_unary_truth_base_initial_raw_leading_key or args.coercive_integer_bitnot_truth_base_initial_raw_leading_key or args.boolean_null_unary_truth_base_initial_raw_leading_key or args.coercive_integer_binary_truth_base_initial_raw_leading_key or args.folded_scalar_comparison_truth_base_initial_raw_leading_key or args.folded_scalar_boolean_truth_base_initial_raw_leading_key or args.float_conditional_base_initial_raw_leading_key or args.null_conditional_base_initial_raw_leading_key or args.null_shorthand_base_initial_raw_leading_key or args.false_shorthand_base_initial_raw_leading_key or args.integer_zero_shorthand_base_initial_raw_leading_key or args.float_zero_shorthand_base_initial_raw_leading_key or args.negative_zero_shorthand_base_initial_raw_leading_key or args.unary_plus_zero_shorthand_base_initial_raw_leading_key or args.boolean_not_true_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_true_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key or args.boolean_not_float_shorthand_base_initial_raw_leading_key or args.boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_string_shorthand_base_initial_raw_leading_key) else 'AL fixture',
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'source_credit': 0, 'passed': False}
    if args.request_callback_scalar_key:
        report['case_ids'] = [case['id'] for case in cases]
        report['premise_count_scope'] = 'written helper conditions plus three concrete source invocations; no unique aggregate'
    if args.request_callback_rebound_key:
        report['reference_control'] = {'path': str(control_source),
            'origin': 'tests/semantics/string_offset_request_callback_rebound_key_cases.py:CONTROL',
            'scope': 'initial-reference live old-wrapper payload returns b', 'source_credit': 0}
    elif control_source is not None:
        report['derived_source'] = {'path': str(control_source), 'parent': str(source),
            'change': 'replace the sole outer key CV with literal true', 'source_credit': 0}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            checked_scalars = []
            for extra_source in scalar_sources:
                parsed_extra = frontend.request({'op':'parse', 'source':base64.b64encode(extra_source.read_bytes()).decode()})
                assert parsed_extra['accepted']
                checked_scalars.append(adapter.request({'op':'check', 'ast':parsed_extra['ast'], 'fixture':True}))
            if control_source is not None:
                parsed_control = frontend.request({'op': 'parse',
                    'source': base64.b64encode(control_source.read_bytes()).decode()})
                assert parsed_control['accepted']
                checked_control = adapter.request({'op': 'check', 'ast': parsed_control['ast'], 'fixture': True})
        finally:
            adapter.close()
        program = out / 'original.program'
        program.write_text(checked['fixture'])
        generated = [program]
        render_args = [checked['fixture'], base64.b64encode(bytes(source)).decode()]
        for i, (extra_source, checked_extra) in enumerate(zip(scalar_sources, checked_scalars, strict=True)):
            extra_program = out / ('scalar-' + str(i) + '.program')
            extra_program.write_text(checked_extra['fixture'])
            generated.append(extra_program)
            render_args += [checked_extra['fixture'], base64.b64encode(bytes(extra_source)).decode()]
        if control_source is not None:
            control_program = out / 'literal-key-control.program'
            control_program.write_text(checked_control['fixture'])
            generated.append(control_program)
            render_args += [checked_control['fixture'], base64.b64encode(bytes(control_source)).decode()]
        fixture = out / 'continuation.watsup'
        text, report['premises'], report['derived_conditions'] = selected_render(*render_args)
        fixture.write_text(text)
        generated.append(fixture)
        report['generated'] = {str(path): digest(path) for path in generated}
        report['compiler'] = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo',
            *map(str, modules), str(fixture)], out / 'compiler', 120)
        assert report['compiler']['exit'] == 0 and not report['compiler']['timeout']
        assert not (out / 'compiler.stderr').read_bytes()
        assert b'def $main' in (out / 'compiler.stdout').read_bytes()
        report['execution'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
            *(['--sl'] if (args.request_release_prior or args.request_release_distinct or args.request_release_key or args.request_release_callback or args.request_callback_owner or args.request_callback_cast_owner or args.request_callback_known_key or args.request_known_key_release or args.request_variable_key_release or args.request_callback_rebound_key or args.request_callback_referenced_key or args.request_callback_late_reference or args.request_callback_scalar_key or args.request_callback_ordinary_key or args.request_callback_text_key or args.request_callback_old_key or args.request_callback_plain_key or args.request_callback_request_key or args.request_callback_marked_request_key or args.request_callback_marked_interned_key or args.request_callback_raw_message_key or args.request_callback_ordinary_raw_key or args.request_callback_reference_raw_key or args.request_callback_raw_key_cell_owner or args.request_callback_marked_raw_key_cell_owner or args.request_callback_reference_raw_key_cell_owner or args.literal_callback_raw_key or args.initial_raw_leading_key or args.variable_base_initial_raw_leading_key or args.reference_base_initial_raw_leading_key or args.conditional_base_initial_raw_leading_key or args.shorthand_base_initial_raw_leading_key or args.string_conditional_base_initial_raw_leading_key or args.coalesce_base_initial_raw_leading_key or args.raw_truth_shorthand_base_initial_raw_leading_key or args.folded_boolean_not_truth_base_initial_raw_leading_key or args.raw_truth_conditional_base_initial_raw_leading_key or args.integer_division_truth_base_initial_raw_leading_key or args.integer_binary_truth_base_initial_raw_leading_key or args.integer_bitnot_truth_base_initial_raw_leading_key or args.integer_conditional_base_initial_raw_leading_key or args.float_unary_truth_base_initial_raw_leading_key or args.float_arithmetic_truth_base_initial_raw_leading_key or args.numeric_arithmetic_truth_base_initial_raw_leading_key or args.numeric_unary_truth_base_initial_raw_leading_key or args.numeric_string_unary_truth_base_initial_raw_leading_key or args.coercive_arithmetic_truth_base_initial_raw_leading_key or args.coercive_integer_arithmetic_truth_base_initial_raw_leading_key or args.coercive_integer_unary_truth_base_initial_raw_leading_key or args.coercive_integer_bitnot_truth_base_initial_raw_leading_key or args.boolean_null_unary_truth_base_initial_raw_leading_key or args.coercive_integer_binary_truth_base_initial_raw_leading_key or args.folded_scalar_comparison_truth_base_initial_raw_leading_key or args.folded_scalar_boolean_truth_base_initial_raw_leading_key or args.float_conditional_base_initial_raw_leading_key or args.null_conditional_base_initial_raw_leading_key or args.null_shorthand_base_initial_raw_leading_key or args.false_shorthand_base_initial_raw_leading_key or args.integer_zero_shorthand_base_initial_raw_leading_key or args.float_zero_shorthand_base_initial_raw_leading_key or args.negative_zero_shorthand_base_initial_raw_leading_key or args.unary_plus_zero_shorthand_base_initial_raw_leading_key or args.boolean_not_true_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_true_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_arithmetic_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_integer_arithmetic_shorthand_base_initial_raw_leading_key or args.boolean_not_float_shorthand_base_initial_raw_leading_key or args.boolean_not_numeric_string_unary_shorthand_base_initial_raw_leading_key or args.boolean_not_string_shorthand_base_initial_raw_leading_key) else []),
            *map(str, modules), str(fixture)], out / 'state', 180)
        report['passed'] = (report['execution']['exit'] == 0 and not report['execution']['timeout']
            and (out / 'state.stdout').read_bytes() == b'true\n'
            and not (out / 'state.stderr').read_bytes())
        report['generated_stable'] = report['generated'] == {str(path): digest(path) for path in generated}
        report['passed'] = report['passed'] and report['generated_stable']
    finally:
        frontend.close()
        report['inputs_stable'] = before == {str(path): digest(path) for path in watched}
        report['head_stable'] = report['head'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['premises'], 'pass' if report['passed'] else 'fail')
    assert report['passed']


if __name__ == '__main__':
    main()
