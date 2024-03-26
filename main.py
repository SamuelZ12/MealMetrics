import requests
import cv2

from PIL import Image

import firebase_admin
from firebase_admin import firestore 

from firebase_admin import db

cred = firebase_admin.credentials.Certificate("/Users/samuelzhang/Desktop/Projects/Python/logmeal/bluecoin.json")
firebase_admin.initialize_app(cred)

# Open the webcam (0 for built-in webcam, 1 for external webcam)
cam = cv2.VideoCapture(0)
done = True

ref = db.reference("mealmetrics/fwmass", None, "https://bluecoin-9af7d-default-rtdb.firebaseio.com")

dbs = firestore.client()

global newvalue
foodPhotoCollection = dbs.collection('food_photos')
foodFamilyCollection = dbs.collection('food_family')
foodNameCollection = dbs.collection('food_name') 

currentvalue = ref.get()

while done:

    newvalue = ref.get()

    if(newvalue!=currentvalue):
        result, image = cam.read()
        
        if result:
            cv2.imwrite('randomimage.jpg', image)
            cv2.imshow('window', image)
        
            cv2.destroyAllWindows()
            done = False

        else:
            print('did not work')


# Parameters
img = '/Users/samuelzhang/Desktop/Projects/Python/randomimage.jpg'
api_user_token = '555d3f8fd1f917fe7d8de0ffadd9aef728037e0b'
headers = {'Authorization': 'Bearer ' + api_user_token}

f = open(img, "r")

# Food Type Detection
api_url = 'https://api.logmeal.es'
endpoint = '/v2/image/segmentation/complete'
response = requests.post(api_url + endpoint,
                    files={'image': open(img, 'rb')},
                    headers=headers)

resp = response.json()
print(resp)
    
foodFamily = resp['segmentation_results'][0]['recognition_results'][0]['subclasses'][0]['foodFamily'][0]['name']
foodName = resp['segmentation_results'][0]['recognition_results'][0]['name'] 

res = foodPhotoCollection.add({ 
    'food': foodName,
    'probs': resp['segmentation_results'][0]['recognition_results'][0]['prob'],
    'family': foodFamily,
    'weight': newvalue
})

doc_ref_family = foodFamilyCollection.document(foodFamily)
doc_family = doc_ref_family.get()
print(doc_family)

if doc_family.exists:
    doc_ref_family.update({'weight': firestore.Increment(newvalue),
                           'count': firestore.Increment(1)})
else:
    doc_ref_family.set({'count': 1,
                        'weight' : newvalue})
    
doc_ref_name = foodNameCollection.document(foodName)
doc_name = doc_ref_name.get()

if doc_name.exists:
    doc_ref_name.update({'count': firestore.Increment(1),
                         'weight': firestore.Increment(newvalue)})
else:
    doc_ref_name.set({'count': 1,
                      'weight' : newvalue})