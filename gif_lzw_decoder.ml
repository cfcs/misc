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
    let clear_code = 1 lsl (lzw_code_size) in
    let end_of_information = (1 lsl lzw_min_size) + 1 in
    let _first_available_symbol = clear_code + 1 in
    let o, v, remain  =
      let o_mod = o mod 8 in
      let()=Printf.eprintf "remain:%d o:%d o_mod %d lzw_counter:%d lzw_code_size:%d lzw_min_size:%d CC:%d EOI:%d\n!" remain o o_mod lzw_counter lzw_code_size lzw_min_size clear_code end_of_information in
      let vlw = lzw_code_size + 1 in
      let current_byte = int_of_char x.[char_idx] in
      if remain + o_mod (*o_mod + vlw*) <= 8 then begin
        Printf.eprintf "o_mod + vlw <=8\n%!";
        let mask ~mask i =
          let result = ((i lsl (8-remain)) & 0xff) lsr (8-remain) in
          Printf.eprintf "mask ((%d<<%d) & 0xff) >> %d: %d\n%!" i remain remain result ;
          result in
        let next_o = o + remain in
        let next_v = ((mask ~mask:remain (current_byte >> o_mod)) << (vlw-remain)) lor v in
        let next_remain = 0 in
        Printf.eprintf "next n_o:%d n_v:%d n_remain:%d | o:%d v:%d o_mod:%d current_byte:%d remain:%d vlw:%d\n%!"
          next_o next_v next_remain o v o_mod current_byte remain vlw;
        next_o, next_v, next_remain
      end else begin
        Printf.eprintf "! <= 8\n%!" ;
        let vikanta = 8 - o_mod in
        o   + vikanta, (* <- o *)
        ((current_byte >> (8 - vikanta)) << (vlw - remain)) lor v,
        vlw - vikanta  (* <- remain *)
      end
    in if 0 = remain then begin
      if v = end_of_information then begin
        Printf.eprintf "FINISH\n%!";
        `finish
      end else begin
        let remain, lzw_counter, lzw_code_size =
          if lzw_counter = clear_code-2 then lzw_code_size+2,(-1), succ lzw_code_size
          else lzw_code_size+1,lzw_counter, lzw_code_size
        in
        Printf.eprintf "next, output v:\x1b[31;1m%d\x1b[0m lzw_code_size:%d remain:%d EOI:%d\n%!" v lzw_code_size remain end_of_information;
        `next ((remain, o, x, lzw_counter+1,
                lzw_code_size, lzw_min_size), v)
      end
    end else begin
      Printf.eprintf "recursing o:%d v:%d remain:%d\n%!" o v remain;
      lzw_stream v (remain,o,x,lzw_counter,lzw_code_size,lzw_min_size)
    end

let goparse buf ~lzw_min_size=
  let first_code_size = if lzw_min_size = 2 then 3 else lzw_min_size in
  begin match
      lzw_stream 0 ((first_code_size+1),0,buf,0,
                    first_code_size,
                    lzw_min_size) with
  | `next (state, clear) when clear = 1 lsl lzw_min_size ->
    let (remain,o,x,lzw_counter,lzw_code_size,lzw_min_size) = state in
    Printf.eprintf "next CLEAR %d (remain:%d,o:%d,lzw_counter:%d,lzw_code_size:%d,lzw_min_size:%d)\n%!" clear remain o lzw_counter lzw_code_size lzw_min_size ;
    ((lzw_min_size+1),o,x,0,lzw_min_size,lzw_min_size)
  | `next (state,_) -> (*failwith "oops"*) state
  | `need_more -> failwith "need_more"
  | `finish -> failwith "finish"
  end
  |> let rec loop acc v state =
    match lzw_stream v state with
    | `next (state, value) -> loop (value::acc) 0 state
    | `finish -> List.rev acc
    | `need_more -> failwith "corrupted image: need_more"
  in loop [] 0

let () =
  let gif = "\x90\x21\x17\xca\x3b\xcd\x00\x25\xc8\x1a\x49\x04"
  and lzw_min_size = 4 in
  let gif = (*fut fut*)
    "\x00\x07\x14\x08\xc0`\x01\x00\x04\x02\x0e<H\xd0@\x01\x01\x07\x06\x02\x02"
  and lzw_min_size = 8 in
  let gif = (*god.gif*)
    "\x90\x25\x27\xccC\xed\x045\xca\x22\x40\x04"
  and lzw_min_size = 4 in
  let gif = (* wat.gif *)
    "x8c\x8f\xa9\xcb\xed\x0f\xa3\x9c\xb4\xda\x8b\xb3\xde\xbc\xfb\x0f\x86\xe2H\x96\xe6\x89\xa6\xea\xca\xb6\xee\x0b\xc7\xf2L\xd7\xf6\x8d\xe7\xfa\xce\xf7\r\xe0\x0b\n\x87\xc4\xa2\xb1\x07\x00z\x92\xca\xa3\xf3\t\x8dJ\xa7\x89$\x88I\xcdj\xb7\xdc\xee\xc9zmz\xc7\xe4\xb2y\x0c\xfe\xa4\xcf\xec\xb6\xfb\xad[w\xe4\xf0\xba\xfd\x8eW\x8b\xe7\xfb\xbc\xff\x0f\x18h@\xb7\x81%x\x88\x98hf\xa8\xa6\xe8\xf8\x08\x19E\x981\x19iy\x89\xb9U\x99\xc9\xd9\xe9\xe9\xb3\xf9):J\xda\x12Z\x8a*Z\x00"
  and lzw_min_size = 2 in
  List.iter (fun x -> print_newline();(@@)print_int x)
    (goparse gif ~lzw_min_size)
