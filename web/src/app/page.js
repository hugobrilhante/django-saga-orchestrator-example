"use client"
import {useEffect, useState} from "react";
import Image from 'next/image';
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

const defaultViewport = {x: 0, y: 0, zoom: 1.5};

const initialEdges = [];
for (let i = 1; i <= 3; i++) {
    const edge = {
        id: `e${i}-${i + 1}`,
        source: `${i}`,
        target: `${i + 1}`,
        type: "step",
        animated: true,
        markerEnd: {
            type: MarkerType.Arrow,
        },
        style: {
            strokeWidth: 2,
        },
    };
    initialEdges.push(edge);
}



export default function Home() {
    const [nodes, setNodes] = useNodesState([]);
    const [edges] = useEdgesState(initialEdges);
    const [price, setPrice] = useState(2600)
    const [quantity, setQuantity] = useState(1)
    const [transactionId, setTransactionID] = useState("")
    const [logs, setLogs] = useState({'stock': '', 'payment': ''})

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/order/api/v1/transactions/${transactionId}`);
                setNodes(response.data['nodes'])
                if (response.data['logs']) {
                    setLogs({...logs, ...response.data['logs']})
                }
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        if (transactionId !== "") {
            const interval = setInterval(fetchData, 500);
            return () => clearInterval(interval);
        }

    }, [transactionId, setNodes, setLogs]);

    const createOrder = async () => {
        setLogs({'order': '', 'stock': '', 'payment': ''})
        try {
            const response = await axios.post('http://localhost:8000/order/api/v1/orders/', {
                "customer_id": 1,
                "items": [
                    {
                        "product": 1,
                        "quantity": quantity,
                        "price": price
                    }
                ]
            });
            console.log('Server Response:', response.data);
            console.log('Order created successfully!');
            setTransactionID(response.data["transaction_id"])
        } catch (error) {
            console.error('An error occurred while creating the order:', error);
        }
    };
    const handleQuantity = (event) => setQuantity(event.target.value);
    const handlePrice = (event) => setPrice(event.target.value);


    return (
        <main className="h-dvh">
            <PanelGroup direction="horizontal">
                <Panel defaultSize={5}>
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
                                fitView={true}
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
                                    </Stack>
                                </PanelFlow>
                            </ReactFlow>
                        </Panel>
                        <PanelResizeHandle className="h-0.5 bg-black"/>
                        <Panel defaultSize={30}>
                            <PanelGroup direction="horizontal">
                                <Panel defaultSize={50} className="pt-lg-2 p-lg-2">
                                    <h5>Transaction ID: {transactionId}</h5>
                                </Panel>
                                <PanelResizeHandle className="w-0.5 bg-black"/>
                                <Panel defaultSize={50} className="pt-lg-2 p-lg-2">
                                    <h5>Logs:</h5>
                                    <h5>Stock: <span className="text-sm  text-red-600">{logs.stock}</span></h5>
                                    <h5>Payment: <span className="text-sm  text-red-600">{logs.payment}</span></h5>
                                </Panel>
                            </PanelGroup>
                        </Panel>
                    </PanelGroup>
                </Panel>
                <PanelResizeHandle className="w-0.5 bg-black"/>
                <Panel defaultSize={25} className="flex justify-center items-center h-full">
                    <div className="-mt-2 p-2 lg:mt-0 lg:w-full lg:max-w-md lg:flex-shrink-0">
                        <div
                            className="rounded-2xl bg-gray-50 py-10 text-center ring-1 ring-inset ring-gray-900/5 lg:flex lg:flex-col lg:justify-center lg:py-16">
                            <h1 className="font-semibold text-gray-600">
                                Store
                            </h1>
                            <div className="mx-auto max-w-xs px-8">
                                <Image src={"/macbook.png"} alt="MacBook Pro" width={300} height={300}/>
                                <p className="text-base font-semibold text-gray-600">MacBook Pro 14</p>
                                <p className="mt-6 flex items-baseline justify-center gap-x-2">
                                    <span className="text-sm font-semibold leading-6 tracking-wide text-gray-600">
                                        QTY
                                    </span>
                                    <input onChange={handleQuantity}
                                           className="block w-full rounded-md px-3 py-2 text-center text-sm font-semibold text-black shadow-sm"
                                           value={quantity}
                                    />
                                </p>
                                <p className="mt-6 flex items-baseline justify-center gap-x-2">
                                    <span className="text-sm font-semibold leading-6 tracking-wide text-gray-600">
                                        USD
                                    </span>
                                    <input onChange={handlePrice}
                                           className="block w-full rounded-md  px-3 py-2 text-center text-sm font-semibold text-black shadow-sm"
                                           value={price}/>
                                </p>
                                <p className="mt-10 block w-full rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                                   onClick={createOrder}>
                                    Buy now
                                </p>
                                <p className="mt-6 text-xs leading-5 text-gray-600">
                                    Press buy now and watch the magic happen.
                                </p>
                                <p className="text-xs text-gray-600">
                                    {"For stock error: QTY > 100"}
                                </p>
                                <p className="-m-3 text-xs text-gray-600">
                                    {"For payment error: USD > 5000"}
                                </p>
                            </div>
                        </div>
                    </div>
                </Panel>
            </PanelGroup>
        </main>
    );
}
