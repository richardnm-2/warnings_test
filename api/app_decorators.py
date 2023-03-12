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

from update_response_body import update_response_body

from fastapi.dependencies.utils import get_dependant


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


def alerts_decorator(func):
    async def wrapper():
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            response = await func()

            warns = []

            for warn in caught_warnings:
                warn_message = warn.message.args[0]

                if isinstance(warn_message, Alert):
                    warns.append(
                        {'message': warn_message.message, 'type': warn_message.alert_type})

            if warns:
                response.update({'alerts': warns})
            return response

    return wrapper


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


for route in router.routes:
    route.endpoint = alerts_decorator(route.endpoint)
    route.dependendant = get_dependant(
        path=route.path_format, call=route.endpoint)

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run('app_decorators:app', host='0.0.0.0', port=8000, reload=True)
