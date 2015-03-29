# -------------------------------------------------------------------------------
# Copyright (c) 2014 Forged Alliance Forever Community Project.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the GNU Public License v3.0
# which accompanies this distribution, and is available at
# http://www.gnu.org/licenses/gpl.html
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#-------------------------------------------------------------------------------

import os
import bsdiff4
import shutil
import logging
from hashlib import sha256
from base64 import b64decode

log = logging.getLogger(__name__)

import util
from util import settings, work_dir

class PatchFailedError(StandardError):
    pass

from faftools.api import *

class PatchService(RestService):
    @staticmethod
    def GetPatch(from_exe_hash, to_commit_hash):
        return RestService._post(PATCH_SERVICE_URL + "/get-patch",
                          {'from_exe_hash': from_exe_hash,
                           'to_commit_hash': to_commit_hash})

    @staticmethod
    def Verify(exe_hash, version_hash):
        return RestService._post(PATCH_SERVICE_URL + "/verify",
            { 'a': exe_hash, 'b': version_hash })

def get_current_version():
    "Gets the stored version hash"
    with work_dir(util.BIN_DIR):
        try:
            with open('version.txt', 'rb') as ver_file:
                return ver_file.read().strip()
        except IOError:
            # File does not exist
            return None


def init_bin():
    "Initializes FAForever bin with files from settings-pointed FA game directory."

    log.debug('Initializing bin directory.')

    with work_dir(util.BIN_DIR):
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

        game_path = os.path.join(str(settings.value("ForgedAlliance/app/path", type=str)), "bin")

        for file in files:
            shutil.copyfile(os.path.join(game_path, file), file)

        if os.path.isfile(os.path.join(game_path, "steam_api.dll")):
            # Steam version
            shutil.copyfile(os.path.join(game_path, 'SupremeCommander.exe'), 'ForgedAllianceForever.exe')
        else:
            # Assume retail
            shutil.copyfile(os.path.join(game_path, 'ForgedAlliance.exe'), 'ForgedAllianceForever.exe')

def patch_engine(to_hash):
    "Assumes engine needs patching."
    with work_dir(util.BIN_DIR):
        with open('ForgedAllianceForever.exe', 'r+b') as exe_file:
            exe_data = exe_file.read()
            exe_file.seek(0)
            exe_hash = sha256(exe_data).hexdigest()[:32]

            def error(code, message):
                raise PatchFailedError(code, message)

            def done(data):
                exe_data_ = exe_data

                for patch in data['patch_list']:
                    patch_bin = b64decode(patch)

                    exe_data_ = bsdiff4.patch(exe_data_, patch_bin)

                new_hash = sha256(exe_data_).hexdigest()[:32]

                if new_hash != data['hash_check']:
                    raise PatchFailedError('Post-patching hash check failed.')

                exe_file.write(exe_data_)

            patch_req = PatchService.GetPatch(exe_hash, to_hash)
            patch_req.error.connect(error)
            patch_req.done.connect(done)

            util.waitForSignals(patch_req.error, patch_req.done)

        with open('version.txt', 'wb') as ver_file:
            ver_file.write(to_hash)

def verify_engine():
    "Verifies engine hash against stored engine version."

    with work_dir(util.BIN_DIR):

        # Hash the engine
        with open('ForgedAllianceForever.exe', 'rb') as exe_file:
            exe_hash = sha256(exe_file.read()).hexdigest()[:32]

        # Get the stored version hash
        with open('version.txt', 'rb') as ver_file:
            ver_hash = ver_file.read().strip()

        ret = []
        def error(code, message):
            ret.append(False)

        def done(data):
            ret.append(True)

        verify_req = PatchService.Verify(exe_hash, ver_hash)
        verify_req.error.connect(error)
        verify_req.done.connect(done)

        util.waitForSignals(verify_req.error, verify_req.done)

        return ret[0]

def update_engine(to_hash):
    "Updates/verifies the engine executable to a specific git hash version."

    try:
        if not os.path.exists(util.BIN_DIR):
            os.mkdir(util.BIN_DIR)
            current_version = None
        else:
            current_version = get_current_version()

        if current_version is None:
            init_bin()
            current_version = 'unknown'

        if current_version == to_hash:
            log.info("Updating Engine to %s => Verifying", to_hash)
            if not verify_engine():
                # Engine verification failed, likely something corrupted/fiddled with
                init_bin()
                patch_engine(to_hash)
        else:
            log.info("Updating Engine to %s => Patching", to_hash)
            patch_engine(to_hash)
    except Exception as e:
        log.exception("Updating Engine failed: %s",e)
    else:
        log.info('Successfully updated engine.')
