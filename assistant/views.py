import json

from django.http import JsonResponse
from rest_framework.decorators import api_view

from assistant.api_util import send_prompt


@api_view(['POST'])
def prompt_view(request):
    request_data = json.loads(request.body)
    response = send_prompt(request_data, request.headers.get('X-Current-Datetime'))
    print(response)
    return JsonResponse({'content': response})