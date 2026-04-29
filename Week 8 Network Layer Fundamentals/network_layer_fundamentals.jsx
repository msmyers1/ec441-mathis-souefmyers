import { useState, useCallback } from "react";

const TABS = ["IPv4", "IPv6", "DHCP", "NAT"];

// ─── IPv4 Section ────────────────────────────────────────
function IPv4Section() {
  const [octets, setOctets] = useState([192, 168, 1, 100]);
  const [prefix, setPrefix] = useState(24);

  const toBin = (n) => n.toString(2).padStart(8, "0");
  const mask = Array.from({ length: 4 }, (_, i) => {
    const bits = Math.min(8, Math.max(0, prefix - i * 8));
    return bits === 8 ? 255 : bits === 0 ? 0 : (256 - Math.pow(2, 8 - bits));
  });
  const network = octets.map((o, i) => o & mask[i]);
  const broadcast = network.map((n, i) => n | (~mask[i] & 255));
  const hosts = Math.pow(2, 32 - prefix) - 2;

  const getClass = () => {
    if (octets[0] < 128) return { cls: "A", range: "0–127", default: "/8", net: "8 bits", host: "24 bits" };
    if (octets[0] < 192) return { cls: "B", range: "128–191", default: "/16", net: "16 bits", host: "16 bits" };
    if (octets[0] < 224) return { cls: "C", range: "192–223", default: "/24", net: "24 bits", host: "8 bits" };
    if (octets[0] < 240) return { cls: "D", range: "224–239", default: "N/A", net: "Multicast", host: "—" };
    return { cls: "E", range: "240–255", default: "N/A", net: "Reserved", host: "—" };
  };
  const info = getClass();

  return (
    <div>
      <h2 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 28, color: "#f1f5f9", margin: "0 0 6px", fontWeight: 400 }}>
        IPv4 Addressing
      </h2>
      <p style={{ color: "#94a3b8", fontSize: 13, margin: "0 0 24px", lineHeight: 1.6 }}>
        32-bit addresses in dotted decimal. Drag the sliders to explore subnets interactively.
      </p>

      {/* Interactive address builder */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 4, alignItems: "center", justifyContent: "center", marginBottom: 16 }}>
          {octets.map((o, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{ textAlign: "center" }}>
                <div style={{
                  fontFamily: "'JetBrains Mono', monospace", fontSize: 28, fontWeight: 700,
                  color: i < Math.ceil(prefix / 8) ? "#14b8a6" : "#f59e0b",
                  background: "#0f172a", borderRadius: 8, padding: "6px 12px", minWidth: 60,
                }}>
                  {o}
                </div>
                <input type="range" min={0} max={255} value={o}
                  onChange={e => { const n = [...octets]; n[i] = +e.target.value; setOctets(n); }}
                  style={{ width: 70, marginTop: 6, accentColor: "#14b8a6" }} />
              </div>
              {i < 3 && <span style={{ fontSize: 28, color: "#475569", fontWeight: 700 }}>.</span>}
            </div>
          ))}
          <span style={{ fontSize: 28, color: "#475569", fontWeight: 700, marginLeft: 4 }}>/</span>
          <div style={{ textAlign: "center" }}>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: 28, fontWeight: 700,
              color: "#3b82f6", background: "#0f172a", borderRadius: 8, padding: "6px 12px", minWidth: 40,
            }}>
              {prefix}
            </div>
            <input type="range" min={0} max={32} value={prefix}
              onChange={e => setPrefix(+e.target.value)}
              style={{ width: 60, marginTop: 6, accentColor: "#3b82f6" }} />
          </div>
        </div>

        {/* Binary view */}
        <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, textAlign: "center", lineHeight: 1.8, color: "#94a3b8" }}>
          {octets.map((o, i) => {
            const bin = toBin(o);
            return (
              <span key={i}>
                {bin.split("").map((bit, j) => {
                  const globalBit = i * 8 + j;
                  return (
                    <span key={j} style={{
                      color: globalBit < prefix ? "#14b8a6" : "#f59e0b",
                      fontWeight: globalBit === prefix - 1 || globalBit === prefix ? 700 : 400,
                    }}>
                      {bit}
                    </span>
                  );
                })}
                {i < 3 && <span style={{ color: "#334155" }}>.</span>}
              </span>
            );
          })}
        </div>
        <div style={{ textAlign: "center", marginTop: 4, fontSize: 11, color: "#64748b" }}>
          <span style={{ color: "#14b8a6" }}>■ network ({prefix} bits)</span>
          <span style={{ margin: "0 12px" }}>|</span>
          <span style={{ color: "#f59e0b" }}>■ host ({32 - prefix} bits)</span>
        </div>
      </div>

      {/* Results grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
        {[
          { label: "Subnet Mask", value: mask.join("."), color: "#3b82f6" },
          { label: "Network Address", value: network.join("."), color: "#14b8a6" },
          { label: "Broadcast", value: broadcast.join("."), color: "#f59e0b" },
          { label: "Usable Hosts", value: hosts > 0 ? hosts.toLocaleString() : "0", color: "#f43f5e" },
          { label: "First Usable", value: hosts > 0 ? [...network.slice(0, 3), network[3] + 1].join(".") : "—", color: "#8b5cf6" },
          { label: "Last Usable", value: hosts > 0 ? [...broadcast.slice(0, 3), broadcast[3] - 1].join(".") : "—", color: "#8b5cf6" },
        ].map((item, i) => (
          <div key={i} style={{ background: "#1e293b", borderRadius: 10, padding: "12px 16px" }}>
            <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>{item.label}</div>
            <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 15, color: item.color, fontWeight: 600, marginTop: 4 }}>{item.value}</div>
          </div>
        ))}
      </div>

      {/* Classful info */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
        <div style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 10 }}>Classful Reference</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 }}>
          {[
            { cls: "A", r: "0–127", p: "/8" },
            { cls: "B", r: "128–191", p: "/16" },
            { cls: "C", r: "192–223", p: "/24" },
            { cls: "D", r: "224–239", p: "Mcast" },
            { cls: "E", r: "240–255", p: "Rsvd" },
          ].map((c) => (
            <div key={c.cls} style={{
              background: c.cls === info.cls ? "#0f172a" : "transparent",
              border: c.cls === info.cls ? "1px solid #14b8a6" : "1px solid transparent",
              borderRadius: 8, padding: "8px 6px", textAlign: "center",
            }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: c.cls === info.cls ? "#14b8a6" : "#475569" }}>{c.cls}</div>
              <div style={{ fontSize: 10, color: "#64748b" }}>{c.r}</div>
              <div style={{ fontSize: 11, color: "#94a3b8", fontFamily: "'JetBrains Mono', monospace" }}>{c.p}</div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 12, fontSize: 12, color: "#94a3b8" }}>
          <strong style={{ color: "#14b8a6" }}>Private ranges:</strong>{" "}
          10.0.0.0/8 &nbsp;·&nbsp; 172.16.0.0/12 &nbsp;·&nbsp; 192.168.0.0/16
        </div>
      </div>
    </div>
  );
}

// ─── IPv6 Section ────────────────────────────────────────
function IPv6Section() {
  const [showFull, setShowFull] = useState(false);

  const examples = [
    { short: "2001:db8::1", full: "2001:0db8:0000:0000:0000:0000:0000:0001", desc: "Documentation prefix" },
    { short: "fe80::1", full: "fe80:0000:0000:0000:0000:0000:0000:0001", desc: "Link-local address" },
    { short: "::1", full: "0000:0000:0000:0000:0000:0000:0000:0001", desc: "Loopback" },
    { short: "::", full: "0000:0000:0000:0000:0000:0000:0000:0000", desc: "Unspecified (all zeros)" },
  ];

  const comparisons = [
    { feat: "Address size", v4: "32 bits", v6: "128 bits" },
    { feat: "Notation", v4: "Dotted decimal", v6: "Colon hexadecimal" },
    { feat: "Address space", v4: "~4.3 billion", v6: "~3.4 × 10³⁸" },
    { feat: "Header size", v4: "20–60 bytes (variable)", v6: "40 bytes (fixed)" },
    { feat: "Checksum", v4: "In header", v6: "Removed (layer 4 handles)" },
    { feat: "Fragmentation", v4: "Routers can fragment", v6: "Source only (Path MTU)" },
    { feat: "Broadcast", v4: "Yes", v6: "No (uses multicast)" },
    { feat: "Config", v4: "Manual or DHCP", v6: "SLAAC or DHCPv6" },
    { feat: "IPsec", v4: "Optional", v6: "Built-in support" },
  ];

  return (
    <div>
      <h2 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 28, color: "#f1f5f9", margin: "0 0 6px", fontWeight: 400 }}>
        IPv6 Addressing
      </h2>
      <p style={{ color: "#94a3b8", fontSize: 13, margin: "0 0 24px", lineHeight: 1.6 }}>
        128-bit addresses in colon-separated hexadecimal. Designed to solve IPv4 exhaustion.
      </p>

      {/* Header structure */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, marginBottom: 20 }}>
        <div style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 12 }}>IPv6 Header (Fixed 40 bytes)</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 6 }}>
          {[
            { name: "Version", bits: "4b", color: "#14b8a6" },
            { name: "Traffic Class", bits: "8b", color: "#3b82f6" },
            { name: "Flow Label", bits: "20b", color: "#8b5cf6" },
            { name: "", bits: "", color: "transparent" },
            { name: "Payload Length", bits: "16b", color: "#f59e0b" },
            { name: "Next Header", bits: "8b", color: "#f43f5e" },
            { name: "Hop Limit", bits: "8b", color: "#ec4899" },
            { name: "", bits: "", color: "transparent" },
          ].filter(f => f.name).map((f, i) => (
            <div key={i} style={{
              background: `${f.color}18`, border: `1px solid ${f.color}40`,
              borderRadius: 6, padding: "8px 10px", textAlign: "center",
            }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: f.color }}>{f.name}</div>
              <div style={{ fontSize: 10, color: "#64748b", marginTop: 2 }}>{f.bits}</div>
            </div>
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 6, marginTop: 6 }}>
          {[
            { name: "Source Address", bits: "128 bits", color: "#14b8a6" },
            { name: "Destination Address", bits: "128 bits", color: "#3b82f6" },
          ].map((f, i) => (
            <div key={i} style={{
              background: `${f.color}18`, border: `1px solid ${f.color}40`,
              borderRadius: 6, padding: "10px 14px", textAlign: "center",
            }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: f.color }}>{f.name}</span>
              <span style={{ fontSize: 11, color: "#64748b", marginLeft: 8 }}>{f.bits}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Shorthand examples */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, marginBottom: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <span style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>
            Shorthand Rules
          </span>
          <button onClick={() => setShowFull(!showFull)} style={{
            background: "#334155", border: "none", borderRadius: 6, padding: "4px 12px",
            color: "#94a3b8", fontSize: 11, cursor: "pointer", fontFamily: "'JetBrains Mono', monospace",
          }}>
            {showFull ? "Show short" : "Show expanded"}
          </button>
        </div>
        <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 14, lineHeight: 1.7 }}>
          <strong style={{ color: "#f59e0b" }}>Rule 1:</strong> Drop leading zeros in each group ({" "}
          <span style={{ fontFamily: "'JetBrains Mono', monospace", color: "#64748b" }}>0db8</span> →{" "}
          <span style={{ fontFamily: "'JetBrains Mono', monospace", color: "#14b8a6" }}>db8</span>)
          <br />
          <strong style={{ color: "#f59e0b" }}>Rule 2:</strong> Replace one longest run of all-zero groups with{" "}
          <span style={{ fontFamily: "'JetBrains Mono', monospace", color: "#14b8a6" }}>::</span> (once only)
        </div>
        {examples.map((ex, i) => (
          <div key={i} style={{
            display: "flex", justifyContent: "space-between", alignItems: "center",
            padding: "8px 12px", borderRadius: 8, marginBottom: 4,
            background: i % 2 === 0 ? "#0f172a" : "transparent",
          }}>
            <div>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, color: "#14b8a6", fontWeight: 600 }}>
                {showFull ? ex.full : ex.short}
              </span>
            </div>
            <span style={{ fontSize: 11, color: "#64748b" }}>{ex.desc}</span>
          </div>
        ))}
      </div>

      {/* Comparison table */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 20 }}>
        <div style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 12 }}>IPv4 vs IPv6</div>
        <div style={{ fontSize: 12 }}>
          <div style={{ display: "grid", gridTemplateColumns: "2fr 2fr 2fr", gap: 0, padding: "8px 12px", borderRadius: "8px 8px 0 0", background: "#0f172a" }}>
            <span style={{ color: "#64748b", fontWeight: 600 }}>Feature</span>
            <span style={{ color: "#f59e0b", fontWeight: 600 }}>IPv4</span>
            <span style={{ color: "#14b8a6", fontWeight: 600 }}>IPv6</span>
          </div>
          {comparisons.map((row, i) => (
            <div key={i} style={{
              display: "grid", gridTemplateColumns: "2fr 2fr 2fr", gap: 0,
              padding: "7px 12px", background: i % 2 === 0 ? "transparent" : "#0f172a08",
              borderBottom: "1px solid #1e293b",
            }}>
              <span style={{ color: "#cbd5e1", fontWeight: 500 }}>{row.feat}</span>
              <span style={{ color: "#94a3b8", fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>{row.v4}</span>
              <span style={{ color: "#94a3b8", fontFamily: "'JetBrains Mono', monospace", fontSize: 11 }}>{row.v6}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── DHCP Section ────────────────────────────────────────
function DHCPSection() {
  const [step, setStep] = useState(0);

  const steps = [
    {
      name: "DISCOVER",
      from: "Client", to: "Broadcast",
      fromColor: "#3b82f6", toColor: "#64748b",
      desc: "Client broadcasts: \"I need an IP address!\" Sent to 255.255.255.255 (broadcast) because the client has no IP yet. Source IP is 0.0.0.0.",
      details: "UDP src port 68 → dst port 67 | Includes client MAC address and a transaction ID",
      arrow: "→",
    },
    {
      name: "OFFER",
      from: "Server", to: "Broadcast",
      fromColor: "#14b8a6", toColor: "#64748b",
      desc: "Server responds: \"Here's 192.168.1.50, with a lease of 24 hours.\" Multiple servers may respond with different offers.",
      details: "Includes: offered IP, subnet mask, default gateway, DNS server, lease time",
      arrow: "←",
    },
    {
      name: "REQUEST",
      from: "Client", to: "Broadcast",
      fromColor: "#3b82f6", toColor: "#64748b",
      desc: "Client broadcasts: \"I'll take 192.168.1.50 from server X.\" Broadcast so other DHCP servers know their offers were declined.",
      details: "Still broadcast (not unicast) because client hasn't configured the IP yet",
      arrow: "→",
    },
    {
      name: "ACK",
      from: "Server", to: "Client",
      fromColor: "#14b8a6", toColor: "#3b82f6",
      desc: "Server confirms: \"192.168.1.50 is yours for 24 hours. Welcome to the network.\" Client can now configure its interface.",
      details: "Client sets IP, mask, gateway, DNS. Lease timer starts. Renewal at T1 (50%), rebind at T2 (87.5%)",
      arrow: "←",
    },
  ];

  const cur = steps[step];

  return (
    <div>
      <h2 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 28, color: "#f1f5f9", margin: "0 0 6px", fontWeight: 400 }}>
        DHCP — Dynamic Host Configuration Protocol
      </h2>
      <p style={{ color: "#94a3b8", fontSize: 13, margin: "0 0 24px", lineHeight: 1.6 }}>
        Automatically assigns IP addresses via the DORA handshake (Discover → Offer → Request → Ack).
      </p>

      {/* Step selector */}
      <div style={{ display: "flex", gap: 4, marginBottom: 20 }}>
        {steps.map((s, i) => (
          <button key={i} onClick={() => setStep(i)} style={{
            flex: 1, padding: "10px 8px", borderRadius: 8, border: "none", cursor: "pointer",
            fontFamily: "'JetBrains Mono', monospace", fontSize: 13, fontWeight: 700, letterSpacing: "0.02em",
            background: step === i ? (i % 2 === 0 ? "#3b82f6" : "#14b8a6") : "#1e293b",
            color: step === i ? "#fff" : "#64748b",
            transition: "all 0.2s",
          }}>
            {s.name}
          </button>
        ))}
      </div>

      {/* Visualization */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 24, marginBottom: 20 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          {/* Client */}
          <div style={{
            width: 100, textAlign: "center", padding: "16px 12px", borderRadius: 12,
            background: "#0f172a", border: `2px solid ${step === 0 || step === 2 ? "#3b82f6" : "#334155"}`,
          }}>
            <div style={{ fontSize: 24 }}>💻</div>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#3b82f6", marginTop: 4 }}>Client</div>
            <div style={{ fontSize: 10, color: "#64748b", fontFamily: "'JetBrains Mono', monospace" }}>
              {step < 3 ? "0.0.0.0" : "192.168.1.50"}
            </div>
          </div>

          {/* Arrow */}
          <div style={{ flex: 1, padding: "0 16px", textAlign: "center" }}>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: 14, fontWeight: 700,
              color: step % 2 === 0 ? "#3b82f6" : "#14b8a6", marginBottom: 4,
            }}>
              {cur.name}
            </div>
            <div style={{
              height: 3, borderRadius: 2, margin: "0 auto",
              background: `linear-gradient(${cur.arrow === "→" ? "to right" : "to left"}, #3b82f6, #14b8a6)`,
            }} />
            <div style={{ fontSize: 20, marginTop: -2, color: step % 2 === 0 ? "#3b82f6" : "#14b8a6" }}>
              {cur.arrow === "→" ? "→" : "←"}
            </div>
          </div>

          {/* Server */}
          <div style={{
            width: 100, textAlign: "center", padding: "16px 12px", borderRadius: 12,
            background: "#0f172a", border: `2px solid ${step === 1 || step === 3 ? "#14b8a6" : "#334155"}`,
          }}>
            <div style={{ fontSize: 24 }}>🖥️</div>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#14b8a6", marginTop: 4 }}>DHCP Server</div>
            <div style={{ fontSize: 10, color: "#64748b", fontFamily: "'JetBrains Mono', monospace" }}>192.168.1.1</div>
          </div>
        </div>

        <div style={{ background: "#0f172a", borderRadius: 10, padding: 16 }}>
          <p style={{ fontSize: 13, color: "#e2e8f0", margin: "0 0 8px", lineHeight: 1.7 }}>{cur.desc}</p>
          <p style={{ fontSize: 11, color: "#64748b", margin: 0, fontFamily: "'JetBrains Mono', monospace", lineHeight: 1.6 }}>{cur.details}</p>
        </div>
      </div>

      {/* Lease lifecycle */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 20 }}>
        <div style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 14 }}>Lease Lifecycle</div>
        <div style={{ position: "relative", height: 60 }}>
          <div style={{ position: "absolute", top: 20, left: 0, right: 0, height: 6, background: "#0f172a", borderRadius: 3 }} />
          <div style={{ position: "absolute", top: 20, left: 0, width: "100%", height: 6, borderRadius: 3,
            background: "linear-gradient(to right, #14b8a6 0%, #14b8a6 50%, #f59e0b 50%, #f59e0b 87.5%, #f43f5e 87.5%, #f43f5e 100%)",
          }} />
          {[
            { pct: 0, label: "Lease start", color: "#14b8a6" },
            { pct: 50, label: "T1: Renew (50%)", color: "#f59e0b" },
            { pct: 87.5, label: "T2: Rebind (87.5%)", color: "#f43f5e" },
            { pct: 100, label: "Expires", color: "#64748b" },
          ].map((m, i) => (
            <div key={i} style={{ position: "absolute", left: `${m.pct}%`, top: 0, transform: "translateX(-50%)", textAlign: "center" }}>
              <div style={{ fontSize: 9, color: m.color, fontWeight: 600, whiteSpace: "nowrap" }}>{m.label}</div>
              <div style={{ width: 2, height: 10, background: m.color, margin: "2px auto 0" }} />
            </div>
          ))}
        </div>
        <p style={{ fontSize: 11, color: "#94a3b8", marginTop: 16, lineHeight: 1.6 }}>
          At <strong style={{ color: "#f59e0b" }}>T1</strong>, client unicasts a renewal to the original server.
          At <strong style={{ color: "#f43f5e" }}>T2</strong>, if no response, client broadcasts to find any DHCP server.
          If lease expires, the client must stop using the IP and restart DORA.
        </p>
      </div>
    </div>
  );
}

// ─── NAT Section ─────────────────────────────────────────
function NATSection() {
  const [entries] = useState([
    { privateIP: "192.168.1.10", privatePort: "3456", publicPort: "40001", dest: "93.184.216.34:80" },
    { privateIP: "192.168.1.20", privatePort: "7890", publicPort: "40002", dest: "142.250.80.46:443" },
    { privateIP: "192.168.1.10", privatePort: "3457", publicPort: "40003", dest: "93.184.216.34:443" },
    { privateIP: "192.168.1.30", privatePort: "5555", publicPort: "40004", dest: "151.101.1.69:443" },
  ]);

  return (
    <div>
      <h2 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 28, color: "#f1f5f9", margin: "0 0 6px", fontWeight: 400 }}>
        NAT — Network Address Translation
      </h2>
      <p style={{ color: "#94a3b8", fontSize: 13, margin: "0 0 24px", lineHeight: 1.6 }}>
        Maps private IPs to a single public IP, allowing many devices to share one address.
      </p>

      {/* Diagram */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 24, marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {/* Private side */}
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 8, textAlign: "center" }}>
              Private Network (LAN)
            </div>
            {["192.168.1.10", "192.168.1.20", "192.168.1.30"].map((ip, i) => (
              <div key={i} style={{
                background: "#0f172a", borderRadius: 8, padding: "8px 12px", marginBottom: 6,
                display: "flex", alignItems: "center", gap: 8, border: "1px solid #334155",
              }}>
                <span style={{ fontSize: 16 }}>{["💻", "📱", "🖥️"][i]}</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "#3b82f6" }}>{ip}</span>
              </div>
            ))}
          </div>

          {/* NAT Router */}
          <div style={{
            width: 90, textAlign: "center", padding: "16px 8px", borderRadius: 12,
            background: "linear-gradient(135deg, #14b8a618, #3b82f618)",
            border: "2px solid #14b8a6",
          }}>
            <div style={{ fontSize: 22 }}>🔀</div>
            <div style={{ fontSize: 11, fontWeight: 700, color: "#14b8a6", marginTop: 4 }}>NAT</div>
            <div style={{ fontSize: 9, color: "#64748b", marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>
              138.76.29.7
            </div>
          </div>

          {/* Public side */}
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 8, textAlign: "center" }}>
              Public Internet (WAN)
            </div>
            {["93.184.216.34", "142.250.80.46", "151.101.1.69"].map((ip, i) => (
              <div key={i} style={{
                background: "#0f172a", borderRadius: 8, padding: "8px 12px", marginBottom: 6,
                display: "flex", alignItems: "center", gap: 8, border: "1px solid #334155",
              }}>
                <span style={{ fontSize: 16 }}>🌐</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "#f59e0b" }}>{ip}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Translation table */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, marginBottom: 20 }}>
        <div style={{ fontSize: 12, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 14 }}>
          NAT Translation Table (PAT / NAPT)
        </div>
        <div style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}>
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1.2fr 1.2fr 2fr", gap: 0, padding: "8px 10px", background: "#0f172a", borderRadius: "8px 8px 0 0" }}>
            <span style={{ color: "#3b82f6", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>Private IP:Port</span>
            <span style={{ color: "#14b8a6", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>Public Port</span>
            <span style={{ color: "#f59e0b", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>Dest IP:Port</span>
            <span style={{ color: "#64748b", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace", textAlign: "right" }}>Outgoing As</span>
          </div>
          {entries.map((e, i) => (
            <div key={i} style={{
              display: "grid", gridTemplateColumns: "2fr 1.2fr 1.2fr 2fr", gap: 0,
              padding: "7px 10px", borderBottom: "1px solid #0f172a",
              background: i % 2 === 0 ? "transparent" : "#0f172a08",
            }}>
              <span style={{ color: "#94a3b8" }}>{e.privateIP}:{e.privatePort}</span>
              <span style={{ color: "#94a3b8" }}>{e.publicPort}</span>
              <span style={{ color: "#94a3b8" }}>{e.dest}</span>
              <span style={{ color: "#64748b", textAlign: "right" }}>138.76.29.7:{e.publicPort}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Key concepts */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {[
          { title: "Why NAT?", content: "IPv4 exhaustion — NAT lets an entire LAN share one public IP. Provides a layer of security by hiding internal structure.", color: "#14b8a6" },
          { title: "PAT / NAPT", content: "Port Address Translation: uses port numbers to distinguish flows. Most home routers use this — it's what lets multiple devices browse simultaneously.", color: "#3b82f6" },
          { title: "Problems", content: "Breaks end-to-end principle. Complicates peer-to-peer, VoIP, gaming. Servers can't initiate connections inward without port forwarding rules.", color: "#f43f5e" },
          { title: "NAT Traversal", content: "Techniques like STUN, TURN, ICE (used by WebRTC) and UPnP let applications work around NAT. Hole punching exploits existing table entries.", color: "#f59e0b" },
        ].map((card, i) => (
          <div key={i} style={{ background: "#1e293b", borderRadius: 10, padding: 16, borderLeft: `3px solid ${card.color}` }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: card.color, marginBottom: 6 }}>{card.title}</div>
            <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6 }}>{card.content}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Main Component ──────────────────────────────────────
export default function NetworkingGuide() {
  const [tab, setTab] = useState(0);
  const sections = [IPv4Section, IPv6Section, DHCPSection, NATSection];
  const Section = sections[tab];

  return (
    <div style={{
      background: "#0f172a", color: "#e2e8f0", minHeight: "100vh",
      fontFamily: "'DM Sans', -apple-system, sans-serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif&family=JetBrains+Mono:wght@400;600;700&display=swap');
        * { box-sizing: border-box; }
        input[type=range] { height: 4px; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
      `}</style>

      <div style={{ maxWidth: 680, margin: "0 auto", padding: "32px 20px" }}>
        {/* Header */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 11, color: "#64748b", fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            EC 441 · Computer Networking
          </div>
          <h1 style={{
            fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 38, color: "#f8fafc",
            margin: "8px 0 0", fontWeight: 400, lineHeight: 1.1,
          }}>
            Network Layer<br />
            <span style={{ color: "#14b8a6" }}>Fundamentals</span>
          </h1>
        </div>

        {/* Tab bar */}
        <div style={{
          display: "flex", gap: 2, marginBottom: 28, padding: 3,
          background: "#1e293b", borderRadius: 10,
        }}>
          {TABS.map((t, i) => (
            <button key={t} onClick={() => setTab(i)} style={{
              flex: 1, padding: "10px 8px", borderRadius: 8, border: "none", cursor: "pointer",
              fontSize: 13, fontWeight: 600, fontFamily: "'DM Sans', sans-serif",
              background: tab === i ? "#14b8a6" : "transparent",
              color: tab === i ? "#0f172a" : "#64748b",
              transition: "all 0.2s",
            }}>
              {t}
            </button>
          ))}
        </div>

        {/* Content */}
        <Section />

        {/* Footer */}
        <div style={{ textAlign: "center", marginTop: 32, paddingTop: 20, borderTop: "1px solid #1e293b" }}>
          <span style={{ fontSize: 11, color: "#475569", fontFamily: "'JetBrains Mono', monospace" }}>
            EC 441 · Mathis Souef-Myers · Prof. Carruthers · Spring 2026
          </span>
        </div>
      </div>
    </div>
  );
}
