import { useContext, useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom";

import { ConnectionContext } from "../contexts/ConnectionHandler";
import { RefreshContext } from "@renderer/contexts/RefreshHandler";

import ReadingsGraph, { ChartDataType } from "@renderer/components/ReadingsGraph"
import { ToastContext } from "@renderer/contexts/ToastHandler";

export default function Home() {
	const navigate  = useNavigate();
	const { getPath } = useContext(ConnectionContext)
	const { enableAutoRefresh } = useContext(RefreshContext)
	const { showToast } = useContext(ToastContext)

	// values
	const [currentTemp, setCurrentTemp] = useState<string | undefined>(undefined);
	const [average, setAverage] = useState<string | undefined>(undefined);
	const [activeThresholds, setActiveThresholds] = useState<number>(0);
	const [connectedNodes, setConnectedNodes] = useState<number>(0);
	const [autoScale, setAutoScale] = useState(false);
	const [error, setError] = useState<boolean>(false); // move to graph

	// graph
	//const lineChartRef = useRef<LineChartRef>(null)
	//const [graphRefreshKey, setGraphRefreshKey] = useState<number>(0);

	//const refreshGraph = function () {
	//	setGraphRefreshKey(prev => prev + 1);
	//}

	// other

	const update = function() {
		const getActiveThresholds = async function() {
			const response = await fetch(getPath("/api/thresholds-alert-count"))
			if (!response.ok) { return; }

			const data = await response.json()
			
			setActiveThresholds(data);
		}

		const getConnectedNodes = async function() {
			const response = await fetch(getPath("/api/nodes-get"))
			if (!response.ok) { return; }

			const responseJson = await response.json()
			const data = responseJson.data
			
			const connected = data.reduce((total, node) => total + (node.last_seen > Math.floor(new Date().getTime() / 1000) - 10 * 60 ? 1 : 0), 0);
			setConnectedNodes(connected);
		}

		const toRun = [getActiveThresholds, getConnectedNodes]

		setError(false);
		toRun.forEach(command => {
			try {
				command()
			} catch {
				setError(true)
			}
		});
	}

	const updateDataFromGraph = async function(data: ChartDataType) {
		const updateData = async function() {
			let averageTemp = 0;
			let validEntries = 0;
			/*let highest: number | undefined = undefined;
			let lowest: number | undefined = undefined;*/
			let latestTemp = 0;

			data.datasets.forEach(dataset => {
				dataset.data.forEach(entry => {
					if (entry.y !== null) {
						if (dataset.label.endsWith("temperature")) {
							validEntries += 1;
							averageTemp += entry.y;
							latestTemp = entry.y; // should be last
							/*if (highest === undefined || entry.y > highest) {
								highest = entry.y
							}
							if (lowest === undefined || entry.y < lowest) {
								lowest = entry.y
							}*/
						}
					}
				})
			});
			
			setAverage((validEntries > 0) ? (averageTemp / validEntries).toFixed(2) : undefined);
			setCurrentTemp((validEntries > 0) ? latestTemp.toFixed(2) : undefined);

			/*if (highest !== undefined && lowest !== undefined) {
				setMinMax([lowest, highest]);
			}*/

		}

		updateData()
	}

	const dataFound = function (data: ChartDataType) { // runs once graph returns data
		const copy = structuredClone(data)
		updateDataFromGraph(copy)
	}

	const goToLatestLog = function() {
		const main = async function() {
			const response = await fetch(getPath("/api/logs-get-latest-id"))
			const responseJson = await response.json()

			if (!response.ok) {
				showToast(responseJson.detail);
				return;
			}

			if (responseJson.data.timestamp === null) {
				navigate("/logs")
				return;
			}

			navigate("/logs/ " + responseJson.data.timestamp)
		}

		main()
	}

	useEffect(() => {
		enableAutoRefresh(true); // might use a callback later
		update();
	},[]);

	const temporary = function() {
		setAutoScale(!autoScale)
	}

	return (
		<div className="centre-page-container h-full space-y-3 overflow-hidden">
			<div className="flex justify-center button-entry-style" onClick={temporary}>
				<div className="w-full p-4 space-y-2">
					<h1 className="text-center text-xl">Past 24 hours</h1>
					<div className="mx-auto w-full max-w-[80vw] h-86">
						<ReadingsGraph onCalculated={dataFound} duration={24 * 60} autoScale={autoScale} showThresholds={true} />
					</div>
				</div>
			</div>
			<div className="flex justify-center space-x-3 *:h-28 *:text-center *:flex-1 mb-3">
				<div className="clickable button-entry-style flex-1 flex flex-col p-6" onClick={() => goToLatestLog()}>
					<div className="grow flex flex-col justify-center">
						<h1 className="text-2xl">{(currentTemp !== undefined) ? currentTemp + "°C" : "Unknown"}</h1>
					</div>
					<h1 className="justify-self-end text-md">Current temp</h1>
				</div>
				<div className="clickable button-entry-style flex-1 flex flex-col p-6" onClick={() => goToLatestLog()}>
					<div className="grow flex flex-col justify-center">
						<h1 className="text-2xl">{(average !== undefined ? average + "°C" : "Unknown")}</h1>
					</div>
					<h1 className="justify-self-end text-md">Average temp</h1>
				</div>
				<div className={"clickable button-entry-style flex-1 flex flex-col p-6 " + (activeThresholds > 0 ? "button-entry-style-error" : "")} onClick={() => navigate("/thresholds")}>
					<div className="grow flex flex-col justify-center">
						<h1 className="text-2xl">{activeThresholds}</h1>
					</div>
					<h1 className="justify-self-end text-md">Threshold alerts</h1>
				</div>
				<div className="clickable button-entry-style flex-1 flex flex-col p-6" onClick={() => navigate("/devices")}>
					<div className="grow flex flex-col justify-center">
						<h1 className="text-2xl">{connectedNodes}</h1>
					</div>
					<h1 className="justify-self-end text-md">Connected nodes</h1>
				</div>
			</div>
		</div>
	)
}
