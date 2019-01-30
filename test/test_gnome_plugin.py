# -*- coding: utf-8 -*-
#
# NotifyGnome - Unit Tests
#
# Copyright (C) 2019 Chris Caron <lead2gold@gmail.com>
#
# This file is part of apprise.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

import mock
import sys
import types
import apprise

try:
    # Python v3.4+
    from importlib import reload
except ImportError:
    try:
        # Python v3.0-v3.3
        from imp import reload
    except ImportError:
        # Python v2.7
        pass


@mock.patch('gi.module.get_parent_for_object')
@mock.patch('gi.repository.Notify.Notification')
@mock.patch('gi.repository.GdkPixbuf.Pixbuf')
def test_gnome_plugin(mock_pixbuf, mock_notify, mock_parent):
    """
    API: NotifyGnome Plugin()

    """

    # Clear any previously loaded libraries
    for mod in list(sys.modules.keys()):
        if mod.startswith('gi.') or mod == 'gi':
            del(sys.modules[mod])

    # We need to fake our gnome environment for testing purposes
    gi_name = 'gi'
    gi_repository_name = 'gi.repository'
    gi = types.ModuleType(gi_name)

    # Emulate require_version function1k:
    gi.require_version = mock.Mock(
        name=gi_name + '.require_version')

    # Now handle dependencies
    gi.repository = mock.Mock(
        name=gi_repository_name)
    gi.repository.Notify = mock.Mock(
        name=gi_repository_name + '.Notify')
    gi.repository.GdkPixbuf = mock.Mock(
        name=gi_repository_name + '.GdkPixbuf')

    sys.modules[gi_name] = gi

    # Notify Object
    notify_obj = mock.Mock()
    notify_obj.set_urgency.return_value = True
    notify_obj.set_icon_from_pixbuf.return_value = True
    notify_obj.set_image_from_pixbuf.return_value = True
    notify_obj.show.return_value = True
    mock_notify.new.return_value = notify_obj

    mock_pixbuf.new_from_file.return_value = True

    # The following allows our mocked content to kick in.
    reload(apprise)

    # Create our instance
    obj = apprise.Apprise.instantiate('gnome://', suppress_exceptions=False)
    obj.duration = 0

    # Check that it found our mocked environments
    assert(obj._enabled is True)

    # test notifications
    assert(obj.notify(title='title', body='body',
           notify_type=apprise.NotifyType.INFO) is True)

    # Test our loading of our icon exception; it will still allow the
    # notification to be sent
    mock_pixbuf.new_from_file.side_effect = AttributeError
    assert(obj.notify(title='title', body='body',
           notify_type=apprise.NotifyType.INFO) is True)
    # Undo our change
    mock_pixbuf.new_from_file.side_effect = None

    # Test our exception handling during initialization
    mock_notify.new.side_effect = AttributeError
    mock_notify.new.return_value = None
    assert(obj.notify(title='title', body='body',
           notify_type=apprise.NotifyType.INFO) is False)
    # Undo our change
    mock_notify.new.side_effect = None

    # Toggle our testing for when we can't send notifications because the
    # package has been made unavailable to us
    obj._enabled = False
    assert(obj.notify(title='title', body='body',
           notify_type=apprise.NotifyType.INFO) is False)

    # Test the setting of a the urgency
    apprise.plugins.NotifyGnome(urgency=0)
