from socket import *
import os
import sys
import struct
import time
import select

ICMP_ECHO_REQUEST = 8

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # timed out, no reply
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # IP header is 20 bytes, so ICMP header starts at byte 20
        icmpHeader = recPacket[20:28]

        # unpack the ICMP header fields
        icmpType, code, checksum_val, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

        # make sure the reply matches our request using the process ID
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            # get the time we sent the packet from the data payload
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]

            # TTL is stored at byte 8 of the IP header
            ttl = struct.unpack("B", recPacket[8:9])[0]

            # calculate round trip time in milliseconds
            rtt = (timeReceived - timeSent) * 1000
            return f"Reply from {destAddr}: bytes={len(recPacket)-28} time={rtt:.2f}ms TTL={ttl}"

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # header format: type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # make a dummy header first with checksum set to 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # now calculate the real checksum using the dummy header + data
    myChecksum = checksum(header + data)
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    # rebuild header with the correct checksum
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    # SOCK_RAW lets us send/receive raw ICMP packets
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF  # use process ID to identify our packets
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay

def ping(host, timeout=1):
    # timeout=1 means if no reply in 1 second, assume packet was lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    while 1:
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1)  # wait one second between pings
    return delay

ping("google.com")