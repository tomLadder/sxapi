#!/usr/bin/python
# coding: utf8

__version__ = '0.5'


import time
import logging
import requests

from .low import LowLevelAPI
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