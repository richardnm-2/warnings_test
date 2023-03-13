import asyncio
from functools import wraps
import random
import time
import warnings

import uvicorn
from fastapi import APIRouter, FastAPI, Header
from fastapi.dependencies.utils import get_dependant
from pydantic import BaseModel
from alerts import AlertWarning
from alerts import AlertA
from middlewares import AlertsLogMiddleware


app = FastAPI()

router = APIRouter()


class Alert(BaseModel):
    message: str
    alert_type: str


def deep_stacked_func():
    '''
        Might be called by other functions, be called outside a route and be declared on a different package.
        Don't want to have to receive a request object to have the session that the call belongs.
        '''
    n = random.randint(1, 10)
    if n <= 28:
        # do function stuff

        # alert = AlertWarning(message='/warnings route', alert_type='error')
        AlertA()
        # warnings.warn(Warning('Other Warning'))

    return 'function stuff ' * n   # must be returned, even after warnings.warn call


def alerts_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.filterwarnings("always", category=AlertWarning)
            response = await func(*args, **kwargs)

            warns = []

            for warn in caught_warnings:
                try:
                    alert = warn.message.alert
                    warns.append(
                        {'message': alert.message, 'type': alert.alert_type})
                except AttributeError as e:
                    if e.name == 'alert':
                        pass
                    else:
                        raise e

            if warns:
                response.update({'alerts': warns})
            return response

    return wrapper


@router.get("/warnings")
async def warnings_route():

    function_stuff = deep_stacked_func()

    # do route stuff, with function stuff

    time.sleep(random.random())
    # time.sleep(50)
    await asyncio.sleep(50)

    return {"return": "route stuff"}


@router.get("/no_warnings")
async def no_warnings_route(analysis_id=Header(default=5)):
    time.sleep(random.random())
    return {"return": "no warning route stuff"}


for route in router.routes:
    route.endpoint = alerts_decorator(route.endpoint)
    route.dependendant = get_dependant(
        path=route.path_format, call=route.endpoint)

app.include_router(router)
app.add_middleware(AlertsLogMiddleware)

if __name__ == '__main__':
    uvicorn.run('app_decorator:app', host='0.0.0.0', port=8000, reload=True)
