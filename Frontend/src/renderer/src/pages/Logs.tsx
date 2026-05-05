import { useState, useEffect, useContext } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"

import { ConnectionContext } from "@renderer/contexts/ConnectionHandler"

export default function Logs() {
	type logType = {
		timestamp: number,
		timestamp_converted: string,
		count: number
	}

	const { getPath } = useContext(ConnectionContext);

	const [searchParams] = useSearchParams()
	const navigate = useNavigate();

	const providedIndexString = searchParams.get("index")
	const providedIndexTemp = Number(providedIndexString ?? "0")
	const providedIndex = !Number.isNaN(providedIndexTemp) ? providedIndexTemp : 0

	const [logs, setLogs] = useState<logType[]>([])
	const [totalLogs, setTotalLogs] = useState<number>(0);
	const [moreLogsAvailable, setMoreLogsAvailable] = useState<boolean>(false);
	const [requested, setRequested] = useState<boolean>(false);


	const loadLogs = async function() {
		const tempQueryParams = providedIndex ? "?id=" + String(providedIndex) : "";
		
		const response = await fetch(getPath("/api/logs-get" + tempQueryParams))

		if (!response.ok) { return; }

		const responseJson = await response.json();
		if (!responseJson) { return; }

		setTotalLogs(responseJson.data.total_logs);
		setMoreLogsAvailable(responseJson.data.more_available);

		const logsDataTemp = responseJson.data.logs ?? [];

		const newLogs: logType[] = logsDataTemp.map(element => {
			const elementDate = new Date(element.timestamp * 1000);

			return {
				timestamp: element.timestamp,
				timestamp_converted: elementDate.toLocaleDateString("en-GB", {
					day: "numeric",
					month: "long",
					year: "numeric"
				}),
				count: element.count
			};
		});
		setLogs(newLogs);
	}

	const pageMove = async function(forward: boolean) {
		if (forward === true){
			navigate("/logs?index=" + String(providedIndex + 10))
		} else {
			navigate("/logs?index=" + String(Math.max(providedIndex - 10, 0)))
		}
	}

	const main = async function() {
		await loadLogs();
		setRequested(true);
	}

	useEffect(() => {
		main();
	},[providedIndex]);

	if (!requested) {
		return;
	}

	return (
		<div className="centre-page-container space-y-3">
			<h1 className={"text-xl text-center w-full " + (logs.length === 0 ? "visible" : "hidden")}>No logs found</h1>
			<h1 className={"text-sm text-right w-full text-gray-400 " + (logs.length > 0 ? "visible" : "hidden")}>{"Showing " + (providedIndex == 0 ? "1" : providedIndex) + "-" + (providedIndex + logs.length) + " out of " + (totalLogs ?? "?") + " logs"}</h1>

			{logs.map(element => (
				<div key={element.timestamp} className="button-entry-style clickable p-4 h-12 clickable" onClick={() => navigate("/logs/" + String(element.timestamp))}>
					<div className="h-full flex items-center justify-between">
						<h1 className="text-xl">{element.timestamp_converted}</h1>
						<h1>{(element.count ?? "?") + " data entries"}</h1>
					</div>
				</div>
			))}

			<div className="flex space-x-6 justify-center mt-6">
				<div className={"clickable w-16 menu-button-container " + (providedIndex <= 0 ? "hidden" : "")} onClick={() => pageMove(false)}>
					<h1 className="text-xl text-center">&lt;</h1>
				</div>
				<div className={"clickable w-16 menu-button-container " + (totalLogs > providedIndex + 10 ? "" : "hidden")} onClick={() => pageMove(true)}>
					<h1 className="text-xl text-center">&gt;</h1>
				</div>
			</div>
		</div>
	)
}