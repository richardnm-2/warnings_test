import asyncio
import json
import os
import random
import time
import warnings
from pydantic import BaseModel

import uvicorn
from fastapi import APIRouter, FastAPI, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import iterate_in_threadpool
from starlette.datastructures import MutableHeaders


app = FastAPI()

router = APIRouter()

LOCK = asyncio.Lock()


class Alert(BaseModel):
    message: str
    alert_type: str


def deep_stacked_func():
    '''
        Might be called by other functions, be called outside a route and be declared on a different package.
        Don't want to have to receive a request object to have the session that the call belongs.
        '''
    n = random.randint(1, 10)
    if n <= 8:
        # do function stuff

        alert = Alert(message='/warnings route', alert_type='error')
        warnings.warn(Warning(alert))

    return 'function stuff ' * n   # must be returned, even after warnings.warn call


@router.get("/warnings")
async def warnings_route():

    function_stuff = deep_stacked_func()

    # do route stuff, with function stuff

    time.sleep(random.random())

    return {"return": "route stuff"}


@router.get("/no_warnings")
async def no_warnings_route():
    time.sleep(random.random())
    return {"return": "no warning route stuff"}


class AlertsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        # async with LOCK: # uncomment to function the proper way
        if True:  # comment to function the proper way
            with warnings.catch_warnings(record=True) as caught_warnings:
                warnings.simplefilter("always")
                response = await call_next(request)
                warns = []

                for warn in caught_warnings:
                    warn_message = warn.message.args[0]
                    if isinstance(warn_message, Alert):
                        warns.append(
                            {'message': warn_message.message, 'type': warn_message.alert_type})

                if warns:
                    response_body = [section async for section in response.body_iterator]

                    body = json.loads(response_body[0])
                    body.update({'alerts': warns})
                    body = json.dumps(
                        body, indent=2, default=str).encode("utf-8")

                    headers = MutableHeaders(raw=response.headers.raw)
                    headers["Content-Length"] = str(len(body))

                    response = Response(
                        content=body,
                        status_code=response.status_code,
                        media_type=response.media_type,
                        headers=headers
                    )
                return response


app.include_router(router)
app.add_middleware(AlertsMiddleware)

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', port=8000, reload=True)
