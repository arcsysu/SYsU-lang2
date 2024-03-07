#include <sysy/sylib.h>
int func(int n) {
    int sum = 0;
    int i = 200;
    int j = 0;
    int s[10];
    int m = 0;
   
    while (m < 10){
        s[m] = 0;
        m=m+1;
    }
    while(j < n) {
        if (i > 1){
            s[1] = 1;
            if (i > 2){
                s[2] = 2;
            }
        }
        j=j+1;
        int m = 0;
        while (m < 10){
            sum = sum + s[m];
            m=m+1;
        }
        sum = sum % 65535;

    }
    return sum;
}


int main() {
    starttime();
    int loopcount = getint();
    putint(func(loopcount));
    putch(10);
    stoptime();
    return 0;
}

