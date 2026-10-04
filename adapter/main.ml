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
  | ListV values | TupleV values -> `List (List.map semantic_json values)
  | OptV None -> `Null
  | OptV (Some v) -> semantic_json v
  | StructV fields -> `Assoc (List.map (fun (key,v) -> Domain.Atom.string_of_atom key.it, semantic_json v) fields)
  | CaseV _ -> let tag,args = split value in `Assoc ["tag", `String tag; "args", `List (List.map semantic_json args)]
  | _ -> fail "unexpected semantic result shape"
let base64_octets bytes =
  let alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/" in
  let result = Buffer.create ((List.length bytes + 2) / 3 * 4) in
  let emit n = Buffer.add_char result alphabet.[n] in
  let rec write = function
    | a :: b :: c :: tail ->
        emit (a lsr 2); emit (((a land 3) lsl 4) lor (b lsr 4));
        emit (((b land 15) lsl 2) lor (c lsr 6)); emit (c land 63); write tail
    | [a; b] ->
        emit (a lsr 2); emit (((a land 3) lsl 4) lor (b lsr 4));
        emit ((b land 15) lsl 2); Buffer.add_char result '='
    | [a] ->
        emit (a lsr 2); emit ((a land 3) lsl 4);
        Buffer.add_string result "=="
    | [] -> () in
  write bytes;
  Buffer.contents result
let pending_from_state state =
  let json = semantic_json state in
  if string (field "tag" (field "COMPLETION" json)) <> "SOURCE_PENDING" then None
  else (
    if field "SERVICELEFT" json = `Null then fail "pending source has no remaining budget";
    let encode_field key context = list (field key context) |> List.map (fun value ->
      let n = int_of_string (string value) in
      if n < 0 || n > 255 then fail "invalid pending source byte" else n)
      |> base64_octets |> fun value -> `String value in
    if field "DIRCONTEXT" json <> `Null then
      let context = field "DIRCONTEXT" json in
      Some (`Assoc ["id", field "NONCE" context; "mode", `String "chdir";
                    "site", field "SITE" (field "CALL" context);
                    "cwd", encode_field "CWD" context;
                    "requested", encode_field "REQUESTED" context])
    else match list (field "FILECONTEXTS" json), list (field "EVALCONTEXTS" json) with
    | context :: _, _ when List.mem
        (string (field "tag" (field "PHASE" context)))
        ["FILE_RESOLVE_WAIT"; "FILE_PARSE_WAIT"] ->
        let phase = string (field "tag" (field "PHASE" context)) in
        if phase = "FILE_RESOLVE_WAIT" then
          Some (`Assoc ["id", field "NONCE" context; "mode", `String "file-resolve";
                        "caller", encode_field "CALLER" context;
                        "requested", encode_field "REQUESTED" context;
                        "cwd", encode_field "CWD" context;
                        "include_path", encode_field "INCLUDEPATH" context])
        else if phase = "FILE_PARSE_WAIT" then
          let payload key = match field key context with
            | `Null -> fail "missing opened file parser fact"
            | _ -> encode_field key context in
          Some (`Assoc ["id", field "NONCE" context; "mode", `String "file";
                        "profile", `String "cli-raw-85";
                        "requested", encode_field "REQUESTED" context;
                        "resolved", (if field "RESOLVED" context = `List [] then `Null
                                     else payload "RESOLVED");
                        "opened", payload "OPENED";
                        "source", payload "BYTES"])
        else fail "pending file source phase mismatch"
    | _, context :: _ ->
        if string (field "tag" (field "PHASE" context)) <> "PARSER_WAIT" then fail "pending source phase mismatch";
        Some (`Assoc ["id", field "UNIT" context; "mode", `String "eval";
                      "profile", `String "cli-raw-85";
                      "source", encode_field "BYTES" context])
    | _, [] -> fail "pending source has no waiting context")
let active_eval = ref None
let active_snapshot = ref None
let import_request (module Runner : Run.RUNNER) json =
  let keys = ["env"; "argv"; "file"; "seconds"; "microseconds"; "variables"; "jit"] in
  exact (if List.mem_assoc "cwd" (assoc json) then keys @ ["cwd"] else keys) json;
  let bytes json =
    match Runner.Interp.eval_func "base64" [] [bytes_value json] with
    | Run.Pass value -> check (typ "preqbytes") value; value
    | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg) in
  let pair_type = T.tuple [typ "preqbytes"; typ "preqbytes"] in
  let env = list (field "env" json) |> List.map (function
    | `List [name; value] -> V.Make.tuple pair_type [bytes name; bytes value]
    | _ -> fail "request environment entry must be a pair") in
  let argv = list (field "argv" json) |> List.map bytes in
  let microseconds = field "microseconds" json |> J.to_int in
  if microseconds < 0 then fail "negative request microseconds";
  let fields = [
    "ENV", V.Make.list (T.list pair_type) env;
    "ARGV", V.Make.list (T.list (typ "preqbytes")) argv;
    "FILE", bytes (field "file" json);
    "SECONDS", int_value (field "seconds" json);
    "MICROSECONDS", V.Make.nat (Bigint.of_int microseconds);
    "VARIABLES", bytes (field "variables" json);
    "JIT", V.Make.bool (J.to_bool (field "jit" json));
    "CWD", V.Make.opt (T.opt (typ "preqbytes")) (Option.map bytes (List.assoc_opt "cwd" (assoc json)))] in
  let value = V.Make.str (typ "prequest") (List.map (fun (name,value) -> (Domain.Atom.Keyword name $ no_region, value)) fields) in
  check (typ "prequest") value;
  value
let source_id json =
  let id = string json in
  if String.length id = 0 || (String.length id > 1 && id.[0] = '0')
     || not (String.for_all (fun c -> c >= '0' && c <= '9') id) then fail "noncanonical source request id";
  id
let source_bytes json =
  ignore (bytes_value json);
  string json
let nonempty_bytes json =
  let value = source_bytes json in
  if value = "" then fail "empty file identity";
  value
let absolute_nul_free_bytes json =
  let encoded = nonempty_bytes json in
  let alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/" in
  let decoded = Buffer.create (String.length encoded * 3 / 4) in
  for i = 0 to String.length encoded / 4 - 1 do
    let digit offset =
      let c = encoded.[4 * i + offset] in
      if c = '=' then 0 else String.index alphabet c in
    let bits = (digit 0 lsl 18) lor (digit 1 lsl 12) lor (digit 2 lsl 6) lor digit 3 in
    Buffer.add_char decoded (Char.chr ((bits lsr 16) land 255));
    if encoded.[4 * i + 2] <> '=' then Buffer.add_char decoded (Char.chr ((bits lsr 8) land 255));
    if encoded.[4 * i + 3] <> '=' then Buffer.add_char decoded (Char.chr (bits land 255))
  done;
  let path = Buffer.contents decoded in
  if path.[0] <> '/' || String.contains path '\000' then fail "invalid canonical chdir path"
let file_snapshot json =
  let version = J.to_int (field "version" json) in
  if version <> 1 && version <> 2 then fail "file snapshot version mismatch";
  exact (["version"; "main"; "cwd"; "include_path"; "entries"] @
         if version = 2 then ["chdir_entries"] else []) json;
  ignore (nonempty_bytes (field "main" json));
  ignore (nonempty_bytes (field "cwd" json));
  ignore (nonempty_bytes (field "include_path" json));
  let entries = list (field "entries" json) in
  let keys = ref [] and opened = ref [] in
  List.iter (fun entry ->
    let status = string (field "status" entry) in
    let context = if version = 2 then ["cwd"; "include_path"] else [] in
    let fields = match status with
      | "missing" -> ["caller"; "requested"] @ context @ ["status"; "stream_error"]
      | "open_failure" -> ["caller"; "requested"] @ context @ ["status"; "resolved"; "warning_path"; "stream_error"]
      | "opened" -> ["caller"; "requested"] @ context @ ["status"; "resolved"; "opened"; "source"]
      | _ -> fail "unknown file resolution status" in
    exact fields entry;
    let caller = nonempty_bytes (field "caller" entry)
    and requested = source_bytes (field "requested" entry)
    and cwd = (if version = 2 then nonempty_bytes (field "cwd" entry)
               else source_bytes (field "cwd" json))
    and include_path = (if version = 2 then nonempty_bytes (field "include_path" entry)
                        else source_bytes (field "include_path" json)) in
    if List.mem (caller, requested, cwd, include_path) !keys then fail "duplicate file resolution key";
    keys := (caller, requested, cwd, include_path) :: !keys;
    if status = "open_failure" then ignore (nonempty_bytes (field "resolved" entry));
    if status = "open_failure" then ignore (nonempty_bytes (field "warning_path" entry));
    if status = "opened" && field "resolved" entry <> `Null then
      ignore (nonempty_bytes (field "resolved" entry));
    if status = "missing" || status = "open_failure" then
      ignore (nonempty_bytes (field "stream_error" entry));
    if status = "opened" then (
      let path = nonempty_bytes (field "opened" entry)
      and source = source_bytes (field "source" entry) in
      match List.assoc_opt path !opened with
      | Some prior when prior <> source -> fail "conflicting bytes for opened file"
      | _ -> opened := (path, source) :: !opened)) entries;
  if version = 2 then (
    let dir_keys = ref [] in
    List.iter (fun entry ->
      let status = string (field "status" entry) in
      exact (match status with
        | "success" -> ["cwd"; "requested"; "status"; "next_cwd"]
        | "failure" -> ["cwd"; "requested"; "status"; "stream_error"; "errno"]
        | _ -> fail "unknown chdir status") entry;
      let cwd = nonempty_bytes (field "cwd" entry)
      and requested = source_bytes (field "requested" entry) in
      if List.mem (cwd, requested) !dir_keys then fail "duplicate chdir key";
      dir_keys := (cwd, requested) :: !dir_keys;
      if status = "success" then absolute_nul_free_bytes (field "next_cwd" entry)
      else (ignore (nonempty_bytes (field "stream_error" entry));
            if J.to_int (field "errno" entry) <= 0 then fail "invalid chdir errno"))
      (list (field "chdir_entries" json)));
  json
let check_file_resolve request =
  exact ["op"; "snapshot"; "pending"; "response"] request;
  let snapshot = file_snapshot (field "snapshot" request) in
  let pending = field "pending" request in
  exact ["id"; "caller"; "requested"; "cwd"; "include_path"] pending;
  let id = source_id (field "id" pending)
  and caller = nonempty_bytes (field "caller" pending)
  and requested = source_bytes (field "requested" pending)
  and cwd = nonempty_bytes (field "cwd" pending)
  and include_path = nonempty_bytes (field "include_path" pending) in
  let version = J.to_int (field "version" snapshot) in
  if version = 1 &&
     (cwd <> source_bytes (field "cwd" snapshot) ||
      include_path <> source_bytes (field "include_path" snapshot)) then
    fail "file resolution context differs from fixed snapshot";
  let entry = match List.find_opt (fun entry ->
      source_bytes (field "caller" entry) = caller
      && source_bytes (field "requested" entry) = requested
      && (version = 1 ||
          (source_bytes (field "cwd" entry) = cwd &&
           source_bytes (field "include_path" entry) = include_path)))
      (list (field "entries" snapshot)) with
    | Some entry -> entry | None -> fail "file resolution absent from finite snapshot" in
  let response = field "response" request in
  let expected = ("id", `String id) :: assoc entry in
  exact (List.map fst expected) response;
  if List.exists (fun (key,value) -> field key response <> value) expected then
    fail "file resolution response differs from finite snapshot";
  `Assoc (("ok", `Bool true) :: expected)
let check_chdir request =
  exact ["op"; "snapshot"; "pending"; "response"] request;
  let snapshot = file_snapshot (field "snapshot" request) in
  if J.to_int (field "version" snapshot) <> 2 then fail "chdir requires a version 2 snapshot";
  let pending = field "pending" request in
  exact ["id"; "site"; "cwd"; "requested"] pending;
  let id = source_id (field "id" pending)
  and site = field "site" pending
  and cwd = nonempty_bytes (field "cwd" pending)
  and requested = source_bytes (field "requested" pending) in
  let entry = match List.find_opt (fun entry ->
      source_bytes (field "cwd" entry) = cwd
      && source_bytes (field "requested" entry) = requested)
      (list (field "chdir_entries" snapshot)) with
    | Some entry -> entry | None -> fail "chdir absent from finite snapshot" in
  let expected = ["id", `String id; "site", site] @ assoc entry in
  let response = field "response" request in
  exact (List.map fst expected) response;
  if List.exists (fun (key,value) -> field key response <> value) expected then
    fail "chdir response differs from finite snapshot";
  `Assoc (("ok", `Bool true) :: expected)
let execute value request =
  if !active_eval <> None then fail "eval parser response still pending";
  let budget = field "steps" request |> J.to_int in
  if budget < 0 then fail "negative transition budget";
  let filename_json = field "filename" request in
  let filename = bytes_value filename_json in
  let (module Runner : Run.RUNNER) = Lazy.force semantic_runner in
  let snapshot = List.assoc_opt "file_snapshot" (assoc request) |> Option.map file_snapshot in
  Option.iter (fun facts ->
    if field "main" facts <> filename_json then fail "file snapshot main path mismatch";
    match List.assoc_opt "request" (assoc request) with
    | Some q when List.assoc_opt "cwd" (assoc q) <> Some (field "cwd" facts) ->
        fail "file snapshot request cwd mismatch"
    | _ -> ()) snapshot;
  let decode_bytes json =
    match Runner.Interp.eval_func "base64" [] [bytes_value json] with
    | Run.Pass value -> check (typ "preqbytes") value; value
    | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg) in
  let startup_json = match List.filter (fun (key,_) -> key = "startup_ini") (assoc request) with
    | [] -> None | [(_,json)] -> Some json | _ -> fail "duplicate startup INI field" in
  let startup = startup_json |> Option.map (fun json ->
    exact ["error_reporting"; "include_path"] json;
    let reporting = match field "error_reporting" json with
      | `Null -> None | value -> Some (decode_bytes value) in
    let fields = [
      "REPORTING", V.Make.opt (T.opt (typ "preqbytes")) reporting;
      "INCLUDEPATH", decode_bytes (field "include_path" json)] in
    let value = V.Make.str (typ "pstartup")
        (List.map (fun (name,value) -> Domain.Atom.Keyword name $ no_region, value) fields) in
    check (typ "pstartup") value;
    (match Runner.Interp.eval_func "startup_valid" [] [value] with
     | Run.Pass valid when V.Get.bool valid -> ()
     | Run.Pass _ -> fail "invalid startup INI facts"
     | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg));
    value) in
  Option.iter (fun facts ->
    let include_path = match startup_json with
      | None -> `String "Ljo="
      | Some json ->
          (match Runner.Interp.eval_func "c_string" [] [decode_bytes (field "include_path" json)] with
           | Run.Pass value -> `String (list (semantic_json value)
                |> List.map (fun n -> int_of_string (string n)) |> base64_octets)
           | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg)) in
    if field "include_path" facts <> include_path then
      fail "file snapshot include_path differs from startup INI") snapshot;
  let arguments = [value; V.Make.nat (Bigint.of_int budget); filename] in
  let file_arguments = [value; V.Make.nat (Bigint.of_int budget); decode_bytes filename_json] in
  let name, arguments = match List.filter (fun (key,_) -> key = "request") (assoc request) with
    | [] -> (match snapshot with
        | None -> "php_run", arguments
        | Some facts -> "php_file_run", file_arguments @ [decode_bytes (field "cwd" facts)])
    | [(_,json)] -> (match snapshot with
        | None -> "php_request_run", arguments @ [import_request (module Runner) json]
        | Some facts -> "php_request_file_run",
            file_arguments @ [import_request (module Runner) json; decode_bytes (field "cwd" facts)])
    | _ -> fail "duplicate request field" in
  let name, arguments = match startup with
    | None -> name, arguments
    | Some value ->
        (match name with
         | "php_run" -> "php_startup_run"
         | "php_request_run" -> "php_request_startup_run"
         | "php_file_run" -> "php_file_startup_run"
         | "php_request_file_run" -> "php_request_file_startup_run"
         | _ -> assert false), arguments @ [value] in
  match Runner.Interp.eval_func name [] arguments with
  | Run.Pass state -> check (typ "pstate") state;
      let pending = pending_from_state state in
      (match pending with Some request -> active_eval := Some (state, request) | None -> ());
      active_snapshot := snapshot;
      `Assoc (["ok", `Bool true; "state", semantic_json state] @
              match pending with Some request -> ["pending", request] | None -> [])
  | Run.Fail (at,msg) ->
      `Assoc ["ok", `Bool false; "category", `String "interpreter_failure";
              "message", `String (Util.Error.string_of_error at msg)]
type source_pending = { id : string; mode : string; profile : string; source : string }
let source_pending json =
  exact ["id"; "mode"; "profile"; "source"] json;
  let mode = string (field "mode" json) and profile = string (field "profile" json) in
  if mode <> "eval" || profile <> "cli-raw-85" then fail "unsupported source service mode/profile";
  { id = source_id (field "id" json); mode; profile; source = source_bytes (field "source" json) }
let check_source_service request =
  exact ["op"; "pending"; "response"] request;
  let pending = source_pending (field "pending" request) in
  let response = field "response" request in
  let accepted = match field "accepted" response with `Bool b -> b | _ -> fail "invalid parser acceptance flag" in
  exact (if accepted then ["id"; "mode"; "profile"; "source"; "accepted"; "ast"]
         else ["id"; "mode"; "profile"; "source"; "accepted"; "category"; "message"; "line"]) response;
  if source_id (field "id" response) <> pending.id
     || string (field "mode" response) <> pending.mode
     || string (field "profile" response) <> pending.profile
     || source_bytes (field "source" response) <> pending.source then fail "source response does not match pending request";
  let identity = ["id", `String pending.id; "mode", `String pending.mode;
                  "profile", `String pending.profile; "source", `String pending.source] in
  if accepted then (
    let value = import_program (field "ast" response) in
    check (typ "program") value;
    `Assoc (["ok", `Bool true; "accepted", `Bool true; "ast", export_program value] @ identity))
  else (
    let category = string (field "category" response) in
    if category <> "parser_rejection" && category <> "parser_static_rejection" then
      fail "invalid parser rejection category";
    let line = field "line" response |> J.to_int in
    if line < 1 then fail "invalid parser rejection line";
    let message = source_bytes (field "message" response) in
    `Assoc (["ok", `Bool true; "accepted", `Bool false; "category", `String category;
             "message", `String message; "line", `Int line] @ identity))
let check_file_source_service request =
  exact ["op"; "pending"; "response"] request;
  let pending = field "pending" request in
  let keys = ["id"; "mode"; "profile"; "requested"; "resolved"; "opened"; "source"] in
  exact keys pending;
  ignore (source_id (field "id" pending));
  if string (field "mode" pending) <> "file"
     || string (field "profile" pending) <> "cli-raw-85" then
    fail "unsupported file parser mode/profile";
  List.iter (fun key -> ignore (source_bytes (field key pending)))
    ["requested"; "opened"; "source"];
  if field "resolved" pending <> `Null then
    ignore (nonempty_bytes (field "resolved" pending));
  if field "opened" pending = `String "" then
    fail "empty file parser identity";
  let response = field "response" request in
  let accepted = match field "accepted" response with
    | `Bool value -> value | _ -> fail "invalid file parser acceptance flag" in
  exact (keys @ if accepted then ["accepted"; "ast"]
         else ["accepted"; "category"; "message"; "line"]) response;
  if List.exists (fun key -> field key response <> field key pending) keys then
    fail "file parser response identity mismatch";
  let identity = List.map (fun key -> key, field key pending) keys in
  if accepted then (
    let value = import_program (field "ast" response) in
    check (typ "program") value;
    `Assoc (["ok", `Bool true; "accepted", `Bool true;
             "ast", export_program value] @ identity))
  else (
    let category = string (field "category" response) in
    if category <> "parser_rejection" && category <> "parser_static_rejection" then
      fail "invalid file parser rejection kind";
    let line = field "line" response |> J.to_int in
    if line < 1 then fail "invalid file parser rejection line";
    let message = nonempty_bytes (field "message" response) in
    `Assoc (["ok", `Bool true; "accepted", `Bool false;
             "category", `String category; "message", `String message;
             "line", `Int line] @ identity))
let resume_file_resolve request =
  exact ["op"; "response"] request;
  let state, pending = match !active_eval with
    | Some active -> active | None -> fail "no pending file resolution" in
  if string (field "mode" pending) <> "file-resolve" then fail "not waiting for file resolution";
  let snapshot = match !active_snapshot with
    | Some facts -> facts | None -> fail "file resolution has no finite snapshot" in
  let identity = `Assoc ["id", field "id" pending; "caller", field "caller" pending;
                         "requested", field "requested" pending;
                         "cwd", field "cwd" pending;
                         "include_path", field "include_path" pending] in
  let checked = check_file_resolve (`Assoc ["op", `String "check_file_resolve";
                                             "snapshot", snapshot; "pending", identity;
                                             "response", field "response" request]) in
  let (module Runner : Run.RUNNER) = Lazy.force semantic_runner in
  let decode_bytes json =
    match Runner.Interp.eval_func "base64" [] [bytes_value json] with
    | Run.Pass value -> check (typ "preqbytes") value; value
    | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg) in
  let id = V.Make.nat (Bigint.of_string (source_id (field "id" pending))) in
  let caller = decode_bytes (field "caller" checked)
  and requested = decode_bytes (field "requested" checked) in
  let response = match string (field "status" checked) with
    | "missing" -> mk "pfileopenresponse" "FILE_MISSING"
        [id; caller; requested; decode_bytes (field "stream_error" checked)]
    | "open_failure" -> mk "pfileopenresponse" "FILE_OPEN_FAILURE"
        [id; caller; requested; decode_bytes (field "resolved" checked);
         decode_bytes (field "warning_path" checked);
         decode_bytes (field "stream_error" checked)]
    | "opened" -> mk "pfileopenresponse" "FILE_OPENED"
        [id; caller; requested; decode_bytes (if field "resolved" checked = `Null
                                               then `String "" else field "resolved" checked);
         decode_bytes (field "opened" checked); decode_bytes (field "source" checked)]
    | _ -> fail "unknown checked file resolution status" in
  check (typ "pfileopenresponse") response;
  match Runner.Interp.eval_func "file_open_continue" [] [state; response] with
  | Run.Pass next -> check (typ "pstate") next;
      let following = pending_from_state next in
      active_eval := Option.map (fun request -> (next, request)) following;
      `Assoc (["ok", `Bool true; "state", semantic_json next] @
              match following with Some request -> ["pending", request] | None -> [])
  | Run.Fail (at,msg) ->
      `Assoc ["ok", `Bool false; "category", `String "interpreter_failure";
              "message", `String (Util.Error.string_of_error at msg)]
let resume_chdir request =
  exact ["op"; "response"] request;
  let state, pending = match !active_eval with
    | Some active -> active | None -> fail "no pending chdir request" in
  if string (field "mode" pending) <> "chdir" then fail "not waiting for chdir";
  let snapshot = match !active_snapshot with
    | Some facts -> facts | None -> fail "chdir has no finite snapshot" in
  let identity = `Assoc ["id", field "id" pending; "site", field "site" pending;
                         "cwd", field "cwd" pending;
                         "requested", field "requested" pending] in
  let checked = check_chdir (`Assoc ["op", `String "check_chdir";
                                     "snapshot", snapshot; "pending", identity;
                                     "response", field "response" request]) in
  let (module Runner : Run.RUNNER) = Lazy.force semantic_runner in
  let decode_bytes json =
    match Runner.Interp.eval_func "base64" [] [bytes_value json] with
    | Run.Pass value -> check (typ "preqbytes") value; value
    | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg) in
  let id = V.Make.nat (Bigint.of_string (source_id (field "id" pending))) in
  let cwd = decode_bytes (field "cwd" checked)
  and requested = decode_bytes (field "requested" checked) in
  let response = match string (field "status" checked) with
    | "success" -> mk "pdirresponse" "DIR_CHANGED"
        [id; cwd; requested; decode_bytes (field "next_cwd" checked)]
    | "failure" -> mk "pdirresponse" "DIR_FAILED"
        [id; cwd; requested; decode_bytes (field "stream_error" checked);
         V.Make.nat (Bigint.of_int (J.to_int (field "errno" checked)))]
    | _ -> fail "unknown checked chdir status" in
  check (typ "pdirresponse") response;
  match Runner.Interp.eval_func "dir_continue" [] [state; response] with
  | Run.Pass next -> check (typ "pstate") next;
      let following = pending_from_state next in
      active_eval := Option.map (fun request -> (next, request)) following;
      `Assoc (["ok", `Bool true; "state", semantic_json next] @
              match following with Some request -> ["pending", request] | None -> [])
  | Run.Fail (at,msg) ->
      `Assoc ["ok", `Bool false; "category", `String "interpreter_failure";
              "message", `String (Util.Error.string_of_error at msg)]
let resume_file_parse request =
  exact ["op"; "response"] request;
  let state, pending = match !active_eval with
    | Some active -> active | None -> fail "no pending file parser request" in
  if string (field "mode" pending) <> "file" then fail "not waiting for file parser";
  let checked = check_file_source_service (`Assoc
    ["op", `String "check_file_source_service"; "pending", pending;
     "response", field "response" request]) in
  let context = match list (field "FILECONTEXTS" (semantic_json state)) with
    | head :: _ -> head | [] -> fail "file parser has no active context" in
  let unit = V.Make.nat (Bigint.of_string (string (field "UNIT" context))) in
  let (module Runner : Run.RUNNER) = Lazy.force semantic_runner in
  let decode_bytes json =
    match Runner.Interp.eval_func "base64" [] [bytes_value json] with
    | Run.Pass value -> check (typ "preqbytes") value; value
    | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg) in
  let source = decode_bytes (field "source" checked) in
  let response = if J.to_bool (field "accepted" checked) then
      mk "psourceresponse" "SOURCE_ACCEPT"
        [unit; source; import_program (field "ast" checked)]
    else (
      let constructor = match string (field "category" checked) with
        | "parser_rejection" -> "SOURCE_PARSE_REJECT"
        | "parser_static_rejection" -> "SOURCE_COMPILE_REJECT"
        | _ -> fail "invalid file parser rejection" in
      mk "psourceresponse" constructor
        [unit; source; decode_bytes (field "message" checked);
         V.Make.int (Bigint.of_int (J.to_int (field "line" checked)))]) in
  check (typ "psourceresponse") response;
  match Runner.Interp.eval_func "file_parse_continue" [] [state; response] with
  | Run.Pass next -> check (typ "pstate") next;
      let following = pending_from_state next in
      active_eval := Option.map (fun request -> (next, request)) following;
      `Assoc (["ok", `Bool true; "state", semantic_json next] @
              match following with Some request -> ["pending", request] | None -> [])
  | Run.Fail (at,msg) ->
      `Assoc ["ok", `Bool false; "category", `String "interpreter_failure";
              "message", `String (Util.Error.string_of_error at msg)]
let resume_eval request =
  exact ["op"; "response"] request;
  let state, pending = match !active_eval with
    | Some active -> active
    | None -> fail "no pending eval parser request" in
  let checked = check_source_service (`Assoc ["op", `String "check_source_service";
                                               "pending", pending; "response", field "response" request]) in
  let (module Runner : Run.RUNNER) = Lazy.force semantic_runner in
  let decode_bytes json =
    match Runner.Interp.eval_func "base64" [] [bytes_value json] with
    | Run.Pass value -> check (typ "preqbytes") value; value
    | Run.Fail (at,msg) -> fail (Util.Error.string_of_error at msg) in
  let id = V.Make.nat (Bigint.of_string (string (field "id" pending))) in
  let source = decode_bytes (field "source" pending) in
  let response = if J.to_bool (field "accepted" checked) then
      mk "psourceresponse" "SOURCE_ACCEPT" [id; source; import_program (field "ast" checked)]
    else (
      let constructor = match string (field "category" checked) with
        | "parser_rejection" -> "SOURCE_PARSE_REJECT"
        | "parser_static_rejection" -> "SOURCE_COMPILE_REJECT"
        | _ -> fail "invalid checked parser rejection" in
      mk "psourceresponse" constructor
        [id; source; decode_bytes (field "message" checked);
         V.Make.int (Bigint.of_int (J.to_int (field "line" checked)))]) in
  check (typ "psourceresponse") response;
  match Runner.Interp.eval_func "eval_continue" [] [state; response] with
  | Run.Pass next -> check (typ "pstate") next;
      let following = pending_from_state next in
      active_eval := Option.map (fun request -> (next, request)) following;
      `Assoc (["ok", `Bool true; "state", semantic_json next] @
              match following with Some request -> ["pending", request] | None -> [])
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
      else if op = "check_source_service" then check_source_service request
      else if op = "check_file_resolve" then check_file_resolve request
      else if op = "check_chdir" then check_chdir request
      else if op = "check_file_source_service" then check_file_source_service request
      else if op = "resume_file_resolve" then resume_file_resolve request
      else if op = "resume_chdir" then resume_chdir request
      else if op = "resume_file_parse" then resume_file_parse request
      else if op = "resume_eval" then resume_eval request
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
