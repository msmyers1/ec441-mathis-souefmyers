# Routing Algorithms Visualization — EC 441

This is an interactive step through of **Dijkstra (Link State)** and **Distance Vector** on a 5-node network.

## How to Use

This is a React component (`.jsx`). If you want to run it locally:

1. Drop `routing_algorithms_viz.jsx` into any React project (Vite, Next.js, Create React App, etc.)
2. Make sure you have React 18+ installed
3. Import and render the default export:

```jsx
import RoutingViz from "./routing_algorithms_viz";

function App() {
  return <RoutingViz />;
}
```

## What's Inside

- **Dijkstra (Link State):** Pick any source node (A–E) and step through the algorithm. Watch the shortest-path tree build as nodes get visited. The table tracks distance, previous node, and visited status at each step.
- **Distance Vector:** Step through rounds of DV exchange. Each node's full distance table is shown, with updated entries highlighted in amber.

## Network Topology

```
    A ---2--- B ---3--- D
    |         |         |
    5         1         2
    |         |         |
    C --------+----4--- E
       C--D cost 1
```

Nodes: A, B, C, D, E  
Edges: A–B(2), A–C(5), B–C(1), B–D(3), C–D(1), C–E(4), D–E(2)
