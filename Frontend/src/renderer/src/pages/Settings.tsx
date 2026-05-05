import { useNavigate } from "react-router-dom";

export default function Settings() {
	const navigate = useNavigate();

	return (
		<div className="flex flex-col space-y-2 centre-page-container">
			<div className="settings-entry">
				<div className="settings-entry-container">
					<h1 className="settings-entry-container-title">SMS settings</h1>
					<h1 className="button-entry-style clickable h-12 w-24 text-center flex flex-col justify-center pl-4 pr-4" onClick={() => navigate("/settings/sms")}>View</h1>
				</div>
			</div>
			<div className="settings-entry border-none">
				<div className="settings-entry-container">
					<h1 className="settings-entry-container-title">System settings</h1>
					<h1 className="button-entry-style clickable h-12 w-24 text-center flex flex-col justify-center pl-4 pr-4" onClick={() => navigate("/settings/system")}>View</h1>
				</div>
			</div>
		</div>
	)
}