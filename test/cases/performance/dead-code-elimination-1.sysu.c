#include <sysy/sylib.h>

int loopCount = 0;
int deadVarGlobal;

int func()
{
  int result = 0;
  int i = 0;
  while(i<loopCount)
  {
    int sum = 0;
    int deadVar = 0;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVar = (deadVar + i) % 65536;
    deadVarGlobal = deadVar;
    sum = sum + i;
    sum = sum / 3;
    result = result + sum;
    result = result % 1500000001;
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
