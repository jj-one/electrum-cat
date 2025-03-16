from electrum_cat.i18n import _

fullname = _('Watchtower')
description = """
Watchtower for Electrum-CAT.

Example setup:

  electrum-cat -o setconfig enable_plugin_watchtower True
  electrum-cat -o setconfig watchtower_user wtuser
  electrum-cat -o setconfig watchtower_password wtpassword
  electrum-cat -o setconfig watchtower_port 12345
  electrum-cat daemon -v

"""

available_for = ['cmdline']
