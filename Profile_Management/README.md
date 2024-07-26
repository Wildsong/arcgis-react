# arctic/Profile_Management

## ArcGIS Profiles

In ArcGIS Portal, profiles can be used instead of username and password in scripts.
Create a profile based on your username and you will be able
to run the scripts without providing your password.

If you have CREATOR permissions then the scripts will actually
be able to function as intended!

### How to create a profile

Run **MakeProfile.bat** and enter username and password and click "Make Profile".
This is darn fancy with a GUI and all.

You can run a couple lines from Python to do the same thing, for example this would create a profile called "NameOfProfile" that would log you in to the portal at myportal.somewhere.com.

```python
from arcgis.gis import GIS
GIS(url="https://my_portal.somewhere.com/portal", username="jsmith", password="YOUR_PLAINTEXT_PASSWORD", profile="NameOfProfile") 
```

## Internals

The MakeProfile.py script uses ArcGIS code to write to your .arcgisrprofile 
(in your home directory) and also to the Windows "credential manager". 
It will store the server name and username in the .arcgisprofile file and your password
will be securely stored in the credential manager.

*Linux note, I have not tested it there, Linux obviously does not use the Windows
credential manager but does support something else.*

### How profiles are used in Python scripts

Normally you'd have to put your username and password in a file somewhere
or type it in everytime you run a script. Here is how that looks in Python.

```python
gis = GIS(url="https://my_portal.somewhere.com/portal", username="jsmith", password="YOUR_PLAINTEXT_PASSWORD") 
```

Using a profile looks like this; no credentials are stored. It gets everything
from the profile including the Portal URL, username, and password.

```python
myprofile="whatever you called it when you created the profile"
gis = GIS(profile=myprofile) 
```

### To-do

* Make it work on Linux
* Make sure it works on ArcGIS Online
* I did not create any way to see what credentials exist or to delete old ones.
You can look in the file.
* Add pictures to this doc!

## Resources

There are some samples here on how to view and delete existing profiles.
https://github.com/achapkowski/profile_tools

