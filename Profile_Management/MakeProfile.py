import os
import tkinter as tk
from arcgis.gis import GIS

default_profile_name = "delta"
default_url = "https://delta.co.clatsop.or.us/portal/"

# Some users have an @CLATSOP and some don't, the profile is always named after the basic name,
# and you have to know if you need to add the @CLATSOP or not. (Brian or Krysta)
default_user = os.environ.get('USERNAME')

def make_profile(profile_name: str, url: str, user: str, passwd: str) -> None:
    """ Make a new profile entry

    Args:
        profile_name (str): the name of the profile, eg. "delta"
        url (str): the url of the portal
        user (str): the username
        passwd (str): the password

    Returns:
        str: Returns None on success or the error message in a string. 
    """
    try:
        gis = GIS(url = url, username=user, password=passwd, profile=profile_name)
        print("Result", gis)
        if gis: 
            result = None
    except Exception as e:
        print("Error:",e)
        result=e
    return result

def we_are_done():
    exit(0)

def process_credentials() :
    global default_url, default_user, profleentry, urlentry, userentry, passentry, response, window

    profile = profileentry.get()
    url = urlentry.get()
    user = userentry.get()
    password = passentry.get()
    #print(f"Username=\"{user}\" Password=\"{password}\"")

    if not url:
        response.configure(text="Enter Portal URL.")
        return

    if user and password: 
        result = make_profile(profile, url, user, password)
        if not result:
            response.configure(text="Saved.")
            tk.Button(window, text="Finish", command=we_are_done).grid(row=7, column=1)
        else:
            response.configure(text=result)
    else:
        response.configure(text="Enter username and password.")

    return


window = tk.Tk()
window.title("Create ArcGIS Profile")
window.geometry("400x180")

MINWIDTH=55

tk.Label(window, text="Profile").grid(row=0, column=0, sticky="w")
profileentry = tk.Entry(window, width=MINWIDTH)
profileentry.grid(row=0, column=1, sticky="w")
profileentry.insert(0, default_profile_name)

tk.Label(window, text="Portal URL").grid(row=1, column=0, sticky="w")
urlentry = tk.Entry(window, width=MINWIDTH)
urlentry.grid(row=1, column=1, sticky="w")
urlentry.insert(0, default_url)
    
tk.Label(window, text="Username").grid(row=2, column=0)
userentry = tk.Entry(window, width=MINWIDTH)
userentry.grid(row=2, column=1, sticky="w")
userentry.insert(0, default_user)

tk.Label(window, text="Password").grid(row=3, column=0, sticky="w")
passentry = tk.Entry(window, show="*", width=MINWIDTH)
passentry.grid(row=3, column=1)

tk.Button(window, text="Make profile", command=process_credentials, justify="left").grid(row=4, column=1, sticky="w")

response = tk.Label(window, text="Krysta and Brian should add @CLATSOP to username.", justify="left")
response.grid(row=6, column=1, sticky="w")

print("There should be a dialog on your screen somewhere now.")
window.mainloop()

# That's all!
