import { Route, Routes } from "react-router-dom"

import { NotificationHandler } from "./contexts/NotificationHandler"

import Layout from "./components/Layout"
import Loading from "./pages/Loading"
import Home from "./pages/Home"
import Logs from "./pages/Logs"
import Devices from "./pages/Devices"
import DeviceEdit from "./pages/DeviceEdit"
import Settings from "./pages/Settings"
import ConnectionHelp from "./pages/ConnectionHelp"
import { ConnectionHandler } from "./contexts/ConnectionHandler"

export default function App(): React.JSX.Element {
	return (
		<div className="min-h-screen w-full flex flex-col">
			<ConnectionHandler>
				<NotificationHandler> {/* maybe move to main.tsx */}
					<Routes>
						<Route path="/" element={<Loading />}/>
						<Route path="/connection-help" element={<ConnectionHelp />} />
						<Route element={<Layout />}>
							<Route path="/home" element={<Home />}/>
							<Route path="/logs" element={<Logs />}/>
							<Route path="/devices" element={<Devices />}/>
							<Route path="/devices/:id" element={<DeviceEdit />}/>
							<Route path="/settings" element={<Settings />}/>
						</Route>
					</Routes>
				</NotificationHandler>
			</ConnectionHandler>
		</div>
	)
}