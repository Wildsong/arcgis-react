"""
    The Portal keeps lots of information about its contents,
    this script gets information from it and puts it into our database.
"""
import os
import json
import datetime
from collections import defaultdict
from arcgis.gis import GIS
from arcgis.gis.admin import PortalAdminManager, PortalResourceManager
from arcgis.mapping import WebMap

import database
from config import Config

VERSION = '1.0.1'
path, exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

exclude_esri = '-owner:esri -owner:esri_apps'

class PortalScan(object):

    types = [
        'AppBuilder Extension', 
        'Application', 
        'Desktop Application','Desktop Application Template', 
        'Site Application', 
        'Document Link', 
        'Administrative Report',
        'Form', 'Site Page',
        'CSV', 'Microsoft Excel', 'Microsoft Word', 'PDF', 'KML',
        'Map Area', 
        'WMS', 'WMTS',
        'Code Attachment', 'Code Sample',
        'Geoprocessing Service',
        'Dashboard', 'StoryMap', 'StoryMap Theme',
        'Web Experience', 'Web Mapping Application', 
        'Image', 
        'Geometry Service',
        'Feature Service',
        'Shapefile',  
        'Layer Package', 'Tile Package', 
        'SQLite Geodatabase',
        'Vector Tile Service', 'Vector Tile Package', 
        'Web Scene', 'Service Definition', 'Map Service', 
        'Web Map', ]

    def __init__(self, gis) -> None:
        self.gis = gis
        pass

    def scanEverything(self) -> None:

        #self.inventory_apps() # This is not done yet
        self.inventory_maps()
        self.inventory_services()

        # https://developers.arcgis.com/python/api-reference/arcgis.gis.admin.html#portaladminmanager
        pam = PortalAdminManager(self.gis.url + 'sharing/rest/', gis=self.gis)
        # pam.category_schema # manage categories

        print("Version:", pam.info['currentversion'])

        # TODO whatever I think I know this already anyway
        #for machine in pam.machines.list():
        #    print("machine:", machine.name)

        pdb = pam.system.database # internal database properties

        # There are 4 of these, content, index, db, temp
        for dir in pam.system.directories:
            print(dir.properties)

        emailman = pam.system.email
#        emailman.update(server='YOURDOMAIN.gov', 
#                        from_email='you@yourdomaingov', 
#                        require_auth=True,
#                        port=587, encryption='TLS',
#                        username='joe', password='joe')
        # you can update all the email settings
        try :
#            emailman.test('bwilson@clatsopcounty.gov')
            pass
        except Exception as e:
            print("Email send failed.", e)

        print("Indexes:")
        indexman = pam.system.indexer
        # you can run the indexer or check its status
        istatus = indexman.status
        # same as
        #index_status = pam.system.index_status
        for inx in istatus['indexes']:
            print(inx)

        # I can get the we machine name, url, ip address...
        print("Web adaptors:")
        for wa in pam.system.web_adaptors.properties['webAdaptors']:
            print(wa)

        print("UX: ")
        print(pam.ux.name,
            pam.ux.admin_contacts,
            pam.ux.contact_link,
            pam.ux.description,
            pam.ux.summary)
#        pam.ux.featured_content
#        pam.ux.gallery_group
#        pam.ux.get_logo
#        pam.ux.navigation_bar()
#        pam.ux.shared_theme()

        print("Web hooks:")
        whman = pam.webhooks
        # You can create webhooks, change settings
        for wh in whman.list():
            print(wh.properties)

        tasks = pam.scheduled_tasks()
        if tasks:
            print("Scheduled tasks:")
            for item in tasks:
                print(item)
            print()
        
        feds = pam.federation.servers['servers']
        for server in feds:
            print("Federated server:", server['name'])
        
        self.licenses(pam.license)
        self.resources()
        self.logs(pam.logs)

        return

    def maps(self) -> None:
        contents = self.gis.content.search(query="*")
        print(contents)
        return
    
    def resources(self) -> None:
        """ "Resources" are typically image files and other files. """

        # Not sure how there can be duplicate keys here but...
        print("Portal \"resources\":")
        prm = PortalResourceManager(self.gis)
        i = 0
        for item in prm.list():
            print(i, item['key'])
            i += 1
        print()
        return

    def licenses(self, licman) -> None:
        # I don't have any?
        # I think this would be extra licenses like image server or something
        all = licman.all()
        print("licenses:", all)
        return


    def inventory_apps(self):
        dtype = {} # A dictionary of all item types
        applications = [
            'Application',
            'Code Attachment',
            'Dashboard',
            'Desktop Application Template',
            'Desktop Application',
            'Web Experience', 
            'Web Mapping Application',
        ]
        for item in items: 
            if item.type in applications:
                print(item)
                if not item.type in dtype:
                    dtype[item.type] = {}
                dtype[item.type][item.id] = item

        return dtype


    def inventory_maps(self, query=''):
        q = query + ' ' + exclude_esri
        list_of_maps = self.gis.content.search(q, item_type='web map', max_items=-1)
        print("Maps found %d" % len(list_of_maps))
        
        # Build a dictionary with each layer as the index
        # and a list of the maps that the layer participates in
        layer_dict = defaultdict(list)

        for item in list_of_maps:
            # Look up the layers.
            wm = WebMap(item)
            mapId = wm.item.id
            for l in wm.layers:
                try:
                    layer_dict[l.itemId].append(mapId)
                    pass
                except Exception as e:
                    layer_dict[l.id].append(mapId)
                    pass

        # Each item is indexed by a layer id and contains a list of the maps containing that id.
        print(layer_dict)

        # Now make another dictionary that is indexed by type.
        dtype = defaultdict(dict)
        for item in list_of_maps: 
            dtype[item.type][item.id] = item

        print(dtype)
        return


    def inventory_services(self) -> None:
        self.interesting_services = list()
        interesting_types = ['Map Service', 'Feature Service']
        urls = list()

        myservers = self.gis.admin.servers.list()
        for f in myservers[0].services.folders:
            services = myservers[0].services.list(folder=f)
            print("Checking folder=\"%s\"; %d services." % (f, len(services)))
            for s in services:
                properties = s.iteminformation.properties
                if 'type' in properties:
                    #print(properties['type'])
                    if properties['type'] in interesting_types:
                        self.interesting_services.append(s)
                    else:
                        print("Not interesting: ", properties['title'], ':', properties['type'])
                else:
                    if 'GPServer' in s.url:
                        continue
                    if 'GeometryServer' in s.url:
                        continue
                    if 'VectorTileServer' in s.url:
                        continue
                    if 'ImageServer' in s.url:
                        continue
                    urls.append(s.url)

        for url in urls:
            print(url)

        for s in self.interesting_services:
            properties = s.iteminformation.properties
            if properties['type'] == 'Map Service':
                print("MapServer", s.url)
                continue
            else:
                print(properties)

        cm = self.gis.content

        q = 'title:EGDB_surveys -owner:esri -owner:esri_apps -owner:esri_nav'

        items = cm.search(q, item_type='Feature Service', max_items=-1)
        print("Feature Services", len(items))
        for item in items:
            print(item.title, item.type)
            try:
                for l in item.layers:
                    print(l)
                    continue
            except Exception as e:
                pass

        items = cm.search(q, item_type='Map Service', max_items=-1)
        print("Map Services", len(items))
        for item in items:
            print(item.title)
            for layer in item.layers:
                print(layer, layer.source)

        

#    q = "NOT owner:esri_apps"
#    items = gis.content.search(q, outside_org=False, max_items=5000)
#    print("Items found %d" % len(items))
#    dtype = get_apps(items)
#    print(dtype)
#    generate_html(dtype)


    def logs(self, log) -> None:
        """
        logs is a Logs object
        which is different than the one that Server uses!!
        """
        # https://developers.arcgis.com/python/api-reference/arcgis.gis.admin.html#arcgis.gis.admin.Logs

        # Let's look at a week of logs
        start = datetime.datetime.now() - datetime.timedelta(days=7)

        # There is also a "query_filter" parameter here that could be useful
        logdict = log.query(start_time=start, level="WARNING", page_size=1000)
        
        for entry in logdict['logMessages']:
            unixtime = int(entry['time']) / 1000
            ts = datetime.datetime.fromtimestamp(unixtime).strftime("%Y-%m-%d %H:%M:%S")
            machine = entry['machine'] # I need to truncate this
            print(f"{ts} {entry['source']} {machine} {entry['message']}")

        return

if __name__ == "__main__":

    gis = GIS(profile=Config.PORTAL_PROFILE)
    portal = PortalScan(gis)

    #portal.scanEverything()
    services = portal.inventory_services() # All I am interested in today.

    print("All done!")

