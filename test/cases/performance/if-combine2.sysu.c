#include <sysy/sylib.h>
int func(int n) {
    int sum = 0;
    int i = 200;
    int j = 0;
    int s[16];
    int m = 0;
   
    while (m < 16){
        s[m] = 0;
        m=m+1;
    }
    while(j < n) {
        if (i > 1){
            s[1] = 1;
            if (i > 2){
                s[2] = 2;
                if (i > 3){
                    s[3] = 3;
                    if (i > 4){
                        s[4] = 4;
                        if (i > 5){
                            s[5] = 5;
                            if (i > 6){
                                s[6] = 6;
                                if (i > 7){
                                    s[7] = 7;
                                    if (i > 8){
                                        s[8] = 8;
                                        if (i > 9){
                                            s[9] = 9;
                                            if (i > 10){
                                                s[10] = 10;
                                                if (i > 11){
                                                    s[11] = 11;
                                                    if (i > 12){
                                                        s[12] = 12;
                                                        if (i > 13){
                                                            s[13] = 13;
                                                            if (i > 14){
                                                                s[14] = 14;
                                                                if (i > 15){
                                                                    s[15] = 15;
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        j=j+1;
        int m = 0;
        while (m < 16){
            sum = sum + s[m];
            m=m+1;
        }
        sum = sum % 1024;

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

