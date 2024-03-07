#include <sysy/sylib.h>
//gcc dead-code-elimination.c sylib.c -include sylib.h -Wall -Wno-unused-result -Wno-unused-variable -o binary-dead-code-elimination && time ./binary-dead-code-elimination < dead-code-elimination.in
int loopCount = 0;
int global = 0;

void func(int i0)
{
  int i1 = 1;
  int i2 = 2;
  int i3 = 3;
  int i4 = 4;
  global = i0;
  return;
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
    while(j<6)
    {
      func(i);
      tmp = tmp + global;
      j = j + 1;
    }
    tmp = tmp / 6;
    sum = sum + tmp;
    sum = sum % 134209537;
    i = i + 1;
  }
  stoptime();
  putint(sum);
  putch(10);
  return 0;
}
