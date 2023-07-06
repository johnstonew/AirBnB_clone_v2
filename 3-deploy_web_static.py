#!/usr/bin/python3
#  Fabric script that creates and distributes an archive to your web servers
import os.path
from datetime import datetime
from fabric.api import env
from fabric.api import local
from fabric.api import put
from fabric.api import run

env.hosts = ["18.207.235.123", "54.89.80.137"]


def do_pack():
    """Create tar gzip archive of the web_static"""
    dete = datetime.utcnow()
    file = "versions/web_static_{}{}{}{}{}{}.tgz".format(dete.year,
                                                         dete.month,
                                                         dete.day,
                                                         dete.hour,
                                                         dete.minute,
                                                         dete.second)
    if os.path.isdir("versions") is False:
        if local("mkdir -p versions").failed is True:
            return None
    if local("tar -cvzf {} web_static".format(file)).failed is True:
        return None
    return file


def do_deploy(archive_path):
    """Distributes archive to a web server.
    Args:
        archive_path (str): path of the archive to distribute.
    Returns:
        If the file doesn't exist at archive_path or an error occurs - False
    """
    if os.path.isfile(archive_path) is False:
        return False
    file = archive_path.split("/")[-1]
    name = file.split(".")[0]

    if put(archive_path, "/tmp/{}".format(file)).failed is True:
        return False
    if run("rm -rf /data/web_static/releases/{}/".
           format(name)).failed is True:
        return False
    if run("mkdir -p /data/web_static/releases/{}/".
           format(name)).failed is True:
        return False
    if run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".
           format(file, name)).failed is True:
        return False
    if run("rm /tmp/{}".format(file)).failed is True:
        return False
    if run("mv /data/web_static/releases/{}/web_static/* "
           "/data/web_static/releases/{}/".format(name, name)).failed is True:
        return False
    if run("rm -rf /data/web_static/releases/{}/web_static".
           format(name)).failed is True:
        return False
    if run("rm -rf /data/web_static/current").failed is True:
        return False
    if run("ln -s /data/web_static/releases/{}/ /data/web_static/current".
           format(name)).failed is True:
        return False
    return True


def deploy():
    """Create and distribute archive to a web server."""
    file = do_pack()
    if file is None:
        return False
    return do_deploy(file)
