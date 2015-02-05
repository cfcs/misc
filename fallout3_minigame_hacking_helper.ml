#!/usr/bin/env ocaml
(* the post-apocalyptic video game Fallout 3 has a mini-game resembling a reduced version of Mastermind
   this script helps solve the puzzle by using a meet-in-the-middle algorithm to determine the best guesses.

   sample session:
crazy
plays
plans
grave
trees
coats
grows
class
clans
claws
calls
crass
craft
cross
clump

Best guess: [trees] (3/15) candidates: calls, clans, class, claws, clump, coats, craft, crass, crazy, cross, grave, grows, plans, plays, trees
trees 2
Best guess: [grows] (1/3) candidates: crass, cross, grows
grows 3
Solution found: cross

*)

open List

let find_words_matching_num_with words num word =
  List.filter ( fun w ->
    let matched = ref 0 in
    for i = 0 to (String.length word) -1 do
      if String.get word i = String.get w i then
        incr matched
      else ()
    done ;
    num = !matched
  ) words

let () =
let words = ref [] in
let word_len = ref 0 in
let rec loop = function | "" -> ()
(* read initial list of words *)
| w -> words := String.trim w :: !words ; loop (input_line stdin)
in let () = loop "." in

let words = List.filter
(* determine word length from first word; use to eliminate crap input *)
  (fun w -> w <> "." &&
   match !word_len with
   | 0 -> word_len := String.length w ; true
   | x -> String.length w = x)
  (List.sort String.compare (!words)) in

let rec new_word_entered words =
(* main input loop *)
  if List.length words = 1 then
    Printf.printf "Solution found: %s\n" (List.hd words)
  else
  let best_guess = ref (0, "none") in
  let () = List.iter (fun w ->
    Printf.printf "\n%s: " w ;
    for i = 1 to !word_len -1 do
    (* if no best match is found for "one matching letter", we keep trying *)
      match (find_words_matching_num_with words i w) with
      | [] -> ()
      | matches ->
        let n   = List.length matches in
        let words_f = float_of_int (List.length words) in
        let best_guess_f     = (float_of_int (fst !best_guess)) /. words_f in
        let new_best_guess_f = min (abs_float (-0.5 +. best_guess_f))
                                   (abs_float (-0.5 +. (float_of_int n) /. words_f ))
        in (* "meet in the middle": find guess that is closest to eliminating half the possibilities *)
        if new_best_guess_f <> best_guess_f
        then best_guess := (n, w) else ();
        Printf.printf "\n\t||%d: %d|| " i n;
        List.iter (fun w -> Printf.printf "%s, " w) matches
    done
  ) words in
  let () = Printf.printf "\nBest guess: [%s] (%d/%d) candidates: %s\n%!" (snd !best_guess) (fst !best_guess) (List.length words) (String.concat ", " words) in
  let input = input_line stdin in
  (* read "[guess] [space] [amount of matching characters]" *)
  let idx   = String.index input ' ' in
  let word , similar  = String.( sub input 0 idx , sub input (idx+1) (((length input)-idx)-1) ) in
  let words = find_words_matching_num_with words (int_of_string similar) word in
  new_word_entered words
in
  new_word_entered words

