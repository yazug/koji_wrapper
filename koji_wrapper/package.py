# -*- coding: utf-8 -*-

""" KojiPackage Module """

from koji_wrapper.wrapper import KojiWrapper
from koji_wrapper.validators import validate_required, validate_str_or_list
from koji_wrapper.util import convert_to_list


class KojiPackage(KojiWrapper):
    """Class to work with and gather koji package information"""

    def __init__(self, tag_id=None, userID=None, pkgID=None, **kwargs):
        self._list_packages_args = {}
        # TODO(jmls): figure out better way of seperating out kwargs
        self.list_packages_args = kwargs

        super().__init__(**kwargs)

    @property
    def list_packages_args(self):
        """:param tag_id: tag_id to filter results with."""
        return self.__tag_id

    @tag.setter
    def list_packages_args(self, **kwargs):
        for key, value in kwargs.items():
            if key in ('pkgID', 'userID', 'tagID', 'prefix', 'inherited', 'with_dups', 'event'):
                if value is None and key in self.__list_packages_args:
                    del self.__list_packages_args[key]
                else: 
                    self.__list_packages_args[key] = value
            elif self.debug:
               raise ValueError('Key {0} not on supported list for listPackages'.format(key))


    def __iter__(self):
        self.__list = self.session.listPackages(**self.list_packages_args)
        return self.__list
