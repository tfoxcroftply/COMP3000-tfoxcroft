import { Route, Routes } from "react-router-dom"

import { ConnectionHandler } from "./contexts/ConnectionHandler"
import { NotificationHandler } from "./contexts/NotificationHandler"
import { PopupHandler } from "./contexts/PopupHandler"
import { ToastHandler } from "./contexts/ToastHandler"

import Layout from "./components/Layout"
import Loading from "./pages/Loading"
import Home from "./pages/Home"
import Logs from "./pages/Logs"
import LogView from "./pages/LogView"
import Thresholds from "./pages/Thresholds"
import ThresholdEdit from "./pages/ThresholdEdit"
import Devices from "./pages/Devices"
import DeviceEdit from "./pages/DeviceEdit"
import Settings from "./pages/Settings"
import SettingsSMS from "./pages/SettingsSMS"
import SettingsSystem from "./pages/SettingsSystem"
import ConnectionHelp from "./pages/ConnectionHelp"


export default function App(): React.JSX.Element {
	return (
		<div className="min-h-screen w-full flex flex-col">
			<ConnectionHandler>
					<PopupHandler>
						<NotificationHandler> {/* maybe move to main.tsx */}
							<ToastHandler>
								<Routes>
									<Route path="/" element={<Loading />}/>
									<Route path="/connection-help" element={<ConnectionHelp />} />
									<Route element={<Layout />} >
										<Route path="/home" element={<Home />}/>
										<Route path="/logs" element={<Logs />}/>
										<Route path="/logs/:id" element={<LogView />}/>
										<Route path="/thresholds" element={<Thresholds />}/>
										<Route path="/thresholds/:id" element={<ThresholdEdit />}/>
										<Route path="/devices" element={<Devices />}/>
										<Route path="/devices/:id" element={<DeviceEdit />}/>
										<Route path="/settings" element={<Settings />}/>
										<Route path="/settings/sms" element={<SettingsSMS />}/>
										<Route path="/settings/system" element={<SettingsSystem />}/>
									</Route>
								</Routes>
							</ToastHandler>
						</NotificationHandler>
					</PopupHandler>
			</ConnectionHandler>
		</div>
	)
}