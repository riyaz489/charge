from rest_framework.views import exception_handler
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    print(exec)
    print(context)
    temp = {}
    if response is not None:
        temp["status"] = "FAILURE"
        temp['status_code'] = response.status_code
        if exc:
            temp['statusMessage'] = str(exc)
        else:
            temp['statusMessage'] = response.data['detail']

        response.data = temp
        response.status_code = status.HTTP_200_OK
    return response
