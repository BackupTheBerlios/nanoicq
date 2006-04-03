
#include <algorithm>
#include <functional>
#include <memory>
#include <cassert>
#include <iostream>

template <class K, class D>
class PatriciaTree;


template <class K, class D>
class PatriciaTreeNode {

    typedef PatriciaTreeNode<K, D>* TPT;

    K key;
    D data;
    TPT right, left;
    int split_bit;

    friend class PatriciaTree<K, D>;

public:
    PatriciaTreeNode();
    ~PatriciaTreeNode();

    PatriciaTreeNode(const PatriciaTreeNode& ptn);
    PatriciaTreeNode& operator=(const PatriciaTreeNode& ptn);

    void setData(const D& d) {
        D tmp(d);
        std::swap<D>(data, tmp);
    }
    const D getData() const {
        return data;
    }

    bool operator==(const PatriciaTreeNode& ptn) const;
    bool operator!=(const PatriciaTreeNode& ptn) const;

    const K& getKey() const {
        return key;
    }
    const TPT getRight() const {
        return right;
    }
    const TPT getLeft() const {
        return left;
    }

};


template <class K, class D>
PatriciaTreeNode<K, D>::PatriciaTreeNode() : key(), data(), split_bit(-1) {
    right = this;
    left = this;
}

template <class K, class D>
PatriciaTreeNode<K, D>::~PatriciaTreeNode() {
    // empty
}

template <class K, class D>
PatriciaTreeNode<K, D>::PatriciaTreeNode(const PatriciaTreeNode& ptn) {
    key = ptn.key;
    data = ptn.data;
    right = ptn.right;
    left = ptn.left;
    split_bit = ptn.split_bit;
}

template <class K, class D> PatriciaTreeNode<K, D>&
PatriciaTreeNode<K, D>::operator=(const PatriciaTreeNode& ptn) {

    PatriciaTreeNode<K, D> tmp(ptn);
    std::swap(key, tmp.key);
    std::swap(data, tmp.data);
    std::swap(right, tmp.right);
    std::swap(left, tmp.left);
    std::swap(split_bit, tmp.split_bit);

    return *this;
}

template <class K, class D> bool
PatriciaTreeNode<K, D>::operator==(const PatriciaTreeNode& ptn) const {
    return (key == ptn.key &&
        data == ptn.data &&
        right == ptn.right &&
        left == ptn.left &&
        split_bit == ptn.split_bit);
}

template <class K, class D> bool
PatriciaTreeNode<K, D>::operator!=(const PatriciaTreeNode& ptn) const {
    return !operator==(ptn);
}

template <class K, class D>
class PatriciaTree {

    typedef PatriciaTreeNode<K, D> node;
    typedef node* pnode;

    pnode root;

    int getBit(K d, int n);

    template <class Y>
    bool compare(Y k1, Y k2) {
        return k1 == k2;
    }

public:
    PatriciaTree() {
        root = new node();
    }

    bool insert(K key, D data);
};

template <class K, class D>
int PatriciaTree<K, D>::getBit(K d, int n) {

    if (n < 0)
        return 2;

    const int byte = n >> 3;
    const int bit = n & 7;

    return (d[byte] & (1 << bit));

}

template <class K, class D>
bool PatriciaTree<K, D>::insert(K key, D data) {
    bool rc = false;

    pnode p = root;
    pnode r = p->right;

    while(p->split_bit < r->split_bit) {
        p = r;
        r = getBit(key, r->split_bit) ? r->right : r->left;
    }

    if(compare(key, r->key))
        return rc;

    return rc;
}

// Patricia tree insertion
// http://www.dcc.uchile.cl/~rbaeza/handbook/algs/3/3445.ins.c.html

template <class K, class D>
int PatriciaTree<K, D>::findSplitBit(const K& k1, const K& k2) {
    int byte = 0;

    for(; k1[byte] != 0 && k2[byte] != 0 && k1[byte] == k2[byte]; ++byte) {
        // empty
    }

    int bit = 0;
    for(; getBit(k1[byte], bit) != getBit(k2[byte], bit); ++bit) {
        // empty
    }

    return (8 * byte) + bit;
}

int main() {
    PatriciaTreeNode<char*, int> ptn1;
    PatriciaTreeNode<char*, int>* ptn2 = new PatriciaTreeNode<char*, int>();

    ptn2 = &ptn1;

    PatriciaTreeNode<char*, int> ptn3;
    PatriciaTreeNode<char*, int> ptn4(ptn3);

    ptn3.setData(100);
    //assert(ptn3.getData() == 100);

    PatriciaTreeNode<char*, char*> ptn5;
    ptn5.setData("abcd");

    assert(strcmp("abcd", ptn5.getData()) == 0);

    PatriciaTree<char*, int>* ptn6 = new PatriciaTree<char*, int>();
    ptn6->insert("string 100", 100);

    delete ptn6;
    std::cout << "Ok" << std::endl;

    return 0;
}

//