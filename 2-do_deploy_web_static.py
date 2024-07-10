#!/usr/bin/env python3
"""
Fabric script to generate a .tgz archive from web_static folder
and deploy it to web servers.
"""
from fabric.api import env, local, put, run
from datetime import datetime
import os

env.hosts = ['<IP web-01>', '<IP web-02>']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'

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

def do_deploy(archive_path):
    """
    Distributes an archive to web servers.
    Args:
        archive_path (str): The path to the archive to distribute.
    Returns:
        True if all operations succeed, False otherwise.
    """
    if not os.path.exists(archive_path):
        return False

    try:
        # Upload the archive to /tmp/ directory of the web server
        put(archive_path, "/tmp/")
        
        # Extract the archive filename and folder name
        archive_file = os.path.basename(archive_path)
        archive_folder = "/data/web_static/releases/{}".format(archive_file.split('.')[0])

        # Uncompress the archive to the folder
        run("mkdir -p {}".format(archive_folder))
        run("tar -xzf /tmp/{} -C {}".format(archive_file, archive_folder))
        run("rm /tmp/{}".format(archive_file))
        run("mv {}/web_static/* {}/".format(archive_folder, archive_folder))
        run("rm -rf {}/web_static".format(archive_folder))

        # Delete the existing symbolic link
        run("rm -rf /data/web_static/current")

        # Create a new symbolic link
        run("ln -s {} /data/web_static/current".format(archive_folder))

        return True
    except:
        return False

