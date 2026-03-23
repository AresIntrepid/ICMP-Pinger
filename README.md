# ICMP Pinger

A simple Ping application built in Python using raw sockets and ICMP echo request/reply messages.

## Overview

This program replicates the core functionality of the standard `ping` command. It sends ICMP echo request packets to a target host once per second and listens for echo replies, reporting the round-trip time (RTT) and TTL for each response.

## Requirements

- Python 3.x
- **Root/Administrator privileges** (required for raw socket access)

## Usage

1. Clone the repository and navigate to the project directory.
2. Open `ICMPPinger.py` and set your target host at the bottom of the file:
   ```python
   ping("google.com")
   ```
3. Run the script with elevated privileges:

**Linux/Mac:**
```bash
sudo python3 ICMPPinger.py
```

**Windows (run terminal as Administrator):**
```bash
python ICMPPinger.py
```

## Example Output

```
Pinging 142.250.80.46 using Python:

Reply from 142.250.80.46: bytes=8 time=12.34ms TTL=117
Reply from 142.250.80.46: bytes=8 time=11.98ms TTL=117
Reply from 142.250.80.46: bytes=8 time=13.02ms TTL=117
Request timed out.
```

## How It Works

1. A raw ICMP socket is created using `SOCK_RAW`
2. An ICMP echo request packet is constructed with a timestamp payload and sent to the target host
3. The program waits up to 1 second for an echo reply
4. On receiving a reply, it extracts the ICMP header (starting at byte 20 of the IP packet), verifies the packet ID, calculates the RTT from the timestamp, and reads the TTL from the IP header
5. If no reply is received within 1 second, a timeout message is printed

## Notes

- Raw sockets require root/administrator privileges on most operating systems
- The program pings indefinitely until interrupted (`Ctrl+C`)
- The implementation follows ICMP as described in RFC 792, with minor simplifications per course requirements
