from django.shortcuts import render,redirect
from FilDrop.models import *
import os
from API_KEYS.keys import keys
from pathlib import Path
from utility.nftstorage import NftStorage
import json
import shutil
from pathlib2 import Path as Path2_
import requests
from PIL import Image
from PIL.ExifTags import TAGS
import exifread

base_uri = "ipfs://"
NFTSTORAGE_API_KEY = keys['NFTSTORAGE']
PINATA_JWT = keys['PINATA']


img_file_list = [] 
meta_file_list = []
gen_imgs = {}

user_d = {}


# Create your views here.
def Home(request):
    
    return render(request,'home.html')


def Login(request):
    request.session['WalletAddress'] = "xxx"
    if request.POST:
        WalletAddress = request.POST.get('WalletAddress')
        request.session['WalletAddress'] = WalletAddress
        obj = User.objects.get_or_create(WalletAddress=WalletAddress)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        print(WalletAddress)
        return redirect('userpage')
    else:
        return redirect('home')

def AddCollection(request):
    WalletAddress = request.session['WalletAddress']
    print('Collection')
    print(WalletAddress)
    if request.POST:
        user = User.objects.get(WalletAddress=WalletAddress)
        collection_name = request.POST.get('collection-item')
        obj = UserCollection.objects.get_or_create(user=user,collection_name=collection_name)

    return redirect('userpage')

def UserPage(request):
    WalletAddress = request.session['WalletAddress']
    user = User.objects.get(WalletAddress=WalletAddress)
    usercollection_objects=None
    usercollection_objects_is_active=False
    data=[]
    is_pic_active = True
    try:
        usercollection_objects=UserCollection.objects.get(user=user)
        print('11111111111111')
        i = usercollection_objects
        temp = []
        j =i.collection_count
        temp.append(i.collection_hash)
        data.append([i.collection_name,i.collection_hash,temp])
        print('22222222222222222')


        usercollection_objects_is_active=True
        print('333333333333333333')

    except:
        print('fuk')
        usercollection_objects = None
        usercollection_objects_is_active=False
    
    if usercollection_objects==None:
        is_pic_active = False
    else:
        if usercollection_objects.collection_hash!=None:
            is_pic_active = True
        else:
            is_pic_active = False

    return render(request,'userpage.html',{'WalletAddress':WalletAddress,'usercollection_objects':usercollection_objects,'data':data,'usercollection_objects_is_active':usercollection_objects_is_active,'is_pic_active':is_pic_active})

def update_meta_cid(file, cid):
    for i in file:
        with open(i) as f:
             data = json.load(f)
             img_file = data['image'].replace(base_uri, '')
             data['image'] = base_uri + cid + '/' + img_file
        
        with open(i, 'w') as outfile:
            json.dump(data, outfile, indent=4)    


def ImageUpload(request,pkk):
    global gen_imgs
    global user_d
    global img_file_list
    files = request.FILES.getlist('allimages')
    WalletAddress = request.session['WalletAddress']
    usercollection_obj = UserCollection.objects.get(id=pkk)
    meta_file_list = []
    user = User.objects.get(WalletAddress=WalletAddress)

    path =Path(os.path.normpath( str(BASE_DIR) + '/'+ str(user.id) + '/'+str(usercollection_obj.collection_name)+'/metadata/'))
    print(path)
    path_images =Path(os.path.normpath( str(BASE_DIR) + '/'+ str(user.id) + '/'+str(usercollection_obj.collection_name)+'/images/'))


    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)
    
    count_image=0
    images = {}
    image_count = 0
    for f in files:
        a = UserCollectionImage.objects.get_or_create(usercollection=usercollection_obj,image=f,user=user)

    i=1
    for filename in os.listdir(path_images):
        os.rename(os.path.join(path_images,filename),os.path.join(path_images,str(i)+'.jpg'))
        i+=1
    
    for filename in os.listdir(path_images):
        img_file_list.append(str(Path(os.path.normpath(str(path_images)+'\\'+str(filename)))))
    
    for k in img_file_list:
        image_count +=1
        token = {
            "name": str(usercollection_obj.collection_name) + ' ' + str(image_count),
            "image": base_uri + str(image_count),
            "desc": "Hello World"
        }
        meta_file =   Path(str(path)+'/' + str(image_count) + '.json')
        meta_file_list.append(meta_file)
        print(meta_file)
    
        with open(meta_file, 'w') as outfile:
            json.dump(token, outfile, indent=4)
    
    nstorage = {}
    c = NftStorage(NFTSTORAGE_API_KEY)
    print('LISTSTSTST----------------------------------------------------------------------')
    print(img_file_list)
    #fetchAndSaveDataloc
    fetchAndSaveDataloc(request)
 
    cid = c.upload(img_file_list, 'image/png')
    usercollection_obj = UserCollection.objects.get(id=pkk)
    usercollection_obj.collection_hash=cid
    usercollection_obj.is_active=False
    usercollection_obj.collection_count=image_count
    usercollection_obj.save()
    print(cid)
    img_file_list.clear()
    user_id = str(user.id)

 

    return redirect('userpage')

def fetchAndSaveDataloc(request):
    WalletAddress = request.session['WalletAddress']
    user = User.objects.get(WalletAddress=WalletAddress)
    
    obj_img=UserCollectionImage.objects.get(user=user)
    pathh = Path(os.path.normpath(str(obj_img.user.id) + "/" + str(obj_img.usercollection.collection_name) +"/images/1.jpg"))
    with open(pathh, 'rb') as f:
        exif_dict = exifread.process_file(f)
        print ('shooting time: ', exif_dict['EXIF DateTimeOriginal'])
        print ('camera manufacturer: ', exif_dict['Image Make'])
        print ('camera model: ', exif_dict['Image Model'])
        print ('photo size: ', exif_dict['EXIF ExifImageWidth'], exif_dict['EXIF ExifImageLength'])

        #Longitude
        lon_ref = exif_dict["GPS GPSLongitudeRef"].printable
        lon = exif_dict["GPS GPSLongitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
        lon = float(lon[0]) + float(lon[1]) / 60 + float(lon[2]) / float(lon[3]) / 3600
        if lon_ref != "E":
            lon = lon * (-1)

        #Latitude
        lat_ref = exif_dict["GPS GPSLatitudeRef"].printable
        lat = exif_dict["GPS GPSLatitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
        lat = float(lat[0]) + float(lat[1]) / 60 + float(lat[2]) / float(lat[3]) / 3600
        if lat_ref != "N":
            lat = lat * (-1)
        print ('latitude and longitude of photo: ', (lat, lon))

        for key in exif_dict:
            print("%s: %s" % (key, exif_dict[key]))




def Deploy(request,collectionname):
    path =Path(os.path.normpath( str(BASE_DIR) +'/NFT.sol'))
    path2 =Path(os.path.normpath( str(BASE_DIR) +'/contracts/NFT.sol'))
    WalletAddress = request.session['WalletAddress']
    print(WalletAddress)



    user = User.objects.get(WalletAddress=WalletAddress)
    obj = UserCollection.objects.get(collection_name=collectionname,user=user)
    print(obj.collection_hash)
    shutil.copyfile(path,path2)
    file = Path2_(path2)
    data = file.read_text()
    data = data.replace("USER_ADDRESS", WalletAddress)
    file.write_text(data)
    



    file = Path2_(path2)
    data = file.read_text()
    data = data.replace("TOKENURI", str("https://ipfs.io/ipfs/")+str(obj.collection_hash))
    file.write_text(data)
    #https://mumbai.polygonscan.com/tx/0xec4fb2c38a2cee48c6019c009c0866850d793533e5511d96ab3ece421a67fc2b

    try:
        shutil.rmtree("contracts/artifacts")
        shutil.rmtree("contracts/cache")
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))


    os.system("npx hardhat run scripts/deploy.js --network mumbai")


    q = open('address.txt','r')
    pqrq=q.read()
    print(pqrq)
    
    deployed_url = "https://mumbai.polygonscan.com/tx/"+str(pqrq)
    print('xxxxxxxxxxxxxxxxxxx')
    print(deployed_url)

    return render(request,'deploy.html',{'response':deployed_url})




    # url = "https://api.nftport.xyz/v0/contracts"
    # payload = "{\n  \"chain\": \"polygon\",\n  \"name\": \"CRYPTOPUNKS\",\n  \"symbol\": \"CYBER\",\n  \"owner_address\":wallet,\n  \"metadata_updatable\": false,\n  \"type\": \"erc721\"\n}"
    

    # payload = payload.replace('CRYPTOPUNKS',"NFTGEN")
    # payload = payload.replace('CYBER',"MATIC")
    # payload = payload.replace('wallet','"'+WalletAddress+'"')

    # headers = {
    #     'Content-Type': "application/json",
    #     'Authorization': "4c658b59-2263-4cb8-a3c4-dacca73e4700"
    # }

    # response = requests.request("POST", url, data=payload, headers=headers)
    # #print(response.text)
    # print('--------------------')
    # print(response)





    




# full_path = os.path.normpath(str(BASE_DIR)+str('/')+str(pkk)+"/images/"+str(usercollection_obj.collection_name))
############################################################
# metadata_path = os.path.normpath(str(BASE_DIR)+str('/')+str(pkk)+str(usercollection_obj.collection_name)+'/metadata//')
