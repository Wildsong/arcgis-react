import os
from arcgis.gis import GIS

class Config(object):

    PORTAL_PROFILE = os.environ.get("PORTAL_PROFILE")

    #SERVER_URL = os.environ.get('SERVER_URL')
    #SERVER_ADMIN_USER = os.environ.get("SERVER_ADMIN_USER")
    #SERVER_ADMIN_PASSWORD = os.environ.get("SERVER_ADMIN_PASSWORD")

    #ARCGIS_ID = os.environ.get("ARCGIS_ID")
    #ARCGIS_SECRET = os.environ.get("ARCGIS_SECRET")

if __name__ == "__main__":
    import requests
    import json

    assert Config.PORTAL_PROFILE
    #assert Config.SERVER_URL
    #assert Config.SERVER_ADMIN_USER
    #assert(Config.SERVER_ADMIN_PASSWORD)

    # Test a connection via normal auth
    gis = GIS(profile=Config.PORTAL_PROFILE)
    print(gis)

    q = '*'
    list_of_maps = gis.content.search(
        q, item_type='web map', outside_org=False, max_items=5000)
    print("Maps found %d" % len(list_of_maps))

    # Dump the whole environment
    #d = os.environ
    #for k in d:
    #    print("%s : %s" % (k, d[k]))
    print("PYTHONPATH=", os.environ.get("PYTHONPATH"))

