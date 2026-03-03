import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

import ToggleButton from "../components/ToggleButton";

export default function DeviceEdit() {
	type device = {
		hwid: number,
		name: string,
		is_active: number,
		last_seen: number,
		disabled: number,
		debug: number,
	}

	const params = useParams()
	const [node, setNode] = useState<device>();

	useEffect(() => {
		const fetchDevice = async function () {
			if (!params.id) {throw new Error("Missing hwid")}
			const response = await fetch("http://127.0.0.1/api/get-node-info", {
				headers: {"node-hwid": params.id}
			})
			if (!response.ok) {
				return
			}
			const data = await response.json()
			setNode(data.data)
		}

		fetchDevice()
	}, [params.id])

	if (node == null) {
		return <div>Failed to retrieve node information</div> // add timeout later, dont show by default as first check is running
	}

	return (
		<div className="space-y-4">
			<h1 className="leading-none mt-auto">Name: {node.name}</h1>
			<h1 className="leading-none mt-auto">HWID: {node.hwid}</h1>
			<h1 className="leading-none mt-auto">Connected: {node.is_active === 1 ? "Yes" : "No"}</h1>
			<h1 className="leading-none mt-auto">Last seen: {node.last_seen === -1 ? "Unknown" : node.last_seen}</h1>
			
			<div className="w-full flex"> {/* maybe automate these later */}
				<h1 className="leading-none mt-auto">Disabled: {node?.disabled === 1 ? "Yes" : "No"}</h1>
				<div className="ml-auto justify-self-end">
					<ToggleButton setValue={node?.disabled}/> {/* needs to be able to respond to failed api requests */}
				</div>
			</div>
			<div className="w-full flex">
				<h1 className="leading-none mt-auto">Debug: {node?.debug === 1 ? "Yes" : "No"}</h1>
				<div className="ml-auto justify-self-end">
					<ToggleButton setValue={node?.debug}/>
				</div>
			</div>
		</div>
	)
}