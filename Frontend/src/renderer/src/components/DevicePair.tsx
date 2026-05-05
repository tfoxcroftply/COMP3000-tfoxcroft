// potentially merge new popuphandler
// buggy, fix later
// works most of the time

import { useContext, useEffect, useState } from "react"
import useWebSocket, { ReadyState } from "react-use-websocket";

import { ConnectionContext } from "../contexts/ConnectionHandler";
import { RefreshContext } from "../contexts/RefreshHandler";

import progressIcon from "../assets/icons/progress_activity_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import closeIcon from "../assets/icons/close_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"

export default function DevicePair({ visible, closed } : { visible?: boolean, closed?: () => void}) {

	const [running, setRunning] = useState(false); // websocket running
	const [websocketActive, setWebsocketActive] = useState(false); // should try websocket connect
	const [messages, setMessages] = useState<string[]>([]);

	const { connected, ip, getPath } = useContext(ConnectionContext);
	const { refresh	} = useContext(RefreshContext)

	const { sendMessage, lastMessage, readyState } = useWebSocket(websocketActive ? "ws://" + ip + ":8080" : null)

	const delay = async function(milliseconds: number) {
        return new Promise(finish => setTimeout(finish, milliseconds))
    }

	const addMessage = function(input: string) {
		setMessages(prev => [...prev, input]);
	}

	useEffect(() => {
		if (readyState === ReadyState.CONNECTING) {
			addMessage("Connecting to websocket.")
		}
		if (readyState === ReadyState.OPEN) {
			if (running) { return; }
			try {
				setRunning(true);
				addMessage("Successfully connected to websocket.")

			} finally {
				setRunning(false);
			}
		}
	},[readyState]);

	useEffect(() => {
		if (lastMessage !== null) {
			if (lastMessage.data === "refresh") {
				setWebsocketActive(false);
				refresh();
				return;
			}
			addMessage(lastMessage.data);
		}
	},[lastMessage]) // add any incoming websocket messages to lock

	useEffect(() => {
		const start = async function () {
			if (visible === true && !websocketActive && connected) {
				const response = await fetch(getPath("/api/websocket-start"), { method: "POST" })
				console.log(response.status)
				setWebsocketActive(response.status === 200 ? true : false)
			}
		}

		if (!connected) {
			setMessages([]);
			setWebsocketActive(false);
		}

		start()
	},[visible, connected]) // active = devicepair.tsx visible

	return (
		<div className={"fixed flex inset-0 z-30 transition-opacity duration-default " + (visible === true ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none") }> {/* flex works for some reason */}
			<div className="absolute inset-0 bg-black/30"/>
			<div className="relative h-64 w-lg p-4 flex flex-col space-y-4 bg-white m-auto rounded-2xl">
				<div className="absolute inset-x-0">
					<h1 className="text-2xl text-center">Pairing mode</h1>
				</div>
				<button className="absolute clickable menu-button-container w-fit z-10" onClick={closed}>
					<img className="menu-button" src={closeIcon} />
				</button>

				<div className={"h-full w-full overflow-y-auto flex flex-col grow items-center justify-center mt-8 " + (websocketActive ? "hidden" : "visible")}>
					<div className="space-y-4">
						<h1 className="text-xl">Connecting to the server.</h1>
						<div className="flex justify-center">
							<img src={progressIcon} className="h-6 animate-spin"/>
						</div>
					</div>
				</div>

				<div className={"max-w-full w-full overflow-auto h-full mt-14 bg-gray-100 rounded-2xl p-2 " + (websocketActive ? "visible" : "hidden")}>
					{messages.map((message, index) => (
						<h1 key={index}>{message}</h1>
					))}
				</div>
			</div>
		</div>
	)
}