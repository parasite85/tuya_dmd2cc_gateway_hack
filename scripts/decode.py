#!/bin/env python3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def swapPos(list, pos1, pos2):
    list[pos1], list[pos2] = list[pos2], list[pos1]
    return list

def getKey():
    f_key = open("License.key", mode="rb")
    key = list(f_key.read())
    print("key before change")
    print(list(map(hex,key)))
    swapPos(key,0,8);swapPos(key,1,9);
    swapPos(key,2,10);swapPos(key,3,11);

    swapPos(key,4,12);swapPos(key,5,13);
    swapPos(key,6,14);swapPos(key,7,15);

    # swap bytes
    converted = bytearray([])
    for i in range(int(len(key)/2)):
        converted += bytearray([ key[i*2+1], key[i*2] ])
    print("key after change")
    print(list(map(hex,converted)))
    return bytes(converted)

def getData():
    # validation of data can be added
    # basically, at the beginning of license file
    # there is 4 byte magic cookie next, 4 byte length
    # and at the end also 4 bytes magic
    f_data = open("License.file1", mode="rb")
    data = list(f_data.read())[8:-4]
    print("Encrypted data");
    print(list(map(hex,data)))
    return bytes(data)

key = getKey()
data = getData()
decipher = AES.new(key, AES.MODE_ECB)
decoded = decipher.decrypt(data)
print("Decrypted data")
print(decoded)
f_outdata = open("License.out", mode="wb")
f_outdata.write(decoded)
