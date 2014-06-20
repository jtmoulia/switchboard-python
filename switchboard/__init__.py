# -*- coding: utf-8 -*-

"""
A Switchboard worker/client implementation.
"""

__author__ = u"Thomas Moulia <jtmoulia@pocketknife.io>"
__copyright__ = u"Copyright © 2014, ThusFresh, Inc. All rights reserved."



from ws4py.client.threadedclient import WebSocketClient
import aplus
import json
import email

import logging
logger = logging.getLogger(__name__)


class Client(WebSocketClient):
    """
    Base behavior shared between workers and clients.
    """

    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self._tag = 0
        self._cmd_groups = {}

    # WebSocketClient Hooks
    # ---------------------

    def opened(self):
        """
        Handle the websocket opening.
        """
        logger.debug("Connection is open....")

    def closed(self, code, reason=None):
        """
        Handle the websocket closing.
        """
        logger.debug("Connection has closed: %s - %s.", code, reason)

    def received_message(self, msg):
        """
        Handle receiving a message by checking whether it is in response
        to a command or unsolicited, and dispatching it to the appropriate
        object method.
        """
        logger.debug("Received message: %s", msg)
        if msg.is_binary:
            raise ValueError("Binary messages not supported")
        resps = json.loads(msg.data)

        cmd_group = _get_cmds_id(*resps)
        if cmd_group:
            (cmds, promise) = self._cmd_groups[cmd_group]
            promise.fulfill((cmds, resps))
        else:
            self.received_unsolicited(resps)

    # Callbacks
    # ---------

    def received_unsolicited(self, response):
        """
        Handle a unsolicited response.
        """
        logger.debug("Received unsolicited message: %s", response)

    # Public Interface
    # ----------------

    def _tag_cmds(self, *cmds):
        """
        Yields tagged commands.
        """
        for (method, args) in cmds:
            tagged_cmd = [method, args, self._tag]
            self._tag = self._tag + 1
            yield tagged_cmd

    def send_cmds(self, *cmds):
        """
        Tags and sends the commands to the Switchboard server, returning
        None.

        Each cmd be a 2-tuple where the first element is the method name,
        and the second is the arguments, e.g. ("connect", {"host": ...}).
        """
        promise = aplus.Promise()
        tagged_cmds = list(self._tag_cmds(*cmds))
        logger.debug("Sending cmds: %s", tagged_cmds)

        cmd_group = _get_cmds_id(*tagged_cmds)
        self._cmd_groups[cmd_group] = (tagged_cmds, promise)
        self.send(json.dumps(tagged_cmds))
        return promise


class Fetcher(Client):
    """
    A basic Switchboard worker that will listen for new email
    notifications.  When it receives a notification, it fetches the
    raw email from Switchboard and parses it using the email module.
    """

    def received_unsolicited(self, resps):
        def post_fetch((cmds, resps)):
            """Post fetch callback."""
            for raw_msg in resps[0][1]['list']:
                self.received_new(email.message_from_string(raw_msg['raw']))

        for resp in resps:
            if resp[0] == 'newMessage':
                args = resp[1]
                self.send_cmds(('getMessages',
                                {'account': args['account'],
                                 'ids': [args['messageId']],
                                 'properties': ['raw']})).then(post_fetch)

            else:
                logger.warning("Unknown unsolicted response: %s", response)

    def received_new(self, msg):
        """
        Override this message to handle new emails.
        """
        raise NotImplementedError


## Helpers
## =======

def _take(d, key, default=None):
    """If the key is present in dictionary, remove it and return it's
    value. If it is not present, return None.
    """
    if key in d:
        cmd = d[key]
        del d[key]
        return cmd
    else:
        return default


def _get_cmds_id(*cmds):
    """Returns an identifier for a group of partially tagged commands.
    If there are no tagged commands, returns None.
    """
    tags = [cmd[2] if len(cmd) == 3 else None for cmd in cmds]
    if [tag for tag in tags if tag != None]:
        return tuple(tags)
    else:
        return None
