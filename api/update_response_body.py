import json
from typing import Any
from fastapi import Response
from starlette.datastructures import MutableHeaders
from starlette.concurrency import iterate_in_threadpool

# from api.app import Alert


async def get_response_body(response: Response):
    response_body = [section async for section in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))

    return response_body


async def update_response_body(response: Response, data: dict[str, Any]):

    response_body = await get_response_body(response)

    body = json.loads(response_body[0])
    body.update(data)
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
