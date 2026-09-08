open Util.Source
open Lang.Il
module V = Runtime.Value
module T = Runtime.Type.Typ.Make
module M = Domain.Mixfix
module J = Yojson.Basic.Util

let fail message = failwith message
let assoc = function `Assoc xs -> xs | _ -> fail "expected object"
let list = function `List xs -> xs | _ -> fail "expected list"
let string = function `String s -> s | _ -> fail "expected string"
let field key json = try List.assoc key (assoc json) with Not_found -> fail ("missing " ^ key)
let exact keys json =
  if List.sort compare (List.map fst (assoc json)) <> List.sort compare keys then fail "unexpected/missing fields"
let typ name = T.var (name $ no_region) []
let mk name constructor args =
  let op = constructor ^ String.concat "" (List.map (fun _ -> " x") args) in
  V.Make.(op <| args <<| name)
let int_value json =
  let s = string json in
  let n = Bigint.of_string s in
  if Bigint.to_string n <> s then fail "noncanonical integer";
  if Bigint.compare n (Bigint.of_string "-9223372036854775808") < 0
     || Bigint.compare n (Bigint.of_string "9223372036854775807") > 0 then fail "integer outside PHP 64-bit range";
  V.Make.int n
let bytes_value json =
  let s = string json in
  let alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/" in
  let len = String.length s in
  if len mod 4 <> 0 then fail "invalid base64 length";
  let pad = if len = 0 || s.[len-1] <> '=' then 0 else if len > 1 && s.[len-2] = '=' then 2 else 1 in
  for i = 0 to len-pad-1 do if not (String.contains alphabet s.[i]) then fail "invalid base64 character" done;
  if pad > 0 then (
    let digit = String.index alphabet s.[len-pad-1] in
    if digit mod (if pad = 2 then 16 else 4) <> 0 then fail "noncanonical base64 padding");
  V.Make.text s
let float_value json =
  let s = string json in
  if String.length s <> 16 || not (String.for_all (fun c -> String.contains "0123456789abcdef" c) s) then fail "invalid float bits";
  V.Make.text s

let root = Sys.argv.(1)
let schema = Yojson.Basic.from_file (root ^ "/spec/schema.json")
let nodes = assoc (field "nodes" schema)
let domains = assoc (field "domains" schema)
let metadata = assoc (field "metadata" schema)
let constructor_nodes = List.map (fun (tag,n) -> (string (field "constructor" n), (tag,n))) nodes
let definition_table = Hashtbl.create 100
let elab source =
  let result = Result.bind (Pass.parse_string source) Pass.elab_spec in
  match result with
  | Ok spec -> spec
  | Error error -> let at,msg = Pass.to_region_msg error in fail (Util.Error.string_of_error at msg)
let read_all path = let ch = open_in_bin path in Fun.protect ~finally:(fun () -> close_in ch) (fun () -> really_input_string ch (in_channel_length ch))
let source_schema = read_all (root ^ "/spec/php.watsup")
let () = List.iter (fun def -> match def.it with TypD (id, [], deftyp, _) -> Hashtbl.add definition_table id.it deftyp | _ -> ()) (elab source_schema)

(* Strict membership in the elaborated declarations. Never inspect value.note.typ:
   Make annotations are untrusted. This deliberately does not use Runtime.Type.Match. *)
let rec check expected (value : V.t) =
  match expected.it, value.it with
  | BoolT, BoolV _ | TextT, TextV _ -> ()
  | NumT `IntT, NumV (`Int _) | NumT `IntT, NumV (`Nat _) | NumT `NatT, NumV (`Nat _) -> ()
  | IterT (inner, List), ListV values -> List.iter (check inner) values
  | IterT (inner, Opt), OptV value -> Option.iter (check inner) value
  | TupleT types, TupleV values when List.length types = List.length values -> List.iter2 check types values
  | VarT (id, []), _ -> check_defined (Hashtbl.find definition_table id.it) value
  | _ -> fail ("formal type mismatch: " ^ Lang.Il.Print.string_of_typ expected)
and check_defined deftyp (value : V.t) =
  match deftyp.it, value.it with
  | PlainT expected, _ -> check expected value
  | VariantT cases, CaseV actual ->
      let op, values = M.split actual in
      let candidate = List.find_opt (fun (shape, _, _) -> Domain.Mixop.eq (M.to_mixop shape.it) op) cases in
      (match candidate with
       | None -> fail "unknown constructor or wrong arity in formal domain"
       | Some (shape, _, _) -> List.iter2 check (M.args shape.it) values)
  | StructT fields, StructV values when List.length fields = List.length values ->
      List.iter2 (fun (a,t) (b,v) -> if not (Domain.Atom.eq a.it b.it) then fail "wrong record field"; check t v) fields values
  | _ -> fail "formal constructor shape mismatch"

let domain_list_item name =
  let entries = list (List.assoc name domains) in
  let entry = match List.find_opt (function `List [`String "list"; _] -> true | _ -> false) entries with Some entry -> entry | None -> fail "list supplied to a non-list field" in
  let key = List.nth (list entry) 1 in
  fst (List.find (fun (_,v) -> v = key) domains)
let rec import name json =
  match json with
  | `Null -> mk name "ABSENT" []
  | `Bool b -> mk name "BOOLEAN" [V.Make.bool b]
  | `List xs ->
      let inner = domain_list_item name in
      mk name "SEQUENCE" [V.Make.list (T.list (typ inner)) (List.map (import inner) xs)]
  | `Assoc [("bytes", s)] -> mk name "BYTES" [bytes_value s]
  | `Assoc [("int", s)] -> mk name "INTEGER" [int_value s]
  | `Assoc [("float", s)] -> mk name "FLOAT" [float_value s]
  | `Assoc _ ->
      exact ["node"; "fields"; "meta"] json;
      let tag = string (field "node" json) in
      let contract = try List.assoc tag nodes with Not_found -> fail ("unknown node " ^ tag) in
      let fields = list (field "fields" contract) and values = list (field "fields" json) in
      if List.length fields <> List.length values then fail "wrong node arity";
      let values = List.map2 (fun f v -> import (string (field "domain" f)) v) fields values in
      mk name (string (field "constructor" contract)) (values @ [import_meta (field "meta" json)])
  | _ -> fail "untagged transport value"
and import_meta json =
  let fields = assoc json |> List.sort compare in
  if List.length fields <> List.length (List.sort_uniq compare (List.map fst fields)) then fail "duplicate metadata";
  let values = List.map (fun (key, value) ->
    let domain = try string (List.assoc key metadata) with Not_found -> fail ("unknown metadata " ^ key) in
    let payload = match domain with
      | "int" -> exact ["int"] value; int_value (field "int" value)
      | "text" -> exact ["bytes"] value; bytes_value (field "bytes" value)
      | "bool" -> V.Make.bool (J.to_bool value)
      | "comment*" -> V.Make.list (T.list (typ "comment")) (List.map import_comment (list value))
      | _ -> fail "unknown metadata domain" in
    mk "metadataEntry" ("M" ^ key) [payload]) fields in
  V.Make.list (typ "metadata") values
and import_comment json =
  exact ["comment"] json;
  match list (field "comment" json) with
  | doc :: text :: positions when List.length positions = 6 ->
      mk "comment" "COMMENT" (V.Make.bool (J.to_bool doc) :: bytes_value text :: List.map int_value positions)
  | _ -> fail "malformed comment"
let import_program json =
  let encoded = List.mem_assoc "encoding" (assoc json) in
  exact (["version"; "program"] @ if encoded then ["encoding"] else []) json;
  if field "version" json <> `Int 1 then fail "transport version mismatch";
  let statements = V.Make.list (T.list (typ "statement")) (List.map (import "statement") (list (field "program" json))) in
  if encoded then (
    let encoding = field "encoding" json in
    let spelling = List.mem_assoc "original" (assoc encoding) in
    exact (["source"; "lexer"; "bom"; "preamble"] @ if spelling then ["original"] else []) encoding;
    let args = List.map (fun key -> bytes_value (field key encoding)) ["source"; "lexer"; "bom"; "preamble"] in
    let original = V.Make.opt (T.opt T.text) (if spelling then Some (bytes_value (field "original" encoding)) else None) in
    mk "program" "ENCODEDPROGRAM" (args @ [original; statements]))
  else mk "program" "PROGRAM" [statements]

let split value =
  let op,args = M.split (V.Get.case value) in
  let words = String.split_on_char ' ' (Domain.Mixop.string_of_mixop op) in
  (String.trim (String.concat "" (String.split_on_char '`' (List.hd words))), args)
let only = function [x] -> x | _ -> fail "wrong scalar arity"
let int_json value = `String (Bigint.to_string (match V.Get.num value with `Int n | `Nat n -> n))
let rec export value =
  let tag,args = split value in
  match tag with
  | "ABSENT" -> `Null
  | "BYTES" -> `Assoc ["bytes", `String (V.Get.text (only args))]
  | "INTEGER" -> `Assoc ["int", int_json (only args)]
  | "FLOAT" -> `Assoc ["float", `String (V.Get.text (only args))]
  | "BOOLEAN" -> `Bool (V.Get.bool (only args))
  | "SEQUENCE" -> `List (List.map export (V.Get.list (only args)))
  | _ ->
      let node,_ = try List.assoc tag constructor_nodes with Not_found -> fail "unknown checked constructor" in
      let rev = List.rev args in
      let meta = List.hd rev and fields = List.rev (List.tl rev) in
      `Assoc ["node", `String node; "fields", `List (List.map export fields); "meta", export_meta meta]
and export_meta value =
  `Assoc (List.map (fun value ->
    let tag,args = split value in
    let key = String.sub tag 1 (String.length tag - 1) in
    let value = only args in
    let json = match string (List.assoc key metadata) with
      | "int" -> `Assoc ["int", int_json value]
      | "text" -> `Assoc ["bytes", `String (V.Get.text value)]
      | "bool" -> `Bool (V.Get.bool value)
      | "comment*" -> `List (List.map export_comment (V.Get.list value))
      | _ -> fail "unknown checked metadata" in (key,json)) (V.Get.list value))
and export_comment value =
  let _,args = split value in
  match args with
  | doc :: text :: positions -> `Assoc ["comment", `List (`Bool (V.Get.bool doc) :: `String (V.Get.text text) :: List.map int_json positions)]
  | _ -> fail "wrong checked comment"
let export_program value =
  let tag,args = split value in
  let values, encoding = match tag, args with
    | "PROGRAM", [statements] -> statements, []
    | "ENCODEDPROGRAM", [source; lexer; bom; preamble; original; statements] ->
        let fields = ["source", `String (V.Get.text source); "lexer", `String (V.Get.text lexer); "bom", `String (V.Get.text bom); "preamble", `String (V.Get.text preamble)] in
        let spelling = match V.Get.opt original with None -> [] | Some value -> ["original", `String (V.Get.text value)] in
        statements, ["encoding", `Assoc (fields @ spelling)]
    | _ -> fail "not program" in
  `Assoc (["version", `Int 1; "program", `List (List.map export (V.Get.list values))] @ encoding)

let rec fixture (value : V.t) =
  match value.it with
  | BoolV b -> string_of_bool b
  | NumV (`Int n) | NumV (`Nat n) -> Bigint.to_string n
  | TextV s -> "\"" ^ String.escaped s ^ "\""
  | ListV values -> "[" ^ String.concat ", " (List.map fixture values) ^ "]"
  | OptV None -> "eps"
  | OptV (Some v) -> "(" ^ fixture v ^ ")"
  | CaseV _ -> let tag,args = split value in "(" ^ tag ^ String.concat "" (List.map (fun v -> " (" ^ fixture v ^ ")") args) ^ ")"
  | _ -> fail "unsupported fixture shape"
module Run = Runtime.Dynamic_Runner.Signature
let semantic_paths () =
  let files = Yojson.Basic.from_file (root ^ "/spec/semantics/modules.json") |> list |> List.map string in
  List.map (fun path -> root ^ "/" ^ path) files
let semantic_runner = lazy (
  let paths = semantic_paths () in
  let definitions = match Pass.elab paths with
    | Ok definitions -> definitions
    | Error error -> let at,msg = Pass.to_region_msg error in fail (Util.Error.string_of_error at msg) in
  List.iter (fun def -> match def.it with
    | TypD (id, [], deftyp, _) -> Hashtbl.replace definition_table id.it deftyp
    | _ -> ()) definitions;
  let spec = match Backend_boot.Build.spec_of_mode Run.SL_mode paths with
    | Ok spec -> spec
    | Error error -> let at,msg = Pass.to_region_msg error in fail (Util.Error.string_of_error at msg) in
  match Backend_boot.Build.build_null ~cache:false ~det:true Backend_boot.Config.SL_interface spec with
  | Ok runner -> runner
  | Error error -> fail (Util.Error.string_of_error error.at error.msg))
let rec semantic_json (value : V.t) =
  match value.it with
  | BoolV b -> `Bool b
  | NumV (`Int n) | NumV (`Nat n) -> `String (Bigint.to_string n)
  | TextV s -> `String s
  | ListV values -> `List (List.map semantic_json values)
  | OptV None -> `Null
  | OptV (Some v) -> semantic_json v
  | StructV fields -> `Assoc (List.map (fun (key,v) -> Domain.Atom.string_of_atom key.it, semantic_json v) fields)
  | CaseV _ -> let tag,args = split value in `Assoc ["tag", `String tag; "args", `List (List.map semantic_json args)]
  | _ -> fail "unexpected semantic result shape"
let execute value request =
  let budget = field "steps" request |> J.to_int in
  if budget < 0 then fail "negative transition budget";
  let (module Runner : Run.RUNNER) = Lazy.force semantic_runner in
  match Runner.Interp.eval_func "php_run" [] [value; V.Make.nat (Bigint.of_int budget)] with
  | Run.Pass state -> check (typ "pstate") state;
      `Assoc ["ok", `Bool true; "state", semantic_json state]
  | Run.Fail (at,msg) ->
      `Assoc ["ok", `Bool false; "category", `String "interpreter_failure";
              "message", `String (Util.Error.string_of_error at msg)]
let () =
  try while true do
    let line = read_line () in
    let response = try
      let request = Wire.decode (Yojson.Basic.from_string line) in
      let op = string (field "op" request) in
      if op = "elaborate_fixture" then (
        ignore (elab (source_schema ^ "\ndec $fixture() : program\ndef $fixture() = " ^ string (field "fixture" request) ^ "\n"));
        `Assoc ["ok", `Bool true])
      else (
        if op <> "check" && op <> "elaborate" && op <> "execute" then fail "unknown operation";
        let value = import_program (field "ast" request) in
        check (typ "program") value;
        if op = "execute" then (try execute value request with exn ->
          `Assoc ["ok", `Bool false; "category", `String "runner_failure"; "message", `String (Printexc.to_string exn)]) else (
        let expression = if op = "elaborate" || List.mem_assoc "fixture" (assoc request) then Some (fixture value) else None in
        if op = "elaborate" then ignore (elab (source_schema ^ "\ndec $fixture() : program\ndef $fixture() = " ^ Option.get expression ^ "\n"));
        `Assoc (["ok", `Bool true; "ast", export_program value] @ match expression with None -> [] | Some text -> ["fixture", `String text])))
    with exn -> `Assoc ["ok", `Bool false; "category", `String "adapter_rejection"; "message", `String (Printexc.to_string exn)] in
    print_endline (Yojson.Basic.to_string (Wire.encode response))
  done with End_of_file -> ()
