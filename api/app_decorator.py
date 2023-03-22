import random
import time
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Header, Request
from fastapi.dependencies.utils import get_dependant
from fastapi_wraps import fastapi_wraps, get_request

app = FastAPI()

router = APIRouter()


def alerts_decorator(endpoint):
    @fastapi_wraps(endpoint)
    async def wrapper(*args, __request: Request = Depends(get_request), **kwargs):
        response = await endpoint(*args, **kwargs)
        # do stuff with caught warnings
        return response

    return wrapper


@router.get("/warnings")
async def warnings_route():
    return {"return": '/warnings response'}


def exception_thrower():
    raise HTTPException(403, detail='httpexception')


@router.get("/httpexception")
async def warnings_route():
    exception_thrower()
    # raise HTTPException(403, detail='httpexception')
    # return {"return": '/warnings response'}


@router.get("/no_warnings")
async def no_warnings_route(analysis_id=Header(default=5)):
    time.sleep(random.random())
    return {"return": "/no_warnings response"}

# for route in router.routes:
#     route.endpoint = alerts_decorator(route.endpoint)
#     route.dependendant = get_dependant(
#         path=route.path_format, call=route.endpoint)

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run('app_decorator:app', host='0.0.0.0', port=8000, reload=True)
