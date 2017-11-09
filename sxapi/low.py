#!/usr/bin/python
# coding: utf8


import time
import logging
import requests
from requests.exceptions import HTTPError

from .models import HDict
from .helper import splitTimeRange


class Req(object):
    def __init__(self, url, status, start, end=None):
        self.url = url
        self.start = start
        self.status = status
        if end is None:
            self.end = time.time()
        else:
            self.end = end
    
    @property
    def timer(self):
        return self.end - self.start


class LowLevelAPI(object):
    def __init__(self, email=None, password=None, api_key=None):
        """Initialize a new low level API client instance.
        """
        self.api_base_url = "https://api.smaxtec.com/api/v1"
        self.email = email
        self.password = password
        self.api_key = api_key

        self._session_key = None
        self._session_expiration = time.time() - 1
        self._session = None
        self.counter = 0
        self.requests = []

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

    def track_request(self, url, status, start):
        self.counter += 1
        self.requests.append(Req(url, status, start))
        if len(self.requests) > 100:
            self.requests.pop(0)

    def stats(self):
        out = []
        out.append("{} Requests".format(self.counter))
        for r in self.requests:
            out.append("{} in {} seconds".format(r.url, r.timer))
        return out

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
        self._session_expiration = time.time() + 23 * 60 * 60
        return True

    def get(self, path, *args, **kwargs):
        url = self.to_url(path)
        start = time.time()
        r = self.session.get(url, *args, **kwargs)
        self.track_request(url, r.status_code, start)
        if 400 <= r.status_code < 500:
            raise HTTPError("{} Error: {}".format(r.status_code, r.json().get("message", "unknown")))
        r.raise_for_status()
        return r.json()

    def post(self, path, *args, **kwargs):
        url = self.to_url(path)
        start = time.time()
        r = self.session.post(url, *args, **kwargs)
        self.track_request(url, r.status_code, start)
        if 400 <= r.status_code < 500:
            raise HTTPError("{} Error: {}".format(r.status_code, r.json().get("message", "unknown")))
        r.raise_for_status()
        return r.json()

    def put(self, path, *args, **kwargs):
        url = self.to_url(path)
        start = time.time()
        r = self.session.put(url, *args, **kwargs)
        self.track_request(url, r.status_code, start)
        if 400 <= r.status_code < 500:
            raise HTTPError("{} Error: {}".format(r.status_code, r.json().get("message", "unknown")))
        r.raise_for_status()
        return r.json()

    def get_status(self):
        return self.get("/service/status")

    def get_organisations(self):
        if self.api_key:
            return []
        return self.get("/organisation")

    def get_user(self):
        if self.api_key:
            return {"type": "apikey"}
        u = self.get("/user")
        u["type"] = "email"
        return u

    def get_organisation_animal_ids(self, organisation_id):
        params = HDict({"organisation_id": organisation_id})
        animal_ids = self.get("/animal/ids_by_organisation", params=params)
        return [x["_id"] for x in animal_ids]

    def get_animal_by_id(self, animal_id):
        params = HDict({"animal_id": animal_id})
        return self.get("/animal/by_id", params=params)

    def get_device_by_id(self, device_id):
        params = HDict({"device_id": device_id})
        return self.get("/device/by_id", params=params)

    def get_organisation_by_id(self, organisation_id):
        params = HDict({"organisation_id": organisation_id})
        return self.get("/organisation/by_id", params=params)

    def get_device_sensordata(self, device_id, metric, from_date, to_date):
        data = []
        for f, t in splitTimeRange(from_date, to_date, 100):
            data += self._get_device_sensordata(device_id, metric, f, t)["data"]
        return data

    def _get_device_sensordata(self, device_id, metric, from_date, to_date):
        params = HDict({"device_id": device_id, "metric": metric,
                        "from_date": from_date, "to_date": to_date})
        return self.get("/data/query", params=params)

    def get_animal_sensordata(self, animal_id, metric, from_date, to_date):
        data = []
        for f, t in splitTimeRange(from_date, to_date, 100):
            data += self._get_animal_sensordata(animal_id, metric, f, t)["data"]
        return data

    def _get_animal_sensordata(self, animal_id, metric, from_date, to_date):
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

    def get_device_events(self, device_id, from_date=None, to_date=None):
        params = HDict({"device_id": device_id, "limit": 100, "offset": 0,
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
