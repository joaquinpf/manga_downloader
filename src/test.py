import os
from functools import partial
from pluginbase import PluginBase


# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)


# Setup a plugin base for "example.modules" and make sure to load
# all the default built-in plugins from the builtin_plugins folder.
plugin_base = PluginBase(package='plugins',
                         searchpath=[get_path('./plugins')])


class Application(object):
    """Represents a simple example application."""

    def __init__(self):
        # And a dictionary where it stores "formatters".  These will be
        # functions provided by plugins which format strings.
        self.plugins = {}

        # and a source which loads the plugins from the "app_name/plugins"
        # folder.  We also pass the application name as identifier.  This
        # is optional but by doing this out plugins have consistent
        # internal module names which allows pickle to work.
        self.source = plugin_base.make_plugin_source(
            searchpath=[get_path('./plugins')])

        # Here we list all the plugins the source knows about, load them
        # and the use the "setup" function provided by the plugin to
        # initialize the plugin.
        print('Loading Plugins:')
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            plugin.setup(self)
        print('Finished Loading Plugins:')

    def register_plugin(self, name, plugin):
        """A function a plugin can use to register a formatter."""
        self.plugins[name] = plugin
        print("Loaded Plugin '%s': %s" % (name, plugin))

def main():
    Application()

if __name__ == '__main__':
    main()
