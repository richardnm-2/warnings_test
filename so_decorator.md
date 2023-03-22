Trying to solve the [middleware scrambling concurrent requests](https://stackoverflow.com/questions/75706159/async-warnings-generation-and-catching-inside-starlette-middleware-using-fastapi) problem, I ended up with a hacky way, decorating every `router route.endpoint` in a loop. With the clever implementation of `fastapi_wraps` I can do all I needed to do inside the decorator.

My dynamic decorating loop is implemented so:

```
for route in router.routes:
    route.endpoint = alerts_decorator(route.endpoint)
    route.dependendant = get_dependant(
        path=route.path_format, call=route.endpoint)
```

From what I tested, everything works fine, but
