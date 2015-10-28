#!/usr/bin/env python

# ####################
import os
from functools import partial

from pluginbase import PluginBase

from util.singleton import Singleton


# ####################

# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)
plugin_base = PluginBase(package='plugins',
                         searchpath=[get_path('./plugins'), get_path('../plugins')])

@Singleton
class SiteParserFactory():

    """
    Chooses the right subclass function to call.
    """
    def __init__(self):
        self.plugins = {}

        self.source = plugin_base.make_plugin_source(
            searchpath=[get_path('./plugins'), get_path('../plugins')])

        print('Loading Plugins')
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            setup_op = getattr(plugin, "setup", None)
            if callable(setup_op):
                setup_op(self)

        print('Finished Loading Plugins')

    def register_plugin(self, name, plugin):
        """A function a plugin can use to register a formatter."""
        self.plugins[name] = plugin
        print("Loaded Plugin '%s'" % name)

    def get_instance(self, site):
        parser_class = self.plugins.get(site, None)

        if not parser_class:
            raise NotImplementedError("Site Not Supported")

        return parser_class()
