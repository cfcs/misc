openssl genpkey -algorithm ed25519 | openssl pkey -pubout | \
grep -v '^-' | base64 -d | tail -c +13 | sed '1s,^, ,' | base64 | sed 's,^,ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA,' | ssh-keygen -e -f /dev/stdin

# strip the PEM stuff
# decode the base64
# strip the DER-encoded OID prefix (static, +13 bytes)
# add a 0x20 (length of key) to the first line (1s)
# re-encode
# add ssh key prefix + base64-encoded key header (uint32 len ; "ssh-ed25519" ; uint32 len (0x00 00 00 20) of key)

