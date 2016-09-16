#-------------------------------------------------------------------------------
# Py Name:      pyping3.py
# Author:       BikerDroid
# Created:      23-05-2016
# Revision:     03-06-2016
#-------------------------------------------------------------------------------
class PyPing3():
    """
    Python3 ICMP Ping
    -----------------
    
    Pings host or ip address. Returns Dict containing: 'host', 'ip', 'size', 
    'ttl', 'sent', 'recieved', 'lost', 'min_ms', 'max_ms', 'average_ms'

    Usage
    -----

    >>> p = PyPing3( ping_count=4, timeout=4, verbose=True, cached_stdout=False )
    
    The listed inputs to the class are the default values. Note timeout is in seconds not miliseconds.
    
    >>> res = p.ping('google.com')

    Pinging google.com [172.217.18.14] with 25 bytes of data:\n
    1: Reply from google.com, bytes=25 ttl=57 time=94ms\n
    2: Reply from google.com, bytes=25 ttl=57 time=92ms\n
    3: Reply from google.com, bytes=25 ttl=57 time=94ms\n
    Packets: Sent=3, Received=3, Lost=0 (0.0% loss)\n
    Timing: Min=92ms, Max=94ms, Average=93ms\n
    
    >>> print( res )
    
    {'min_ms': 94, 'ip': '172.217.18.14', 'host': 'google.com', 'size': 25, 'recieved': 3, 'average_ms': 93, 'sent': 3, 'lost': 0, 'ttl': 57, 'max_ms': 94}

    >>> print( res['ip'] )
    
    172.217.18.14
    
    >>> p.showdata( res )

    Pinging google.com [172.217.18.14] with 25 bytes of data:\n
    1: Reply from google.com, bytes=25 ttl=57 time=*93ms\n
    2: Reply from google.com, bytes=25 ttl=57 time=*93ms\n
    3: Reply from google.com, bytes=25 ttl=57 time=*93ms\n
    Packets: Sent=3, Received=3, Lost=0 (0.0% loss)\n
    Timing: Min=92ms, Max=94ms, Average=*93ms\n
    """

    from socket import socket, error, getprotobyname, gethostbyname, gethostbyaddr, htons
    from socket import SOCK_DGRAM, inet_pton, AF_INET, AF_INET6, SOCK_RAW, gaierror, inet_aton
    from struct import pack, unpack
    from select import select
    from random import random
    from time import time, sleep
    
    ICMP_MAX_RECV = 2048
    ICMP_ECHO_REQUEST = 8 # Echo request (per RFC792)
    ICMP_ECHOREPLY = 0 # Echo reply (per RFC792)
    ICMP_CODE = getprotobyname('icmp')
    ERROR_DESCR = {1: 'ERROR: ICMP messages can only be sent from processes running as root.',
                   10013: 'ERROR: ICMP messages can only be sent by users or processes with administrator rights.' }    
    
    def __init__(self,ping_count=4,timeout=4,cached_stdout=False):
        if ping_count < 1: ping_count = 1
        if timeout < 1: timeout = 1
        self.count = ping_count
        self.timeout = timeout
        self.datasize = 0
        self.ip_header = None
        self.cached = cached_stdout
        if not self.is_admin():
            print('Insufficient privileges to open socket and send icmp ping.')
            return

    def __checksum(self, source_string):
        checksum = 0
        count_to = (len(source_string) / 2) * 2
        count = 0
        while count < count_to:
            this_val = source_string[count + 1] * 256 + source_string[count]
            checksum += this_val
            checksum &= 0xffffffff # Necessary?
            count += 2
        if count_to < len(source_string):
            checksum += source_string[len(source_string) - 1]
            checksum &= 0xffffffff  # Necessary?
        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum += checksum >> 16
        answer = ~checksum
        answer &= 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def __create_packet(self, id):
        """Create a new echo request packet based on the given "id"."""
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        header = self.pack('bbHHh', self.ICMP_ECHO_REQUEST, 0, 0, id, 1)
        data = 192 * b'Q'
        header = self.pack('bbHHh', self.ICMP_ECHO_REQUEST, 0, self.htons(self.__checksum(header + data)), id, 1)
        return header + data

    def header2dict(self, names, struct_format, data):
        """ unpack the raw received IP and ICMP header informations to a dict """
        unpacked_data = self.unpack(struct_format, data)
        return dict(zip(names, unpacked_data))

    def __response_handler(self, sock, packet_id, time_sent, timeout):
        """Handles packet response, returning either the delay or timing out (returns "None")."""
        while True:
            ready = self.select([sock], [], [], self.timeout)
            if ready[0] == []:  # Timeout
                return
            time_received = self.time()
            rec_packet, addr = sock.recvfrom(self.ICMP_MAX_RECV)
            icmp_header = rec_packet[20:28]

            self.ip_header = self.header2dict(
                names = ["version", "type", "length",
                    "id", "flags", "ttl", "protocol",
                    "checksum", "src_ip", "dest_ip"],
                struct_format = "!BBHHHBBHII",
                data = rec_packet[:20])
            
            type, code, checksum, rec_id, sequence = self.unpack('bbHHh', icmp_header)
            if rec_id == packet_id:
                return time_received - time_sent
            timeout -= time_received - time_sent
            if timeout <= 0:
                return

    def __echo(self, dest_addr, timeout=1):
        """echo"""
        try:
            sock = self.socket(self.AF_INET, self.SOCK_RAW, self.ICMP_CODE)
        except self.error as exc:
            error_number, msg = exc.args
            if error_number in ERROR_DESCR:
                # Operation not permitted
                raise error('%s\n%s' % ((msg, ERROR_DESCR[error_number])))
            raise  # Raises the original error
        try:
            self.gethostbyname(dest_addr)
        except self.gaierror:
            return
        packet_id = int((id(self.timeout) * self.random()) % 65535)
        packet = self.__create_packet(packet_id)
        self.datasize = packetsize = round(len(packet)/8)
        while packet:
            dummy_port = 1 # The icmp protocol does not use a port
            sent = sock.sendto(packet, (dest_addr, dummy_port))
            packet = packet[sent:]
        delay = self.__response_handler(sock, packet_id, self.time(), self.timeout)
        sock.close()
        return delay

    def __is_valid_ipv4(self, address):
        try:
            self.inet_pton(self.socket.AF_INET, address)
        except AttributeError:  # no inet_pton here, sorry
            try:
                self.inet_aton(address)
            except self.error:
                return False
            return address.count('.') == 3
        except self.error:  # not a valid address
            return False
        return True
    
    def __is_valid_ipv6(self, address):
        try:
            self.inet_pton(self.AF_INET6, address)
        except self.error:  # not a valid address
            return False
        return True
    
    def __is_valid_ip(self, ip):
        """Validates IP addresses."""
        return self.__is_valid_ipv4(ip) or self.__is_valid_ipv6(ip)

    def is_admin(self):
        import ctypes, os
        try:
            admin_rights = os.getuid() == 0
        except AttributeError:
            admin_rights = ctypes.windll.shell32.IsUserAnAdmin() != 0
        return admin_rights
    
    def get_primary_ip(self):
        sock = self.socket(self.AF_INET, self.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            sock.connect(('10.255.255.255',0))
            IP = sock.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            sock.close()
        return IP    
    
    def showdata(self,pingdict,verbose=True):
        """showdata(self, pingdict, verbose=True)"""
        s = ''
        if isinstance(pingdict, dict):
            sHost = pingdict['host']
            sIP = pingdict['ip']
            size = pingdict['size']
            ttl = pingdict['ttl']
            sent = pingdict['sent']
            recieved = pingdict['recieved']
            lost = pingdict['lost']
            losspercent = pingdict['losspercent']
            mindelay = pingdict['min_ms']
            maxdelay = pingdict['max_ms']
            averagedelay = pingdict['average_ms'] 
            s = 'Pinging '+sHost+' ['+sIP+'] with '+str(size)+' bytes of data:\n'
            x = pos = 0
            if sent:
                for x in range(sent-lost):
                    pos = x+1
                    s += str(pos).zfill(len(str(sent)))+": Reply from {}, bytes={} ttl={} time=*{}ms".format(sHost,size,ttl,averagedelay)+'\n'
                x = pos
            for y in range(pos,sent):
                x += 1
                s += str(x).zfill(len(str(sent)))+": Request timed out.\n"
            s += 'Packets: Sent = '+str(sent)+', Received = '+str(recieved)+', Lost = '+str(lost)+' ('+format(losspercent,'.1f')+'% loss)\n'
            s += 'Timing: Min = '+str(mindelay)+'ms, Max = '+str(maxdelay)+'ms, Average = *'+str(averagedelay)+'ms\n'
        if verbose:
            print(s)
        return s
    
    def ping(self, host_or_ip_to_ping,verbose=False):
        """ping(self, host_or_ip_to_ping, verbose=False)"""
        if not self.is_admin():
            print('Ping not possible: Insufficient privileges.')
            return
        replycnt = 0
        delaysum = 0
        recieved = 0
        mindelay = self.timeout * 1000
        maxdelay = 0
        averagedelay = 0
        sIP = ''
        sHost = ''
        ttl = 0
        s2c = ''
        if self.__is_valid_ip(host_or_ip_to_ping):
            sIP = host_or_ip_to_ping
            try:
                sHost = self.gethostbyaddr(sIP)[0]
            except:
                sHost = sIP
        else:
            sHost = host_or_ip_to_ping
            try:
                sIP = self.gethostbyname(host_or_ip_to_ping)
            except:
                sIP = '0.0.0.0'
        if sIP is '0.0.0.0':
            mindelay = 0
            if verbose:
                s1 = 'Unable to resolve '+host_or_ip_to_ping+' [0.0.0.0]:'
                if not self.cached:
                    print(s1)
        else:
            for i in range(self.count):
                corrected_delay = False
                corrected_str = ''
                replycnt += 1
                delay = self.__echo(host_or_ip_to_ping, self.timeout)
                ttl = self.ip_header['ttl']
                if replycnt is 1:
                    if verbose:
                        s1 = 'Pinging '+sHost+' ['+sIP+'] with '+str(self.datasize)+' bytes of data:'
                        if not self.cached:
                            print(s1)
                if delay is None:
                    s2t = str(replycnt).zfill(len(str(self.count)))+": Request timed out."
                    if verbose:
                        if not self.cached:
                            print(s2t)
                        else:
                            s2c += s2t+'\n'
                else:
                    delay = round(delay * 1000)
                    if delay is 0:
                        delay += 1
                        corrected_delay = True
                        corrected_str = '<'
                    delaysum += delay
                    recieved += 1
                    if delay < mindelay:
                        mindelay = delay
                    if delay > maxdelay:
                        maxdelay = delay
                    if verbose:
                        s2 = str(replycnt).zfill(len(str(self.count)))+": Reply from {}, bytes={} ttl={} time={}{}ms".format(host_or_ip_to_ping, self.datasize, ttl, corrected_str, delay)
                        if not self.cached:
                            print(s2)
                        else:
                            s2c += s2+'\n'
                self.sleep(0.1)
        averagedelay = round(delaysum/self.count)
        lost = self.count-recieved
        losspercent = (lost*100)/self.count
        if round(losspercent) is 100:
            mindelay = self.timeout * 1000
            maxdelay = self.timeout * 1000
            averagedelay = self.timeout * 1000
        if verbose:
            s3 = 'Packets: Sent = '+str(self.count)+', Received = '+str(recieved)+', Lost = '+str(lost)+' ('+format(losspercent,'.1f')+'% loss)'
            s4 = 'Timing: Min = '+str(mindelay)+'ms, Max = '+str(maxdelay)+'ms, Average = '+str(averagedelay)+'ms'            
            if not self.cached:
                print(s3)
                print(s4+'\n')
            else:
                print(s1+'\n'+s2c+s3+'\n'+s4+'\n')
        keys = ['host','ip','size','ttl','sent','recieved','lost','min_ms','max_ms','average_ms','losspercent']
        values = [sHost,sIP,self.datasize,ttl,self.count,recieved,lost,mindelay,maxdelay,averagedelay,losspercent]
        return dict(zip(keys,values))

if __name__ == '__main__':
    p = PyPing3()
    local_ip = p.get_primary_ip()
    ping_addr = ['127.0.0.1',local_ip]
    for addr in ping_addr:
        p.ping(addr,verbose=True)
