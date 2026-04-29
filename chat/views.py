import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from chat.services.agent_service import handle_user_message


def chat_page(request):
    return render(request, "chat/index.html")


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "只支持 POST 请求"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({"error": "message 不能为空"}, status=400)

        result = handle_user_message(message)
        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)