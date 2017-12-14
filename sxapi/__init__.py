#!/usr/bin/python
# coding: utf8

__version__ = '0.6'


import time
import logging
import requests

from .low import LowLevelAPI, LowLevelInternAPI
from .models import User, Animal, Organisation


class API(object):
    def __init__(self, email=None, password=None, api_key=None):
        """Initialize a new API client instance.
        """
        self.low = LowLevelAPI(email=email, password=password, api_key=api_key)

    @property
    def status(self):
        return self.low.get_status()

    def print_stats(self):
        for p in self.low.stats():
            print(p)

    @property
    def user(self):
        return User(api=self.low, data=self.low.get_user())

    @property
    def organisations(self):
        return [Organisation.create_from_data(api=self.low, data=x, _id=x["organisation_id"]) 
                for x in self.low.get_organisations()]

    def get_animal(self, animal_id):
        return Animal(api=self.low, _id=animal_id)

    def get_organisation(self, organisation_id):
        return Organisation(api=self.low, _id=organisation_id)


class InternAPI(object):
    def __init__(self, endpoint, api_key):
        """Initialize a new API client instance.
        """
        self.publiclow = LowLevelAPI(api_key=api_key)
        self.privatelow = LowLevelInternAPI(endpoint=endpoint, api_key=api_key)

    # def getAnimalIdsForOrganisation(self, organisation_id):
    #     p = {"organisation_id": organisation_id}
    #     res = self._get("animal/ids_by_organisation", api_type='public',
    #                     params=p)
    #     return res

    # def getAnimalsForOrganisation(self, organisation_id):
    #     p = {"organisation_id": organisation_id}
    #     res = self._get("animal/by_organisation", api_type='public',
    #                     params=p, timeout=20)
    #     return res

    # def getDeviceEventList(self, device_id, from_date, to_date):
    #     p = {"device_id": device_id, "offset": 0, "limit": 100,
    #          "from_date": int(from_date), "to_date": int(to_date)}
    #     res = []
    #     while True:
    #         it = self._get("event/query", api_type='public',
    #                        params=p)
    #         res += it["data"]
    #         if len(it["data"]) < p["limit"]:
    #             break
    #         p["offset"] += p["limit"]
    #     return res

    # def getAnimalEventList(self, animal_id, from_date, to_date):
    #     p = {"animal_id": animal_id, "offset": 0, "limit": 100,
    #          "from_date": int(from_date), "to_date": int(to_date)}
    #     res = []
    #     while True:
    #         it = self._get("event/query", api_type='public',
    #                        params=p)
    #         res += it["data"]
    #         if len(it["data"]) < p["limit"]:
    #             break
    #         p["offset"] += p["limit"]
    #     return res