import { useContext, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { ConnectionContext } from "../contexts/ConnectionHandler";
import { PopupContext } from "../contexts/PopupHandler"
import { ToastContext } from "@renderer/contexts/ToastHandler";

import ToggleButton from "../components/ToggleButton";


export default function ThresholdEdit() {
	const navigate = useNavigate()
	const params = useParams()

	const { getPath } = useContext(ConnectionContext)
	const { showPopup } = useContext(PopupContext)
	const { showToast } = useContext(ToastContext)

	const [createMode, setCreateMode] = useState<boolean>(false);
	const [loaded, setLoaded] = useState<boolean>(false);
 	
	const [id, setId] = useState<number>(-1);
	const [name, setName] = useState<string | null>(null);
	const [thresholdType, setThresholdType] = useState<string>("greater_than");
	const [value, setValue] = useState<number | null>(null);
	const [enabled, setEnabled] = useState<number>(1);

	useEffect(() => {
		const load = async function() {
			if (params.id === undefined) { return; } // to suppress errors
			const response = await fetch(getPath("/api/thresholds-get"), {
				headers: {
					"Content-Type": "application/json", 
					"id": params.id
				},
			})
			if (!response.ok) { return; }

			let data = await response.json();
			data = data.data
			
			setId(data.id)
			setName(data.name)
			setThresholdType(data.threshold_type)
			setValue(data.value)
			setEnabled(data.enabled)
		}

		const main = async function() {
			const useDeviceInfo = params.id !== "-1" && params.id !== undefined // separated to avoid stale state
			setCreateMode(!useDeviceInfo)
			if (useDeviceInfo) {
				await load()
			}
			setLoaded(true)
		}

		main()
	},[])

	const submit = async function() {
		let created_id = null;

		if (createMode) {
			const response = await fetch(getPath("/api/thresholds-create"), { 
				method: "POST",
				headers: {"Content-Type":"application/json"},
				body: JSON.stringify({"name": name, "threshold_type": thresholdType, "value": value, "enabled": enabled})
			})
			const responseJson = await response.json();
			if (!response.ok) { 
				showToast(responseJson.detail);
				return;
			}
			created_id = responseJson.id;
			
		} else {
			const response = await fetch(getPath("/api/thresholds-update"), { 
				method: "PATCH",
				headers: {"Content-Type":"application/json"},
				body: JSON.stringify({"id": id, "name": name, "threshold_type": thresholdType, "value": value, "enabled": enabled})
			})
			if (!response.ok) { return }
		}
		
		navigate("/thresholds/" + (created_id ?? ""))
	}

	if (!loaded) {
		return
	}

	return (
		<div className="centre-page-container">
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Threshold name</h1>
					<input className="button-entry-style clickable editable h-12 w-64 flex flex-col justify-center pl-4 pr-4 text-center" placeholder="Threshold name (optional)" value={name ?? undefined} onChange={(e) => setName(e.target.value)}/>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Threshold type</h1>
					<select className="button-entry-style clickable h-12 w-64 flex flex-col justify-center pl-4 pr-4 text-center" value={thresholdType ?? undefined} onChange={(e) => setThresholdType(e.target.value)}>
						<option value="greater_than">Greater than</option>
						<option value="less_than">Less than</option>
					</select>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Threshold value (°c)</h1>
					<input className="button-entry-style clickable editable h-12 w-24 flex flex-col justify-center pl-4 pr-4 text-center" type="number" value={value ?? undefined} onChange={(e) => setValue(Number(e.target.value))}/>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Enabled</h1>
					<div className="mr-4">
						<ToggleButton onChange={(newValue) => setEnabled(newValue)} setValue={enabled}/>
					</div>
				</div>
			</div>

			<div className="button-entry button-entry-style clickable mt-4" onClick={() => showPopup("Are you sure you want to " + (createMode ? "create" : "modify") + " this threshold?", () => submit)}>
				<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
					<h1 className="mt-px w-full text-center">{(createMode ? "Create" : "Update" ) + " threshold"}</h1>
				</div>
			</div>
		</div>
	)
}