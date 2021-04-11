import sys
import os

import nmap                         # import nmap.py module


try:
    #nm = nmap.PortScanner()         # instantiate nmap.PortScanner object
    nm = nmap.PortScannerAsync()
except nmap.PortScannerError:
    print('Nmap not found', sys.exc_info()[0])
    sys.exit(1)
except:
    print("Unexpected error:", sys.exc_info()[0])
    sys.exit(1)

def check_result(host, scan_result):
    print('------------------')
    print(host, scan_result)

#nm.scan('192.168.99.0/24', '22-443')
nm.scan('192.168.99.0/24', '22-443', arguments='-sP', callback=check_result)
# nm.command_line()
# nm.scaninfo()

while nm.still_scanning():
    print("Waiting >>>")
    nm.wait(2)

# for host in nm.all_hosts():
#     print('----------------------------------------------------')
#     print('Host : %s (%s)' % (host, nm[host].hostname()))
#     print('State : %s' % nm[host].state())
#     if nm[host].state() != 'up':
#         continue

#     for proto in nm[host].all_protocols():
#         print('----------')
#         print('Protocol : %s' % proto)

#         lport = list(nm[host][proto].keys())
#         lport.sort()
#         for port in lport:
#             print ('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))
