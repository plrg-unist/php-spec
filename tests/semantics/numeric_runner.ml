module Run = Runtime.Dynamic_Runner.Signature

let fail at msg =
  prerr_endline (Util.Error.string_of_error at msg);
  exit 1

let () =
  let paths = Array.to_list Sys.argv |> List.tl in
  match Backend_boot.Build.spec_of_mode Run.AL_mode paths with
  | Error error ->
      let at, msg = Pass.to_region_msg error in
      fail at msg
  | Ok spec -> (
      match Backend_boot.Build.build_null ~cache:false ~det:true
              Backend_boot.Config.SL_interface spec with
      | Error error -> fail error.at error.msg
      | Ok (module Runner) -> (
          match Runner.Interp.eval_func "main" [] [] with
          | Run.Pass value -> print_endline (Runtime.Value.to_string value)
          | Run.Fail (at, msg) -> fail at msg))
