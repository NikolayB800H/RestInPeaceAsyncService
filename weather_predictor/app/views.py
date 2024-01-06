from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests
import json

from concurrent import futures

CALLBACK_URL = "http://0.0.0.0:8084/api/forecast_applications/"
TOKEN = "secret_token"

executor = futures.ThreadPoolExecutor(max_workers=1)

def get_random_status(data):
    time.sleep(5)
    res = {
        "id": data["application_id"],
        #"status": bool(random.getrandbits(1)),
        "status": True,
        "outputs": [],
    }
    for i in data["all_inputs"]:
        res["outputs"].append({
            "data_type_id": i["data_type_id"],
            "output": (i["input_first"] + i["input_second"] + i["input_third"]) / 3,
        })
    return res

def status_callback(task):
    try:
      result = task.result()
      #print(result)
    except futures._base.CancelledError:
      return
    
    nurl = str(CALLBACK_URL+str(result["id"])+'/calculate/')
    answer = {
        "calculate_status": result["status"],
        "token": TOKEN,
        "all_outputs": result["outputs"],
    }
    print(answer)
    print(requests.put(nurl, json=answer, timeout=3))

@api_view(['POST'])
def set_status(request):
    if "application_id" in request.data.keys():
        #id = request.data["pk"]        
        #task = executor.submit(get_random_status, id)
        task = executor.submit(get_random_status, request.data)
        task.add_done_callback(status_callback)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)