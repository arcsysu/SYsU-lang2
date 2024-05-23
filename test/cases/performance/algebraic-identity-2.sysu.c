#include <sysy/sylib.h>

int loopCount = 0;

int func()
{
  int result = 0;
  int i = 1;
  while(i<loopCount)
  {
    int sum = 0;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    sum = sum + i * 1 + 1 * i + i / 1 + i % 1 + i * 0 + 0 * i + 0 / i;
    result = result + sum;
    result = result / 2;
    i = i + 1;
  }
  return result;
}

int main()
{
  loopCount = getint();
  starttime();
  int result = func();
  stoptime();
  putint(result);
  putch(10);
  return 0;
}
