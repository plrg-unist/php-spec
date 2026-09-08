(* A bounded-depth wire encoding only. Inflation precedes typed AST conversion. *)
let fail () = failwith "malformed flat wire envelope"
let decode = function
  | `Assoc fields as original when List.assoc_opt "wire" fields = Some (`String "php-flat-1") ->
      if List.length fields <> 3 || List.assoc_opt "root" fields <> Some (`Int 0) then fail ();
      let rows = match List.assoc_opt "values" fields with Some (`List rows) -> Array.of_list rows | _ -> fail () in
      let values = Array.make (Array.length rows) `Null in
      let child index = function `Int ref when ref > index && ref < Array.length rows -> values.(ref) | _ -> fail () in
      for i = Array.length rows - 1 downto 0 do
        values.(i) <- (match rows.(i) with
          | `List [`Int 0; ((`Null | `Bool _ | `String _ | `Int _ | `Float _) as value)] -> value
          | `List [`Int 1; `List refs] -> `List (List.map (child i) refs)
          | `List [`Int 2; `List pairs] ->
              let fields = List.map (function `List [`String key; ref] -> key, child i ref | _ -> fail ()) pairs in
              if List.length fields <> List.length (List.sort_uniq compare (List.map fst fields)) then fail ();
              `Assoc fields
          | _ -> fail ())
      done;
      if Array.length values = 0 then fail ();
      ignore original;
      values.(0)
  | original -> original

let deep value =
  let rec loop = function
    | [] -> false
    | (_, depth) :: _ when depth > 256 -> true
    | (`List children, depth) :: rest -> loop (List.fold_left (fun rest child -> (child, depth+1) :: rest) rest children)
    | (`Assoc fields, depth) :: rest -> loop (List.fold_left (fun rest (_,child) -> (child, depth+1) :: rest) rest fields)
    | _ :: rest -> loop rest
  in loop [value, 0]

let encode value =
  if not (deep value) then value else (
    let pending = Queue.create () in
    let count = ref 1 and rows = ref [] in
    Queue.add value pending;
    let add child = let index = !count in incr count; Queue.add child pending; `Int index in
    while not (Queue.is_empty pending) do
      let row = match Queue.take pending with
        | `List children -> `List [`Int 1; `List (List.map add children)]
        | `Assoc fields -> `List [`Int 2; `List (List.map (fun (key,child) -> `List [`String key; add child]) fields)]
        | scalar -> `List [`Int 0; scalar] in
      rows := row :: !rows
    done;
    `Assoc ["wire", `String "php-flat-1"; "root", `Int 0; "values", `List (List.rev !rows)])
