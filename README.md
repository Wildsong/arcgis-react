# arctic

## Overview

Dashboard for ArcGIS Online/ArcGIS Portal.

This is a sandbox at the moment where I am testing out some ideas.

Today (29-Mar-22) I got an urge to try Webhooks so, see the README in the webhooks/ folder.
I think that it will end up being a microservice that catches events from Enterprise and publishes them via MQTT.
Hence the mqtt_broker/ and mqtt_test/ folders, which I have not look at for a few months.

For Prometheus + Grafana in Docker, 
see the README in the prometheus/ folder.

## Architecture

### Content management

This component recognizes how pathetic it is to not know what the dependencies are
between feature layers and maps and apps. 

Use cases:

1. I want to be able to confidently delete a service, knowing that it's not being used anywhere.
2. I want notification of things that are broken.

inventory_builder/ scans everything, at least once to initialize

* portal_scanner.py scans for maps and layers in Portal
* server_scanner.py scans for services in GIS Server
* aprx_scanner.py scans for maps and layers in APRX files
* app_scanner.py scans web appbuilder apps
* Everything gets records in a database

A python program 

* Watches for changes
* Updates the database

Web app

* GraphQL backend talks to the database
* A React front end visualizes contents of database

### License management

### Server management

## Set up

I stopped embedding username and password in a .env file, now I embed a 
PORTAL_PROFILE setting. Create a Portal profile, embed your username and
password in **it**. Then reference the profile instead of a plaintext password.

### Conda environment for Python packages

    conda create --name=arctic --file=requirements.txt -c conda-forge -c esri
    conda activate arctic

### FlexLM

I am now adding support for the ESRI LicenseManager (flexlm)
by merging in code from my previous docker project docker-flexlm.

The code for it is currently in mqtt_test because I am testing
using it to queue messages using MQTT. There is a client program
that subscribes to messages and a logwatch.py script that will
eventually watch the log file for FlexLM and publish changes to MQTT.

### NPM and Node

The JavaScript portions of this project uses npm and the parcel bundler. Currently I do this by running the whole environment
in a docker container.

This saves me from having to install about 100 node packages
on the hosting server.

## Log files

Processing log files with ArcGIS Enterprise is problematic because the data are split between the web server (I'm using IIS for now),
Portal, Server, and Data Store.

If you want to trace an activity, for example who is using any given REST based service, then you can't just read one log file.
If the service is in Server, then you can find requests but they don't log the IP address of the requestor. The "web adaptor" blocks that.
They need some redesign here to fix this! 

Currently I am thinking about using one of those fancy logging tools that sucks the log files into a database. Apparently I have not
started making notes on this yet, so I think I will put more notes on this for now at this page: 
https://wiki.wildsong.biz/index.php?title=Arctic_Logging

### Cleaning

See [Clean](https://developers.arcgis.com/rest/enterprise-administration/enterprise/clean-logs.htm) for ?everywhere? and [Clean Logs](https://developers.arcgis.com/rest/enterprise-administration/server/cleanlogs.htm) for Server.

There is also a REST service [Clean Directory](https://developers.arcgis.com/rest/enterprise-administration/server/cleandirectory.htm)

I cannot find any way to clean the statistics folder. Mine has files going back to 2019.

### Web adaptors

Web Adaptors come first because these are the most useful logs.

Look for the config files to find the logs.
On IIS, mine were in C:/inetpub/logs/LogFiles/W3SVC

The config files are in an XML file C:/inetpub/wwwroot/{portal|server}/Web.config. Grep for log. There are settings here, for example when to role the files (weekly). The logfile location is in the  "customlocation" property.

***Both adaptors are set to log to the same file, how special!
I am inclined to fix that.***

### Portal logs

Can be queried via API. 

### Server logs

Can be queried via API. Find the config-store location via an API call, then look in the filesystem.

The file {config-store}/arcgis-logsettings.json has "logDir" set
to C:/arcgisserver/logs/ on my server. Other settings are in here
too, like the current logLevel and the number of days to keep logs.

There are separate logs for {serverfolder}/logs/{server|services|errorreports}/. "Errorreports" appears to be dumps that are only useful to forensic technicians at Esri. "Services" has a folder with logs for each running service.

A digression: [Work with server statistics](https://enterprise.arcgis.com/en/server/latest/administer/windows/working-with-server-statistics.htm)
There is something called **statisticsDir** in {directories}/arcgissystem. There is a 'statistics' folder there that has
many many files in it. Looks like one for every day the server has been in operation. Geez! Each one is a CSV with data on each
service. "Do not manually modify or delete files in this directory"
It says here ["Use ArcGIS Server Manager to access, view, configure, and delete reports"](https://enterprise.arcgis.com/en/server/latest/administer/windows/about-server-statistics.htm).

See [Usage Reports Configuration](https://delta.co.clatsop.or.us/server/admin/usagereports/settings). Default for "Keep statistics history" was forever. I changed it to 30 days. I don't see any way to clean up the 1650 extra files. I will leave it a few days, maybe
it will figure out they need to go tonight.

### Datastore

#### Datastore health

I found this REST call to validate the servers, and it gives information
on BOTH not just a generic "yup it works" thing like in ArcGIS Server Manager.

https://delta.co.clatsop.or.us/server/admin/data/items/enterpriseDatabases/AGSDataStore_ds_atjwr8b3/machines/CC-GISLICENSE.CLATSOP.CO.CLATSOP.OR.US/validate

Sample of the JSON returned,

    {
    "datastore.release": "11.2.0.49116",
    "datastore.name": "ds_atjwr8b3",
    "datastore.replmethod": "ASYNC",
    "datastore.isReadOnly": "false",
    "datastore.isConfigured": "true",
    "machines": [
        {
        "machine.overallhealth": "Healthy",
        "datastore.release": "11.2.0.49116",
        "datastore.release.configstore": "1.5",
        "platform": "Windows",
        "machine.isReachable": "true",
        "hostip": "10.10.10.53",
        "name": "CC-GISDATASTORE.CLATSOP.CO.CLATSOP.OR.US",
        "role": "PRIMARY",
        "dbport": 9876,
        "initstarttime": 1710871148935,
        "healthcheck.enable": "true",
        "status": "Started",
        "adminurl": "https://CC-GISDATASTORE.CLATSOP.CO.CLATSOP.OR.US:2443/arcgis/datastoreadmin/",
        "db.isactive": "true",
        "db.isAccepting": "true",
        "db.isInRecovery": "false",
        "db.ActiveReplMethod": "ASYNC",
        "db.isManagedUserConnValid": "true",
        "datastore.release.pg": "14.5",
        "datastore.release.sde": "11.2.0",
        "datastore.release.geometry": "1.30.4.10",
        "datastore.release.geometrylib": "1.30.3.10",
        "db.isSiteConnValid": "true"
        },
        {
        "machine.overallhealth": "Healthy",
        "datastore.release": "11.2.0.49116",
        "datastore.release.configstore": "1.5",
        "platform": "Windows",
        "machine.isReachable": "true",
        "hostip": "10.10.10.150",
        "name": "CC-GISLICENSE.CLATSOP.CO.CLATSOP.OR.US",
        "role": "STANDBY",
        "dbport": 9876,
        "initstarttime": 1708912672553,
        "healthcheck.enable": "true",
        "status": "Started",
        "adminurl": "https://CC-GISLICENSE.CLATSOP.CO.CLATSOP.OR.US:2443/arcgis/datastoreadmin/",
        "db.isactive": "true",
        "db.isAccepting": "true",
        "db.isInRecovery": "true",
        "db.ActiveReplMethod": "ASYNC",
        "db.isManagedUserConnValid": "true",
        "datastore.release.pg": "14.5",
        "datastore.release.sde": "11.2.0",
        "datastore.release.geometry": "1.30.4.10",
        "datastore.release.geometrylib": "1.30.3.10",
        "db.isSiteConnValid": "true"
        }
    ],
    "datastore.release.configstore": "1.5",
    "datastore.release.geometry": "1.30.4.10",
    "datastore.release.geometrylib": "1.30.3.10",
    "datastore.release.sde": "11.2.0",
    "datastore.release.pg": "14.5",
    "datastore.layer.extent.updated": false,
    "datastore.status": "Started",
    "datastore.isActiveHA": "true",
    "datastore.overallhealth": "Healthy",
    "datastore.lastfailover": 1708278446754,
    "datastore.lastbackup": 1707677967241,
    "datastore.isRegistered": "true",
    "datastore.hasValidServerConnection": "true",
    "datastore.validServerMachinesList": [{
        "machineName": "CC-GISSERVER.CLATSOP.CO.CLATSOP.OR.US",
        "adminURL": "https://cc-gisserver.clatsop.co.clatsop.or.us:6443/arcgis/admin"
    }],
    "owningSystemUrl": "https://delta.co.clatsop.or.us/server",
    "status": "success"
    }

#### Datastore logs

Strangely there are no entries in the REST viewer.
I could not see a way to query it in the API. Maybe there is none.

Server has an API call to find out what datastore is connected.
The file is in {config-store}/data/enterpriseDatabases/AGSDataStore*/dataItem.json

Datastore log files are in {arcgisdatastore}/logs/{MACHINE_FQDN}/{server|couchlog|database}

The **server** logs are the most interesting, they are either empty or full of dire messages about the status of validation check failures. I need to look at this.

The **database** logs include vacuum, postgres, and pg_dump entries. The postgresql files are moderately interesting. The pg_dump entries are all empty.

I have not looked at the **couchdb** logs yet but we don't 
do any scene / 3D stuff yet so they are probably empty.

### Enterprise Databases

As with datastores, you can use the REST interface to look at these. 

You can examine (and edit!) configurations here. Caveat emptor.

For example here is the service that won't validate, and right away I see the problem.
It references Sql Server on cc-testmaps which is probably down right now. 
That's it. I brought the server online and validation now succeeds.
A better message than a little red X would be "SQL Server cc-testmaps is unreachable".

https://delta.co.clatsop.or.us/server/admin/data/items/enterpriseDatabases/TaxlotsYesterday_ds_gjiz0v6m2wk0cmdu/edit

    {
        "path": "/enterpriseDatabases/TaxlotsYesterday_ds_gjiz0v6m2wk0cmdu",
        "type": "egdb",
        "id": "7b236f0c5199475f995337723281e72c",
        "totalRefCount": 0,
        "info": {
            "isManaged": false,
            "connectionString": "ENCRYPTED_PASSWORD_UTF8=00022e682b76766176346277626b5554504d5a563161357a7a59376d495167344235624c5546466b6b386d757834633d2a00;ENCRYPTED_PASSWORD=00022e6867455a5535446d687441665351465a72794c393052484c703732466b706f364f70544774504a506f476f303d2a00;SERVER=cc-testmaps.clatsop.co.clatsop.or.us;INSTANCE=sde:sqlserver:cc-testmaps.clatsop.co.clatsop.or.us;DBCLIENT=sqlserver;DB_CONNECTION_PROPERTIES=cc-testmaps.clatsop.co.clatsop.or.us;DATABASE=gis_test;USER=sde;AUTHENTICATION_MODE=DBMS;HISTORICAL_TIMESTAMP=1/1/2024 1:58:28 PM",
            "dataStoreConnectionType": "shared",
            "portalProperties": {"itemID": "7b236f0c5199475f995337723281e72c"}
        }
    }

### File shares

You can also share files via Server, those show up in Data Stores as "folders".
You can see them via REST,

https://delta.co.clatsop.or.us/server/admin/data/items/fileShares

and the broken one shows up at 

https://delta.co.clatsop.or.us/server/admin/data/items/fileShares/TestTaxmaps_ds_ek9e4ig5ou7yrbks

and again I see the problem immediately -- it's a missing folder K:\webmaps\TestMaps
I wonder what was supposed to be in it? I made a new empty folder there.
I put a README in it. The connection JSON looks like this.

    {
        "path": "/fileShares/TestTaxmaps_ds_ek9e4ig5ou7yrbks",
        "type": "folder",
        "id": "be3c283f46014261b8e271010cc8f504",
        "clientPath": "K:\\webmaps\\TestMaps",
        "info": {
            "isManaged": false,
            "path": "\\\\cc-files01\\Applications\\GIS\\webmaps\\TestMaps",
            "hostName": "04-2288",
            "dataStoreConnectionType": "replicated",
            "portalProperties": {"itemID": "be3c283f46014261b8e271010cc8f504"}
        }
    }

I searched for "Data stores" in my content on Portal and see a folder I made 1/2/23.
I tried to delete it in Portal and got this error:
"Unable to delete item. This data store item is registered in at least one server. Go to the Settings tab of this data store to deselect all federated servers."
It says the server "https://delta.co.clatsop.or.us/server (Hosting Server)" is not available, but it is.

The info/path has a problem, it shows cc-files01 which no longer works.
I changed it to //cc-applications/ but that failed with 
"The data store item 'be3c283f46014261b8e271010cc8f504' can only be managed via Portal."
What's the REST for THAT fix?

I can't fix it and I can't delete it. I can't update the path in Portal because
it says it's not valid.

When I tried to share a new folder in Portal it said my hosting server is not available,
this is deeply disturbing.


### Resources

#### Esri

[Administering your GIS](https://developers.arcgis.com/python/guide/administering-your-gis/) Lots of interesting bits and bobs.

[Scripting ArcGIS Server administration](https://enterprise.arcgis.com/en/server/latest/develop/windows/scripting-arcgis-server-administration.htm)

#### Other

[OpenCV documentation](https://docs.opencv.org/4.2.0/)

[React Routing and Components for Signup and Login](https://saasitive.com/tutorial/react-routing-components-signup-login/)


[ArcGIS JavaScript API](https://developers.arcgis.com/javascript/latest/)  
[Portal access](https://developers.arcgis.com/javascript/latest/arcgis-organization-portals/) 

[ArcGIS REST API](https://developers.arcgis.com/rest/)  
[Web Map Specification](https://developers.arcgis.com/web-map-specification/)   
[load_web_map sample](https://developers.arcgis.com/javascript/latest/sample-code/webmap-basic/)  
[save_web_map sample](https://developers.arcgis.com/javascript/latest/sample-code/webmap-save/)  

