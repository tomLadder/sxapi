# sxapi
smaXtec API Client

Python wrapper for the smaXtec public API

## Usage ##
To use the API smaXtec user credentials (smaXtec Messenger Account) are needed.

```
from sxapi import API

a = API(email="myuser@smaxtec.com", password="mypassword")

# Get organisations
orgas = a.organisations
print orgas

# Get Animals in an organisation
animals = orgas[0].animals
print animals
# Get Sensordata for an animal
data = animals[0].get_frame(["temp", "act"], days_back=10)
print(data)

# Get Events for an animal
events = animals[0].get_events()
print(events.to_series())

# Get by id
print a.get_organisation("5721e3f8a80a5f54c6315131").devices
print a.get_animal("572209c1a80a5f54c631513f").name
print a.get_animal("572209c1a80a5f54c631513f").heats
print a.get_animal("572209c1a80a5f54c631513f").lactations

# Show request stats
a.print_stats()
```