###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Tavendo GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

from __future__ import print_function

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.types import PublishOptions, CallOptions
from autobahn.wamp.keyring import KeyRing, Key

from sample_keys import ORIGINATOR_PRIV, RESPONDER_PUB


class Component(ApplicationSession):

    NUM = 3

    @inlineCallbacks
    def onJoin(self, details):
        print("joined")

        keyring = KeyRing()
        key = Key(originator_priv=ORIGINATOR_PRIV, responder_pub=RESPONDER_PUB)
        keyring.set_key(u'com.myapp.encrypted.', key)
        self.set_keyring(keyring)

        yield self._test_rpc()
        yield self._test_pubsub()

        print("done!")
        self.leave()

    @inlineCallbacks
    def _test_rpc(self):
        options = CallOptions(disclose_me=True)
        counter = 1
        while counter <= self.NUM:
            res = yield self.call(u'com.myapp.add2', 23, counter, options=options)
            print("called: {}".format(res))
            res = yield self.call(u'com.myapp.encrypted.add2', 23, counter, options=options)
            print("called: {}".format(res))
            yield sleep(1)
            counter += 1

    @inlineCallbacks
    def _test_pubsub(self):
        options = PublishOptions(acknowledge=True, exclude_me=False, disclose_me=True)
        counter = 1
        while counter <= self.NUM:
            msg = u"Counter is at {}".format(counter)
            pub = yield self.publish(u'com.myapp.hello', msg, options=options)
            print("published: {}".format(pub))
            pub = yield self.publish(u'com.myapp.encrypted.hello', msg, options=options)
            print("published: {}".format(pub))
            yield sleep(1)
            counter += 1

    def onLeave(self, details):
        self.disconnect()

    def onDisconnect(self):
        from twisted.internet import reactor
        reactor.stop()


if __name__ == '__main__':
    runner = ApplicationRunner(u"ws://127.0.0.1:8080", u"realm1")
    runner.run(Component)