#!/usr/bin/python
# coding: utf8

__version__ = '0.3'


import time
import logging
import requests

from .models import HDict, Animal, Organisation


class API(object):
    def __init__(self, email=None, password=None, api_key=None):
        """Initialize a new API client instance.
        """
        self.api_base_url = "https://api.smaxtec.com/api/v1"
        self.email = email
        self.password = password
        self.api_key = api_key

        self._session_key = None
        self._session_expiration = time.time() - 1
        self._session = None

    @property
    def session(self):
        """Geneate a new HTTP session on the fly and login.
        """
        if not self._session:
            self._session = requests.Session()
        # check login
        if not self._login():
            raise ValueError("invalid login information")
        return self._session

    @property
    def status(self):
        return self.get("/service/status")

    @property
    def user(self):
        if self.api_key:
            return None
        return self.get("/user")

    @property
    def organisations(self):
        if self.user:
            return [Organisation(self, x["organisation_id"]) for x in self.get("/organisation")]
        return []

    def to_url(self, path):
        return "{}{}".format(self.api_base_url, path)

    def _login(self):
        """Login to the api with api key or the given credentials.
        """
        # check expiration
        diff = time.time() - self._session_expiration
        if diff < 0.0:
            return True
        # try to use api key
        if self.api_key:
            self._session_key = self.api_key
            self._session.headers.update({"Authorization": "Bearer {}".format(self._session_key)})
            self._session_expiration = time.time() + 30 * 24 * 60 * 60
            return True
        # login with credentials
        if self.email is None or self.password is None:
            raise ValueError("email and password are needed for API access")
        params = {"email": self.email, "password": self.password}
        res = self._session.get(self.to_url("/user/get_token"), params=params)
        if res.status_code == requests.codes.ok:
            pass
        elif res.status_code == 401 or res.status_code == 409 or res.status_code == 422:
            raise ValueError("invalid login credentials")
        else:
            res.raise_for_status()
        self._session_key = res.json()["token"]
        self._session.headers.update({"Authorization": "Bearer {}".format(self._session_key)})
        self._session_expiration = time.time() + 24 * 60 * 60
        return True

    def get(self, path, *args, **kwargs):
        url = self.to_url(path)
        r = self.session.get(url, *args, **kwargs)
        r.raise_for_status()
        return r.json()

    def post(self, path, *args, **kwargs):
        url = self.to_url(path)
        r = self.session.post(url, *args, **kwargs)
        r.raise_for_status()
        return r.json()

    def put(self, path, *args, **kwargs):
        url = self.to_url(path)
        r = self.session.put(url, *args, **kwargs)
        r.raise_for_status()
        return r.json()

    def get_organisation_animal_ids(self, organisation_id):
        params = HDict({"organisation_id": organisation_id})
        animal_ids = self.get("/animal/ids_by_organisation", params=params)
        return [Animal(self, x["_id"]) for x in animal_ids]

    def organisation(self, organisation_id):
        return Organisation(self, organisation_id)

    def get_animal_by_id(self, animal_id):
        params = HDict({"animal_id": animal_id})
        return self.get("/animal/by_id", params=params)

    def get_organisation_by_id(self, organisation_id):
        params = HDict({"organisation_id": organisation_id})
        return self.get("/organisation/by_id", params=params)

    def get_sensor_data(self, animal_id):
        pass

    def animal(self, animal_id):
        return Animal(self, animal_id)

    def get_animal_sensordata(self, animal_id, metric, from_date, to_date):
        params = HDict({"animal_id": animal_id, "metric": metric,
                        "from_date": from_date, "to_date": to_date})
        return self.get("/data/query", params=params)

    def get_animal_events(self, animal_id, from_date=None, to_date=None):
        params = HDict({"animal_id": animal_id, "limit": 100, "offset": 0,
                        "from_date": None, "to_date":None})
        all_events = []
        while True:
            events = self.get("/event/query", params=params)
            all_events += events["data"]
            if len(events["data"]) < params["limit"]:
                break
            else:
                params["offset"] = events["pagination"]["next_offset"]
        return all_events