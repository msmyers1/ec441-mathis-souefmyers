#!/usr/bin/env python3
"""
EC 441 – TCP Trace Analysis Artifact
=======================================
Mathis Souef-Myers | Spring 2026 | Professor Carruthers

This script generates a realistic tshark style TCP trace and walks through some
analysis questions with worked solutions!

Run:  python3 tcp_trace_analysis.py
"""

import textwrap

# ─────────────────────────────────────────────────────────────
# Simulated tshark capture: TCP three-way handshake + data transfer
# between a client (10.0.0.1:54321) and server (172.16.1.100:80)
# ─────────────────────────────────────────────────────────────

TRACE = [
    # No.  Time      Source          Dest            Proto  Len  Info
    ( 1,  0.000000, "10.0.0.1",     "172.16.1.100", "TCP", 74,  "54321 → 80 [SYN] Seq=100 Win=65535 Len=0 MSS=1460"),
    ( 2,  0.025013, "172.16.1.100", "10.0.0.1",     "TCP", 74,  "80 → 54321 [SYN, ACK] Seq=300 Ack=101 Win=65535 Len=0 MSS=1460"),
    ( 3,  0.025500, "10.0.0.1",     "172.16.1.100", "TCP", 66,  "54321 → 80 [ACK] Seq=101 Ack=301 Win=65535 Len=0"),
    ( 4,  0.026000, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=101 Ack=301 Win=65535 Len=1448"),
    ( 5,  0.026100, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=1549 Ack=301 Win=65535 Len=1448"),
    ( 6,  0.051200, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [ACK] Seq=301 Ack=2997 Win=65535 Len=0"),
    ( 7,  0.052000, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=2997 Ack=301 Win=65535 Len=1448"),
    ( 8,  0.052100, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=4445 Ack=301 Win=65535 Len=1448"),
    ( 9,  0.052200, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=5893 Ack=301 Win=65535 Len=1448"),
    (10,  0.052300, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=7341 Ack=301 Win=65535 Len=1448"),
    (11,  0.078000, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [ACK] Seq=301 Ack=5893 Win=65535 Len=0"),
    (12,  0.105000, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [ACK] Seq=301 Ack=8789 Win=65535 Len=0"),
    (13,  0.130000, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=8789 Ack=301 Win=65535 Len=1448"),
    (14,  0.155000, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [ACK] Seq=301 Ack=10237 Win=65535 Len=0"),
    # ── Simulated packet loss: pkt 15 is lost, so pkt 16 triggers dup ACKs ──
    (15,  0.156000, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=10237 Ack=301 Win=65535 Len=1448 [LOST]"),
    (16,  0.156100, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=11685 Ack=301 Win=65535 Len=1448"),
    (17,  0.180000, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [ACK] Seq=301 Ack=10237 Win=65535 Len=0 [DUP ACK #1]"),
    (18,  0.156200, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=13133 Ack=301 Win=65535 Len=1448"),
    (19,  0.181000, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [ACK] Seq=301 Ack=10237 Win=65535 Len=0 [DUP ACK #2]"),
    (20,  0.182000, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [ACK] Seq=301 Ack=10237 Win=65535 Len=0 [DUP ACK #3]"),
    (21,  0.182500, "10.0.0.1",     "172.16.1.100", "TCP", 1514,"54321 → 80 [ACK] Seq=10237 Ack=301 Win=65535 Len=1448 [RETRANSMIT]"),
    # ── Connection teardown (FIN) ──
    (22,  0.210000, "10.0.0.1",     "172.16.1.100", "TCP", 66,  "54321 → 80 [FIN, ACK] Seq=14581 Ack=301 Win=65535 Len=0"),
    (23,  0.235000, "172.16.1.100", "10.0.0.1",     "TCP", 66,  "80 → 54321 [FIN, ACK] Seq=301 Ack=14582 Win=65535 Len=0"),
    (24,  0.235200, "10.0.0.1",     "172.16.1.100", "TCP", 66,  "54321 → 80 [ACK] Seq=14582 Ack=302 Win=65535 Len=0"),
]


def print_trace():
    """Print the trace in tshark-style format."""
    print("=" * 110)
    print(f"{'No.':<5} {'Time':<12} {'Source':<18} {'Destination':<18} {'Proto':<6} {'Len':<6} Info")
    print("=" * 110)
    for pkt in TRACE:
        no, time, src, dst, proto, length, info = pkt
        marker = ""
        if "[LOST]" in info:
            marker = " ◄◄ LOST"
            info = info.replace(" [LOST]", "")
        elif "[RETRANSMIT]" in info:
            marker = " ◄◄ RETRANSMIT"
            info = info.replace(" [RETRANSMIT]", "")
        elif "[DUP ACK" in info:
            marker = " ◄◄ DUP"
        print(f"{no:<5} {time:<12.6f} {src:<18} {dst:<18} {proto:<6} {length:<6} {info}{marker}")
    print("=" * 110)


def print_questions():
    """Print the analysis questions."""
    questions = [
        (
            "Three-Way Handshake",
            "Identify the three packets that form the TCP three-way handshake.\n"
            "   For each, state: (a) which flags are set, (b) the sequence number,\n"
            "   and (c) the acknowledgment number. Why does the ACK number in\n"
            "   packet 2 equal Seq+1 from packet 1?"
        ),
        (
            "Round-Trip Time (RTT)",
            "Estimate the RTT between client and server using the handshake.\n"
            "   Which two packets do you use, and what is the RTT in milliseconds?"
        ),
        (
            "Throughput Calculation",
            "Between packets 4–6, the client sends two data segments and receives\n"
            "   an ACK. Calculate the throughput in Mbps for this window."
        ),
        (
            "Congestion Window Growth",
            "Observe how many segments the client sends before waiting for an ACK.\n"
            "   Packets 4–5: 2 segments. Packets 7–10: 4 segments.\n"
            "   What congestion control phase is this? What is cwnd after each ACK?"
        ),
        (
            "Packet Loss & Fast Retransmit",
            "Packet 15 is lost. Explain:\n"
            "   (a) Why does the server send duplicate ACKs (packets 17, 19, 20)?\n"
            "   (b) What ACK number do the duplicate ACKs carry, and why?\n"
            "   (c) What triggers the retransmission in packet 21?\n"
            "   (d) After fast retransmit, does TCP use slow start or fast recovery?"
        ),
        (
            "Connection Teardown",
            "Identify the connection teardown sequence (packets 22–24).\n"
            "   Is this a standard 4-way FIN or a 3-way FIN? Explain the\n"
            "   sequence/ack numbers in each packet."
        ),
        (
            "Total Data Transferred",
            "How many bytes of application data did the client send in total?\n"
            "   (Hint: compare the initial Seq to the final Seq in the FIN packet.)"
        ),
    ]

    print("\n" + "=" * 70)
    print("  ANALYSIS QUESTIONS")
    print("=" * 70)
    for i, (title, q) in enumerate(questions, 1):
        print(f"\n  Q{i}. {title}")
        print(f"  {'─' * 40}")
        for line in q.split("\n"):
            print(f"  {line}")
    print()


def print_solutions():
    """Print worked solutions."""
    print("\n" + "=" * 70)
    print("  WORKED SOLUTIONS")
    print("=" * 70)

    solutions = [
        (
            "Q1: Three-Way Handshake",
            """\
Packet 1 (SYN):       Client → Server, Seq=100, Ack=0, Flags=[SYN]
Packet 2 (SYN-ACK):   Server → Client, Seq=300, Ack=101, Flags=[SYN,ACK]
Packet 3 (ACK):       Client → Server, Seq=101, Ack=301, Flags=[ACK]

Why Ack=101 in packet 2?  The SYN flag consumes one sequence number,
so the server acknowledges Seq+1 = 100+1 = 101, meaning "I've received
everything up to byte 101 and I expect byte 101 next."

Similarly, packet 3 has Ack=301 because the server's SYN also consumes
one sequence number (300+1 = 301)."""
        ),
        (
            "Q2: RTT Estimation",
            """\
Use packets 1 and 2 (SYN and SYN-ACK):
  RTT ≈ t₂ - t₁ = 0.025013 - 0.000000 = 25.013 ms

This is an underestimate of the true RTT because it excludes the
server's processing time, but for a SYN-ACK this is typically minimal.

Alternative: packets 4→6: t₆ - t₄ = 0.051200 - 0.026000 = 25.2 ms
(includes time for server to process 2 segments)."""
        ),
        (
            "Q3: Throughput Calculation",
            """\
Between packets 4 and 6:
  Data sent: 2 segments × 1448 bytes = 2896 bytes = 23,168 bits
  Time: t₆ - t₄ = 0.051200 - 0.026000 = 0.025200 s

  Throughput = 23,168 / 0.025200 = 919,365 bps ≈ 0.92 Mbps

This is the application-level goodput. The link may be faster, but
TCP's window limits how much data is in flight at once."""
        ),
        (
            "Q4: Congestion Window Growth",
            """\
Round 1 (pkts 4–5):  2 segments sent → cwnd ≈ 2 MSS
Round 2 (pkts 7–10): 4 segments sent → cwnd ≈ 4 MSS

The window doubles each RTT: 2 → 4. This is SLOW START (exponential
growth), where cwnd increases by 1 MSS for each ACK received.

After each ACK in slow start:
  - ACK for pkt 4–5 arrives (pkt 6):  cwnd goes from 2→4 MSS
    (each of the 2 ACKed segments adds 1 MSS, but this is cumulative)
  - ACK for pkts 7–10 (pkts 11,12):   cwnd goes from 4→8 MSS

Slow start continues until cwnd reaches ssthresh, at which point TCP
switches to congestion avoidance (additive increase)."""
        ),
        (
            "Q5: Packet Loss & Fast Retransmit",
            """\
(a) Packet 15 (Seq=10237) is lost. The server receives packet 16
    (Seq=11685) out of order — it has a gap. TCP's cumulative ACK
    mechanism means the server can only acknowledge contiguous data,
    so it re-sends ACK=10237 for every subsequent out-of-order segment.

(b) All duplicate ACKs carry Ack=10237, because that's the next byte
    the server expects. It has received bytes beyond 10237 but cannot
    acknowledge them until the gap is filled.

(c) After receiving 3 duplicate ACKs (packets 17, 19, 20), the sender
    triggers FAST RETRANSMIT — it retransmits the lost segment
    (packet 21, Seq=10237) without waiting for a timeout.

(d) After fast retransmit, TCP enters FAST RECOVERY:
    - ssthresh = cwnd/2
    - cwnd = ssthresh + 3 MSS (for the 3 dup ACKs)
    - Then cwnd grows by 1 MSS per additional dup ACK
    - When the retransmitted data is ACKed, cwnd = ssthresh
      and TCP enters congestion avoidance (additive increase)
    TCP does NOT go back to slow start after fast retransmit."""
        ),
        (
            "Q6: Connection Teardown",
            """\
Packet 22: Client → Server [FIN, ACK] Seq=14581, Ack=301
Packet 23: Server → Client [FIN, ACK] Seq=301,   Ack=14582
Packet 24: Client → Server [ACK]      Seq=14582,  Ack=302

This is a 3-way FIN (also called simultaneous close shortcut):
the server piggybacks its own FIN onto its ACK of the client's FIN,
saving one packet compared to the standard 4-way teardown.

Sequence numbers: FIN consumes 1 sequence number, so:
  - Client's FIN has Seq=14581 → Server ACKs with 14582
  - Server's FIN has Seq=301   → Client ACKs with 302"""
        ),
        (
            "Q7: Total Data Transferred",
            """\
Client's initial Seq (after handshake): 101
Client's FIN Seq: 14581

Total application data = 14581 - 101 = 14,480 bytes

Sanity check: The client sent segments with Len=1448 each.
14,480 / 1448 = 10 segments exactly. ✓

Counting data packets: 4, 5, 7, 8, 9, 10, 13, 15(lost), 16, 18, 21(retransmit)
That's 10 unique data segments (15 and 21 carry the same data), confirming
14,480 bytes of unique application data."""
        ),
    ]

    for title, sol in solutions:
        print(f"\n  {title}")
        print(f"  {'━' * 50}")
        for line in sol.split("\n"):
            print(f"  {line}")
    print()


def main():
    print()
    print("  ╔═══════════════════════════════════════════════════════════╗")
    print("  ║   EC 441 — TCP Trace Analysis Assignment                 ║")
    print("  ║   Mathis Souef-Myers · Prof. Carruthers · Spring 2026    ║")
    print("  ╚═══════════════════════════════════════════════════════════╝")
    print()
    print("  This assignment walks through a simulated tshark TCP capture")
    print("  covering: handshake, data transfer, congestion control,")
    print("  packet loss with fast retransmit, and connection teardown.")
    print()

    print_trace()
    print_questions()

    print("─" * 70)
    show = input("  Show worked solutions? (y/n): ").strip().lower()
    if show in ("y", "yes", ""):
        print_solutions()
    else:
        print("\n  Solutions hidden. Run again and type 'y' to see them.\n")

    print("  ─── End of Assignment ───\n")


if __name__ == "__main__":
    main()
