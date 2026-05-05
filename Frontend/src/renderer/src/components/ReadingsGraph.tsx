import { useContext, useEffect, useState, useMemo } from "react";
import { Line } from "react-chartjs-2";

import { ConnectionContext } from "@renderer/contexts/ConnectionHandler"

import type { NodeData } from "@renderer/Types";

import "chartjs-adapter-date-fns"
import AnnotationPlugin from "chartjs-plugin-annotation"

import {
	Chart as ChartJS,
    TimeScale,
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
    ChartOptions,
	Title,
	Tooltip,
	Legend,
    Decimation
} from 'chart.js';

ChartJS.register(
    TimeScale,
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Title,
	Tooltip,
	Legend,
    AnnotationPlugin,
    Decimation
);

const defaultOptions: ChartOptions<"line"> = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    parsing: false,
    plugins: {
        legend: {
            display: false
        },
        decimation: {
            enabled: true,
            algorithm: "lttb",
            samples: 50,
            threshold: 51,
        }
    },
    interaction: {
        mode: "index",
        intersect: false,
    },
    elements: {
        point: {
            radius: 0
        }
    },
    scales: {
        x: {
            type: "time",
            time: {
                unit: "minute"
            },
        },
        y: {
            title: {
                display: true,
                text: "Temperature"
            },
            suggestedMin: 0,
            suggestedMax: 40,
        },
        y1: {
            title: {
                display: true,
                text: "Humidity"
            },
            position: "right",
            min: 0,
            max: 100,
            grid: { 
                display: false
            }
        },
    }
}

type ReadingsType = {
    x: number
    y: number
    node_hwid: string
}

type DatasetType = {
    label: string
    yAxisID: string
    borderColor: string
    borderWidth: number
    tension: number
    data: ReadingsType[]
    hidden: boolean
    node_hwid: string
}

export type ChartDataType = {
    datasets: DatasetType[]
}

const chartDataDefault: ChartDataType = {
    datasets: [] // changed a lot, maybe remove later
};

type thresholdType = {
    id: number,
    name: string,
    threshold_type: string
    value: number,
    triggered: number,
    last_trigger: number,
    enabled: number
}

type ReadingsGraphProps = {
    source?: string,
    parameters?: {},
    duration?: number,
    node_hwid?: string;
    showThresholds?: boolean,
    autoScale?: boolean,
    autoUpdate?: boolean,
    startTimestamp?: number,
    onCalculated?: (data: ChartDataType) => void | undefined
    nodeHideList?: NodeData[]
}

export default function ReadingsGraph({duration = 1, node_hwid = undefined, showThresholds = true, autoScale = false, autoUpdate = false, startTimestamp = undefined, onCalculated = undefined, nodeHideList = []}: ReadingsGraphProps) {
    const { getPath } = useContext(ConnectionContext)

    const [options, setOptions] = useState<ChartOptions<"line">>(defaultOptions);
    const [collectedData, setCollectedData] = useState<any>(chartDataDefault) // find better type than any
    //const [shownData, setShownData] = useState(collectedData)
    const [noReadings, setNoReadings] = useState<boolean>(true);
    //const [autoScaleState, setAutoScale] = useState<boolean>(autoScale);
    const [autoUpdateState, setAutoUpdate] = useState<boolean>(autoUpdate); // unused

    useEffect(() => {
        const newDuration = duration * 60 * 60 * 1000;
        const currentTime = Date.now();
        setOptions(prev => ({
            ...prev,
            scales: {
                ...prev.scales,
                x: {
                    ...prev.scales?.x,
                    min: autoScale ? (startTimestamp !== undefined ? startTimestamp * 1000 : currentTime - newDuration) : undefined, // duration is mins
                    max: autoScale ? (startTimestamp !== undefined ? startTimestamp * 1000 + newDuration : currentTime) : undefined
                }
            }
        }));
    },[autoScale, duration, startTimestamp])

    const enableAnimation = async function(state: boolean) {
        setOptions(prev => ({ // enables animations after load
            ...prev,
            animation: state ? undefined : false, // undefined uses default
        }))
    }

    const update = async function() {
        const getReadings = async function() {
            const params = new URLSearchParams()
            params.set("duration", String(duration))

            if (startTimestamp !== undefined) {
                params.set("starts_from", String(startTimestamp))
            }

            if (node_hwid != undefined) {
                params.set("node_hwid", String(node_hwid))
            }

            const response = await fetch(getPath("/api/readings-get/?" + params.toString()))
            if (!response.ok) { return false; }
            

            const responseJson = await response.json()
            if (!responseJson) { return false; }

            let tempNodeList: NodeData[] = []
            const nodeResponse = await fetch(getPath("/api/nodes-get"))
            if (nodeResponse.ok) {
                const nodeResponseJson = await nodeResponse.json()
                if (nodeResponseJson) {
                    nodeResponseJson.data.forEach(entry => {
                        tempNodeList.push(entry);
                    });
                }
            }

            // clean
            setCollectedData(chartDataDefault)
            setOptions(defaultOptions)

            const tempCollectedData: ChartDataType = { datasets: [] }

            // update readings
            responseJson.data.forEach(entry => {

                //if (nodeHideList.some(hide => hide.hwid === entry.hwid)) { return; } // update later
                
                try {
                    //const newTime = new Date(entry.timestamp).valueOf() * 1000
                    const newTemp: ReadingsType = { x: entry.timestamp * 1000, y: entry.temp, node_hwid: entry.node_hwid}
                    const newHum: ReadingsType = { x: entry.timestamp * 1000, y: entry.hum, node_hwid: entry.node_hwid} 

                    const foundTempDataset = tempCollectedData.datasets.find(dataset => dataset.node_hwid === entry.node_hwid && dataset.yAxisID === "y")
                    const foundHumDataset = tempCollectedData.datasets.find(dataset => dataset.node_hwid === entry.node_hwid && dataset.yAxisID === "y1")
                    
                    if (foundTempDataset !== undefined && foundHumDataset !== undefined) {
                        foundTempDataset.data.push(newTemp)
                        foundHumDataset.data.push(newHum)
                        return; // should act as continue
                    }

                    const foundNodeInfo: NodeData | undefined = tempNodeList.find(compare => compare.hwid == entry.node_hwid)
                    const nodeName = foundNodeInfo !== undefined ? foundNodeInfo.name : entry.node_hwid

                    // make new entry
                    const newTempDataset: DatasetType = {
                        label: nodeName + " temperature",
                        yAxisID: "y",
                        borderColor: "rgba(255, 92, 77, 1.0)",
                        borderWidth: 2,
                        tension: 0.2,
                        data: [newTemp],
                        hidden: false,
                        node_hwid: entry.node_hwid
                    }

                    const newHumDataset: DatasetType = {
                        label: nodeName + " humidity",
                        yAxisID: "y1",
                        borderColor: "rgba(77, 198, 255, 1.0)",
                        borderWidth: 2,
                        tension: 0.2,
                        data: [newHum],
                        hidden: false,
                        node_hwid: entry.node_hwid
                    }

                    tempCollectedData.datasets.push(newTempDataset, newHumDataset)
                } catch {
                    console.log("Error when parsing readings.")
                    return;
                }
            });

            setCollectedData(tempCollectedData)
            return true;
        }

        const getThresholds = async function() {
            const response = await fetch(getPath("/api/thresholds-get-all"))
            if (!response.ok) { return; }

            const responseJson = await response.json()
            const thresholds: thresholdType[] = [...responseJson.data];

            thresholds.forEach(entry => {
                setOptions(prev => ({
                    ...prev,
                    plugins: {
                        ...prev.plugins,
                        annotation: {
                            ...prev.plugins?.annotation,
                            annotations: {
                                ...prev.plugins?.annotation?.annotations,
                                [entry.id]: {
                                    yMin: entry.value, 
                                    yMax: entry.value,
                                    borderColor: entry.enabled === 1 ? (entry.threshold_type === "greater_than" ? "#ff0000" : "#0000ff") : "rgba(0.0, 0.0, 0.0, 0.3)",
                                    borderWidth: 0.5,
                                    borderDash: [5,5]
                                }
                            }
                        }
                    }
                }))
            });

        }

        await getReadings();
        if (showThresholds) {
            await getThresholds();
        }

        enableAnimation(true)
    }

    useEffect(() => {
        update();
    },[duration, node_hwid, showThresholds])

    useEffect(() => {
        if (onCalculated !== undefined) {
            //console.log(collectedData)
            onCalculated(collectedData);
        }
    },[collectedData])

    const shownData = useMemo(() => ({
        ...collectedData,
        datasets: collectedData.datasets.map(dataset => ({
            ...dataset,
            hidden: nodeHideList.some(node => node.hwid !== dataset.node_hwid)
        }))
    }), [collectedData, nodeHideList])
            
    return (
        <Line data={shownData} options={options} />
    )
}