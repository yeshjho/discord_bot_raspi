from importlib import import_module
from pkgutil import walk_packages

import commands
from commands.command import Command

for module_finder, name, is_pkg in walk_packages(path=commands.__path__,
                                                 prefix=commands.__name__ + '.'):
    if not is_pkg and module_finder.find_spec(name).origin != __file__:
        import_module(name)

print(Command.__subclasses__())
