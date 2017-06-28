#!/usr/bin/python
# coding: utf8

import time
try:
    import pandas as pd
except ImportError:
    pd = None
try:
    import numpy as np
except ImportError:
    np = None


class HDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class Sensordata(object):
    DEFAULT_DAYS_BACK = 30

    def __init__(self, api, animal_id=None, device_id=None, days_back=None):
        self.api = api
        assert animal_id or device_id
        self.animal_id = animal_id
        self.device_id = device_id
        self.data = {}
        self.days_back = days_back or self.DEFAULT_DAYS_BACK

    def set_days_back(self, days_back):
        if int(days_back) == int(days_back):
            return
        # clear cache
        self.data = {}
        self.days_back = days_back

    def get(self, metric, days_back=None):
        if days_back is not None:
            self.set_days_back(days_back)
        if metric not in self.data:
            f = int(time.time() - self.days_back * 24 * 60 * 60)
            f = f - (f % 3600)
            t = int(time.time() + 24 * 60 * 60)
            t = t - (t % 3600)
            if self.animal_id:
                self.data[metric] = self.api.get_animal_sensordata(self.animal_id, metric, f, t)
            elif self.device_id:
                self.data[metric] = self.api.get_device_sensordata(self.device_id, metric, f, t)
        return self.data[metric]["data"]

    def get_series(self, metric, days_back=None):
        data = self.get(metric, days_back=days_back)
        return pd.Series([x[1] for x in data],
                         index=np.array([x[0] for x in data]).astype('datetime64[s]'))

    def get_frame(self, metrics, days_back=None):
        frames = [self.get_series(x, days_back=days_back).to_frame(name=x) for x in metrics]
        frame = pd.concat(frames, join="outer", axis=1)
        return frame


class Organisation(object):
    def __init__(self, api, _id):
        self.api = api
        self._id = _id
        self._data = None
        self._animals = None
        self._events = None

    @property
    def data(self):
        if not self._data:
            self._data = self.api.get_organisation_by_id(self._id)
        return self._data

    @property
    def name(self):
        return self.data["name"]

    @property
    def devices(self):
        return self.data["devices"]

    @property
    def timezone(self):
        return self.data["timezone"]

    @property
    def animals(self):
        if not self._animals:
            self._animals = self.api.get_organisation_animal_ids(self._id)
        return self._animals


class Animal(object):
    def __init__(self, api, _id):
        self.api = api
        self._id = _id
        self._data = None
        self._sensordata = None
        self._events = None

    @property
    def data(self):
        if not self._data:
            self._data = self.api.get_animal_by_id(self._id)
        return self._data

    @property
    def name(self):
        return self.data["name"]

    @property
    def mark(self):
        return self.data["mark"]

    @property
    def group_id(self):
        return self.data["group_id"]

    @property
    def tags(self):
        return self.data["tags"]

    @property
    def sensor(self):
        return self.data["sensor"]

    @property
    def metadata(self):
        return self.data["metadata"]

    @property
    def heats(self):
        return self.data["heats"]

    @property
    def lactations(self):
        return self.data["lactations"]

    @property
    def sensordata(self):
        if not self._sensordata:
            self._sensordata = Sensordata(self.api, animal_id=self._id)
        return self._sensordata

    def get_data(self, metric):
        self._sensordata.get(metric)

    @property
    def events(self):
        if not self._events:
            self._events = self.api.get_animal_events(self._id)
        return self._events