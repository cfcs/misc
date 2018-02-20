#! /bin/sh
RSYNC="rsync -az --delete-excluded --delete"
$RSYNC "$@" ftp.rfc-editor.org::rfcs-text-only ~/usr/share/ietf/in-notes/
$RSYNC "$@" ftp.rfc-editor.org::ids-text-only ~/usr/share/ietf/internet-drafts/
