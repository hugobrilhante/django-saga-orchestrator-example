"use client"
import React, {useEffect} from 'react';
import {Panel, PanelGroup, PanelResizeHandle} from "react-resizable-panels";
import ReactFlow, {MarkerType, useEdgesState, useNodesState} from "reactflow";
import {Badge, Stack} from 'react-bootstrap';
import 'reactflow/dist/style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import "./page.css"
import axios from 'axios';

const style = {
    borderRadius: "50%",
    width: "100px",
    height: "100px",
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: "100%",
    fontWeight: 700,
    background: "#b1b1b1",
    color: "white",
}

const initialNodes = [
    {
        id: '1',
        position: {x: 600, y: 300},
        data: {label: 'Order'},
        style: {...style, background: "#b1b1b1"},
        type: 'input',
        sourcePosition: 'right'
    },
    {
        id: '2',
        position: {x: 1000, y: 300},
        data: {label: 'Stock'},
        style: {...style, background: "#b1b1b1"},
        sourcePosition: 'right',
        targetPosition: 'left'
    },
    {
        id: '3',
        position: {x: 1400, y: 300},
        data: {label: 'Payment'},
        style: {...style, background: "#b1b1b1"},
        sourcePosition: 'right',
        targetPosition: 'left'
    },
    {
        id: '4',
        position: {x: 1800, y: 300},
        data: {label: 'Delivery'},
        style: {...style, background: "#b1b1b1"},
        type: 'output',
        sourcePosition: 'right',
        targetPosition: 'left'
    },
];
const initialEdges = [
    {
        id: 'e1-2',
        source: '1',
        target: '2',
        type: "step",
        markerEnd: {
            type: MarkerType.Arrow,
        },
        style: {
            strokeWidth: 2,
        },
    },
    {
        id: 'e2-3',
        source: '2',
        target: '3',
        type: "step",
        markerEnd: {
            type: MarkerType.Arrow,
        },
        style: {
            strokeWidth: 2,
        },

    },
    {
        id: 'e3-4',
        source: '3',
        target: '4',
        type: "step",
        markerEnd: {
            type: MarkerType.Arrow,
        },
        style: {
            strokeWidth: 2,
        },

    }
];

export default function Home() {
    const [nodes, setNodes] = useNodesState(initialNodes);
    const [edges] = useEdgesState(initialEdges);
    // useEffect(() => {
    //     const fetchData = async () => {
    //         try {
    //             const response = await axios.get("http://localhost:3001/nodes");
    //             setNodes(response.data)
    //         } catch (error) {
    //             console.error('Error fetching data:', error);
    //         }
    //     };
    //
    //     const interval = setInterval(fetchData, 1000);
    //
    //     return () => clearInterval(interval);
    // }, []);
    //
    useEffect(() => {
        const fetchData = async (id) => {
            try {
                const response = await axios.get(`http://localhost:3001/nodes/${id}`);
                setNodes(response.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };

        let currentId = 1;
        const interval = setInterval(() => {
            fetchData(currentId);
            currentId = currentId % 3 + 1;
        }, 1000);

        return () => clearInterval(interval);
    }, []);


    return (
        <PanelGroup direction="horizontal">
            <Panel className={"microservice"} defaultSize={3}>
                <h1>Microservices</h1>
            </Panel>
            <PanelResizeHandle/>
            <Panel defaultSize={100}>
                <PanelGroup direction="vertical">
                    <Panel className={"services"} defaultSize={70}>
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                        >
                            <Stack className={"stack"} direction="horizontal" gap={2}>
                                <h4>
                                    <Badge bg="secondary" text="dark">Waiting</Badge>
                                </h4>
                                <h4>
                                    <Badge bg="success" text="dark">Success</Badge>
                                </h4>
                                <h4>
                                    <Badge bg="danger" text="dark">Failed</Badge>
                                </h4>
                                <h4>
                                    <Badge bg="warning" text="dark"> RollBack </Badge>
                                </h4>
                                <h4>
                                    <Badge bg="light" text="dark"> Canceled </Badge>
                                </h4>
                            </Stack>
                        </ReactFlow>
                    </Panel>
                    <PanelResizeHandle/>
                    <Panel defaultSize={30}>
                        <PanelGroup direction="horizontal">
                            <Panel className={"transactions"} defaultSize={30}>
                                <h5>Transaction ID: 9062dc43-70dd-4d37-b9d7-ad4a4be09227</h5>
                            </Panel>
                            <PanelResizeHandle/>
                            <Panel className={"logs"} defaultSize={30}>
                                <h5>Logs:</h5>
                                <h5>Order: {"{ORDER_DENIED: True}"}</h5>
                                <h5>Stock:</h5>
                                <h5>Payment:</h5>
                                <h5>Delivery:</h5>
                            </Panel>
                            <PanelResizeHandle/>
                        </PanelGroup>
                    </Panel>
                </PanelGroup>
            </Panel>
        </PanelGroup>);
}
