from django.template import RequestContext
from django.shortcuts import render_to_response

def help(request):
    context = {}

    rcon = RequestContext(request)

    return render_to_response('api/help.html', context, rcon)
