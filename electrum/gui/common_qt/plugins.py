from PyQt5.QtCore import pyqtSignal, pyqtProperty, QObject

<<<<<<<< HEAD:electrum_grs/gui/qml/plugins.py
from electrum_grs.i18n import _
from electrum_grs.logging import get_logger
========
from electrum.logging import get_logger
>>>>>>>> upstream/master:electrum/gui/common_qt/plugins.py


class PluginQObject(QObject):
    logger = get_logger(__name__)

    pluginChanged = pyqtSignal()
    busyChanged = pyqtSignal()
    pluginEnabledChanged = pyqtSignal()

    def __init__(self, plugin, parent):
        super().__init__(parent)

        self._busy = False

        self.plugin = plugin
        self.app = parent

    @pyqtProperty(str, notify=pluginChanged)
    def name(self): return self._name

    @pyqtProperty(bool, notify=busyChanged)
    def busy(self): return self._busy

    # below only used for QML, not compatible yet with Qt

    @pyqtProperty(bool, notify=pluginEnabledChanged)
    def pluginEnabled(self): return self.plugin.is_enabled()

    @pluginEnabled.setter
    def pluginEnabled(self, enabled):
        if enabled != self.plugin.is_enabled():
            self.logger.debug(f'can {self.plugin.can_user_disable()}, {self.plugin.is_available()}')
            if not self.plugin.can_user_disable() and not enabled:
                return
            if enabled:
                self.app.plugins.enable(self.plugin.name)
            else:
                self.app.plugins.disable(self.plugin.name)
            self.pluginEnabledChanged.emit()
