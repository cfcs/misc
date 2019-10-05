(* OCaml *)
(* usage:
ocaml branchless_hex.ml
*)

let nibble_to_int ch : int =
  (*
camlExample__nibble_to_int_1199:
        addq    $-32, %rax
        andq    $-65, %rax
        movq    %rax, %rbx
        andq    $45, %rbx
        shrq    $4, %rbx
        orq     $1, %rbx
        imulq   $71, %rbx
        subq    %rbx, %rax
        addq    $71, %rax
        ret
*)
  let x =
    let x =
      let i = Char.code ch in
      (i + 39 - 1 - 54) in
    x land (lnot 0x20) in
  x - (((x land 0x16) lsr 4) * 71)
  (*let x =
    (*let i = Char.code ch in
      (i lor 0b11110000) land (lnot 0x20) in*)
    let x =
      let i = Char.code ch in
      ((i-1) lor ~-16) in
    x land (lnot 0x20) in
  (x - (((x land 0x16) lsr 4) * 71)) land 0xf*)

let to_hex_nibble f : char =
  (*

*)
  let a = 86 + f in
  let c = 1 + ((a - 71 * ((a land 0x10) lsr 4)) lor 0x20) in
  (* avoid plt indirection: *)
  Char.unsafe_chr (c land 0xff)

let () =
  let nibbles = String.init 16 (to_hex_nibble) in
  print_endline nibbles ;
  List.iteri
    (fun idx num ->
       print_int idx ; print_string " -> ";
       print_int num ; print_endline "")
    (List.init (String.length nibbles)
       (fun i -> nibble_to_int nibbles.[i]))
