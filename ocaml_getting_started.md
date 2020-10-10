Bootstrap an OCaml programming environment on a debian system from scratch.

```shell
sudo apt install --no-install-recommends mccs ocaml-nox opam

export OPAMDOWNLOADJOBS=10

opam init --enable-shell-hook --enable-completion --shell-setup --bare

opam switch list-available

opam switch create 4.07.1 --solver=mccs

opam install $(
    # editor:
  ) tuareg merlin ocp-index $(
    # REPL:
  ) down omod ocp-browser cmitomli $(
    # mirage-related:
  ) mirage mirage-protocols-lwt mirage-flow-lwt tcpip tls \
    tsdl mirage-unix mirage-xen $(
    # common utilities for running test suites:
  ) alcotest crowbar ounit

echo '#use "omod.top";;' >> ~/.ocamlinit
echo '#use "down.top";;' >> ~/.ocamlinit
```


