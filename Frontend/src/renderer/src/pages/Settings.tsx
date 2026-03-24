import { useContext } from "react";
import { PopupContext } from "../contexts/PopupHandler";

export default function Settings() {

	const { showPopup } = useContext(PopupContext);

	const updateTime = function() {
		console.log("Updating device time.");
		// trigger refresh when loading logic comes
	}

	return (
		<div className="flex flex-col space-y-3 mx-auto w-[80vw]">
			<div className="h-20 border-b border-(--outline-colour)">
				<div className="h-18 flex items-center justify-between">
					<h1 className="text-xl">Update device time</h1>
					<h1 className="button-entry-style clickable h-12 flex flex-col justify-center pl-4 pr-4" onClick={() => showPopup("Are you sure you want to update the device time? If incorrect, it may cause signfiicant data issues.", () => updateTime)}>Update</h1>
				</div>
			</div>
			<div className="h-20 border-b border-(--outline-colour)">
				<div className="h-18 flex items-center justify-between">
					<h1 className="text-xl">Update phone number</h1>
					<h1 className="button-entry-style clickable h-12 flex flex-col justify-center pl-4 pr-4" onClick={() => showPopup("Are you sure you want to update the stored phone number?", () => updateTime)}>Update</h1>
				</div>
			</div>
		</div>
	)
}