#!/usr/bin/env python

import calendar
import datetime
import decimal
import json
import os
import re
import requests
import signal
import sys
import time

import prettytable as pt


STACKTACH = os.environ['STACKTACH_URL']

# Stolen from stacktach/datetime_to_decimal.py
def dt_to_decimal(utc):
    decimal.getcontext().prec = 30
    return decimal.Decimal(str(calendar.timegm(utc.utctimetuple()))) + \
           (decimal.Decimal(str(utc.microsecond)) /
           decimal.Decimal("1000000.0"))


def dt_from_decimal(dec):
    if dec == None:
        return "n/a"
    integer = int(dec)
    micro = (dec - decimal.Decimal(integer)) * decimal.Decimal(1000000)

    daittyme = datetime.datetime.utcfromtimestamp(integer)
    return daittyme.replace(microsecond=micro)


def sec_to_str(sec):
    sec = int(sec)
    if sec < 60:
        return "%ds" % sec
    minutes = sec / 60
    sec = sec % 60
    if minutes < 60:
        return "%d:%02ds" % (minutes, sec)
    hours = minutes / 60
    minutes = minutes % 60
    return "%02d:%02d:%02d" % (hours, minutes, sec)
#-----


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
    result = request.json
    if isinstance(result, list):
        return result
    return result()


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


def formatted_datetime(dt):
    _date = dt.date()
    _time = dt.time()
    return ("%04d-%02d-%02d" % (_date.year, _date.month, _date.day),
            "%02d:%02d" % (_time.hour, _time.minute))

def get_reports(from_dt, to_dt):
    dstart = dt_to_decimal(from_dt)
    dend = dt_to_decimal(to_dt)

    url = "/stacky/reports?created_from=%f&created_to=%f" % (dstart, dend)
    r = _check(requests.get(STACKTACH + url))
    return get_json(r)


def get_report(rid):
    url = "/stacky/report/%s" % report_id

    r = _check(requests.get(STACKTACH + url))
    return json.loads(r.json())


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
    reports - list all reports created from <start> to <end>
              All times 24-hr UTC in YYYY-MM-DD HH:MM format.
              Example: stacky reports 2013-02-28 00:00 2013-02-28 06:00
                       will return all reports created from midnight to 6am
                       on Feb 28th.
    report  - get json for report <id>
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


    if cmd == 'reports':
        today = datetime.datetime.utcnow().date()

        rstart = datetime.datetime(year=today.year, month=today.month,
                                                              day=today.day)
        rend = rstart + datetime.timedelta(hours=23, minutes=59, seconds=59)

        _date, _time = formatted_datetime(rstart)
        start_date = safe_arg(2, _date)
        start_time = safe_arg(3, _time)
        _date, _time = formatted_datetime(rend)
        end_date = safe_arg(4, _date)
        end_time = safe_arg(5, _time)

        parsed = []
        for _date, _time  in [(start_date, start_time), (end_date, end_time)]:
            try:
                d = time.strptime(_date, "%Y-%m-%d")
                t = time.strptime(_time, "%H:%M")
                parsed.append(datetime.datetime(
                                       year=d.tm_year, month=d.tm_mon,
                                       day=d.tm_mday,
                                       hour=t.tm_hour, minute=t.tm_min))
            except Exception, e:
                print "'%s %s' is in wrong format." % (_date, _time)

        rstart = parsed[0]
        rend = parsed[1]

        print "Querying for reports created from %s to %s" % (rstart, rend)
        r = get_reports(rstart, rend)
        for row in r[1:]:
            for x in range(1, 3):
                dt = dt_from_decimal(decimal.Decimal(str(row[x])))
                row[x] = dt.strftime("%b %d %H:%M")
            dt = dt_from_decimal(decimal.Decimal(str(row[3])))
            row[3] = dt.strftime("%a %b %d")
        dump_results(r)


    if cmd == 'report':
        report_id = safe_arg(2)
        r = get_report(report_id)

        metadata = r[0]
        report = r[1:]
        if metadata.get('raw_text', False):
            for line in report:
                print line
        else:
            metadata_report = [['Key', 'Value']]
            for k, v in metadata.iteritems():
                metadata_report.append([k, v])
            print "Report Metadata"
            dump_results(metadata_report)

            print "Report Details"
            dump_results(report)
