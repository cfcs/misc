#!/usr/bin/env ocaml


(* experiment with fast and unsafe GADT equality *)
(* see: https://ocaml.godbolt.org/z/grLqeS *)

type _ rr =
  Int : int rr | Floating : float rr | Str : string rr

type ('x,'y) order =
  | Lt : ('x,'y) order
  | Eq : ('x,'x) order
  | Gt : ('x,'y) order

(* This seems to compile to a mostly branch-free subroutine
  according to Godbolt:
  camlExample__compare_unsafe_11:
.L100:
  subq %rbx, %rax
  incq %rax
  movq $2, %rbx
  subq %rax, %rbx
  shrq $62, %rbx
  orq $1, %rbx
  shrq $62, %rax
  orq $1, %rax
  movq $4, %rdi
  subq %rax, %rdi
  leaq -1(%rdi,%rbx), %rax
  ret
*)

let compare_unsafe : type a b. a rr -> b rr -> (a, b) order = fun t t' ->
  let x = (Obj.magic t : int) - (Obj.magic t':int) in
  (* Lt: 0 Eq: 1 Gt: 2*)
  (* 1 if negative sign is set (lt): *)
  let negative = x lsr (Sys.int_size -1) in
  (* 1 if negative sign is not set, and is not 0,
     NB this doesn't work for x = min_int: *)
  let positive = -x lsr (Sys.int_size -1) in
  (* default to 1 (eq), include modifiers: *)
  let actual = 1 - negative + positive in
  Obj.magic actual


(* naive implementation:
  camlExample__compare_safe_48:
.L106:
  sarq $1, %rax
  cmpq $1, %rax
  je .L103
  jg .L102
.L105:
  cmpq $1, %rbx
  je .L104
  movq $1, %rax
  ret
.L104:
  movq $3, %rax
  ret
.L103:
  orq $1, %rbx
  movq camlExample__1@GOTPCREL(%rip), %rax
  movq -4(%rax,%rbx,4), %rax
  ret
.L102:
  cmpq $5, %rbx
  jl .L101
  movq $3, %rax
  ret
.L101:
  movq $5, %rax
  ret
*)
let compare_safe : type a b. a rr -> b rr -> (a,b) order = fun t t' ->
  match t, t' with
  | Int, Int -> Eq
  | Floating, Floating -> Eq
  | Str, Str -> Eq
  | Int, Floating -> Lt
  | Int, Str -> Lt
  | Floating, Int -> Gt
  | Floating, Str -> Lt
  | Str, Int -> Gt
  | Str, Floating -> Gt

let print_order (type a) (type b) (a:a rr) (b:b rr) =
  let p : (a,b) order -> unit = function
  | Lt -> print_endline "lt"
  | Eq -> print_endline "eq"
  | Gt -> print_endline "gt"
  in
  p (compare_safe a b) ;
  p (compare_unsafe a b)

let () =
  print_order Str Floating

