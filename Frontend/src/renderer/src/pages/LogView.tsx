import { useState, useContext } from "react"
import { useNavigate, useParams, Navigate } from "react-router-dom"

import { mkConfig, generateCsv, download } from "export-to-csv"

import { ConnectionContext } from "@renderer/contexts/ConnectionHandler";
import { PopupContext } from "@renderer/contexts/PopupHandler";
import { ToastContext } from "@renderer/contexts/ToastHandler";

import ReadingsGraph, { ChartDataType } from "@renderer/components/ReadingsGraph"
import { timestampToDateString } from "@renderer/components/Utils";

import type { NodeData } from "@renderer/Types";


type Stats = {
    entries: number,
    average: number,
    minimum: number,
    maximum: number
}

const defaultStats: Stats = {
    entries: 0,
    average: 0,
    minimum: 0,
    maximum: 0
}

const csvConfig = mkConfig({useKeysAsHeaders: true})

export default function LogView() {
    const params = useParams();
    const navigate = useNavigate();

    const { getPath } = useContext(ConnectionContext)
    const { showPopup } = useContext(PopupContext);
    const { showToast } = useContext(ToastContext)

    const [logDate, setLogDate] = useState<string>("Unknown date");
    const [foundNodes, setFoundNodes] = useState<NodeData[]>([]);
    const [nodeHideList, setNodeHideList] = useState<NodeData[]>([]);

    // data
    const [lastData, setLastData] = useState<ChartDataType | undefined>(undefined);

    // readings
    const [totalReadings, setTotalReadings] = useState<number>(0);
    const [totalDatasets, setTotalDatasets] = useState<number>(0);
    const [scanFreq, setScanFreq] = useState<number>(0);

    // statistics
    const [tempReadings, setTempReadings] = useState<Stats>(defaultStats);
    const [humReadings, setHumReadings] = useState<Stats>(defaultStats);

    const providedId = Number(params.id)
	const selectedId = !Number.isNaN(Number(providedId)) && providedId !== 0 ? Number(providedId * 1000) : undefined

    if (selectedId === undefined) {
        showToast("Log not found")
        return <Navigate to="/logs" replace/>
    }

    const selectedDate = timestampToDateString(selectedId)
    //const previousDate = timestampToDateString(selectedId, 60 * 60 * 24)

    const deleteLog = async function() {
        const response = await fetch(getPath("/api/logs-delete?log_id=" + params.id), {
            method: "DELETE"
        })
        if (response.ok) {
            navigate("/logs")
        }
    }

    const downloadLog = async function() {
        const params = new URLSearchParams()

        params.set("duration", String(24))
        params.set("starts-from", String(providedId))

        const response = await fetch(getPath("/api/readings-get/?" + params))
        if (!response.ok) { return; }

        const responseJson = await response.json()

        download(csvConfig)(generateCsv(csvConfig)(responseJson.data))
    }
    

    const updateStatistics = async function(data?: ChartDataType, newNodeHideList?: NodeData[]) {
        let newTemp: Stats = { ...defaultStats }
        let newHum: Stats = { ...defaultStats }
        let currentReadings: number = 0
        let currentDatasets: number = 0

        const tempNodeHideList = newNodeHideList ?? nodeHideList

        //console.log(data)

        if (data === undefined) {
            if (lastData === undefined) { return; }
            data = lastData
        }

        data.datasets.forEach(dataset => {
            if (!tempNodeHideList.some(entry => entry.hwid == dataset.node_hwid)) {
                currentDatasets += 1
                if (dataset.label.endsWith("temperature")) {
                    dataset.data.forEach(entry => {
                        if (entry.x === null || entry.y === null) { return; }

                        currentReadings += 1; // use temp to count
                        if (entry.y > newTemp.maximum || newTemp.entries == 0) {
                            newTemp.maximum = entry.y
                        }
                        if (entry.y < newTemp.minimum || newTemp.entries == 0) {
                            newTemp.minimum = entry.y
                        }
                        newTemp.entries += 1;
                        newTemp.average += entry.y
                    })
                }
                if (dataset.label.endsWith("humidity")) { // could combine later
                    dataset.data.forEach(entry => {
                        if (entry.x === null || entry.y === null) { return; }
                        if (entry.y > newHum.maximum || newHum.entries == 0) {
                            newHum.maximum = entry.y
                        }
                        if (entry.y < newHum.minimum || newHum.entries == 0) {
                            newHum.minimum = entry.y
                        }
                        newHum.entries += 1;
                        newHum.average += entry.y
                        console.log(newHum.average)
                    })
                }
            }
        });

        if (newTemp.entries > 0) {
            newTemp.average = newTemp.average / newTemp.entries
            newHum.average = newHum.average / newHum.entries // guaranteed to exist
        }

        setTempReadings(newTemp)
        setHumReadings(newHum)
        setTotalReadings(currentReadings)
        setTotalDatasets(currentDatasets)
    }

    const updateDataFromGraph = async function(data: ChartDataType) {
        const updateNodes = async function() {
            const activeNodesTemp: string[] = []
            data.datasets.forEach(dataset => {
                if (!activeNodesTemp.includes(dataset.node_hwid)) {
                    activeNodesTemp.push(dataset.node_hwid)
                }
            });

            const response = await fetch(getPath("/api/nodes-get"))
            if (response.ok) {
                const responseJson: {data: NodeData[]} = await response.json()
                const responseNodeData = responseJson.data;

                const activeNodes: NodeData[] = []
                responseNodeData.forEach(entry => {
                    if (activeNodesTemp.includes(entry.hwid)) {
                        activeNodes.push(entry)
                    }
                });
                setFoundNodes(activeNodes);
            }

            const freqResponse = await fetch(getPath("/api/readings-frequency"))
            if (freqResponse.ok) {
                const freqResponseJson = await freqResponse.json()
                setScanFreq(Number(freqResponseJson.data))
            }
        }

        //console.log("data update")
        updateNodes()
        updateStatistics(data)
        setLastData(data)
    }

    const dataFound = function (data: ChartDataType) { // runs once graph returns data
        const copy = structuredClone(data)
        updateDataFromGraph(copy)
    }

    const hideNode = function(node: NodeData, state: boolean) {
        setNodeHideList(prev => {
            const newList = !state ? [...prev, node] : prev.filter(entry => entry.hwid !== node.hwid)

            updateStatistics(undefined, newList)
            return newList
        })
    }


    const [autoScale, setAutoScale] = useState(false);
	const temporary = function() {
		setAutoScale(!autoScale)
	}

    return (
        <div className="centre-page-container flex flex-col space-y-3">
            <div className="button-entry-style w-full h-76 p-4 flex flex-col space-y-2">
                <h1 className="text-center">{selectedDate}</h1>
                <div className="h-full" onClick={temporary}>
                    <ReadingsGraph onCalculated={dataFound} nodeHideList={nodeHideList} autoScale={autoScale} duration={24} startTimestamp={providedId}/>
                </div>
            </div>
            <div className="flex space-x-3 h-56 justify-between *:flex-1 *:p-2">
                <div className="button-entry-style flex flex-col space-y-1">
                    <h1 className="text-center">Readings</h1>
                    <span className="h-px m-2 mt-0 bg-gray-100"></span>
                    <div className="flex flex-col justify-center p-2">
                        <div className="flex justify-between">
                            <h1>Total readings:</h1>
                            <h1 className="font-bold">{totalReadings}</h1>
                        </div>
                        <div className="flex justify-between">
                            <h1>Total datasets:</h1>
                            <h1 className="font-bold">{totalDatasets}</h1>
                        </div>
                        <div className="flex justify-between">
                            <h1>Scan frequency:</h1>
                            <h1 className="font-bold">{scanFreq + " min" + (scanFreq > 1 ? "s" : "")}</h1>
                        </div>
                    </div>
                </div>

                <div className="button-entry-style flex flex-col space-y-1">
                    <h1 className="text-center">Statistics</h1>
                    <span className="h-px m-2 mt-0 bg-gray-100"></span>
                    <div className="flex flex-col justify-center p-2 grow">
                        <div className="flex justify-between">
                            <h1>Average temp:</h1>
                            <h1 className="font-bold">{tempReadings.average.toFixed(2) + "°C"}</h1>
                        </div>
                        <div className="flex justify-between">
                            <h1>Min temp:</h1>
                            <h1 className="font-bold">{tempReadings.minimum.toFixed(2) + "°C"}</h1>
                        </div>
                        <div className="flex justify-between">
                            <h1>Max temp:</h1>
                            <h1 className="font-bold">{tempReadings.maximum.toFixed(2) + "°C"}</h1>
                        </div>
                        <span className="h-px m-1"></span>
                        <div className="flex justify-between">
                            <h1>Average hum:</h1>
                            <h1 className="font-bold">{humReadings.average.toFixed(2) + "%"}</h1>
                        </div>
                        <div className="flex justify-between">
                            <h1>Min hum:</h1>
                            <h1 className="font-bold">{humReadings.minimum.toFixed(2) + "%"}</h1>
                        </div>
                        <div className="flex justify-between">
                            <h1>Max hum:</h1>
                            <h1 className="font-bold">{humReadings.maximum.toFixed(2) + "%"}</h1>
                        </div>
                    </div>
                </div>

                <div className="button-entry-style flex flex-col space-y-1 overflow-y-auto max-w-42">
                    <h1 className="text-center">Active nodes</h1>
                    <span className="h-px m-2 mt-0 bg-gray-100"></span>
                    <div className="space-y-2">
                        {foundNodes.map(element => (
                            <LogViewNodeButton key={element.hwid} element={element} onChanged={(state) => hideNode(element, state)} />
                        ))}
                    </div>
                </div>
                <div className="button-entry-style flex flex-col max-w-32 space-y-1">
                    <h1 className="text-center">Options</h1>
                    <span className="h-px m-2 mt-0 bg-gray-100"></span>
                    <div className="flex flex-col space-y-2 justify-center h-full">
                        <div className="button-entry-style rounded-lg h-8 flex flex-col justify-center *:leading-none *:text-center *:p-1 opacity-30">
                            <h1>Reset view</h1>
                        </div>
                        <div className="button-entry-style rounded-lg clickable h-8 flex flex-col justify-center *:leading-none *:text-center *:p-1" onClick={() => showPopup("Are you sure you want to download this log?", () => downloadLog)}>
                            <h1>Export</h1>
                        </div>
                        <div className="button-entry-style rounded-lg clickable h-8 flex flex-col justify-center *:leading-none *:text-center *:p-1" onClick={() => showPopup("Are you sure you want to delete this log? Log may be recreated with new data if it is from today.", () => deleteLog)}>
                            <h1 className="text-(--colour-red)">Delete</h1>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function LogViewNodeButton({element, onChanged} : {element: NodeData, onChanged?: (active: boolean) => void}) {

    const [active, setActive] = useState(true)

    const toggle = function() {
        setActive(prev => !prev)
        if (onChanged !== undefined) {
            onChanged(!active) // remember stale
        }
    }

    return (
        <div className="relative">
            <div className="button-entry-style rounded-lg clickable h-8 px-3 transition-colors default-duration" key={element.hwid} onClick={toggle}>
                <h1 className="leading-none mt-px text-md">{element.name}</h1>
            </div>
            <div className={"absolute bg-black/10 outline-gray-300 outline-2 inset-0 rounded-lg pointer-events-none transition-opacity duration-(--duration-default) " + (active ? "opacity-0" : "opacity-100")}/>
        </div>
    )
}
