After an issue with `Starlette BaseHTTPMiddleware` catching warnings using the `warnings` package, questioned [here](https://stackoverflow.com/questions/75706159/async-warnings-generation-and-catching-inside-starlette-middleware-using-fastapi), I tried to achieve the same end result (appending warnings caught within a `warnings.catch_warnings` context) wrapping the endpoint in a custom decorator, and it worked (even got simpler without having to read the contents of `response.body_iterator`, update the body and create a new `Response` instance).

I just did not want to go back to my API and wrap every route endpoint function in this new decorator, nor I'd like to have me or anyone else to remember to do so in new routes.

I achieved the expected behavior by looping through all routes inside the router and editing the `endpoint` property of the route, as well as the `dependant` property:

```
from fastapi.dependencies.utils import get_dependant

router = APIRouter()

...

for route in router.routes:
    route.endpoint = alerts_decorator(route.endpoint)
    route.dependendant = get_dependant(
        path=route.path_format, call=route.endpoint)
```

It would be nice to be able to do so in the router instantiation, as with **prefix**, or some argument on the inclusion of the `router` in the `app`
