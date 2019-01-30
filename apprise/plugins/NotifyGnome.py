# -*- coding: utf-8 -*-
#
# Gnome Notify Wrapper
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
from __future__ import absolute_import
from __future__ import print_function

import re

from .NotifyBase import NotifyBase
from ..common import NotifyImageSize

# Default our global support flag
NOTIFY_GNOME_SUPPORT_ENABLED = False

try:
    # 3rd party modules (Gnome Only)
    import gi

    # require_version() call is required otherwise we generate a warning
    gi.require_version("Notify", "0.7")

    # We can import the actual libraries we care about now:
    from gi.repository import Notify
    from gi.repository import GdkPixbuf

    # We're good to go!
    NOTIFY_GNOME_SUPPORT_ENABLED = True

except ImportError:
    # No problem; we just simply can't support this plugin; we could
    # be in microsoft windows, or we just don't have the python-gobject
    # library available to us (or maybe one we don't support)?
    pass


# Urgencies
class GnomeUrgency(object):
    LOW = 0
    NORMAL = 1
    HIGH = 2


GNOME_URGENCIES = (
    GnomeUrgency.LOW,
    GnomeUrgency.NORMAL,
    GnomeUrgency.HIGH,
)


class NotifyGnome(NotifyBase):
    """
    A wrapper for local Gnome Notifications
    """

    # The default descriptive name associated with the Notification
    service_name = 'Gnome Notification'

    # The default protocol
    protocol = 'gnome'

    # A URL that takes you to the setup/help of the specific protocol
    setup_url = 'https://github.com/caronc/apprise/wiki/Notify_gnome'

    # Allows the user to specify the NotifyImageSize object
    image_size = NotifyImageSize.XY_128

    # This entry is a bit hacky, but it allows us to unit-test this library
    # in an environment that simply doesn't have the gnome packages
    # available to us.  It also allows us to handle situations where the
    # packages actually are present but we need to test that they aren't.
    # If anyone is seeing this had knows a better way of testing this
    # outside of what is defined in test/test_gnome_plugin.py, please
    # let me know! :)
    _enabled = NOTIFY_GNOME_SUPPORT_ENABLED

    def __init__(self, urgency=None, **kwargs):
        """
        Initialize Gnome Object
        """

        super(NotifyGnome, self).__init__(**kwargs)

        # The urgency of the message
        if urgency not in GNOME_URGENCIES:
            self.urgency = GnomeUrgency.NORMAL

        else:
            self.urgency = urgency

    def notify(self, title, body, notify_type, **kwargs):
        """
        Perform Gnome Notification
        """

        if not self._enabled:
            self.logger.warning(
                "Gnome Notifications are not supported by this system.")
            return False

        # Limit results to just the first 10 line otherwise
        # there is just to much content to display
        body = re.split('[\r\n]+', body)
        body[0] = body[0].strip('#').strip()
        body = '\r\n'.join(body[0:10])

        try:
            # App initialization
            Notify.init(self.app_id)

            # image path
            icon_path = self.image_path(notify_type, extension='.ico')

            # Build message body
            notification = Notify.Notification.new(body)

            # Assign urgency
            notification.set_urgency(self.urgency)

            try:
                # Use Pixbuf to create the proper image type
                image = GdkPixbuf.Pixbuf.new_from_file(icon_path)

                # Associate our image to our notification
                notification.set_icon_from_pixbuf(image)
                notification.set_image_from_pixbuf(image)

            except Exception as e:
                self.logger.warning(
                    "Could not load Gnome notification icon ({}): {}"
                    .format(icon_path, e))

            notification.show()
            self.logger.info('Sent Gnome notification.')

        except Exception as e:
            self.logger.warning('Failed to send Gnome notification.')
            self.logger.exception('Gnome Exception')
            return False

        return True

    @staticmethod
    def parse_url(url):
        """
        There are no parameters nessisary for this protocol; simply having
        gnome:// is all you need.  This function just makes sure that
        is in place.

        """

        # return a very basic set of requirements
        return {
            'schema': NotifyGnome.protocol,
            'user': None,
            'password': None,
            'port': None,
            'host': 'localhost',
            'fullpath': None,
            'path': None,
            'url': url,
            'qsd': {},
            # Set the urgency to None so that we fall back to the default
            # value.
            'urgency': None,
        }
