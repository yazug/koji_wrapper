# -*- coding: utf-8 -*-

""" KojiPackage Module """

from koji_wrapper.wrapper import KojiWrapper
from koji_wrapper.validators import validate_required, validate_str_or_list
from koji_wrapper.util import convert_to_list


class KojiPackage(KojiWrapper):
    """Class to work with and gather koji package information"""

    def __init__(self, **kwargs):
        self.__list_packages_args = {}
        # TODO(jmls): figure out better way of seperating out kwargs
        self.list_packages_args = kwargs

        for arg in ('pkgID', 'userID', 'tagID', 'prefix', 'inherited', 'with_dups', 'event'):
            if arg in kwargs:
                del kwargs[arg]

        self.__data_list = None

        super().__init__(**kwargs)

    @property
    def list_packages_args(self):
        """:param list_packages_args: list_packages_args to filter results with."""
        return self.__list_packages_args

    @list_packages_args.setter
    def list_packages_args(self, args):
        for key, value in args.items():
            if key in ('pkgID', 'userID', 'tagID', 'prefix', 'inherited', 'with_dups', 'event'):
                if value is None and key in self.__list_packages_args:
                    del self.__list_packages_args[key]
                else: 
                    self.__list_packages_args[key] = value
            elif False:
               raise ValueError('Key {0} not on supported list for listPackages'.format(key))

    def fetch_data(self):
        self.__data_list = self.session.listPackages(**self.list_packages_args)

    def __iter__(self):
        if self.__data_list is None:
            self.fetch_data()

        self.__iterable = (obj for obj in self.__data_list)
        return self.__iterable

    def __next__(self):
        return next(self.__iterable)
