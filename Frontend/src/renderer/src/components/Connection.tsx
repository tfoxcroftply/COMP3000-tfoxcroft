import { useEffect, useState, useRef, useContext } from "react"

import { ConnectionContext } from "../contexts/ConnectionHandler"

import loadingIcon from "../assets/icons/progress_activity_24dp_FFFFFF_FILL0_wght400_GRAD0_opsz24.svg"
import { useNavigate } from "react-router-dom"

export default function Connection() {
	const navigate = useNavigate()

	const { connected, ip } = useContext(ConnectionContext)
	const [helpVisibility, setHelpVisibility] = useState(false)

	return (
	<div className={"*:z-50 inset-0 " + (connected ? "hidden" : "")}>
		<div className="fixed inset-0 flex flex-col justify-center space-y-2 bg-black/50">
			<h1 className="text-3xl text-center text-white" >Disconnected</h1>
			<h1 className="text-xl text-center text-white">Attempting to reconnect</h1>
			<div className="h-10 w-full mt-3 fill-white">
				<img className="h-full ml-auto mr-auto animate-spin" src={loadingIcon} />
			</div>
		</div>
		<div className={"fixed inset-0 pointer-events-none flex flex-col justify-end items-center p-16" }>
			<h1 className={"text-white text-xl text-center underline transition-opacity duration-1000 cursor-pointer " + (helpVisibility ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none")} onClick={() => navigate("/connection-help")}>Reload application</h1>
		</div> 
	</div>
	)
}