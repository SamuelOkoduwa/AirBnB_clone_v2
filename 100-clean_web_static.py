#!/usr/bin/env python3
"""
Fabric script to generate a .tgz archive from web_static folder,
deploy it to web servers, create a new deployment, and clean old deployments.
"""
from fabric.api import env, local, put, run, cd, lcd
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
    if not os.path.exists("versions"):
        os.makedirs("versions")

    now = datetime.now()
    archive_name = "web_static_{}{}{}{}{}{}.tgz".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second)

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
        put(archive_path, "/tmp/")
        archive_file = os.path.basename(archive_path)
        archive_folder = "/data/web_static/releases/{}".format(archive_file.split('.')[0])

        run("mkdir -p {}".format(archive_folder))
        run("tar -xzf /tmp/{} -C {}".format(archive_file, archive_folder))
        run("rm /tmp/{}".format(archive_file))
        run("mv {}/web_static/* {}/".format(archive_folder, archive_folder))
        run("rm -rf {}/web_static".format(archive_folder))

        run("rm -rf /data/web_static/current")
        run("ln -s {} /data/web_static/current".format(archive_folder))

        return True
    except:
        return False

def deploy():
    """
    Creates and distributes an archive to web servers.
    Returns:
        True if all operations succeed, False otherwise.
    """
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)

def do_clean(number=0):
    """
    Deletes out-of-date archives.
    Args:
        number (int): The number of archives to keep.
    """
    number = int(number)
    if number <= 0:
        number = 1

    archives = sorted(os.listdir("versions"))
    archives_to_delete = archives[:-number]

    with lcd("versions"):
        for archive in archives_to_delete:
            local("rm ./{}".format(archive))

    with cd("/data/web_static/releases"):
        archives = run("ls -1t").split()
        archives = [a for a in archives if "web_static_" in a]
        archives_to_delete = archives[number:]

        for archive in archives_to_delete:
            run("rm -rf ./{}".format(archive))

