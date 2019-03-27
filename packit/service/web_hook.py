# MIT License
#
# Copyright (c) 2018-2019 Red Hat, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from flask import Flask, request
import logging
from io import StringIO

from packit.utils import set_logging

from packit.config import Config
from packit.bot_api import PackitBotAPI


class PackitWebhookReceiver(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_logging(level=logging.DEBUG)


app = PackitWebhookReceiver(__name__)
logger = logging.getLogger("packit")

@app.route("/github_release", methods=["POST"])
def github_release():
    msg = request.get_json()

    buffer = StringIO()
    logHandler = logging.StreamHandler(buffer)
    logHandler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    logger.debug(
        f"Received release event: "
        f"{msg['repository']['owner']['login']}/{msg['repository']['name']}"
        f" - {msg['release']['tag_name']}"
    )
    config = Config()
    api = PackitBotAPI(config)
    # Using fedmsg since the fields are the same
    api.sync_upstream_release_with_fedmsg({"msg": msg})

    logger.removeHandler(logHandler)
    buffer.flush()

    return buffer.getvalue()
