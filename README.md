# stacky

Command line interface to StackTach (https://github.com/rackspace/stacktach)

set STACKTACH_URL to point to your StackTach web server.

## Requires
pip install -r pip_requires.txt

## Help
```
$ ./stacky.py 
Usage: stacky <command>
    deployments - list stacktach deployments
    events      - list of unique event names
    watch       - watch <deployment id> <event-name> <polling sec>
                   deployment id 0 = all
                   event-name empty = all
                   polling = 2s
    show    - inspect event ####
    uuid    - inspect events with uuid xxxxx
    summary - show summarized timings for all events
    timings - show timings for <event-name> (no .start/.end)
    request - show events with <request id>
    reports - list all reports created from <start> to <end>
              Default is today.
              All times 24-hr UTC in YYYY-MM-DD HH:MM format.
              Example: stacky reports 2013-02-28 00:00 2013-02-28 06:00
                       will return all reports created from midnight to 6am
                       on Feb 28th.
    report  - get report <id>
    kpi     - crunch KPIs
    hosts   - list all host names
```

NOTE: *kpi* and *watch* commands are currently disabled. Will be fixed soon.

## Examples

### List event types
```
$ python stacky.py events
+---------------------------------------+
|               Event Name              |
+---------------------------------------+
|      compute.instance.create.end      |
|     compute.instance.create.start     |
|      compute.instance.delete.end      |
|     compute.instance.delete.start     |
|        compute.instance.exists        |
|  compute.instance.finish_resize.start |
|      compute.instance.reboot.end      |
|     compute.instance.reboot.start     |
|      compute.instance.rebuild.end     |
|     compute.instance.rebuild.start    |
|  compute.instance.resize.confirm.end  |
| compute.instance.resize.confirm.start |
|      compute.instance.resize.end      |
|    compute.instance.resize.prep.end   |
|   compute.instance.resize.prep.start  |
|     compute.instance.resize.start     |
|     compute.instance.shutdown.end     |
|    compute.instance.shutdown.start    |
|    compute.instance.snapshot.start    |
|        compute.instance.update        |
|       scheduler.run_instance.end      |
|    scheduler.run_instance.scheduled   |
|      scheduler.run_instance.start     |
+---------------------------------------+
```

### Lookup Nova instance by UUID
```
$ python stacky.py uuid bafe36de-aba8-46e8-9fe7-15b490e4cc01
Events related to bafe36de-aba8-46e8-9fe7-15b490e4cc01
+----------+---+----------------------------+--------------------+----------------------------------+------------------------------------------------------+----------+----------+----------------------+
|    #     | ? |            When            |     Deployment     |              Event               |                         Host                         |  State   |  State'  |        Task'         |
+----------+---+----------------------------+--------------------+----------------------------------+------------------------------------------------------+----------+----------+----------------------+
| 16373586 |   | 2013-04-09 14:31:50.345266 | cellA |     compute.instance.update      |   nova-api.foo.com    | building |   None   |         None         |
| 16373589 |   | 2013-04-09 14:31:54.211449 | cellB  | scheduler.run_instance.scheduled | nova-scheduler.foo.com |          |          |                      |
| 16373603 |   | 2013-04-09 14:32:11.773272 | cellB  |     compute.instance.update      |                   computehostA                    | building | building |      scheduling      |
... (and so on)
```

### Get details for an event
Take an event id from the above example and show its details:
```
$ python stacky.py show 16373586
+------------+-----------------------------------------------------+
|    Key     |                        Value                        |
+------------+-----------------------------------------------------+
|     #      |                       16373586                      |
|    When    |              2013-04-09 14:31:50.345266             |
| Deployment |                        cellA                        |
|  Category  |                     monitor.info                    |
| Publisher  |                  nova-api.foo.com                   |
|   State    |                       building                      |
|   Event    |               compute.instance.update               |
|  Service   |                         api                         |
|    Host    |                  nova-api.foo.com                   |
|    UUID    |         bafe36de-aba8-46e8-9fe7-15b490e4cc01        |
|   Req ID   |       req-5539174d-0cd9-40d9-a7d5-5aa883c20033      |
+------------+-----------------------------------------------------+
... (and so on)
```

### Get all events for request ID
Take the request id from above and get all the associated events:
```
$ python stacky.py request req-5539174d-0cd9-40d9-a7d5-5aa883c20033
+----------+---+----------------------------+--------------------+----------------------------------+------------------------------------------------------+----------+----------+----------------------+
|    #     | ? |            When            |     Deployment     |              Event               |                         Host                         |  State   |  State'  |        Task'         |
+----------+---+----------------------------+--------------------+----------------------------------+------------------------------------------------------+----------+----------+----------------------+
| 16373586 |   | 2013-04-09 14:31:50.345266 | cellA |     compute.instance.update      |   nova-api.foo.com    | building |   None   |         None         |
| 16373587 |   | 2013-04-09 14:31:51.196901 | cellB  |   scheduler.run_instance.start   | nova-scheduler.foo.com |          |          |                      |
| 16373589 |   | 2013-04-09 14:31:54.211449 | cellB  | scheduler.run_instance.scheduled | nova-scheduler.foo.com |          |          |                      |
| 16373592 |   | 2013-04-09 14:31:57.497054 | cellB  |    scheduler.run_instance.end    | nova-scheduler.foo.com |          |          |                      |
| 16373603 |   | 2013-04-09 14:32:11.773272 | cellB  |     compute.instance.update      |                   computehostA                    | building | building |      scheduling      |
... (and so on)
```
