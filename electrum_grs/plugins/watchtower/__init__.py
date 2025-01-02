from electrum_grs.i18n import _

fullname = _('Watchtower')
description = """
Watchtower for Electrum-GRS.

Example setup:

  electrum-grs -o setconfig enable_plugin_watchtower True
  electrum-grs -o setconfig watchtower_user wtuser
  electrum-grs -o setconfig watchtower_password wtpassword
  electrum-grs -o setconfig watchtower_port 12345
  electrum-grs daemon -v

"""

available_for = ['cmdline']
