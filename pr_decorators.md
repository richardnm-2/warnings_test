After a thorough search on `middlewares` and not being able to solve [this scrambling issue with middlewares](https://stackoverflow.com/questions/75706159/async-warnings-generation-and-catching-inside-starlette-middleware-using-fastapi), I thought it would be nice to be able to wrap every route in a router in a decorator (or multiple decorators). #9244

First I tested looping through all the routes as below, but to get it working, I had to update the dependant as well, which felt a little too hacky:

```
for route in router.routes:
    route.endpoint = decorator(route.endpoint)
    route.dependendant = get_dependant(
        path=route.path_format, call=route.endpoint)
```

So I came up with the `decorators` parameter for the `APIRouter` and for the `app.include_router`, passing a list of tuples where the first element of the tuple should be the decorator function and the other elements, the decorator arguments, if any.

`router_decorated = APIRouter(decorators=[(decorator_1, ), (decorator_2, DECORATOR_ARG)])`

In branch `richardnm2/fastapi/tree/dummy_decorator_test` I forced all routes to be wrapped around a dummy decorator, and all tests still passed.

Looking forward for your thoughts on this one, would really help for my use case, described in the SO thread.
