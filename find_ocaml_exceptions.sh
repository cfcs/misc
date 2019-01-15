#!/usr/bin/env bash
set -u
tmp="$(mktemp)"
ocamlpp "$1" > "$tmp"
export i=0
for f in $(<"$tmp" awk "$(cat <<'EOL'
 /^$/ {for(x in c) {c[x]=0}; i=0 }
 /CLOSURE/ {i+=1; c[i]=$5}
 END {for(x in c){print c[x]}}
EOL
         )")
do : $((i++))
  [ "$f" = "0" ] && continue
  echo "$i:$f: $(cmitomli "${1%.cmo}.cmi" | awk '/^val/{i+=1}i=='"$i"'{print}')"
  F="${1%.cmo}" E="$f" awk "$(cat <<'EOL'
    ($1==ENVIRON["E"]) {x=1}
    (x && /RAISE/) {
      offset = ENVIRON["i"];
      print "exception in #" offset " at bc offset", ENVIRON["E"],
            "raises", $1,$2,$3 ;
      system("cmitomli " ENVIRON["F"] ".cmi | awk '/^val/{i+=1}i==" \
                         offset "{print}'")
    }
    (x==1 && /^$/) {exit}
EOL
  )" "$tmp"
done
# TODO cleanup $tmp
