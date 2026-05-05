import { useContext } from "react";

import { ConnectionContext } from "@renderer/contexts/ConnectionHandler";
import { PopupContext } from "@renderer/contexts/PopupHandler";
import { RefreshContext } from "@renderer/contexts/RefreshHandler";

export default function SettingsSystem() {
	const { getPath } = useContext(ConnectionContext);
	const { showPopup } = useContext(PopupContext)
	const { refresh } = useContext(RefreshContext)

	const updateTime = async function() {
		console.log("Updating device time.");
		const timestamp = Math.floor(Date.now() / 1000)

		const response = await fetch(getPath("/api/system-update-time"),{
			method: "POST",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({"timestamp": timestamp})
		})

		if (!response.ok) { return false; }

		refresh();
		return true;
	}

	return (
		<div className="flex flex-col space-y-2 centre-page-container">
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="settings-entry-container-title">Sync system time</h1>
					<h1 className="button-entry-style clickable h-12 w-24 text-center flex flex-col justify-center pl-4 pr-4" onClick={() => showPopup("Are you sure you want to update the device time? A system reset is recommended after updating.", () => updateTime)}>Update</h1>
				</div>
			</div>
		</div>
	)
}