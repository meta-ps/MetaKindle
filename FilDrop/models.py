from django.db import models
from config.settings import BASE_DIR
import os
from pathlib import Path
import datetime

# Create your models here.
class User(models.Model):
    WalletAddress = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.WalletAddress

class UserCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collection_hash = models.CharField(max_length=255, null=True, blank=True)
    collection_name = models.CharField(max_length=255, null=True, blank=True)
    collection_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.collection_name

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    str_path = '/' + str(instance.user.id)+'/'+str(instance)+'/images/'
    layerPath = Path(str(BASE_DIR) + str_path)
    filename_start = filename.replace('.'+ext,'')

    filename = "%s.%s" % (filename_start, ext)
    return os.path.join(layerPath, filename)


class UserCollectionImage(models.Model):
    usercollection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    image = models.FileField(upload_to=get_file_path, verbose_name=(u'File'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.usercollection.collection_name

class ImageMetaData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    usercollection = models.ForeignKey(UserCollection, on_delete=models.CASCADE)
    img = models.ForeignKey(UserCollectionImage, on_delete=models.CASCADE)
    latitude =models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    weekno = models.CharField(max_length=10, null=True, blank=True)
    metadata_date=models.DateField()
    present_date=models.DateField(default=datetime.date.today)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str("Meta data")
