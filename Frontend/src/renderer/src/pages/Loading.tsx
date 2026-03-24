import { useContext, useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom'

import { ConnectionContext } from "../contexts/ConnectionHandler";
import { delay } from "../components/Utils";

export default function Loading() {
	const navigate = useNavigate();

	const [currentMessage, setCurrentMessage] = useState("Discovering devices");
	const { connected, started, ip, startConnection } = useContext(ConnectionContext);

	useEffect(() => {
		if (!started) { return; }
		if (connected) {
			navigate("/home");
			return
		}
	},[connected, started, navigate])

	useEffect(() => {
		if (!started) { return; }
		setCurrentMessage("Attempting to connect to " + ip); // later change to ensure it doesn't override over messages. more of a debug right now
	},[ip, started])

	useEffect(() => {
		const main = async function() {
			await delay(2000); // temporary
			startConnection();
		}
		
		main();
	},[startConnection])

	return (
		<div className="flex-1 flex flex-col items-center justify-center space-y-10">
			<h1 className="text-3xl font-semibold">{currentMessage}</h1>
			<div className="flex flex-row space-x-2 *:inline-block *:h-3 *:w-3 *:rounded-full *:bg-black"> {/* loading dots, animate later*/}
				<span />
				<span />
				<span />
			</div>
		</div>
	)
}

