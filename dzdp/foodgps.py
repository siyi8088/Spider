__author__='鲲鹏数据'
#解析大众点评地图坐标参数

# -*- coding:utf-8 -*-

def to_base36(value):
    if not isinstance(value,int):
        raise TypeError('excepted int, got %s:%r'%(value.__class__.__name__,value))
    if value==0:
        return '0'
    if value<0:
        sign='-'
        value=-value
    else:
        sign=''
    result=[]
    while value:
        value,mod=divmod(value,36)
        result.append('0123456789abcdefghijklmnopqrstuvwxyz'[mod])
    return sign+''.join(reversed(result))

def Decode(c):
    digi=16
    add=10
    plus=7
    cha=36
    I=-1
    H=0
    B=''
    J=len(c)
    G=ord(c[-1])
    C=c[:-1]
    J-=1
    for E in range(J):
        D=int(C[E],cha)-add
        if D>=add:
            D=D-plus
        B+=to_base36(D)
        if D>H:
            I=E
            H=D
    A=int(B[:I],digi)
    F=int(B[I+1:],digi)
    L=(A+F-int(G))/2
    K=float(F-L)/100000
    L=float(L)/100000
    return {'lat':K,'lng':L}

if __name__=='__main__':
    print(Decode('IBGITBZUHGDVEM'))
