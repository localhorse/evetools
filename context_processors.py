from noware.evetools.models import UserApiKey

def api_key_presence(request):

    if request.user.is_authenticated():
        api_keys = UserApiKey.objects.filter(django_user=request.user)
        if api_keys:
            api_key_present = True
        else:
            api_key_present = False
    else:
        api_key_present = False

    return {'api_key_present': api_key_present}
