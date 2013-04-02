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

