# FreeBSD routing/firewalling on QubesOS

This is quick guide to setting up a FreeBSD VM in PVH mode as a router on Qubes 4.

The steps are laid out here chronologically and meant to be followed top-down.

As a general rule, the `dom0` commands should be run as your normal user, and the FreeBSD commands as the root user.

## Step 1: Install FreeBSD

To begin you will need FreeBSD installed as a "stand-alone" VM.
There should be guides for this, but basically:

Download a FreeBSD iso (I used `12.1-RELEASE disc1`) to a vm, mine is called `myvm` (you can use a disposable VM if you like) and create a loopback device for the iso to let us expose it to the standalone vm:
```
# myvm:
sudo losetup -f --show disc1.iso
# it output "/dev/loop0"
```

I named my FreeBSD machine `fbsd` for this guide:
```
# dom0:
qvm-create --label green --standalone fbsd
qvm-prefs fbsd memory 1000
qvm-prefs fbsd maxmem 1000
qvm-prefs fbsd provides_network True # that is the ambition
qvm-start --cdrom myvm:loop0
```

The only thing you really need to pay attention to is that you probably want:
1) `sshd`, since we'll need to retrieve the kernel in a later step
2) to install on `UFS`, not `ZFS`. I couldn't get ZFS to boot in PVH mode, although that's probably just me being stupid.
3) To configure the networking manually. If you open the QubesManager application in dom0 after starting `fbsd` you can learn its intended IP address. Netmask `255.255.255.0`, gateway is whatever the IP of the NetVM you connected it to has (in the manager view).

You can also get these using e.g. `qvm-prefs fbsd ip` and `qvm-prefs fbsd visible_gateway`. Note that `gateway` is something else, likely the gateway address your clients, I'm not sure.

## Step 2: Configure FreeBSD

```
# fbsd:
pkg install xe-guest-utilities
sysrc xenguest_enable=YES

# configure a xen console device:
echo 'xc0   "/usr/libexec/getty Pc"   vt100   onifexists secure' >> /etc/ttys
```

Now we need to upload `/boot/kernel/kernel` to `dom0`.
I used SSH to `scp` it from `fbsd` to `myvm`.

And then you can precede to:
```
# fbsd:
poweroff
```

QubesOS being slightly linux-centric, we need to set up a directory structure that mimics various Linux kernels, and will refuse to boot if there is no `initramfs` file for example:

```
# dom0
mkdir /var/lib/qubes/vm-kernels/fbsdkernel
qvm-run -p myvm 'cat disc1.iso' > /var/lib/qubes/vm-kernels/fbsdkernel/vmlinuz
truncate -s 16M /var/lib/qubes/vm-kernels/fbsdkernel/initramfs

qvm-prefs fbsd kernel 'fbsdkernely'
qvm-prefs fbsd kernelopts ''
qvm-prefs fbsd virt_mode 'pvh'
qvm-start fbsd
```

## Step 3: Resurrecting your FreeBSD machine in PVH mode

To use your new fancy console from dom0:
```
# dom0:

# Install socat - note that you can probably use 'screen' or whatever,
# I first tried that and miserably failed, so here goes:
sudo qubes-dom0-update socat

## 'virsh ttyconsole' translates behind the scenes to:
## 'xenstore-read /local/domain/$domid/console/tty'
## It gives you the location of the pty that xen has allocated for
## the fbsd vm's console in dom0
sudo socat stdin,raw,echo=0 file:$(sudo virsh ttyconsole fbsd),echo=0

# (you likely want to save that last command as that's how you will be
#  talking to this VM unless you come up with something better)
# (( you probably also want to type 'resizewin' as the first thing you do ))
```

It'll likely be stuck complaining that it can't figure out how to boot, and drop you in a `mountboot>` prompt because the block devices are now using a different driver or something.
This is the part I couldn't get working with ZFS, but with UFS is was simple enough:
```
mountboot> ufs:xbd0s1a
```

If that works, make sure to alter your /etc/fstab accordingly. If not, I have no idea.

If you're having trouble you can switch it back to booting in HVM mode:
```
qvm-prefs fbsd kernel ''
qvm-prefs fbsd kernelopts ''
qvm-prefs fbsd virt_mode 'hvm'
qvm-start fbsd
```

# Step 4: Xenstore crash course

Xen comes with a pretty basic key-value store that VMs (called "domains") can use to share information with each other. Each VM is allocated an id at each boot (meaning that it likely changes for each boot). The only domain that has a fixed id is the privileged domain ("dom0") since it's always the first to start, hence the name.

There's a bunch of different `xenstore-` tools that came with `xen-guest-tools` which got pulled in by the `xe-guest-utilities` package that we installed in step 2.
You don't need to familiarize yourself with all of these, but the TL;DR is that:
- `xenstore-list` is a bit like `ls`;
- `xenstore-read` is like `cat`;
- `xenstore-ls` is a bit like `find -print -execdir cat {} \;`, it recursively lists and reads entries.

# Step 5: Pulling IPs from xenstore

```
# fbsd:

# find our current domain id:
domid=$(xenstore-read domid)

# (I got '87' this time around)

Check out which keys are available in our domain's namespace:
xenstore-list /local/domain/$domid
```

We are now ready for our first network client!
Start a disposable VM to use for this exercise, mine got the name `disp3905`, and assign `fbsd` as the upstream for this.
```
# dom0:
qvm-prefs disp3905 netvm fbsd
```

Let's see what that looks like in FreeBSD:
```
# fbsd:
ifconfig
# should show something like xnb90.0
# the 90 is the domid of the client

# we can list the connected clients with e.g.
xenstore-ls /local/domain/$domid/backend/vif
```

We are predominantly interested in the keys that have the `online=1` property.

Since I was goofing around with generating pf configs dynamically I wrote this Python script to parse the output (not required to follow the tutorial). If you want to play with that you will need `pkg install python3`.

```python3
import subprocess
domid = subprocess.getoutput('xenstore-read domid')
full = subprocess.getoutput(f'xenstore-ls -f /local/domain/{domid}/backend/vif').splitlines()
nice = {}
for line in full:
  path, value = line.split(' = ')
  cursor = nice # reference to output dict
  skip = len(['','local','domain',domid,'backend','vif'])
  for node in path.split(r'/')[skip:]:
    if node not in cursor: cursor[node] = {}
    cursor = cursor[node]
  value = '"'.join(value.split('"')[1:-1]) # fingers crossed
  if value: cursor['val'] = value

# pull ip for our client:
# >>> nice['90']['0']['ip']['val']
# '10.138.15.65'
```

In QubesOS, all VMs have exactly one IP address (by default at least), so we can copy the one from our upstream interface, or we can pull it from xenstore:
```
# fbsd:

# note that what the Linux people call 'eth0' is probably
# called 'xn0' for you:
xenstore-read /local/domain/$domid/attr/eth0/ip
# my fbsd machine is supposed to use 10.137.0.38

# We assign this address to the host-side of the newly
# connected client:
ifconfig xnb90.0 10.137.0.38

# this means both xn0 and xnb90.0 will have the same address.
```

Now we can talk to the client, and they can talk to us.

**NB:** The default firewall policy for the debian appvms is to block incoming packets, so to debug you can turn that off:

```
# disp3905 / client vm:
iptables -F INPUT
iptables -P INPUT ACCEPT
```

# Step 6: Internet!

Cool, now we are able to ping each other!
But not the rest of the world yet.

Here's my `pf` config that you should probably add actual firewall rules to to avoid domains connecting to each other, and/or spoofed packet weirdness between domains or the upstream gateway:

```pf
# put this in /etc/pf.conf in the fbsd domain

ext_if=xn0

# remember to substitute your own:
fbsd_ip=10.137.0.38

nat on $ext_if from ! $fbsd_ip to any -> $fbsd_ip
```

```
# fbsd:

sysrc pf_enable=YES
sysrc pf_rules=/etc/pf.conf
sysrc gateway_enable=YES
service pf start
```

If all that went well, your disposable VM should now have a connection to the internet. Everything else left as an exercise to the reader, feel free to leave comments, suggestions, corrections in the "Issues" tab on this repository, and improvements in the "Pull requests" tab. Thank you!
