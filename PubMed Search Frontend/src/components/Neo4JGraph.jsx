import React, { useEffect, useState } from 'react';
import Graph from 'react-graph-vis';
import neo4j from 'neo4j-driver';
import { Container } from "react-bootstrap";

const Neo4JGraph = () => {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);

  const uri = import.meta.env.VITE_NEO4J_URI;
  const user = import.meta.env.VITE_NEO4J_USER;
  const password = import.meta.env.VITE_NEO4J_PASSWORD;
  const query = import.meta.env.VITE_NEO4J_QUERY;

  useEffect(() => {
    if (!uri || !user || !password || !query) {
      console.error("Missing environment variables for Neo4j connection.");
      return;
    }

    const fetchData = async () => {
      const driver = neo4j.driver(uri, neo4j.auth.basic(user, password));
      const session = driver.session();

      try {
        const result = await session.run(query);

        const nodes = [];
        const edges = [];
        const nodeIds = new Set();  // Track added nodes
        const edgeIds = new Set();  // Track added edges

        result.records.forEach(record => {
          record.keys.forEach(key => {
            const value = record.get(key);
            console.log(value);
            if (value instanceof neo4j.types.Node) {
              const nodeId = value.identity.toString();

              // Skip if node already added
              if (!nodeIds.has(nodeId)) {
                nodeIds.add(nodeId);
                nodes.push({
                  id: nodeId,
                  label: value.labels.join(', '),
                  title: JSON.stringify(value.properties),
                });
              }
            } else if (value instanceof neo4j.types.Relationship) {
              const edgeId = `${value.start.toString()}-${value.end.toString()}-${value.type}`;

              // Skip if edge already added
              if (!edgeIds.has(edgeId)) {
                edgeIds.add(edgeId);
                edges.push({
                  from: value.start.toString(),
                  to: value.end.toString(),
                  label: value.type,
                  title: JSON.stringify(value.properties),
                });
              }
            }
          });
        });

        setGraphData(prevData => {
          // Only update if the data has actually changed
          const newNodes = nodes.length !== prevData.nodes.length || nodes.some(node => !prevData.nodes.find(n => n.id === node.id));
          const newEdges = edges.length !== prevData.edges.length || edges.some(edge => !prevData.edges.find(e => e.from === edge.from && e.to === edge.to));

          if (newNodes || newEdges) {
            return { nodes, edges };
          }
          return prevData;
        });
      } catch (error) {
        console.error('Error fetching data from Neo4j:', error);
      } finally {
        await session.close();
        await driver.close();
        setLoading(false);
      }
    };

    fetchData();
  }, [uri, user, password, query]);

  if (loading) return <div>Loading graph data...</div>;

  const graphOptions = {
    layout: { hierarchical: false },
    nodes: { shape: 'dot', size: 25 },
    edges: { color: '#000', arrows: { to: { enabled: true, scaleFactor: 0.5 } } },
    physics: { enabled: true },
    interaction: { dragNodes: true },
  };

  return (
      <Container style={{ height: '80vh', width: '100%' }}>
        <Graph
            graph={graphData}
            options={graphOptions}
            style={{ height: '100%', width: '100%' }}  // Ensures the graph takes full space
            events={{
              select: ({ nodes, edges }) => {
                console.log('Selected nodes:', nodes);
                console.log('Selected edges:', edges);
              },
            }}
        />
      </Container>
  );
};

export default Neo4JGraph;
