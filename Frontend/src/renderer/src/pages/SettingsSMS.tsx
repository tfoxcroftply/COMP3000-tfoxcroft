import { useContext, useEffect, useEffectEvent, useState } from "react";
import { useNavigate } from "react-router-dom"

import { ConnectionContext } from "@renderer/contexts/ConnectionHandler";
import { PopupContext } from "@renderer/contexts/PopupHandler";
import { RefreshContext } from "@renderer/contexts/RefreshHandler";
import { ToastContext } from "@renderer/contexts/ToastHandler";

import ToggleButton from "../components/ToggleButton";

export default function SettingsSMS() {
	const navigate = useNavigate();

	const { getPath } = useContext(ConnectionContext);
	const { showPopup } = useContext(PopupContext)
	const { refresh } = useContext(RefreshContext)
	const { showToast } = useContext(ToastContext)

	const [recipient, setRecipient] = useState<string | undefined>(undefined);
	const [enabled, setEnabled] = useState(0);
	const [loaded, setLoaded] = useState(false);

	// signal
	const [signalPercent, setSignalPercent] = useState<number>(0);
	const [signalError, setSignalError] = useState<boolean>(false);

	const submit = async function() {
		const response = await fetch(getPath("/api/system-set-recipient"),{
			method: "PATCH",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({"recipient": recipient})
		})

		const responseJson = await response.json()

		if (!response.ok) {
			showToast(responseJson.detail)
			return;
		}
		
		refresh();
	}

	const updateEnabled = async function(enabled: number) {
		const main = async function() {
			const response = await fetch(getPath("/api/system-set-sms-enabled"),{
				method: "PATCH",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({"enabled": String(enabled)})
			})
			
			//if (!response.ok) {
			//	setEnabled(enabled === 0 ? 1 : 0)
			//}
		}
		main()
	}

	useEffect(() => {
		const getRecipientNumber = async function() {
			const response = await fetch(getPath("/api/system-get-recipient"))
			if (response.ok) {
				const responseJson = await response.json()
				if (responseJson) {
					setRecipient(responseJson.recipient);
					return;
				}
			}
		}
		
		const getSignal = async function() {
			const response = await fetch(getPath("/api/system-signal"))
			if (response.ok) {
				const responseJson = await response.json()
				if (responseJson) {
					if (responseJson.signal === -1) {
						setSignalPercent(100);
						setSignalError(true);
						return;
					}

					setSignalPercent(responseJson.signal + 1);
					setSignalError(false);
					return;
				}
			}

			setSignalPercent(100);
			setSignalError(true);
		}

		const getEnabled = async function() {
			const response = await fetch(getPath("/api/system-sms-enabled"))
			if (!response.ok) { return; }

			const responseJson = await response.json()
			setEnabled(Number(responseJson.value))
		}

		const main = async function() {
			await getRecipientNumber()
			await getSignal()
			await getEnabled()
			setLoaded(true)
		}

		main()
	},[])

	return (
		<div className="flex flex-col space-y-2 centre-page-container">
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="settings-entry-container-title">Recipient phone number</h1>
					<input className="button-entry-style clickable editable h-12 w-64 flex flex-col justify-center pl-4 pr-4 text-center" placeholder="Phone number (+44)" value={recipient} onChange={(e) => setRecipient(e.target.value)}/>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="text-xl">Enabled</h1>
					<div className="mr-4">
						<ToggleButton onChange={(newValue) => updateEnabled(1)} setValue={1}/>
					</div>
				</div>
			</div>
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="settings-entry-container-title">Current signal</h1>
					<div className="flex flex-col justify-center">
						<h1 className={"text-center leading-none mb-2 " + (signalError ? "visible" : "hidden") }>No signal found</h1>
						<div className="h-2 w-64 bg-gray-200 rounded-full">
							<div className={"h-2 rounded-full " + (!signalError ? "bg-[#66C1E8]" : "bg-(--colour-red)")} style={{width: `${signalPercent}%`}}/>
						</div>
					</div>
				</div>
			</div>
			<div className="button-entry button-entry-style clickable mt-2" onClick={() => showPopup("Are you sure you want to update the SMS settings?", () => submit)}>
				<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
					<h1 className="mt-px w-full text-center">Update number</h1>
				</div>
			</div>
		</div>
	)
}