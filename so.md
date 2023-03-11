I'm trying to get a relatively big api (FastAPI), with multiple APIRoutes to be able to have functions throwing alerts (with the `warnings` package) to the api consumer in a way that the alert generation is properly attached to the business logic and properly separated from the api base operations.

The routes themselves have a return that is non dependent if a warning has been thrown or not, and `exceptions` are not an option because the calculations inside the function must be continued even on a warning beeing thrown. Only if it is not possible to continue the calculation an `Exception` will be raised and a FastAPI `HTTPException` will be raised.

I kind of achieved this with the logic in [this minimal reproducible example](https://github.com/richardnm-2/warnings_test), where I set up a custom `starlette BaseHTTPMiddleware`, pass the request to the `call_next` function inside the `warnings.catch_warnings` context and so I'm able to catch the warnings generated wherever they're called while executing the route.

The only problem is that I assumed (correctly apparently), that concurrent calls to the routes, that might take longer or shorter depending on what is beeing requested (thus the random `time.sleep`), might scramble the requests with the warnings. This happens apparently due to the async nature of FastAPI.

Assume, as in the example, that I have two routes, `/warnings` and `/no_warnings`, where `/warnings` has a function call that sometimes generates a `warnings.warn(Warning())`

```
def deep_stacked_func():
    # do function stuff

    n = random.randint(1, 10)
    if n <= 8:

        alert = Alert(message='/warnings route', alert_type='error')
        warnings.warn(Warning(alert))

    return 'function stuff ' * n  # must be returned, even after warnings.warn call
```

`deep_stacked_func` gets called only from the `/warnings` route, never from `/no_warnings`.

```
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
```

Then, inside the Middleware, I catch the warnings and append them, if any, to the response.

```
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
```

With the middleware asynchronously calling the routes, and the requests being concurrently called, there is leakage from the warnings generated in `/warnings`, with the caught warnings beeing sent to `/no_warnings` calls.

`request.py`, with concurrent calls to the api routes

```
def get_warn():
    resp_warn = requests.get('http://127.0.0.1:8000/warnings')
    resp_body = json.loads(resp_warn.content)
    return resp_body


def get_no_warn():
    resp_no_warn = requests.get('http://127.0.0.1:8000/no_warnings')
    resp_body = json.loads(resp_no_warn.content)

    if resp_body.get('alerts'):
        print('ALERT ON NON ALERT')

    return resp_body


while True:
    try:
        t1 = threading.Thread(target=get_warn)
        t2 = threading.Thread(target=get_no_warn)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    finally:
        pass
```

To overcome this, I've put the whole `dispach` logic inside an `asyncio.Lock`, and it prevents the scrambling, but I'm afraid that with this solution, I've completly destroyed the `async` nature of FastAPI.

```
LOCK = asyncio.Lock()

...

class AlertsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
    async def dispatch(self, request, call_next):
        async with LOCK:
            with warnings.catch_warnings(record=True) as caught_warnings:
                ...
```

I really wouldn't like to set the warnings catch in every route I have, nor I'd like to pass a `request` object to every function call until it gets to the function generating the warnings, in order to append it to a session using a `SessionMiddleware`

Any help on how I could achieve this without messing with `asyncio.Lock` is much appreciated.
