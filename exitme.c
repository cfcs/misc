/*
cc -Wall -Wpedantic exitme.c -o exitme && ./exitme
UNIX extended status word exit test
*/

#include <stdio.h>
#include <stdint.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <assert.h>

#include <unistd.h>
#include <sys/wait.h>

int
main(int argc, char**argv)
{
	pid_t me = fork();
        if (fork)
	{
		siginfo_t infop = {0};
		waitid(P_PID, me, &infop, WEXITED);
		printf("status was %x\n", infop.si_status);
	}
	printf("fork %d", me);
	_exit(0x3334);
}
