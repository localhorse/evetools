from django.db import models
from django.contrib.auth.models import User

class UserApiKey(models.Model):
    django_user = models.ForeignKey(User)
    key_id = models.CharField(max_length=255)
    verification_code = models.CharField(max_length=256)

    def __unicode__(self):
        return "%s (%s)" % (self.django_user, self.key_id)

class CorpApiKey(models.Model):
    key_id = models.CharField(max_length=255)
    verification_code = models.CharField(max_length=255)

    def __unicode__(self):
        return self.key_id

class CachedRequest(models.Model):
    hash_key = models.IntegerField(primary_key=True)
    pickled_data = models.TextField()

    def __unicode__(self):
        return str(self.hash_key)

