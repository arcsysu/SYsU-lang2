#include <sysy/sylib.h>
//gcc integer-divide-optimization.c sylib.c -include sylib.h -Wall -Wno-unused-result -o binary-integer-divide-optimization && time ./binary-integer-divide-optimization < integer-divide-optimization.in
int loopCount = 0;
int multi = 2;
int size = 1000;

int func(int i1, int i2) 
{
    i1 = i1 / 2;
    i2 = i2 / 2;
    return i1 + i2;
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
    while(j<300)
    {
      tmp = tmp + func(i*multi, i*multi);
      j = j + 1;
    }
    tmp = tmp / 300;
    sum = sum + tmp;
    sum = sum % 2147385347;
    i = i + 1;
  }
  stoptime();
  putint(sum);
  putch(10);
  return 0;
}
