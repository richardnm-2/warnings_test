import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.background import BackgroundTask
from update_response_body import get_response_body
from copy import copy, deepcopy


async def write_log_data(request: Request, response: Response, response_body):
    print('Logging...')
    time.sleep(5)
    print(request.headers.get('analysis-id'))
    print()
    print(response_body)
    print('Logged!')
    # logger.info(request.method + ' ' + request.url.path,
    #             extra={'extra_info': get_extra_info(request, response)})


class AlertsLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response_body = await get_response_body(response)

        response.background = BackgroundTask(
            write_log_data, request, response, response_body)

        return response
