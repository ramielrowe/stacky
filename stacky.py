#!/usr/bin/env python

import os
import re
import requests
import signal
import sys
import time

import prettytable as pt


STACKTACH = os.environ['STACKTACH_URL']


def signal_handler(signal, frame):
    sys.exit(0)


def _check(response):
    if response.status_code == 200:
        return response

    print "Error fetching results (%d)" % response.status_code
    x = response.text
    search = re.search('<title>(.*)</title>', x, re.IGNORECASE)
    if search:
        print "Server reported:", search.group(1)
    sys.exit(response.status_code)


def get_json(request):
    if isinstance(request.json, list):
        return request.json
    else:
        return request.json()


def get_event_names():
    r = _check(requests.get(STACKTACH + "/stacky/events/"))
    return get_json(r)


def get_host_names():
    r = _check(requests.get(STACKTACH + "/stacky/hosts/"))
    return get_json(r)


def get_deployments():
    r = _check(requests.get(STACKTACH + "/stacky/deployments/"))
    return get_json(r)


def show_timings_for_uuid(uuid):
    params = {'uuid' : uuid}
    r = _check(requests.get(STACKTACH + "/stacky/timings/uuid/", params=params))
    return get_json(r)


def related_to_uuid(uuid):
    params = {'uuid' : uuid}
    r = _check(requests.get(STACKTACH + "/stacky/uuid/", params=params))
    return get_json(r)


def list_usage_launches(filter = None):
    r = _check(requests.get(STACKTACH + "/stacky/usage/launches",
                            params=filter))
    return get_json(r)


def list_usage_deletes(filter = None):
    r = _check(requests.get(STACKTACH + "/stacky/usage/deletes",
                            params=filter))
    return get_json(r)


def list_usage_exists(filter = None):
    r = _check(requests.get(STACKTACH + "/stacky/usage/exists",
                            params=filter))
    return get_json(r)


def dump_results(results):
    if not results:
        return

    title = results.pop(0)
    if not results:
        print "No results"
        return

    t = pt.PrettyTable(title)
    for x in results:
        t.add_row(x)
    print str(t)


def safe_arg(index, default=None):
    if len(sys.argv) <= index:
        if not default:
            print "Missing parameter"
            sys.exit(1)
        return default
    return sys.argv[index]


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print """Usage: stacky <command>
    deployments - list stacktach deployments
    events      - list of unique event names
    watch       - 'watch <deployment id> <event-name> <polling sec>'
                   deployment id 0 = all
                   event-name empty = all
                   polling = 2s
    show    - inspect event ####
    uuid    - inspect events with uuid xxxxx
    summary - show summarized timings for all events
    timings - show timings for <event-name> (no .start/.end)
    request - show events with <request id>
    kpi     - crunch KPI's
    hosts   - list all host names"""
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == 'deployments':
        dump_results(get_deployments())

    if cmd == 'events':
        dump_results(get_event_names())

    if cmd == 'hosts':
        dump_results(get_host_names())

    if cmd == 'uuid':
        uuid = safe_arg(2)
        print "Events related to", uuid
        dump_results(related_to_uuid(uuid))
        dump_results(show_timings_for_uuid(uuid))

    if cmd == 'timings':
        name = safe_arg(2)
        params = {'name' : name}
        r = _check(requests.get(STACKTACH + "/stacky/timings/", params=params))
        dump_results(get_json(r))

    if cmd == 'summary':
        r = _check(requests.get(STACKTACH + "/stacky/summary/"))
        dump_results(get_json(r))

    if cmd == 'request':
        request_id = safe_arg(2)
        params = {'request_id': request_id}
        r = _check(requests.get(STACKTACH + "/stacky/request/", params=params))
        dump_results(get_json(r))

    if cmd == 'show':
        event_id = safe_arg(2)
        results = _check(requests.get(STACKTACH + "/stacky/show/%s/" %
                                                                    event_id))
        results = get_json(results)
        if len(results) == 0:
            print "Event %d not found" % event_id
            sys.exit(0)

        key_values = results.pop(0)
        data, uuid = results
        dump_results(key_values)
        if uuid:
            dump_results(related_to_uuid(uuid))

    if cmd == 'watch':
        event_name = ""
        deployment_id = 0
        poll = 2  # seconds

        if len(sys.argv) > 2:
            deployment_id = int(sys.argv[2])
            print "Deployment id:", deployment_id
        else:
            print "All Deployments"

        if len(sys.argv) > 3:
            event_name = sys.argv[3]
            print "Event name:", event_name
        if len(sys.argv) > 4:
            poll = int(sys.argv[4])
        print "Polling every %d seconds" % poll

        signal.signal(signal.SIGINT, signal_handler)

        last = None
        row = 0
        while 1:
            params = {}
            if event_name:
                params['event_name'] = event_name
            if last:
                params['since'] = last
            results = _check(requests.get(STACKTACH + "/stacky/watch/%d/" %
                                          deployment_id, params=params))
            c, results, last = get_json(results)
            for r in results:
                _id, typ, dait, tyme, deployment_name, name, uuid = r
                if row < 1:
                    print "+" + "+".join(['-' * width for width in c]) + "+"
                    print "|" + "|".join(['#'.center(c[0]), '?',
                               dait.center(c[2]),
                               'Deployment'.center(c[3]),
                               'Event'.center(c[4]),
                               'UUID'.center(c[5])]) + "|"
                    print "+" + "+".join(['-' * width for width in c]) + "+"

                    row = 20
                print "|" + "|".join([str(_id).center(c[0]),
                                typ,
                                tyme.center(c[2]),
                                deployment_name.center(c[3]),
                                name.center(c[4]),
                                uuid.center(c[5])]) + "|"

                row -= 1
            time.sleep(poll)


    if cmd == 'kpi':
        url = "/stacky/kpi/"
        if len(sys.argv) > 2:
            tenant_id = sys.argv[2]
            url += "%s/" % tenant_id
            print "Filtering by Tenant ID:", tenant_id

        r = _check(requests.get(STACKTACH + url))
        dump_results(r)


    if cmd == 'usage':
        sub_cmd = safe_arg(2)
        filter = {}
        if len(sys.argv) == 4:
            filter['instance'] = sys.argv[3]
        if sub_cmd == 'launches':
            dump_results(list_usage_launches(filter))
        elif sub_cmd == 'deletes':
            dump_results(list_usage_deletes(filter))
        elif sub_cmd == 'exists':
            dump_results(list_usage_exists(filter))
