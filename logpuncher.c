// PoC log truncator, not usable atm

#define _GNU_SOURCE
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>

#include <stdio.h>

int main(int argc, char **argv)
{
  if(argc < 3){
    usage_and_exit:
    printf("Usage: %s 100M file1 [file2..]\n", argv[0]);
    exit(1);
  }

  size_t size_arg_len = strlen(argv[1]);
  if(size_arg_len < 1)
    goto usage_and_exit;

  size_t size_digit_len = strspn(argv[1], "0123456789");
  if( size_digit_len < (size_arg_len-1) || 0 == size_digit_len)
    goto usage_and_exit;

  errno = 0;
  off_t len_cap = strtoll(argv[1], NULL, 10);
  if(0 != errno)
    goto usage_and_exit;

  switch(toupper( argv[1][size_digit_len] )){
    case 'T': len_cap *= 1024;
    case 'G': len_cap *= 1024;
    case 'M': len_cap *= 1024;
    case 'K': len_cap *= 1024;
  }

  printf("len cap: %Ld\n", len_cap);
  int fds[argc-2];
  for(uint i=2; i < argc; i++){
    fds[i-2] = open(argv[i], O_WRONLY);
    if(fds[i-2] < 0){
      printf("unable to open file: %s\n", argv[i]);
    }
    else
      printf("file %d: %s\n", i, argv[i]);
  }

  struct stat s;
  off_t remove_len;
  while(1){
    for(uint i = 0; i < sizeof(fds); i++){
      fstat(fds[i], &s);
      if(!S_ISREG(s.st_mode)){
        //not regular file
        exit(2);
      }
      remove_len  = s.st_size - len_cap;
      remove_len -= remove_len % s.st_blksize;
      if(remove_len > 0){
        printf("Removing %Ld out of %Ld bytes from %s", remove_len, s.st_size, argv[i+2]);

	// TODO this is where we copy (0, remove_len) to somewhere else

	if(-1 == fallocate(fds[i], FALLOC_FL_COLLAPSE_RANGE, 0, remove_len))
          perror("fallocate");
      }
    }
    sleep(2);
  }

  return 0;
}
