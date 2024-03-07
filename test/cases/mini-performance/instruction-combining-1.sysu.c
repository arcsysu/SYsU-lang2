#include <sysy/sylib.h>
//gcc instruction-combining.c sylib.c -include sylib.h -Wall -Wno-unused-result -o binary-instruction-combining && time ./binary-instruction-combining < instruction-combining.in
int loopCount = 0;

int func(int input, int size)
{
  input = input + 1;
  input = input + 1;
  input = input - size;
  return input;
}

int main()
{
  int sum = 0;
  int i = 0;
  loopCount = getint();
  starttime();
  while(i<loopCount)
  {
    int tmp = 0;
    int j = 0;
    while(j<60)
    {
      tmp = tmp + func(i, 2);
      j = j + 1;
    }
    tmp = tmp / 60;
    sum = sum + tmp;
    sum = sum % 536854529;
    i = i + 1;
  }
  stoptime();
  putint(sum);
  putch(10);
  return 0;
}
