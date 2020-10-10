#!/usr/bin/env bash
# usage:
# git bisect start HEAD HEAD~40
# git bisect run git-ocaml-bisect.sh

# see https://git-scm.com/docs/git-bisect

# TODO git apply ./testcase.patch || exit 200

set -eu
ocaml pkg/pkg.ml build || dune build || make || exit 125 # skip
ocaml pkg/pkg.ml test || dune runtest || make test || exit 1 # bad/new

# TODO custom command || exit 1 ?
