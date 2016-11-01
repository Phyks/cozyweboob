#!/usr/bin/env python2
"""
Wrapper script around Weboob to be able to use it in combination with Cozy +
Konnectors easily.

Part of this code comes from [Kresus](https://github.com/bnjbvr/kresus/)
written by bnjbvr and released under MIT.
"""
from __future__ import absolute_import
from __future__ import print_function

import logging

from weboob.core import Weboob
from weboob.exceptions import ModuleInstallError

import cozyweboob.tools.weboob_tools as weboob_tools

from cozyweboob.tools.progress import DummyProgress


# Module specific logger
logger = logging.getLogger(__name__)


class WeboobProxy(object):
    """
    Connector is a tool that connects to common websites like bank website,
    phone operator website... and that grabs personal data from there.
    Credentials are required to make this operation.

    Technically, connectors are weboob backend wrappers.
    """

    @staticmethod
    def version():
        """
        Get Weboob version.

        Returns:
            the version of installed Weboob.
        """
        return Weboob.VERSION

    def __init__(self):
        """
        Create a Weboob handle.
        """
        # Get a weboob instance
        self.weboob = Weboob()
        self.backend = None

    def install_modules(self, capability=None, name=None):
        """
        Ensure latest version of modules is installed.

        Args:
            capability: Restrict the modules to install to a given capability.
            name: Only install the specified module.
        Returns: A map between name and infos for all installed modules.
        """
        repositories = self.weboob.repositories
        # Update modules list
        repositories.update_repositories(DummyProgress())
        # Get module infos
        if name:
            modules = {name: repositories.get_module_info(name)}
        else:
            modules = repositories.get_all_modules_info(capability)
        # Install modules if required
        for infos in modules.values():
            if infos is not None and (
                    not infos.is_installed() or
                    not infos.is_local()
            ):
                try:
                    repositories.install(infos, progress=DummyProgress())
                except ModuleInstallError as exception:
                    logger.info(str(exception))
        return {
            module_name: dict(infos.dump())
            for module_name, infos in modules.items()
            if infos.is_installed()
        }

    def list_modules(self, capability=None, name=None):
        """
        Ensure latest version of modules is installed.

        Args:
            capability: Restrict the modules to install to a given capability.
            name: Only install the specified module.
        Returns: The list of installed module infos.
        """
        # Update modules and get the latest up to date list
        installed_modules = self.install_modules(
            capability=capability,
            name=name
        )
        # For each module, get back its config options and website base url
        for module_name in installed_modules:
            module = self.weboob.modules_loader.get_or_load_module(module_name)
            installed_modules[module_name]["config"] = (
                weboob_tools.dictify_config_desc(module.config)
            )
            installed_modules[module_name]["website"] = module.website
        return installed_modules

    def init_backend(self, modulename, parameters):
        """
        Backend initialization.

        Returns:
            the built backend.
        """
        # Ensure module is installed
        self.install_modules(name=modulename)
        # Build backend
        self.backend = self.weboob.build_backend(modulename, parameters)
        return self.backend
