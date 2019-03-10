#!/usr/bin/env ocaml




(* OCaml implementation of the LZW decompression function from GIF87a *)
(* See gif_lzw_decoder.py for the Python implementation. *)



let rec lzw_stream v (remain,o,x,lzw_counter,lzw_code_size,lzw_min_size) =
  (* # lzw_code_size: current bitlength we read
     # lzw_counter: the amount of symbols we have read using lzw_code_size
     # lzw_min_size: the original bitlength we read
     # vlw: variable-length word bitlength (lzw_code_size + 1)
     # v:   decompressed value (may be partial, when remain = 0)
     # x:   compressed input string
     # o:   bit offset
     # *)
  let char_idx = o / 8 and (<<) = (lsl) and (>>) = (lsr) and (&),(%) = (land),(mod) in
  if char_idx >= String.length x then
    `need_more
  else
    let o,v, remain  =
      let vlw = lzw_code_size + 1 in
      let o_mod = o mod 8
      and current_byte = int_of_char x.[char_idx] in
      if o_mod + vlw <= 8 then
        let mask ~mask i = ((1 << mask) -1) & i in
        o + remain, (* <- o *)
        ((mask ~mask:remain (current_byte >> o_mod)) << (vlw-remain)) lor v,
        0           (* <- remain*)
      else
        let vikanta = 8 - o_mod in
        o   + vikanta, (* <- o *)
        ((current_byte >> (8 - vikanta)) << (vlw - remain)) lor v,
        vlw - vikanta  (* <- remain *)
    in if 0 = remain then begin
      if v = (1 << lzw_min_size) + 1 then
        `finish
      else
        let lzw_counter, lzw_code_size =
          if lzw_counter = (1 << lzw_code_size) -1 then 0, succ lzw_code_size
          else lzw_counter, lzw_code_size
        in `next ((lzw_code_size+1, o, x, lzw_counter+1,
                   lzw_code_size, lzw_min_size), v)
    end else begin
      Printf.printf "v: %d o: %d remain: %d\n%!" v o remain ;
      lzw_stream v (remain,o,x,lzw_counter,lzw_code_size,lzw_min_size)
    end

let goparse buf ~lzw_min_size=
  begin match
      lzw_stream 0 ((lzw_min_size+1),0,buf,0, lzw_min_size, lzw_min_size) with
  | `next (state, clear) when clear = 1 lsl lzw_min_size -> state
  | _ -> failwith "oops" end
  |> let rec loop acc v state =
    match lzw_stream v state with
    | `next (state, value) -> loop (value::acc) 0 state
    | `finish -> List.rev acc
    | `need_more -> failwith "corrupted image"
  in loop [] 0

let () =
  let gif = "\x90\x21\x17\xca\x3b\xcd\x00\x25\xc8\x1a\x49\x04"
  and lzw_min_size = 4 in
  List.iter (fun x -> print_newline();(@@)print_int x) (goparse gif ~lzw_min_size)
