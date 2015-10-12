import pytest

@pytest.fixture(scope="module")
def application(qapp, request):
    return qapp

@pytest.fixture(scope="function")
def signal_receiver(application):
    from PyQt4 import QtCore
    class SignalReceiver(QtCore.QObject):
        def __init__(self, parent=None):
            QtCore.QObject.__init__(self, parent)
            self.int_values = []
            self.generic_values = []
            self.string_values = []

        @QtCore.pyqtSlot()
        def generic_slot(self):
            self.generic_values.append(None)

        @QtCore.pyqtSlot(str)
        def string_slot(self, value):
            self.string_values.append(value)

        @QtCore.pyqtSlot(int)
        def int_slot(self, value):
            self.int_values.append(value)

    return SignalReceiver(application)
