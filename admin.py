from noware.evetools.models import UserApiKey
from noware.evetools.models import CorpApiKey
from noware.evetools.models import CachedRequest
from django.contrib import admin

admin.site.register(UserApiKey)
admin.site.register(CorpApiKey)
admin.site.register(CachedRequest)
