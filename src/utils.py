import re
import os
import subprocess
import ipaddress
import asyncio


def get_network() -> str:
    """
    get_network

        Returns:
            str: network in cidr notation
    """
    is_mac = False
    try:
        output = subprocess.check_output(['uname', '-a'])
        if 'Darwin Kernel Version' in output.decode('utf-8'):
            is_mac = True
    except subprocess.CalledProcessError as err:
        raise err

    try:
        cmd = ['ifconfig', 'eth0']
        if is_mac:
            cmd = ['ifconfig', 'en0']
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as err:
        raise err

    regex = r'inet\s(\d+.\d+.\d+.\d+)\s\snetmask\s(\d+.\d+.\d+.\d+)\s'
    if is_mac:
        regex = r'inet\s(\d+.\d+.\d+.\d+)\snetmask\s(0x[0-8a-f]+)\s'
    match = re.search(regex, output.decode('utf-8'))
    ip_address = '127.0.0.1'
    if match:
        ip = match.group(1)
        mask = match.group(2)
        if is_mac:
            mask_addr = str(ipaddress.IPv4Address(int(mask, 0)))
            mask = mask_addr
        bits = ipaddress.IPv4Network(f'0.0.0.0/{mask}').prefixlen
        ip_int = int(ipaddress.IPv4Address(ip))
        mask_int = int(ipaddress.IPv4Address(mask))
        net_int = ip_int & mask_int
        net_addr = str(ipaddress.IPv4Address(net_int))
        ip_address = f'{net_addr}/{bits}'
    return ip_address


def get_ip() -> str:
    """
    get_ip

        Returns:
            str: ip address
    """
    is_mac = False
    ip = ''
    try:
        output = subprocess.check_output(['uname', '-a'])
        if 'Darwin Kernel Version' in output.decode('utf-8'):
            is_mac = True
    except subprocess.CalledProcessError as err:
        raise err

    try:
        cmd = ['ifconfig', 'eth0']
        if is_mac:
            cmd = ['ifconfig', 'en0']
        output = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as err:
        raise err

    regex = r'inet\s(\d+.\d+.\d+.\d+)\s'
    match = re.search(regex, output.decode('utf-8'))
    if match:
        ip = match.group(1)

    return ip


def get_cluster_nodes(exclude_ip: str = None) -> list:
    """
    get_cluster_nodes

        Parameters:
            exclude_ip (String): exclude ip address

        Returns:
            list: ip addresses
    """
    raft_service = os.getenv("RAFT_SERVICE_NAME", None)

    if raft_service is None:
        return []

    cmd = ['nslookup', raft_service]

    output = subprocess.check_output(cmd)

    dns_response = output.decode()
    ip_addresses = []
    for lines in dns_response.split('\n'):
        if 'Address' in lines:
            ip_addresses.append(lines.replace('Address: ', ''))

    ip_addresses.pop(0)
    if exclude_ip is not None:
        try:
            ip_addresses.remove(exclude_ip)
        except ValueError:
            pass

    return ip_addresses
