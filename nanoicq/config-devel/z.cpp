
#include <iostream>

using namespace std;

void as_bin(const int bb) {
    for(int ii = sizeof(bb) << 3; ii >= 0; --ii) {
        if(bb & (1 << ii))
            cout << "1";
        else
            cout << "0";
    }
    cout << endl;
}

int main() {
    const int JMX = 8;
    int ii = 29;

    for(int jj = 0; jj < JMX; ++jj) {
        cout << "j = " << jj << ", " << ii << " << " << jj << " = " << (ii << jj) << endl;
    }

    cout << endl;

    for(int jj = 0; jj < JMX; ++jj) {
        cout << "j = " << jj << ", " << jj << " << " << ii << " = " << (jj << ii) << endl;
    }

    cout << endl;

    for(int jj = 0; jj < JMX * 2; ++jj) {
        cout << "j = " << jj << ", " << ii << " & " << jj << " = " << (ii & jj) << endl;
    }

    cout << endl;

    for(int jj = 0; jj < JMX; ++jj) {
        cout << "j = " << jj << ", " << ii << " | " << jj << " = " << (ii | jj) << endl;
    }

    cout << endl;

//    for(int jj = 0; jj < JMX; ++jj) {
//        cout << "j = " << jj << ", " << jj << " << " << ii << " = " << (jj << ii) << endl;
//    }

    //cout << "64 * 8 = " << (64 * 8) << endl;
    //cout << "64 * 16 = " << (64 * 16) << endl;

    as_bin(29);
    //as_bin(69);

    return 0;
}
