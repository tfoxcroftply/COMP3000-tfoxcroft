import { useState, useEffect, useContext } from "react";
import { useParams } from "react-router-dom";

import { ConnectionContext } from "../contexts/ConnectionHandler";
import { PopupContext } from "@renderer/contexts/PopupHandler";
import { ToastContext } from "@renderer/contexts/ToastHandler";

import ToggleButton from "../components/ToggleButton";


export default function DeviceEdit() {
	const params = useParams()

	const { getPath } = useContext(ConnectionContext)
	const { showPopup } = useContext(PopupContext)
	const { showToast } = useContext(ToastContext)

	const [name, setName] = useState<string | undefined>(undefined);
	const [hwid, setHwid] = useState<number | undefined>(undefined);
	const [connected, setConnected] = useState<boolean>(false);
	const [lastSeen, setLastSeen] = useState<number | undefined>(undefined);
	const [disabled, setDisabled] = useState<number>(0);

	const [loaded, setLoaded] = useState(false);

	const submit = function() {
		const main = async function() {
			const response = await fetch(getPath("/api/nodes-set-info"), {
				method: "PATCH",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({name: name, node_hwid: hwid, disabled: disabled})
			});
			const responseJson = await response.json();

			if (!response.ok) {
				showToast(responseJson.detail)
				return;
			}
		}
		main();
	}

	useEffect(() => {
		const fetchDevice = async function () {
			if (!params.id) {throw new Error("Missing hwid")}
			const response = await fetch(getPath("/api/nodes-info"), {
				headers: {"Content-Type":"application/json", "node-hwid": params.id}
			})
			const responseJson = await response.json()

			if (!response.ok) {
				showToast(responseJson.detail)
				return;
			}

			setName(responseJson.data.name)
			setHwid(responseJson.data.hwid)
			setLastSeen(responseJson.data.last_seen)
			setDisabled(responseJson.data.disabled)

			setConnected((lastSeen ?? 0) > Math.floor(new Date().getTime() / 1000) - 10 * 60)
		}
		
		const update = async function() {
			await fetchDevice()
			setLoaded(true);
		}

		update()
	}, [params.id])

	if (loaded === false) {
		return
	}

	if (name === undefined || name === null) { // use undefined anyway to suppress warnings
		showToast("Failed to retrieve node information")
		return // add timeout later, dont show by default as first check is running
	}

	if (lastSeen === undefined) { return; } // mostly for suppressing errors

	return (
		<div className="centre-page-container">
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Device name</h1>
					<input className="button-entry-style clickable editable h-12 w-56 flex flex-col justify-center pl-4 pr-4 text-center" type="text" value={name ?? undefined} onChange={(e) => setName(e.target.value)}/>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">HWID</h1>
					<h1 className="button-entry-style h-12 w-56 flex flex-col justify-center pl-4 pr-4 text-center inactive-box">{hwid ?? "Unknown"}</h1>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Connected</h1>
					<div className={"h-4 w-4 rounded-full align-bottom m-auto mr-2 " + (connected ? "bg-(--colour-green)" : "bg-(--colour-grey)")}/>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Last seen</h1>
					<h1>{new Date(lastSeen * 1000).toString()}</h1>
				</div>
			</div>
			<div className="settings-entry border-none">
				<div className="settings-entry-container">
					<h1 className="text-xl">Disabled</h1>
					<ToggleButton setValue={disabled} onChange={setDisabled}/>
				</div>
			</div>
			<div className="button-entry button-entry-style clickable mt-4" onClick={() => showPopup("Are you sure you want to modify this device?", () => submit)}>
				<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
					<h1 className="mt-px w-full text-center">Update node</h1>
				</div>
			</div>
		</div>
	)
}