from electrum_cat.i18n import _

fullname = _('SwapServer')
description = """
Submarine swap server for an Electrum-CAT daemon.

Example setup:

  electrum-cat -o setconfig enable_plugin_swapserver True
  electrum-cat -o setconfig swapserver_port 5455
  electrum-cat daemon -v

"""

available_for = ['cmdline']
