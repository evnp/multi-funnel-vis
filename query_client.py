#! /usr/bin/env python
#
# Mixpanel, Inc. -- http://mixpanel.com/
#
# Python API client library to consume mixpanel.com analytics data.

# THIS FILE IS FOR TESTING AGAINST THE API ONLY, NOT USING IN CODE

import hashlib
import json
import time
import urllib
import urllib2

class Mixpanel(object):

    ENDPOINT = 'https://mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def request(self, endpoint, method, params, format='json'):
        """
            endpoint - Parent level access point (e.g. events, properties, etc.)
            method - Child level access point (e.g. general, unique, etc.)
            params - Extra parameters associated with method
        """
        params['api_key'] = self.api_key
        params['expire'] = int(time.time()) + 600   # Grant this request 10 minutes.
        params['sig'] = self.hash_args(params)

        request_url = self.ENDPOINT + '/' + str(self.VERSION) + '/' + endpoint + '/' + method
        request_params = self.unicode_urlencode(params)
        try:
            return self.get_data(request_url, request_params)
        except Exception as e:
            print e.read()

    def get_data(self, request_url, request_params):
        return urllib2.urlopen(request_url, data=request_params, timeout=120).read()

    def unicode_urlencode(self, params):
        if isinstance(params, dict):
            params = params.items()

        for i, param in enumerate(params):
            if isinstance(param[1], list):
                params[i] = (param[0], json.dumps(param[1]),)

        return urllib.urlencode(
            [(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params]
        )

    def hash_args(self, args, secret=None):
        """
            Hashes arguments by joining key=value pairs, appending a secret, and
            then taking the MD5 hex digest.
        """
        for a in args:
            if isinstance(args[a], list): args[a] = json.dumps(args[a])

        args_joined = ''
        for a in sorted(args.keys()):
            if isinstance(a, unicode):
                args_joined += a.encode('utf-8')
            else:
                args_joined += str(a)

            args_joined += '='

            if isinstance(args[a], unicode):
                args_joined += args[a].encode('utf-8')
            else:
                args_joined += str(args[a])

        hash = hashlib.md5(args_joined)

        if secret:
            hash.update(secret)
        elif self.api_secret:
            hash.update(self.api_secret)
        return hash.hexdigest()


def make_query(custom_query_script_path=None):
    import sys
    script = """
var result = {};

function scan (event, user) {
    if (event.name in result) {
        result[event.name] += 1;
    } else {
        result[event.name] = 1;
    }
}

"""
    script_params = '{}'

    if custom_query_script_path or len(sys.argv) > 1:
        with open(custom_query_script_path or sys.argv[1], 'r') as f:
            script = f.read()

    if len(sys.argv) > 2:
        script_params = json.dumps(json.loads(sys.argv[2]))

    api = Mixpanel(
        api_key = '794e2c0c5a75a6b9b7a98bcfce74b0a0',
        api_secret = '96893320bc2706b278fb35280156de5c'
    )
    data = api.request('custom_query', '', {
        'from_date': '2015-06-01',
        'to_date': '2015-06-30',
        'script': script,
        'params': script_params
    })

    nodesMap = {}
    linksMap = {}
    nodesArray = []
    linksArray = []
    maxNodeValue = 0
    maxLinkValue = 0

    funnels = json.loads(data)['results']

    def indexObjToArray(obj):
        arr = []
        for k, v in obj.iteritems():
            v['index'] = k
            arr.append(v)
        arr.sort(key=lambda v: v['index'])
        for v in arr:
            del v['index']
        return arr

    for funnel_events, funnel in funnels.iteritems():
        events = funnel_events.split('|')
        steps = indexObjToArray(funnel)

        for event, step in zip(events, steps):
            value = step['value']
            maxNodeValue = max(maxNodeValue, value)

            if event in nodesMap:
                nodesMap[event]['value'] = max(nodesMap[event]['value'], value)
            elif value:
                node = dict(
                    event=event,
                    value=value)

                nodesMap[event] = node
                nodesArray.append(node)

        for event, step, i in zip(events, steps, xrange(len(steps))):
            if i + 1 < len(funnel):
                nextEvent = events[i + 1]
                nextStep = steps[i + 1]
                nextValue = nextStep['value']
                maxLinkValue = max(maxLinkValue, step['value'], nextValue)

                if value and nextEvent in nodesMap:
                    linkKey = '%s-%s' % (event, nextEvent)

                    if linkKey not in linksMap:
                        link = dict(
                            source=nodesArray.index(nodesMap[event]),
                            target=nodesArray.index(nodesMap[nextEvent]),
                            value=nextValue)

                        linksMap[linkKey] = link
                        linksArray.append(link)

    formatted_data = dict(
        nodes=nodesArray,
        links=linksArray,
        maxNodeValue=maxNodeValue,
        maxLinkValue=maxLinkValue)

    return formatted_data
