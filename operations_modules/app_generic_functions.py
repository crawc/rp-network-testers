"""
    'KootNet Ethernet Testers' is a collection of scripts and programs
    to test Ethernet cables and or network routes.
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import re
import subprocess
import time
import requests
import socket
from threading import Thread
from ipaddress import ip_address as _check_ip_address


class CreateMonitoredThread:
    def __init__(self, function, args=None, thread_name="Generic Thread", max_restart_tries=5):
        self.is_running = True
        self.function = function
        self.args = args
        self.thread_name = thread_name

        self.current_restart_count = 0
        self.max_restart_count = max_restart_tries

        self._thread_and_monitor()

    def _thread_and_monitor(self):
        try:
            monitored_thread = Thread(target=self._worker_thread_and_monitor)
            monitored_thread.daemon = True
            monitored_thread.start()
        except Exception as error:
            print(str(error))

    def _worker_thread_and_monitor(self):
        if self.args is not None:
            monitored_thread = Thread(target=self.function, args=self.args)
        else:
            monitored_thread = Thread(target=self.function)
        monitored_thread.daemon = True
        monitored_thread.start()

        while True:
            time.sleep(30)
            if not monitored_thread.is_alive():
                self.is_running = False
                self.current_restart_count += 1
                if self.current_restart_count < self.max_restart_count:
                    if self.args is not None:
                        monitored_thread = Thread(target=self.function, args=self.args)
                    else:
                        monitored_thread = Thread(target=self.function)
                    monitored_thread.daemon = True
                    monitored_thread.start()
                    self.is_running = True
                else:
                    log_msg = self.thread_name + " has attempted to restart " + str(self.current_restart_count)
                    print(log_msg + " Times.  No further restart attempts will be made.")
                    while True:
                        time.sleep(600)


def thread_function(function, args=None):
    if args:
        system_thread = Thread(target=function, args=[args])
    else:
        system_thread = Thread(target=function)
    system_thread.daemon = True
    system_thread.start()


def get_subprocess_str_output(command):
    return str(subprocess.check_output(command, shell=True)).replace("\\n", "\n")


def get_os_name_version():
    """ Returns sensors Operating System Name and Version. """
    try:
        os_release_content_lines = get_file_content("/etc/os-release").split("\n")
        os_release_name = ""
        for line in os_release_content_lines:
            name_and_value = line.split("=")
            if name_and_value[0].strip() == "PRETTY_NAME":
                os_release_name = name_and_value[1].strip()[1:-1]
        return os_release_name
    except Exception as error:
        print("Linux System - Unable to get Raspbian OS Version: " + str(error))
        return "Error retrieving OS information"


def get_file_content(load_file, open_type="r"):
    """ Loads provided file and returns it's content. """
    if os.path.isfile(load_file):
        try:
            loaded_file = open(load_file, open_type)
            file_content = loaded_file.read()
            loaded_file.close()
        except Exception as error:
            print(str(error))
            file_content = ""
        return file_content


def write_file_to_disk(file_location, file_content, open_type="w"):
    """ Writes provided file and content to local disk. """
    try:
        write_file = open(file_location, open_type)
        write_file.write(file_content)
        write_file.close()
    except Exception as error:
        print("Write to Disk Error: " + str(error))


def send_command(url):
    """ Sends command URL using requests. """
    try:
        requests.get(url=url, timeout=5, headers={'Connection': 'close'}, verify=False)
        print("Command '" + url + "' OK")
        return True
    except Exception as error:
        print(str(error))
        return False


def get_raspberry_pi_model():
    if os.path.isfile("/proc/device-tree/model"):
        pi_version = str(subprocess.check_output("cat /proc/device-tree/model", shell=True))
        if len(pi_version) > 10:
            pi_version = pi_version[2:-5]
            if pi_version[:17] == "Raspberry Pi Zero":
                return "Raspberry Pi Zero"
            elif pi_version[:27] == "Raspberry Pi 3 Model B Plus":
                return "Raspberry Pi 3 Model B Plus"
            elif pi_version[:22] == "Raspberry Pi 4 Model B":
                return "Raspberry Pi 4 Model B"
    return get_os_name_version()


def hostname_is_valid(text_hostname):
    """
    Returns True if provided text only uses Alphanumeric characters plus underscores and dashes.
    Otherwise returns False.
    """
    if text_hostname is None:
        return False
    if re.match(r'^[a-zA-Z0-9_-]*$', text_hostname):
        return True
    return False


def text_is_alphanumeric(text_string):
    """
    Returns True if provided text only uses Alphanumeric characters.
    Otherwise returns False.
    """
    if text_string.isalnum():
        return True
    else:
        return False


def ip_address_is_valid(ip_address):
    return _check_ip_address(ip_address)


def subnet_mask_is_valid(subnet_mask):
    if re.match(r'/[0-9][0-9]|/[0-9]', subnet_mask):
        return True
    return False


def wireless_ssid_is_valid(text_ssid):
    """
    Returns True if provided text only uses Alphanumeric characters, spaces, underscores and dashes.
    Otherwise returns False.
    """
    if re.match(r'^[a-zA-Z0-9][ A-Za-z0-9_-]*$', text_ssid):
        return True
    else:
        return False


def check_for_none_and_blank(check_variable):
    if check_variable is None or check_variable == "":
        return True
    return False


def get_network_ip():
    """ Returns IPv4 Address as a String. """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = (s.getsockname()[0])
        s.close()
    except Exception as error:
        print("Get IP Failed: " + str(error))
        ip_address = "0.0.0.0"
    return ip_address