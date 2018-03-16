a list of projects suggested by me, or other people, in passing conversation, that I would like to see realized :)

# *MirageOS / QubesOS integration*

- SOCKS proxy MirageOS unikernel
  - there's a [socks library](https://github.com/cfcs/ocaml-socks)

- [MirageOS](https://mirage.io) image cleaner (converting `* -> bitmap`), for inclusion in [QubesOS](https://qubes-os.org/)
  - see [qubes-convert-img](https://github.com/QubesOS/qubes-app-linux-img-converter)
  - easy! except we don't have a BMP library. see points about `imagelib` below

- wireless / wired setup
  - mirage-firewall vm
    - `WPA2` auth
    - `802.1x`?
    - handling of ?some? captive portals
  - linux stub kernel as sys-net
    - `init` process:
      - forward netlink to mirage-firewall vm
      - ethernet bridge to mirage-firewall vm

- pdf normalizer/cleaner
  - lots of pdf libs in ocaml, could whitelist stuff
  - no font rendering in OCaml, so we cannot write a layout-respecting PDF renderer
  - could look into [patoline](https://patoline.github.io/)

- jukebox unikernel ([MPD clone?](https://www.musicpd.org/))
  - there's an [mpd frontend](https://github.com/cedlemo/rameau) using [notty](https://github.com/pqwy/notty)
    - needs a mpd host unix process somewhere, so not directly usable
    - uses @cedlemo's [mpd client library](https://github.com/cedlemo/OCaml-libmpdclient)
      - if we implement an mpd server people can use custom interfaces
    - also some other [mpd thingie](https://github.com/fosu/camusical) (haven't evaluated yet)
  - prototype cross-platform audio playback available in [mirage-framebuffer-audio](https://github.com/cfcs/mirage-framebuffer-audio)
    - uses signed 16-bit PCM waves at fixed frequency. we need transcoders that can produce this.
  - we need audio format decoders (WAV takes too much space to be practical):
  - [FLAC](https://en.wikipedia.org/wiki/FLAC) decoder
    - [format / spec](https://xiph.org/flac/format.html)
    - see be
  - [Ogg](https://en.wikipedia.org/wiki/Ogg) decoder
    - ([OPUS](https://en.wikipedia.org/wiki/Opus_%28audio_format%29) / RFC 6716)
  - AAC / MP3 ? some people seem to want proprietary formats
    - I dislike proprietary formats, mostly due to lack of public documentation or reference implementations
    - [nice article about MP3](http://blog.bjrn.se/2008/10/lets-build-mp3-decoder.html)

# *Misc ~ less advanced* (maybe)
- [.po file format](http://pology.nedohodnik.net/doc/user/en_US/ch-poformat.html) for internationalization
  - parser (using [Angstrom](https://github.com/inhabitedtype/angstrom)?)
  - Fmt / Logs integration ?
  - ppx ?
- pure CRC library ([CRC-32](https://en.wikipedia.org/wiki/CRC32), `CRC16`, etc)
  - there are various pure implementations around of misc CRC variants, would be nice to have them in one place
  - [openpgp crc-24](https://github.com/cfcs/ocaml-openpgp/blob/13dfb087fc4dacec33f69cc57ef768bc0a617dd7/lib/types.ml#L708-L754)
  - fast [sRGB](https://en.wikipedia.org/wiki/SRGB)`<->`[HSV](https://en.wikipedia.org/wiki/HSL_and_HSV) (or whatever) conversions for color gradients
    - with/without floats (I'm mainly interested in *without*)
- [Sakura tree hashing (with a streaming API)](https://keccak.team/files/Sakura.pdf)
  - see [HN thread](https://news.ycombinator.com/item?id=16572793)
- qcheck `"_factorial" Gen.t` that takes a string-like `(length, sub)` module and a `type t` and returns lists of `type t` split in various permutations
- WAV decoder/transcoder
  - maybe [G.711](https://en.wikipedia.org/wiki/G.711), a simple 64kbps audio codec, patent expired
  - [.au (by Sun)](https://en.wikipedia.org/wiki/Au_file_format) is very similar
  - [Codec 2](https://en.wikipedia.org/wiki/Codec_2), a seemingly simple PCM codec used by ham radio operators
- tool to make torrents with file-aligned chunk padding, see
  - Rudy has a [Bencode library](https://github.com/rgrinberg/bencode)
  - [BEP-35: signing](http://bittorrent.org/beps/bep_0035.html)
    - [BEP039: additional signing](http://www.bittorrent.org/beps/bep_0039.html)
  - [BEP-47: padding](http://www.bittorrent.org/beps/bep_0047.html)
  - [BEP-46: updating via DHT](http://www.bittorrent.org/beps/bep_0046.html)
  - [`libtorrent make_torrent.c` example](https://libtorrent.org/examples.html)
  - [BEP-49: deletion/revision](http://bittorrent.org/beps/bep_0049.html)
- [RFC 7677: SASL/SCRAM authentication](https://tools.ietf.org/html/rfc7677)
- [imagelib](https://github.com/rlepigre/ocaml-imagelib) has a pure picture format implementations
  - JPG support in imagelib
  - GIF support in imagelib

- pure QRcode library, ideally working with imagelib
  - perhaps inspired by https://github.com/cozmo/jsQR
- [ZIP](https://en.wikipedia.org/wiki/Zip_%28file_format%29) file utility using [decompress](https://github.com/dinosaure/decompress)
- `diff`/`patch` (TODO research different formats/algorithms, does ocaml-git implement this?)
- graphviz implementation (just the layouting/positioning/coordinates, not necessarily the drawing)
- adding session resumption to [tlsping](https://github.com/cfcs/tlsping)

# *Misc ~ more advanced* (maybe)
- CI tool for determining if an opam package update breaks the API and enforces semantic versioning
  - maybe see Camelus
  - [paper on OPAM + CI](http://www.ocamlpro.com/wp-content/uploads/2016/08/ocaml2016-opam-builder.pdf)
- erlang-style bit-based pattern matching ppx
- OpenVPN implementation
  - [SoftEther implements it](https://github.com/SoftEtherVPN/SoftEtherVPN)
    - [relevent .c file](https://github.com/SoftEtherVPN/SoftEtherVPN/blob/93d9ade990bd277539138572d7f2bcccfa108407/src/Cedar/Interop_OpenVPN.c) - and the [corresponding .h file](https://github.com/SoftEtherVPN/SoftEtherVPN/blob/93d9ade990bd277539138572d7f2bcccfa108407/src/Cedar/Interop_OpenVPN.h)

- Multimedia formats;
  - video decoding: [AOMedia Video 1 (aka "AV1")](https://en.wikipedia.org/wiki/AV1) seems to be the coolest, and openest, standard
    - [VP9](https://en.wikipedia.org/wiki/VP9) is the predecessor, perhaps simpler to implement
    - TODO look into Matroska
  - audio (for chat applications?)
    - [OggPCM](https://en.wikipedia.org/wiki/OggPCM)
    - [Speex (maybe? not sure how this compares to OPUS in terms of complexity)](https://en.wikipedia.org/wiki/Speex)

- [zstd](https://en.wikipedia.org/wiki/Zstandard) compression/decompression
- investigate getting [libpqcrypto](https://libpqcrypto.org/) to work on mirage (replacing openssl with nocrypto as far as possible?)
