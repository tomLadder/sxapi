# sxapi
smaXtec API Client

Python wrapper for the smaXtec public API

## Usage ##
To use the API smaXtec user credentials (smaXtec Messenger Account) are needed.

```
from sxapi import API

a = API(email="myuser@smaxtec.com", password="password")

# Get organisations
orgas = a.organisations

# Get Animals in an organisation
animals = orgas[0].animals

# Get Sensordata for an animal
data = animals[0].sensordata.get("temp")

# Get Events for an animal
events = animals[0].events
```