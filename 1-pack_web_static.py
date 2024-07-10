#!/usr/bin/env python3
"""
Fabric script to generate a .tgz archive from web_static folder.
"""
from fabric.api import local
from datetime import datetime
import os

def do_pack():
    """
    Creates a .tgz archive from web_static folder.
    Returns:
        Archive path if successful, None if not.
    """
    # Create directory if it doesn't exist
    if not os.path.exists("versions"):
        os.makedirs("versions")

    # Current timestamp
    now = datetime.now()
    archive_name = "web_static_{}{}{}{}{}{}.tgz".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second)

    # Execute the compression command
    result = local("tar -cvzf versions/{} web_static".format(archive_name))

    if result.failed:
        return None
    else:
        return "versions/{}".format(archive_name)

