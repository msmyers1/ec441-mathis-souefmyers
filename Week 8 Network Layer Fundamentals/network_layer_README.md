# Network Layer Fundamentals — EC 441

Interactive study guide covering **IPv4**, **IPv6**, **DHCP**, and **NAT** in a tabbed interface.

## How to Run Locally

This is a React component (`.jsx`). To run it:

1. **Quick option — drop into any React project:**

```bash
# If you don't have one yet:
npm create vite@latest network-guide -- --template react
cd network-guide
npm install
```

2. Replace `src/App.jsx` with:

```jsx
import NetworkingGuide from "./network_layer_fundamentals";

export default function App() {
  return <NetworkingGuide />;
}
```

3. Copy `network_layer_fundamentals.jsx` into `src/`.

4. Run it:

```bash
npm run dev
```

Open `http://localhost:5173` in your browser.

## What's Inside

| Tab | What it covers |
|-----|----------------|
| **IPv4** | Interactive subnet calculator with sliders for each octet + prefix length, live binary view with network/host bit coloring, results grid (mask, network, broadcast, usable range), and classful reference with private range callout. |
| **IPv6** | Fixed 40-byte header structure diagram, shorthand rules with toggle to expand/collapse example addresses, and a full IPv4 vs IPv6 comparison table (9 features). |
| **DHCP** | Step-through DORA handshake (Discover → Offer → Request → Ack) with client/server animation, per-step explanations, and a lease lifecycle timeline showing T1 renewal and T2 rebind thresholds. |
| **NAT** | LAN/WAN network diagram, live PAT translation table showing private IP:port → public port mapping, and concept cards covering why NAT exists, PAT/NAPT, problems it causes, and traversal techniques (STUN, TURN, ICE). |

## Dependencies

- React 18+
- No other libraries required (all styling is inline)
- Fonts loaded from Google Fonts: DM Sans, Instrument Serif, JetBrains Mono
