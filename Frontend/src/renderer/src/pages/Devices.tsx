import { useEffect, useState, useContext } from "react"
import { useNavigate } from "react-router-dom"

import { ConnectionContext } from "../contexts/ConnectionHandler"

import nodeIcon from "../assets/icons/router_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"

import DevicePair from "../components/DevicePair"

export default function Devices() {
	type device = {
		hwid: number,
		name: string,
		is_active: number
	}

	const navigate = useNavigate();

	const [nodes, setNodes] = useState<device[] | null>(null);
	const [pairVisibility, setPairVisibility] = useState<boolean>(false);
	const { getPath } = useContext(ConnectionContext)
	
	useEffect(() => {
		const fetchDevices = async() => {
			const response = await fetch(getPath("/api/get-nodes"))
			if (!response.ok) {
				return // add some sort of error handling
			}

			const data = await response.json()
			let foundDevices : device[] = []

			for (const node of data.data) { // { id : { data } }
				foundDevices.push({ hwid: node.hwid, name: node.name, is_active: node.is_active })
			}

			setNodes(foundDevices)
		}

		fetchDevices()

	}, []);

	if (nodes === null) {
		return <div>Unable to retrieve node list.</div> // add timeout later
	}

	return (
	<div className="flex flex-col space-y-3 mx-auto w-[80vw]">
		{ nodes.map(element => (
			<div key={element.hwid} className="button-entry button-entry-style clickable" onClick={() => navigate(`/devices/${element.hwid}`)}>
				<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
					<img src={nodeIcon} className="button-icon" />
					<h1 className="mt-px">{element.name}</h1>
					<div className={"h-4 w-4 rounded-full align-bottom m-auto mr-2 " + (element.is_active === 1 ? "bg-(--colour-green)" : "bg-(--colour-grey)")}/>
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