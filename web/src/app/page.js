"use client"
import Image from 'next/image';
import {useEffect} from 'react';
import {Panel, PanelGroup, PanelResizeHandle} from "react-resizable-panels";
import ReactFlow, {
    Background,
    Controls,
    MarkerType,
    MiniMap,
    Panel as PanelFlow,
    useEdgesState,
    useNodesState
} from "reactflow";
import {Badge, Stack} from 'react-bootstrap';
import axios from 'axios';
import 'reactflow/dist/style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import "./page.css"

const defaultViewport = {x: 0, y: 0, zoom: 5};
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
const labels = ['Order', 'Stock', 'Payment'];
const initialNodes = [];
const initialEdges = [
    {
        id: 'e1-2',
        source: '1',
        target: '2',
        type: "step",
        animated: true,
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
        animated: true,
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
        animated: true,
        markerEnd: {
            type: MarkerType.Arrow,
        },
        style: {
            strokeWidth: 2,
        },

    }
];
for (let i = 0; i < labels.length; i++) {
    const nodeId = (i + 1).toString();
    const node = {
        id: nodeId,
        position: {x: 100 + i * 300, y: 75},
        data: {label: labels[i]},
        style: style,
        type: nodeId === '1' ? 'input' : nodeId === '3' ? 'output' : 'default',
        sourcePosition: 'right',
        targetPosition: 'left'
    };
    initialNodes.push(node);
}

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
        <main className="h-dvh">
            <PanelGroup direction="horizontal">
                <Panel defaultSize={3}>
                    <h1 className="mx-3 [writing-mode:vertical-lr] h-full text-5xl text-center">Microservices</h1>
                </Panel>
                <PanelResizeHandle className="w-0.5 bg-black"/>
                <Panel defaultSize={70}>
                    <PanelGroup direction="vertical">
                        <Panel defaultSize={70}>
                            <ReactFlow
                                nodes={nodes}
                                edges={edges}
                                defaultViewport={defaultViewport}
                            >
                                <MiniMap zoomable pannable/>
                                <Controls/>
                                <Background color="#aaa" gap={16}/>
                                <PanelFlow position="bottom-center">
                                    <Stack direction="horizontal" gap={2}>
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
                                </PanelFlow>
                            </ReactFlow>
                        </Panel>
                        <PanelResizeHandle className="h-0.5 bg-black"/>
                        <Panel defaultSize={30}>
                            <PanelGroup direction="horizontal">
                                <Panel defaultSize={50} className="pt-lg-2 p-lg-2">
                                    <h5>Transaction ID: 9062dc43-70dd-4d37-b9d7-ad4a4be09227</h5>
                                </Panel>
                                <PanelResizeHandle className="w-0.5 bg-black"/>
                                <Panel defaultSize={50} className="pt-lg-2 p-lg-2">
                                    <h5>Logs:</h5>
                                    <h5>Order: {"{ORDER_DENIED: True}"}</h5>
                                    <h5>Stock:</h5>
                                    <h5>Payment:</h5>
                                </Panel>
                            </PanelGroup>
                        </Panel>
                    </PanelGroup>
                </Panel>
                <PanelResizeHandle className="w-0.5 bg-black"/>
                <Panel defaultSize={27} className="flex justify-center items-center h-full">
                    <div className="-mt-2 p-2 lg:mt-0 lg:w-full lg:max-w-md lg:flex-shrink-0">
                        <div
                            className="rounded-2xl bg-gray-50 py-10 text-center ring-1 ring-inset ring-gray-900/5 lg:flex lg:flex-col lg:justify-center lg:py-16">
                            <h1 className="font-semibold text-gray-600">Store</h1>
                            <div className="mx-auto max-w-xs px-8">
                                <Image src={"/macbook.png"} alt="MacBook Pro" width={300} height={300}/>
                                <p className="text-base font-semibold text-gray-600">MacBook Pro 14</p>
                                <p className="mt-6 flex items-baseline justify-center gap-x-2">
                                    <span
                                        className="text-sm font-semibold leading-6 tracking-wide text-gray-600">QTD</span>
                                    <input
                                        className="block w-full rounded-md  px-3 py-2 text-center text-sm font-semibold text-black shadow-sm"
                                        value={1}/>
                                </p>
                                <p className="mt-6 flex items-baseline justify-center gap-x-2">
                                    <span
                                        className="text-sm font-semibold leading-6 tracking-wide text-gray-600">USD</span>
                                    <input
                                        className="block w-full rounded-md  px-3 py-2 text-center text-sm font-semibold text-black shadow-sm"
                                        value={2600}/>
                                </p>
                                <p className="mt-10 block w-full rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                                >
                                    Buy now
                                </p>
                                <p className="mt-6 text-xs leading-5 text-gray-600">
                                    Press buy and watch the magic happen
                                </p>
                            </div>
                        </div>
                    </div>
                </Panel>
            </PanelGroup>
        </main>
    );
}
