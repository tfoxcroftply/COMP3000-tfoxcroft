import { useEffect, useState, useContext } from "react"
import { useNavigate } from "react-router-dom"

import { ConnectionContext } from "../contexts/ConnectionHandler"
import { ToastContext } from "@renderer/contexts/ToastHandler"
import type { NodeData } from "@renderer/Types"

import DevicePair from "../components/DevicePair"

import nodeIcon from "../assets/icons/router_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"


export default function Devices() {
	const navigate = useNavigate();
	const { getPath } = useContext(ConnectionContext)
	const { showToast } = useContext(ToastContext)

	const [nodes, setNodes] = useState<NodeData[] | null>(null);
	const [pairVisibility, setPairVisibility] = useState<boolean>(false);

	const [loaded, setLoaded] = useState(false);

	useEffect(() => {
		const fetchDevices = async function() {
			const response = await fetch(getPath("/api/nodes-get"))
			if (!response.ok) {
				return // add some sort of error handling
			}

			const data = await response.json()
			let foundDevices : NodeData[] = []

			for (const node of data.data) { // { id : { data } }
				foundDevices.push({ hwid: node.hwid, name: node.name, is_active: node.is_active, last_seen: node.last_seen })
			}

			setNodes(foundDevices)
		}

		const main = async function() {
			await fetchDevices()
			setLoaded(true)
		}

		main()
	}, []);

	if (!loaded) { return; }

	if (nodes === null) {
		showToast("Unable to retrieve node list")
		return
	}

	return (
	<div className="flex flex-col space-y-3 centre-page-container">
		{ nodes.map(element => (
			<div key={element.hwid} className="button-entry button-entry-style clickable" onClick={() => navigate(`/devices/${element.hwid}`)}>
				<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
					<img src={nodeIcon} className="button-icon" />
					<h1 className="mt-px">{element.name}</h1>
					<div className={"h-4 w-4 rounded-full align-bottom m-auto mr-2 " + (element.last_seen > Math.floor(new Date().getTime() / 1000) - 10 * 60 ? "bg-(--colour-green)" : "bg-(--colour-grey)")}/>
				</div>
			</div>
		))}
		
		<div className="button-entry button-entry-style clickable" onClick={() => setPairVisibility(true)}>
			<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
				<h1 className="mt-px w-full text-center">+ Add new device</h1>
			</div>
		</div>

		<DevicePair visible={pairVisibility} closed={() => setPairVisibility(false)} />
	</div>
	)
}