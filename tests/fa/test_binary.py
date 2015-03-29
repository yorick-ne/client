from PyQt4.QtCore import QObject, pyqtSignal, QTimer

import bsdiff4
import pytest
import os
import fa
import random
import util
from util import work_dir
from mock import patch
from base64 import b64encode
import shutil

from hashlib import sha256

def randstr():
    return "%6x" % random.randint(0,0xFFFFFF)

retail_bin = None
faf_bin = None

@pytest.fixture(scope='module')
def fake_retail_bin(module_dir):
    files = [
        'BsSndRpt.exe',  # -v BugSplat Files
        'BugSplat.dll',  #  |
        'BugSplatRc.dll',#  |
        'DbgHelp.dll',   # -^

        'msvcm80.dll',       # -v MSVC80 Files
        'msvcp80.dll',
        'msvcr80.dll',
        'wxmsw24u-vs80.dll', # -^

        'SHSMP.DLL',   # -v Extra Files
        'sx32w.dll',
        'zlibwapi.dll',
        'splash.png'  # -^
    ]

    random.seed()
    global retail_bin
    retail_bin = module_dir + '/retail'
    os.mkdir(retail_bin)
    os.mkdir(retail_bin + '/bin')

    with work_dir(retail_bin + '/bin'):
        for file in files:
            with open(file, 'wb') as f:
                f.write(randstr())

        with open('ForgedAlliance.exe', 'wb') as f:
            f.write(b'Nobody expects the spanish inquisition.')

    return retail_bin

class FakeResponse(QObject):

    error = pyqtSignal(int, object)
    done = pyqtSignal(object)

    def __init__(self, data, error_code=None):
        super(FakeResponse,self).__init__()
        self.data = data
        self.error_code=error_code

        QTimer.singleShot(0, self.finish)

    def finish(self):
        if self.error_code:
            self.error.emit(self.error_code, self.data)
        else:
            self.done.emit(self.data)

@staticmethod
def mock_get_patch(from_hash, to_hash):

    patch = b64encode( bsdiff4.diff(b'Nobody expects the spanish inquisition.',
                 b'NOBODY!') )

    hash_check = sha256(b'NOBODY!').hexdigest()[:32]

    return FakeResponse({'patch_list':[patch], 'hash_check': hash_check})

@staticmethod
def mock_verify(a, b):
    return FakeResponse(True)

@pytest.fixture(scope='module')
def fake_client(module_dir):
    global faf_bin
    faf_bin = module_dir + '/faf_bin'
    os.mkdir(faf_bin)


pytestmark = pytest.mark.usefixtures("fake_retail_bin", "fake_client")

from contextlib import contextmanager

@contextmanager
def CONTEXT_EVERYTHING():
    with patch.object(fa.binary.PatchService, 'GetPatch', mock_get_patch):
        with patch.object(fa.binary.PatchService, 'Verify', mock_verify):
            with patch.object(util, 'BIN_DIR', faf_bin):
                with patch.object(util.settings, 'value', lambda x,**kwargs: retail_bin):
                    yield

def test_update(application):
    with CONTEXT_EVERYTHING():
        shutil.rmtree(faf_bin)
        os.mkdir(faf_bin)

        fa.binary.update_engine('something')

def test_patch(application):
    with CONTEXT_EVERYTHING():
        fa.binary.init_bin()
        fa.binary.patch_engine('something')

def test_verify(application):
    with CONTEXT_EVERYTHING():
        fa.binary.update_engine('something')
        assert fa.binary.verify_engine()

