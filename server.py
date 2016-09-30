#!/usr/bin/env python2
import os

from bottle import post, request, run

from cozyweboob import main as cozyweboob


@post("/")
def index():
    params = request.forms.get("params")
    return cozyweboob(params)

if __name__ == "__main__":
    # Get host to listen on
    host = os.environ.get("COZYWEBOOB_HOST", "localhost")
    port = os.environ.get("COZYWEBOOB_PORT", 8080)
    run(host=host, port=port)
