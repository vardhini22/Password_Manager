from django.shortcuts import render
from pymongo import MongoClient 
from PIL import Image
from io import BytesIO
from passapp import image_encryption as ie
from passapp import hush as h
import numpy as np 
from gridfs import GridFS
import tkinter as tk
import math 
def split_image_into_rgb(img):
    image=img.resize((256, 256), Image.BILINEAR)
    image_array = np.array(image)
    red_channel = image_array[:, :, 0]
    green_channel = image_array[:, :, 1]
    blue_channel = image_array[:, :, 2]
    k1=np.array(red_channel)
    k2=np.array(green_channel)
    k3=np.array(blue_channel)
    k1 =k1.flatten()
    k2=k2.flatten()
    k3=k3.flatten()
    k=[]
    k.append(k1)
    k.append(k2)
    k.append(k3)
    return k

def decrypt_data(db,b,key):
    mottham=""
    fs=GridFS(db,collection='imagecollections')
    file_data=fs.find_one({'filename':key})
    imagebin=file_data.read()
    image=Image.open(BytesIO(imagebin))
    image=image.resize((256, 256), Image.BILINEAR)
    img= ie.imgdecr(image)
    k=split_image_into_rgb(img)
    count=0
    result=[]
    for i in b:
        a=[]
        bytes_data = i.encode('latin1')
        binary_data = ''.join(format(byte, '08b') for byte in bytes_data)
        a.append(binary_data)
        m_list=ie.x1
        x_list=ie.y1
        m=str(m_list[count])
        m=m[:15]
        m=int(float(m)*3)
        a1=str(x_list[count])
        a1=a1[:15]
        a1=int(float(a1)*256)
        n=(20+k[m][a1]+1)%160
        test2=list(a[0])
        t=0
        while(t<=n):
            char=test2.pop()
            test2.insert(0,char)
            t+=1
        y=""
        y="".join(test2)
        result.append(y)
        decry=[]

        cnt =0
        s1=""
        for i in range(0,len(result)):
            for j in result[i]:
                cnt+=1
                s1+=j
                if(cnt==8):
                    decry.append(s1)
                    cnt=0
                    s1=""
        final=[]
        txt=""
        p=0
        for i in decry:
            p+=1
            txt+=chr(int(i,2))
            if( p==len(decry)):
                final.append(txt)
                txt=""
        m="".join(final)
        count=count+1

        '''def print_value():
            global value
            value = m
            label['text'] = value
        
        root = tk.Tk()
        root.title("Print Value Example")


        label = tk.Label(root, text="")
        label.pack()


        button = tk.Button(root, text="Print Value", command=print_value)
        button.pack()

        root.mainloop()'''

    return m


def encrypt_data(uploaded_image,text,hval):
    k=split_image_into_rgb(uploaded_image)
    x=0
    l=[]
    s=""
    cnt=math.floor(len(text)/20)
    y=1
    p=0
    for i in text:
        x=x+1
        p+=1
        binary=list(bin(ord(i))[2:])
        while(len(binary)!=8):
            binary.insert(0,'0')
        new=""
        new="".join(binary)
        s=s+new
        if(x==20 or ( y==cnt+1 and p==len(text) )):
            y+=1
            l.append(s)
            x=0
            s=""                
    leng=len(l)
    
    test1=[]
    last_index=-1
    client = MongoClient('localhost', 27017)
    '''db = client['Kutty']
    collection = db['PerusuCollections']
    key = hval
    query = {"id": key}  
    document = collection.find_one(query)
    if document:
        encrypted_text = document.get("encrypted_text", [])
        last_index = len(encrypted_text)-1'''
    count=0
    for x in range(last_index+1,leng+last_index+1):
        if len(l)>1  and count!=0:
            l=l[1:]
        m_list=ie.x1
        x_list=ie.y1
        m=str(m_list[x])
        m=m[:15]
        m=int(float(m)*3)
        a=str(x_list[x])
        a=a[:15]
        a=int(float(a)*256)
        test=list(l[0])
        n=(20+k[m][a]+1)%160
        t=0
        while(t<=n):
            char=test[0]
            test.pop(0)
            test.append(char)
            t+=1
        y=""
        y="".join(test)
        count+=1
        bytes_list = [y[i:i+8] for i in range(0, len(y), 8)]
        c = ''.join(chr(int(byte, 2)) for byte in bytes_list)
        test1.append(c) 
    return test1

def registerpage(request):
    if(request.method=='POST'):
        n=request.POST.get('name')
        c=request.POST.get('nick')
        fc=request.POST.get('chocolate')
        fa=request.POST.get('actor')
        image=request.FILES.get('img')
        key=h.sha(n[0:3]+c[0:3]+fc[0:3]+fa[0:3])
        text=n+c+fc+fa
        new_img=Image.open(image)
        encrypted_text=encrypt_data(new_img,text,key)
        client=MongoClient('mongodb://localhost:27017/')
        db=client['Kutty']
        collection=db['KuttyCollections']
        data={"id": key,"encrypted_text":encrypted_text}
        collection.insert_one(data)
        encrypted_img =ie.imgencr(image)
        fs=GridFS(db,collection='imagecollections')
        image_bytes=BytesIO()
        encrypted_img.save(image_bytes,format='PNG')
        file_id=fs.put(image_bytes.getvalue(),filename=key)
        return render(request,"result.html",context={'process':"REGISTER",'state':"SUCCESS"})
    return render(request,"register.html")
def login(request):
    if(request.method=='POST'):
        n=request.POST.get('name')
        c=request.POST.get('nick')
        fc=request.POST.get('chocolate')
        fa=request.POST.get('actor')
        key=h.sha(n[0:3]+c[0:3]+fc[0:3]+fa[0:3])
        text=n+c+fc+fa
        client=MongoClient('mongodb://localhost:27017/')
        db=client['Kutty']
        collection=db['KuttyCollections']
        data={"id": key}
        b=collection.find_one(data)
        if b:
            b=b['encrypted_text']
            decrypted=decrypt_data(db,b,key)
            if decrypted==text:
                request.session['id'] = key
                return render(request,"result.html",context={'process':"LOGIN",'state':"SUCCESS"})
            else:
                return render(request,"result.html",context={'process':"LOGIN",'state':"FAILURE"})

    return render(request,"login.html")

def enter(request):
    id1 = request.session.get('id')
    if id1=="":
        return render(request,"home.html")        
    if(request.method=="POST"):
        c=request.POST.get('category')
        u=request.POST.get('username')
        p=request.POST.get('password')
        text='?'+c+'?'+u+'?'+p+'?'
        client=MongoClient('mongodb://localhost:27017/')
        db=client['Kutty']
        fs=GridFS(db,collection='imagecollections')
        file_data=fs.find_one({'filename':id1})
        imagebin=file_data.read()
        image=Image.open(BytesIO(imagebin))
        image=image.resize((256, 256), Image.BILINEAR)
        img=ie.imgdecr(image)
        coll = db["PerusuCollections"]
        check={"id":id1}
        b=coll.find_one(check)
        if(b):
             para=text
             para=encrypt_data(img,para,id1)
             text1 = b['encrypted_text']+ para
             coll.update_one({"id": id1 }, {"$set": {"encrypted_text": text1}})
        else:
            para=encrypt_data(img,text,id1)
            data={"id":id1,"encrypted_text":para}
            coll.insert_one(data)
           
        request.session['id'] = ""
        return render(request,"result.html",context={'process':"ENTER",'state':"SUCCESS"})
    return render(request,"enter.html")
def remove_all_occurrences(lst, element):
    return [x for x in lst if x != element]
def see(request):
    id1 = request.session.get('id')
    if id1=="":
        return render(request,"home.html")
    client=MongoClient('mongodb://localhost:27017/')
    db=client['Kutty']
    collection = db["PerusuCollections"]
    data={"id":id1}
    b=collection.find_one(data)
    b=b['encrypted_text']
    ans1=decrypt_data(db,b,id1)
    request.session['id'] = ""
    s=''
    result=[]
    ans={}
    cntt=0
    l=ans1.split('?')
    l=remove_all_occurrences(l,'')
    r=[]
    for i in range(0,len(l)):
        if i%3==0:
            r.append(l[i])
        elif i%3==1:
            r.append(l[i])
        elif i%3==2:
            r.append(l[i])
            result.append(r)
            r=[]
    return render(request,"see.html",context={"see":result})
def homepage(request):
    return render(request,"home.html")

