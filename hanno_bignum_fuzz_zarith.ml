(* try some testcases from https://github.com/hannob/bignum-fuzz *)
#require "zarith";;
#require "num";;
open Z;;
let of_hex = of_string_base 16;;
let to_num z = Z.to_string z |> Num.num_of_string;;

let z_f : 'a * 'b * 'c * 'd * 'e * 'f * 'g * 'h * 'i * 'j =
   Z.(of_hex, mul, div_rem, add, sub, equal, zero, powm, pow, (fun i -> i));;
let num_f = Num.( (fun x -> of_hex x |> to_num) , mult_num,
    (fun a b -> div_num a b, mod_num a b),
    add_num, sub_num, eq_num, num_of_int 0,
    (fun a b c -> power_num c (mult_num a b)), power_num,
    num_of_int
  );;
(* bignum-fuzz/CVE-2016-1938-nss-mp_div.c *)
let nss_mp_div (of_hex, mul, div_rem, add, sub, equal, zero, powm, pow, ii) a_s b_s =
  let a , b = of_hex a_s , of_hex b_s in
  let res1 , res2 = div_rem a b in
  let res3 = mul b res1 in
  let res4 = add res3 res2 in
  let res5 = sub res4 a in
  equal res5 zero , equal res4 a, a_s, b_s;;
nss_mp_div z_f "10000000000000001000000000000000000000"
               "10000000000000001001" ;;
nss_mp_div num_f "10000000000000001000000000000000000000"
               "10000000000000001001" ;;

nss_mp_div z_f "801C4D3A9DE4691ADDBFC7D2D2DE2DA7114125A77FECE17FDA204B73FA3CDA4FF783AEE4453952BEF81DF7A9114125A700"
               "801C4D3A9DE4691ADDBFC7D2D2DE2DA7114125A7CEF66E9B76BAC1";;
nss_mp_div num_f "801C4D3A9DE4691ADDBFC7D2D2DE2DA7114125A77FECE17FDA204B73FA3CDA4FF783AEE4453952BEF81DF7A9114125A700"
               "801C4D3A9DE4691ADDBFC7D2D2DE2DA7114125A7CEF66E9B76BAC1";;

nss_mp_div z_f "B7B7B7B7B7B7B7B7B7B7B7939393939393939393939393939393B7B7B7B7B7B70080FFFFC1B7BAB70001B7"
               "B7B7B7B7B7B7B7B7B7B7C1B7BAB7DE00648B";;
nss_mp_div num_f "B7B7B7B7B7B7B7B7B7B7B7939393939393939393939393939393B7B7B7B7B7B70080FFFFC1B7BAB70001B7"
                 "B7B7B7B7B7B7B7B7B7B7C1B7BAB7DE00648B";;

nss_mp_div z_f "BFC7D2E66986FFFCE1B4D2DEF82CBEF80000FADACE4B73F710AED25E000004001DE9BEF81DE91DE9A9556301F7A9551C"
           "BFC7D2E66986FFFCE1B4D2DEF82CBEF81DE9A9556301F7A9551CBFC7D2E46986FFFCE1B4D2BAC1";;
nss_mp_div num_f "BFC7D2E66986FFFCE1B4D2DEF82CBEF80000FADACE4B73F710AED25E000004001DE9BEF81DE91DE9A9556301F7A9551C"
           "BFC7D2E66986FFFCE1B4D2DEF82CBEF81DE9A9556301F7A9551CBFC7D2E46986FFFCE1B4D2BAC1";;

(* bignum-fuzz/CVE-2015-3193-openssl-vs-gcrypt-modexp.c *)
let openssl_powm (of_hex, mul, div_rem, add, sub, equal, zero, powm, pow, ii) m_s b_s a_s =
  let a,b,m = of_hex a_s, of_hex b_s, of_hex m_s in
  equal (of_hex "19324B647D967D644B3219") @@ powm a b m;;

openssl_powm z_f "414141414141414141414127414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005" "02" "050505050505";;
openssl_powm num_f "414141414141414141414127414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005" "02" "050505050505";;

(* bignum-fuzz/CVE-2016-1938-nss-mp_exptmod.c *)
let nss_exptmod (of_hex, mul, div_rem, add, sub, equal, zero, powm, pow, ii) a_s b_s m_s =
  let a, b, m = of_hex a_s, of_hex b_s, of_hex m_s in
  powm a b m = (div_rem (pow a (ii (to_int b))) m |> snd) ;;
nss_exptmod z_f "80" "fc" "0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0EED0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F7C000000000000000000000000000000000000000000000000000000000000000000000000000000000000";;

nss_exptmod num_f "80" "fc" "0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0EED0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F7C000000000000000000000000000000000000000000000000000000000000000000000000000000000000";;

