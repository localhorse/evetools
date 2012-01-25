from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.models import User

from noware.evetools.eveapi import eveapi
from noware.evetools import apicache

from noware.evetools.models import UserApiKey

from django.utils import simplejson

from noware.evetools import util

##from noware.apachelogger import CustomApacheLogger

# auth.account.Characters
# auth.account.APIKeyInfo
# auth.char.AccountBalance

def index(request):

    ##apache_logger = CustomApacheLogger(True)
    ##apache_logger.log("Setup logging object (index view).")
    ##apache_logger.log("%s (index)" % ('HTTP_X_REQUESTED_WITH' in request.META))

    characters = {}

    if request.user.is_authenticated():
        # debugging on
        cached_api = eveapi.EVEAPIConnection(cacheHandler=apicache.cache_handler(debug=True))
        api_keys = UserApiKey.objects.filter(django_user=request.user)
        if len(api_keys) > 0:
            message = "Characters attached to this account:"
            for api_num, cur_eve_key in enumerate(api_keys):
                auth = cached_api.auth(keyID=cur_eve_key.key_id, vCode=cur_eve_key.verification_code)
                result = auth.account.Characters()
                for char_num, character in enumerate(result.characters):
                    # div ids cannot technically contain spaces
                    characters[character.name] = "/eve_tools/char_page/%s/%s/%s/" % (request.user.id, api_num, char_num)
        else:
            message = "You have no associated API keys."
    else:
        message = "You are not logged in."

    context = RequestContext(request)
    return render_to_response('index.html', {'message': message, 'characters': characters}, context)

def char_page(request, user_id, api_num, char_num):

    ##apache_logger = CustomApacheLogger(True)
    ##apache_logger.log("Setup logging object (char_page view).")
    ##apache_logger.log("%s (char_page)" % ('HTTP_X_REQUESTED_WITH' in request.META))

    if request.user.is_authenticated():

        # debugging is on
        cached_api = eveapi.EVEAPIConnection(cacheHandler=apicache.cache_handler(debug=True))
        viewed_user = User.objects.filter(id=user_id)
        api_keys = UserApiKey.objects.filter(django_user=viewed_user)

        if len(api_keys) > 0:

            message = ""

            key_id = api_keys[int(api_num)].key_id
            verification_code = api_keys[int(api_num)].verification_code
            auth = cached_api.auth(keyID=key_id, vCode=verification_code)

            result = auth.account.Characters()
            character = result.characters[int(char_num)]
            char_name = character.name
            char_id = character.characterID

            # cache these images as well...
            img_url = "http://image.eveonline.com/Character/%s_%s.jpg" % (char_id, "128")

            key_info = auth.account.APIKeyInfo()
            if key_info.key.accessMask & 1:
                # key can access wallet balance
                wallet = auth.char.AccountBalance(characterID=char_id)
                isk_balance = util.comma(float(wallet.accounts[0].balance))
                wallet_msg = "%s ISK" % isk_balance
            else:
                # no wallet access
                wallet_msg = "Can't access wallet!"

        else:
            message = "No API keys attached to this Django account?"

    else:
        message = "You are not logged in."

    # this _should_ be "if not request.is_ajax()", but seems broken
    if not 'HTTP_X_REQUESTED_WITH' in request.META:

        context = RequestContext(request)
        return render_to_response('evetools/char_page.html', {'message': message, 'char_name': char_name, 'wallet_msg': wallet_msg, 'img_url': img_url}, context)

    # if the request _is_ AJAX...?
    else:

        results = {'wallet_msg': wallet_msg, 'img_url': img_url}
        raw_json = simplejson.dumps(results)
        return HttpResponse(raw_json, mimetype='application/json')
