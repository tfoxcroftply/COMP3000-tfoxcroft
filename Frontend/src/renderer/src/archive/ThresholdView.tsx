import { useContext, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ConnectionContext } from "@renderer/contexts/ConnectionHandler";
import { PopupContext } from "@renderer/contexts/PopupHandler";

type thresholdType = {
	id: number,
	name: string,
	value: number,
	threshold_type: string,
	enabled: number,
	triggered: number
	last_trigger: number | undefined
}

export default function ThresholdView() {
	const navigate = useNavigate()
	const params = useParams()

	const { getPath } = useContext(ConnectionContext)
	const { showPopup } = useContext(PopupContext)

	const [threshold, setThreshold] = useState<thresholdType | undefined>(undefined)
	const [requested, setRequested] = useState<boolean>(false);

	useEffect(() => {
		const load = async function() {
			const response = await fetch(getPath("/api/thresholds-get"), {
				headers: {"Content-Type": "application/json", "id": String(params.id ?? -1)}
			})

			if (!response.ok) { 
				return; 
			}

			const data = await response.json()
			const threshold: thresholdType = {...data.data}

			setThreshold(threshold)
		}

		const main = async function() {
			await load()
			setRequested(true)
		}

		main()
	},[])

	const remove = async function() {
		const response = await fetch(getPath("/api/thresholds-delete?id=" + String(threshold?.id)), {
			method: "DELETE"
		})

		if (response.ok) { navigate("/thresholds") }
	}

	if (!requested) {
		return
	}

	if (threshold === undefined) {
		return (<h1>Unable to load threshold information.</h1>)
	}

	return (
		<div className="centre-page-container space-y-6">
			<div>
				<h1>{"Name: " + (threshold.name)}</h1>
				<h1>{"Type: " + (threshold.threshold_type)}</h1>
				<h1>{"Value: " + (threshold.value)}</h1>
				<h1>{"Triggered: " + (threshold.triggered)}</h1>
				<h1>{"Last trigger: " + (threshold.last_trigger)}</h1>
				<h1>{"Enabled: " + (threshold.enabled)}</h1>
			</div>

			<div className="flex justify-between *:flex-1 space-x-2">
				<div className="button-entry-style clickable" onClick={() => navigate("/thresholds/modify?=" + threshold?.id)}>
					<h1 className="mt-px text-center text-xl inset-0">Edit threshold</h1>
				</div>
				<div className="button-entry-style clickable" onClick={() => showPopup("Are you sure you want to delete this threshold?", () => remove)}>
					<h1 className="mt-px text-center text-xl inset-0">Delete threshold</h1>
				</div>
			</div>
		</div>
	)
}