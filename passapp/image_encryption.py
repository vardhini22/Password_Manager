import math as m
from pymongo import MongoClient
from gridfs import GridFS
from PIL import Image
import io
import numpy as np
import random
from itertools import chain

#logistic map

x=3*2*3*4*5*6*7*8*9*10/(26**10)
x0=[]
lgmap=[]
while(x<0.1):
    x=x*10
x0=[x]

for i in range(1,256*256):
    xn=x0[i-1]
    xn_1=3.9999*xn*(1-xn)
    x0.append(xn_1)
   
   
for i in range(0,len(x0)):
    a=str(x0[i])
    a=a[:15]
    a=int(float(a)*256)
    lgmap.append(a)
   
#zaslavasky map

zymap=[]
zymap_s=[]
x1=[x]
y1=[0.1]
a=m.pi
alpha=9.1
beta=12.6695
gamma=3
mu=(1- m.exp(-gamma))/gamma
counter=0
for i in range(1,256*256):
    xn=x1[i-1]

    yn=y1[i-1]
   
    xn_1=xn+ beta*(1+ mu* yn ) + alpha*beta*( m.cos( a*2*xn)  )

    xn_1=xn_1-m.floor(xn_1)

    x1.append(xn_1)

    yn_1=(( m.exp(-gamma) )*yn ) + alpha* m.cos( a*2*xn)

    y1.append(yn_1)

for i in range(len(x1)):
    a=str(x1[i])
    a=a[:15]
    a=int(float(a)*256)
    zymap.append(a)
    if(counter<128):
        if(a not in zymap_s):
            zymap_s.append(a)
            counter=counter+1

#3D henon map

x2=[x]
y2=[0.1]
z2=[0.1]
a=1.76
b=0.1
henmap=[]
henmap_s=[]
counter=0
for i in range(1,256*256):
    xn=x2[i-1]

    yn=y2[i-1]

    zn=z2[i-1]
   
    xn_1=a-yn*yn-b*zn

    x2.append(xn_1)

    yn_1=xn

    y2.append(yn_1)

    zn_1=yn

    z2.append(zn_1)
for i in range(0,256*256):

    x2[i]=x2[i]-m.floor(x2[i])

    a=str(x2[i])
    a=a[:15]
    a=int(float(a)*256)

    henmap.append(a)

    if(counter<128):
        if(a not in zymap_s):
            if(a not in henmap_s):
                if(a<256 and a>=0):
                    henmap_s.append(a)
                    counter=counter+1

    y2[i]=y2[i]-m.floor(y2[i])

    a=str(y2[i])
    a=a[:15]
    a=int(float(a)*256)
    y2[i]=a

    z2[i]=z2[i]-m.floor(z2[i])

    a=str(z2[i])
    a=a[:15]
    a=int(float(a)*256)
    z2[i]=a

sbox=[]
sbox=zymap_s+henmap_s
sboxinv=[]


for i in range(len(sbox)):
    sboxinv.append(sbox.index(i))


def scramble(channel,matrix):
    c=0
    s1=""
    for i in range(0,len(channel)):
        k = bin(channel[i])[2:]
        while(len(k)!=8):
            k='0'+k
        s1 = s1+k      
    cnt = 0
    empty = ""
    empty2 = ""
    j = 0
    while(j<len(s1)):
        cnt = cnt+1
        empty = empty+s1[j]
        if(cnt==16):
            temp1 = empty[0:4]
            temp2 = empty[12:]
            temp3 = temp2+empty[4:12]+temp1
            empty2 = empty2+temp3
            cnt =0
            empty=""
        j=j+1      
    lol = ""
    f=[]
    for i in range(0,len(empty2)):
        lol = lol+empty2[i]
        if((i+1)%8==0):
            f.append(str(int(lol,2)))
            lol=""
    f1=[]
    temp=[]
    for i in range(0,len(f)):
        temp.append(f[i])
        if((i+1)%256==0):
            f1.append(temp)
            temp=[]
    scramble = []
    for i in range(0,len(matrix)):
        scramble.append(f1[matrix[i]])

    flattened_list =list(chain(*scramble))
    return flattened_list



def imgencr(path):
    image=Image.open(path)
    image=image.resize((256, 256), Image.BILINEAR)
    imgarray=np.array(image)
    rc=imgarray[:,:,0]
    gc=imgarray[:,:,1]
    bc=imgarray[:,:,2]
    rc=np.array(rc)
    gc=np.array(gc)
    bc=np.array(bc)
    rc=rc.flatten()
    bc=bc.flatten()
    gc=gc.flatten()
   
    finalrc=[]
    finalgc=[]
    finalbc=[]

    finalrc=scramble(rc,sbox)
    finalgc=scramble(gc,sbox)
    finalbc=scramble(bc,sbox)
    im1=np.stack([finalrc,finalgc,finalbc],axis=-1)
    im1=im1.reshape((256,256,3))
    im1=Image.fromarray(im1.astype('uint8'))
   

    hybridmap=[]
    for i in range(0,256*256):
        if(i%2==0):
            hybridmap.append(y2[i])
        else:
            hybridmap.append(z2[i])

    for i in range(0,256*256):
        finalrc[i]=int(finalrc[i])^lgmap[i]
        finalgc[i]=int(finalgc[i])^henmap[i]
        finalbc[i]=int(finalbc[i])^hybridmap[i]


    im1=np.stack([finalrc,finalgc,finalbc],axis=-1)
    im1=im1.reshape((256,256,3))
    im1=Image.fromarray(im1.astype('uint8'))
    return im1


def imgdecr(im1):
    img=np.array(im1)
    r=img[:,:,0]
    g=img[:,:,1]
    b=img[:,:,2]

    r=np.array(r)
    g=np.array(g)
    b=np.array(b)
    r=r.flatten()
    b=b.flatten()
    g=g.flatten()
    hybridmap=[]
    for i in range(0,256*256):
        if(i%2==0):
            hybridmap.append(y2[i])
        else:
            hybridmap.append(z2[i])

    for i in range(0,256*256):
        r[i]=r[i]^lgmap[i]
        g[i]=g[i]^henmap[i]
        b[i]=b[i]^hybridmap[i]

    im1=np.stack([r,g,b],axis=-1)
    im1=im1.reshape((256,256,3))
    im1=Image.fromarray(im1.astype('uint8'))
    r=scramble(r,sboxinv)
    g=scramble(g,sboxinv)
    b=scramble(b,sboxinv)
    im1=np.stack([r,g,b],axis=-1)
    im1=im1.reshape((256,256,3))
    im1=Image.fromarray(im1.astype('uint8'))
    return im1
