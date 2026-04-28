import { useState, useCallback, useMemo } from "react";

const GRAPH = {
  nodes: ["A", "B", "C", "D", "E"],
  edges: [
    { from: "A", to: "B", cost: 2 },
    { from: "A", to: "C", cost: 5 },
    { from: "B", to: "C", cost: 1 },
    { from: "B", to: "D", cost: 3 },
    { from: "C", to: "D", cost: 1 },
    { from: "C", to: "E", cost: 4 },
    { from: "D", to: "E", cost: 2 },
  ],
};

const POSITIONS = {
  A: { x: 80, y: 160 },
  B: { x: 240, y: 60 },
  C: { x: 240, y: 260 },
  D: { x: 420, y: 100 },
  E: { x: 420, y: 260 },
};

function buildAdj(graph) {
  const adj = {};
  graph.nodes.forEach((n) => (adj[n] = {}));
  graph.edges.forEach(({ from, to, cost }) => {
    adj[from][to] = cost;
    adj[to][from] = cost;
  });
  return adj;
}

function runDijkstra(adj, src, nodes) {
  const steps = [];
  const dist = {};
  const prev = {};
  const visited = new Set();
  nodes.forEach((n) => {
    dist[n] = n === src ? 0 : Infinity;
    prev[n] = null;
  });
  steps.push({
    title: "Initialize",
    desc: `Set d(${src})=0, all others = ∞. No nodes visited yet.`,
    dist: { ...dist },
    prev: { ...prev },
    visited: new Set(visited),
    current: null,
    considering: null,
  });

  for (let i = 0; i < nodes.length; i++) {
    let u = null;
    let best = Infinity;
    nodes.forEach((n) => {
      if (!visited.has(n) && dist[n] < best) {
        best = dist[n];
        u = n;
      }
    });
    if (u === null) break;
    visited.add(u);
    const neighbors = Object.keys(adj[u]).filter((n) => !visited.has(n));
    let relaxed = [];
    neighbors.forEach((v) => {
      const alt = dist[u] + adj[u][v];
      if (alt < dist[v]) {
        relaxed.push({ v, old: dist[v], new: alt });
        dist[v] = alt;
        prev[v] = u;
      }
    });
    const relaxDesc =
      relaxed.length > 0
        ? relaxed
            .map(
              (r) =>
                `d(${r.v}): ${r.old === Infinity ? "∞" : r.old} → ${r.new}`
            )
            .join(", ")
        : "no updates";
    steps.push({
      title: `Visit ${u} (d=${best})`,
      desc: `Extract min: ${u}. Relax neighbors: ${relaxDesc}.`,
      dist: { ...dist },
      prev: { ...prev },
      visited: new Set(visited),
      current: u,
      considering: neighbors,
    });
  }
  return steps;
}

function runBellmanFord(adj, src, nodes) {
  const steps = [];
  const tables = {};
  nodes.forEach((n) => {
    tables[n] = {};
    nodes.forEach((d) => {
      tables[n][d] = { cost: n === d ? 0 : Infinity, via: n === d ? n : null };
    });
  });
  // Initialize direct neighbors
  nodes.forEach((n) => {
    Object.entries(adj[n]).forEach(([nb, c]) => {
      tables[n][nb] = { cost: c, via: nb };
    });
  });

  const cloneTables = (t) => {
    const c = {};
    Object.keys(t).forEach((n) => {
      c[n] = {};
      Object.keys(t[n]).forEach((d) => {
        c[n][d] = { ...t[n][d] };
      });
    });
    return c;
  };

  steps.push({
    title: "Initialize",
    desc: "Each node knows cost to direct neighbors. All other destinations = ∞.",
    tables: cloneTables(tables),
    exchangeNode: null,
    updates: [],
  });

  for (let iter = 0; iter < 4; iter++) {
    let anyChange = false;
    const roundUpdates = [];
    nodes.forEach((n) => {
      Object.keys(adj[n]).forEach((nb) => {
        const linkCost = adj[n][nb];
        nodes.forEach((dest) => {
          const newCost = linkCost + tables[nb][dest].cost;
          if (newCost < tables[n][dest].cost) {
            roundUpdates.push({
              node: n,
              dest,
              old: tables[n][dest].cost,
              new: newCost,
              via: nb,
            });
            tables[n][dest] = { cost: newCost, via: nb };
            anyChange = true;
          }
        });
      });
    });
    if (!anyChange && iter > 0) break;
    const updDesc =
      roundUpdates.length > 0
        ? roundUpdates
            .map(
              (u) =>
                `${u.node}→${u.dest}: ${u.old === Infinity ? "∞" : u.old}→${u.new} via ${u.via}`
            )
            .join("; ")
        : "no changes — converged!";
    steps.push({
      title: `Round ${iter + 1}`,
      desc: `Each node exchanges DV with neighbors. Updates: ${updDesc}`,
      tables: cloneTables(tables),
      exchangeNode: null,
      updates: roundUpdates,
    });
    if (!anyChange) break;
  }
  return steps;
}

function NetworkGraph({ visited, current, considering, highlightEdges }) {
  const vSet = visited || new Set();
  const cSet = new Set(considering || []);
  return (
    <svg viewBox="0 0 500 320" style={{ width: "100%", maxWidth: 500 }}>
      <defs>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {GRAPH.edges.map(({ from, to, cost }, i) => {
        const p1 = POSITIONS[from];
        const p2 = POSITIONS[to];
        const mx = (p1.x + p2.x) / 2;
        const my = (p1.y + p2.y) / 2;
        const isHL =
          highlightEdges &&
          highlightEdges.some(
            (e) =>
              (e[0] === from && e[1] === to) || (e[0] === to && e[1] === from)
          );
        return (
          <g key={i}>
            <line
              x1={p1.x}
              y1={p1.y}
              x2={p2.x}
              y2={p2.y}
              stroke={isHL ? "#f59e0b" : "#64748b"}
              strokeWidth={isHL ? 3 : 1.5}
              opacity={isHL ? 1 : 0.5}
            />
            <rect
              x={mx - 12}
              y={my - 10}
              width={24}
              height={20}
              rx={4}
              fill="#1e293b"
              stroke="#475569"
              strokeWidth={0.5}
            />
            <text
              x={mx}
              y={my + 1}
              textAnchor="middle"
              dominantBaseline="central"
              fill="#e2e8f0"
              fontSize={11}
              fontWeight="bold"
              fontFamily="monospace"
            >
              {cost}
            </text>
          </g>
        );
      })}
      {GRAPH.nodes.map((n) => {
        const p = POSITIONS[n];
        const isCurrent = n === current;
        const isVisited = vSet.has(n);
        const isConsidering = cSet.has(n);
        let fill = "#334155";
        let stroke = "#64748b";
        if (isCurrent) {
          fill = "#059669";
          stroke = "#34d399";
        } else if (isConsidering) {
          fill = "#d97706";
          stroke = "#fbbf24";
        } else if (isVisited) {
          fill = "#1e40af";
          stroke = "#60a5fa";
        }
        return (
          <g key={n} filter={isCurrent ? "url(#glow)" : undefined}>
            <circle cx={p.x} cy={p.y} r={22} fill={fill} stroke={stroke} strokeWidth={2} />
            <text
              x={p.x}
              y={p.y + 1}
              textAnchor="middle"
              dominantBaseline="central"
              fill="white"
              fontSize={16}
              fontWeight="bold"
              fontFamily="monospace"
            >
              {n}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function DVTable({ tables, nodes, updates }) {
  const upSet = new Set((updates || []).map((u) => `${u.node}-${u.dest}`));
  return (
    <div style={{ overflowX: "auto" }}>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        {nodes.map((n) => (
          <div key={n} style={{ minWidth: 100 }}>
            <div
              style={{
                background: "#1e40af",
                color: "white",
                padding: "4px 8px",
                borderRadius: "6px 6px 0 0",
                fontWeight: "bold",
                fontFamily: "monospace",
                fontSize: 13,
                textAlign: "center",
              }}
            >
              Node {n}
            </div>
            <table
              style={{
                borderCollapse: "collapse",
                fontSize: 12,
                fontFamily: "monospace",
                width: "100%",
              }}
            >
              <thead>
                <tr>
                  <th style={{ padding: "3px 6px", borderBottom: "1px solid #475569", color: "#94a3b8" }}>
                    Dst
                  </th>
                  <th style={{ padding: "3px 6px", borderBottom: "1px solid #475569", color: "#94a3b8" }}>
                    Cost
                  </th>
                  <th style={{ padding: "3px 6px", borderBottom: "1px solid #475569", color: "#94a3b8" }}>
                    Via
                  </th>
                </tr>
              </thead>
              <tbody>
                {nodes.map((d) => {
                  const entry = tables[n][d];
                  const isUp = upSet.has(`${n}-${d}`);
                  return (
                    <tr
                      key={d}
                      style={{
                        background: isUp ? "rgba(245,158,11,0.2)" : "transparent",
                      }}
                    >
                      <td style={{ padding: "2px 6px", textAlign: "center" }}>{d}</td>
                      <td style={{ padding: "2px 6px", textAlign: "center", color: isUp ? "#fbbf24" : "#e2e8f0" }}>
                        {entry.cost === Infinity ? "∞" : entry.cost}
                      </td>
                      <td style={{ padding: "2px 6px", textAlign: "center", color: "#94a3b8" }}>
                        {entry.via || "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function RoutingViz() {
  const [algo, setAlgo] = useState("dijkstra");
  const [src, setSrc] = useState("A");
  const [step, setStep] = useState(0);
  const adj = useMemo(() => buildAdj(GRAPH), []);

  const steps = useMemo(() => {
    if (algo === "dijkstra") return runDijkstra(adj, src, GRAPH.nodes);
    return runBellmanFord(adj, src, GRAPH.nodes);
  }, [algo, src, adj]);

  const cur = steps[step] || steps[0];

  const prevEdges = useMemo(() => {
    if (algo !== "dijkstra" || !cur.prev) return [];
    const edges = [];
    GRAPH.nodes.forEach((n) => {
      if (cur.prev[n]) edges.push([cur.prev[n], n]);
    });
    return edges;
  }, [algo, cur]);

  const handleAlgo = useCallback(
    (a) => {
      setAlgo(a);
      setStep(0);
    },
    []
  );
  const handleSrc = useCallback(
    (s) => {
      setSrc(s);
      setStep(0);
    },
    []
  );

  return (
    <div
      style={{
        background: "#0f172a",
        color: "#e2e8f0",
        minHeight: "100vh",
        fontFamily:
          'ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace',
        padding: 24,
      }}
    >
      <div style={{ maxWidth: 800, margin: "0 auto" }}>
        <h1
          style={{
            fontSize: 22,
            fontWeight: 800,
            color: "#f8fafc",
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          EC 441 — Routing Algorithms
        </h1>
        <p style={{ color: "#94a3b8", margin: "4px 0 20px", fontSize: 13 }}>
          Step through Dijkstra (Link State) and Distance Vector on a sample
          network
        </p>

        {/* Controls */}
        <div
          style={{
            display: "flex",
            gap: 12,
            flexWrap: "wrap",
            marginBottom: 16,
          }}
        >
          <div style={{ display: "flex", gap: 4 }}>
            {["dijkstra", "dv"].map((a) => (
              <button
                key={a}
                onClick={() => handleAlgo(a)}
                style={{
                  padding: "6px 14px",
                  borderRadius: 6,
                  border: "none",
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: 600,
                  fontFamily: "inherit",
                  background: algo === a ? "#3b82f6" : "#1e293b",
                  color: algo === a ? "white" : "#94a3b8",
                  transition: "all 0.15s",
                }}
              >
                {a === "dijkstra" ? "Dijkstra (LS)" : "Distance Vector"}
              </button>
            ))}
          </div>
          {algo === "dijkstra" && (
            <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
              <span style={{ fontSize: 12, color: "#64748b" }}>Source:</span>
              {GRAPH.nodes.map((n) => (
                <button
                  key={n}
                  onClick={() => handleSrc(n)}
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: 6,
                    border: "none",
                    cursor: "pointer",
                    fontSize: 12,
                    fontWeight: 700,
                    fontFamily: "inherit",
                    background: src === n ? "#059669" : "#1e293b",
                    color: src === n ? "white" : "#94a3b8",
                  }}
                >
                  {n}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Graph */}
        <div
          style={{
            background: "#1e293b",
            borderRadius: 12,
            padding: 16,
            marginBottom: 16,
          }}
        >
          <NetworkGraph
            visited={algo === "dijkstra" ? cur.visited : undefined}
            current={cur.current}
            considering={cur.considering}
            highlightEdges={algo === "dijkstra" ? prevEdges : undefined}
          />
          {algo === "dijkstra" && (
            <div
              style={{
                display: "flex",
                gap: 16,
                justifyContent: "center",
                marginTop: 8,
                fontSize: 11,
              }}
            >
              {[
                { color: "#059669", label: "Current" },
                { color: "#d97706", label: "Considering" },
                { color: "#1e40af", label: "Visited" },
                { color: "#334155", label: "Unvisited" },
              ].map((l) => (
                <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <div
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      background: l.color,
                    }}
                  />
                  <span style={{ color: "#94a3b8" }}>{l.label}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Step info */}
        <div
          style={{
            background: "#1e293b",
            borderRadius: 12,
            padding: 16,
            marginBottom: 16,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 10,
            }}
          >
            <span style={{ fontSize: 14, fontWeight: 700, color: "#f8fafc" }}>
              Step {step + 1}/{steps.length}: {cur.title}
            </span>
            <div style={{ display: "flex", gap: 6 }}>
              <button
                onClick={() => setStep(Math.max(0, step - 1))}
                disabled={step === 0}
                style={{
                  padding: "4px 12px",
                  borderRadius: 6,
                  border: "none",
                  cursor: step === 0 ? "default" : "pointer",
                  background: step === 0 ? "#0f172a" : "#334155",
                  color: step === 0 ? "#475569" : "#e2e8f0",
                  fontSize: 12,
                  fontFamily: "inherit",
                }}
              >
                ← Prev
              </button>
              <button
                onClick={() => setStep(Math.min(steps.length - 1, step + 1))}
                disabled={step === steps.length - 1}
                style={{
                  padding: "4px 12px",
                  borderRadius: 6,
                  border: "none",
                  cursor: step === steps.length - 1 ? "default" : "pointer",
                  background: step === steps.length - 1 ? "#0f172a" : "#3b82f6",
                  color: step === steps.length - 1 ? "#475569" : "white",
                  fontSize: 12,
                  fontFamily: "inherit",
                }}
              >
                Next →
              </button>
            </div>
          </div>
          <p style={{ margin: 0, fontSize: 13, color: "#cbd5e1", lineHeight: 1.6 }}>
            {cur.desc}
          </p>
        </div>

        {/* Data tables */}
        <div
          style={{
            background: "#1e293b",
            borderRadius: 12,
            padding: 16,
          }}
        >
          {algo === "dijkstra" ? (
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: 13,
              }}
            >
              <thead>
                <tr>
                  <th style={{ padding: "6px 10px", textAlign: "left", borderBottom: "1px solid #334155", color: "#64748b" }}>
                    Node
                  </th>
                  <th style={{ padding: "6px 10px", textAlign: "center", borderBottom: "1px solid #334155", color: "#64748b" }}>
                    Distance
                  </th>
                  <th style={{ padding: "6px 10px", textAlign: "center", borderBottom: "1px solid #334155", color: "#64748b" }}>
                    Previous
                  </th>
                  <th style={{ padding: "6px 10px", textAlign: "center", borderBottom: "1px solid #334155", color: "#64748b" }}>
                    Visited
                  </th>
                </tr>
              </thead>
              <tbody>
                {GRAPH.nodes.map((n) => (
                  <tr key={n}>
                    <td style={{ padding: "5px 10px", fontWeight: 700 }}>{n}</td>
                    <td
                      style={{
                        padding: "5px 10px",
                        textAlign: "center",
                        color: cur.dist[n] === Infinity ? "#475569" : "#34d399",
                      }}
                    >
                      {cur.dist[n] === Infinity ? "∞" : cur.dist[n]}
                    </td>
                    <td style={{ padding: "5px 10px", textAlign: "center", color: "#94a3b8" }}>
                      {cur.prev[n] || "—"}
                    </td>
                    <td style={{ padding: "5px 10px", textAlign: "center" }}>
                      {cur.visited.has(n) ? "✓" : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <DVTable
              tables={cur.tables}
              nodes={GRAPH.nodes}
              updates={cur.updates}
            />
          )}
        </div>

        <p style={{ color: "#475569", fontSize: 11, textAlign: "center", marginTop: 16 }}>
          EC 441 · Routing Algorithms · Mathis Souef-Myers · Spring 2026
        </p>
      </div>
    </div>
  );
}
