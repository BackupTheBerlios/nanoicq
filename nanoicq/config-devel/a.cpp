
#include <algorithm>
#include <iostream>
#include <string>

using namespace std;

template <class K, class D>
class A {
    typedef typename D inner;

public:
    void w() { cout << "A<K, D>" << endl; }

    template <class Y> friend
        void ff(A<class K, class D>& a);

    template <class Z> void f(Z val) {
        cout << "f(Z)" << endl;
    }
    template <> void f(int val) {
        cout << "f(int)" << endl;
    }
    template <> void f(char* val) {
        cout << "f(char*)" << endl;
    }
};

template <class D>
class A<char*, D> {
public:
    void w() { cout << "A<char*, D>" << endl; }
};

template <class K>
class A<K, string> {
public:
    void w() { cout << "A<K, string>" << endl; }
};

template <class Y> void ff(A<K, D>& a, const Y& val) {
    cout << "A<K, D>::f<D>()" << endl;
}

int main() {
    A<int, int> a1;
    a1.w();

    A<int, char*> a2;
    a2.w();

    A<char*, int> a3;
    a3.w();

    A<int, string> a4;
    a4.w();

    //A<char*, string> a5;
    //a5.w();

    //A<int, int>& a11 = a1;
    //
    //f(a11, 1);


    char* junk1;
    const char* junk2;
    a1.f(1.1);    
    a1.f(1);    
    a1.f("ab");    
    a1.f(junk1);    
    a1.f(junk2);    

    int i = 20;
    cout << (i<<3) << ":" << (i * 8) << endl;

    return 0;
}
