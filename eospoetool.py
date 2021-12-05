#!/usr/bin/env python3

from jsonrpclib import Server
import ssl
import argparse
import os
import time


def poecontrol(hostname, user, passwd, port, p_action, action):
    """Connect to switch and manipulate the poe on a port

    Args:
        hostname (string): hostname of switch
        user (string): user name
        passwd (string): password
        port (uint): port number 
        p_action (string): on|off|toggle
    """
    host = hostname.strip()
    _create_unverified_https_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_https_context
    response = os.system(f"ping -c 2 {host} > /dev/null 2>&1")
    if response == 0:
        pingstatus = "Network Active"
        try:
            device = Server(
                f'https://{user}:{passwd}@{host}/command-api')
            ispoePort = device.runCmds(
                version=1, cmds=['enable', f'show poe interface Ethernet {port}'], format='json')
            try:
                if ispoePort:
                    print(f'\t\t\tEthernet {port}, on {host} is PoE capable')
                    if p_action != "toggle":
                        result = device.runCmds(
                            version=1, cmds=['enable', 'configure terminal', f'interface Ethernet {port}', f'{p_action}'], format='text')
                        print(
                            f'\t\t\tEthernet {port}, on {host} action {action.upper()} has been executed')
                    else:
                        result = device.runCmds(
                            version=1, cmds=['enable', 'configure terminal', f'interface Ethernet {port}', 'poe disabled'], format='text')
                        time.sleep(3)
                        result1 = device.runCmds(
                            version=1, cmds=['enable', 'configure terminal', f'interface Ethernet {port}', 'no poe disabled'], format='text')
                        print(
                            f'\t\t\tEthernet {port}, on {host} action {action.upper()} has been executed')
            except:
                print(f'{host} / Ethernet {port} does not support PoE, exiting!')
                exit()
        except Exception as e:
            print(
                f"something went wrong on {host}, check password\n\n{str(e)}\n")
    else:
        pingstatus = "Network Error"
        print(f"{pingstatus}: {host} does not respond to ping, moving on..\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--host", type=str, default="",
        help="specify the switch name", required=True)
    parser.add_argument(
        "-u", "--user", type=str, default="",
        help="specify a username", required=True)
    parser.add_argument(
        "-p", "--passwd", type=str, default="",
        help="for passing password interactively", required=True)
    parser.add_argument(
        "-e", "--port", type=int, default="",
        help="specify an Ethernet port number", required=True)
    parser.add_argument(
        "-a", "--action", type=str, default="",
        help="specify an action of: on|off|toggle", required=True)
    args = parser.parse_args()

    host = args.host
    user = args.user
    passwd = args.passwd
    port = args.port
    action = args.action

    if action == "off":
        p_action = "poe disabled"
    elif action == "on":
        p_action = "no poe disabled"
    elif action == "toggle":
        p_action = "toggle"
    else:
        print("\nunknown action requested. Exiting!")
        exit()

    print(
        f"\nPoE Action: Power {action.upper()} requested on:\n\n\t{host}\t\tEthernet {port}")
    poecontrol(host, user, passwd, port, p_action, action)


if __name__ == '__main__':
    main()
