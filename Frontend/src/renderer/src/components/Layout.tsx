import { useContext, useEffect, useState } from "react";
import { useLocation, useNavigate, Outlet, matchPath } from "react-router-dom"

import { RefreshHandler } from "@renderer/contexts/RefreshHandler"
import { NotificationContext } from "@renderer/contexts/NotificationHandler"

import Connection from "./Connection"; // fixed path
import NotificationWindow from "./NotificationWindow";

import menuIcon from "../assets/icons/menu_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import backIcon from "../assets/icons/arrow_back_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import notificationIcon from "../assets/icons/notifications_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import homeIcon from "../assets/icons/home_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"
import logsIcon from "../assets/icons/analytics_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"
import thresholdsIcon from "../assets/icons/thermometer_alert_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"
import nodeIcon from "../assets/icons/router_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import settingsIcon from "../assets/icons/settings_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"

export default function Layout() {
	const location = useLocation();
	const navigate = useNavigate();

	const { read } = useContext(NotificationContext);

	const [menuVisibility, setMenuVisibility] = useState(false);
	const [menuZOffset, setMenuZOffset] = useState(false);
	const [notificationVisibility, setNotificationVisibility] = useState(false);
	const [notificationZOffset, setNotificationZOffset] = useState(false);
	const [disconnected, setDisconnected] = useState(false);
	const [backVisibility, setBackVisibility] = useState(false);
	const [loaded, setLoaded] = useState(false);

	type PageData = {
		path: string;
		name: string;
		icon?: string;
		offset: boolean;
		inMenu: boolean;
	}

	const pages : PageData[] = [
		{path: "/home", name: "Dashboard", icon: homeIcon, offset: false, inMenu: true},
		{path: "/logs", name: "Logs", icon: logsIcon, offset: false, inMenu: true},
		{path: "/logs/:id", name: "Log view", icon: logsIcon, offset: false, inMenu: false},
		{path: "/thresholds", name: "Thresholds", icon: thresholdsIcon, offset: false, inMenu: true},
		{path: "/thresholds/:id", name: "Threshold view", icon: undefined, offset: false, inMenu: false},
		{path: "/thresholds/modify/:id", name: "Create/modify threshold", icon: undefined, offset: false, inMenu: false},
		{path: "/devices", name: "Devices", icon: nodeIcon, offset: true, inMenu: true},
		{path: "/devices/:id", name: "Modify device", icon: undefined, offset: false, inMenu: false},
		{path: "/settings", name: "Settings", icon: settingsIcon, offset: false, inMenu: true},
		{path: "/settings/sms", name: "SMS settings", icon: undefined, offset: false, inMenu: false},
		{path: "/settings/system", name: "System settings", icon: undefined, offset: false, inMenu: false},
	]

	const pageTitle = pages.find(page => 
		matchPath({ path: page.path, end: true}, location.pathname)
	)?.name ?? "Page";

	const toggleMenu = () => {
		setMenuVisibility(!menuVisibility);
		if (!menuVisibility) {
			setNotificationVisibility(false);
			setMenuZOffset(true)
		}
	}

	const toggleNotifications = () => {
		setNotificationVisibility(!notificationVisibility);
		if (!notificationVisibility) {
			//console.log("opening")
			setNotificationZOffset(true);
			setMenuVisibility(false);
		}
	}

	const setAll = (state : boolean) => {
		setMenuVisibility(state);
		setNotificationVisibility(state);
	}

	const updateZ = () => { // runs after animation
		if (!notificationVisibility) {
			setNotificationZOffset(false);
		}
		if (!menuVisibility) {
			setMenuZOffset(false);
		}
	}

	const goTo = function (path : string) {
		setMenuVisibility(false);
		navigate(path);
	}

	const backIsValid = function () {
		//console.log(location.pathname)
		return location.pathname !== "/home"
	}

	const goBack = function () {
		if (menuVisibility === true) {
			setMenuVisibility(false);
			setNotificationVisibility(false);
			return;
		}

		if (backIsValid()) {
			const count = location.pathname.split("/").length - 1
			if (count === 1) {
				navigate("/home")
			} else {
				let path = location.pathname.replace("modify/", "")
				path = path.substring(0, path.lastIndexOf("/"))
				console.log(path)
				navigate(path)
			}
		}
	}

	useEffect(() => { // for back button checking
		setBackVisibility(backIsValid())
	},[location.pathname])

	return (
		<RefreshHandler>
			<Connection />
			<div className="min-h-screen flex flex-col">
				<div className="bg-linear-to-tr from-[#66C1E8] to-[#A2DBEB] h-20 flex flex-col shadow-sm">
					<div className={"fixed flex top-5 left-5 space-x-5 right-5 pointer-events-none " + (menuZOffset ? "z-30" : "z-0")}>
						<button className="clickable menu-button-container shadow-md" onClick={toggleMenu}>
							<img className="menu-button" src={menuIcon} />
						</button>
						{ backVisibility && 
							<button className="clickable menu-button-container shadow-sm" onClick={goBack}>
								<img className="menu-button" src={backIcon} />
							</button>
						}
					</div>
					<div className={"fixed flex top-5 left-20 space-x-5 right-5 pointer-events-none " + (notificationZOffset ? "z-30" : "z-0") }>
						<button className={"clickable menu-button-container ml-auto transition-colors duration-(--duration-long) shadow-md " + (read ? "" : "outline-(--colour-red)")} onClick={toggleNotifications}>
							<img className="menu-button" src={notificationIcon} />
						</button>
					</div>
					<div className="title leading-none mt-auto text-white">{pageTitle}</div>
				</div>
				<div className="grow p-6">
					<Outlet />
				</div>

			</div>
			<div className={"absolute left-0 top-0 w-72 h-full pt-14 z-20 overflow-hidden overlay-colour transition-[transform, box-shadow] duration-(--duration-default) ease-out " + (menuVisibility ? "translate-x-0 shadow-2xl" : "-translate-x-full shadow-none") }>
				<div className="p-6 flex flex-col space-y-3 h-full">
					<div className="h-px w-full mb-6" />
					{ pages.map((page) =>
						(page.inMenu ?? false) ? (
							<button key={page.path} className={"clickable button-entry button-entry-style " + (page.offset ? "mt-auto" : "")} onClick={() => goTo(page.path)}>
								<div className="button-icon-container">
									<img className="button-icon" src={page.icon}/>
								</div>
								<div className="button-text-container">
									<h1 className="button-text">{page.name}</h1>
								</div>
							</button>
						) : null
					)}

				</div>
			</div>
			<div className={"fixed top-0 w-96 h-fit p-3 rounded-2xl overlay-colour shadow-md mt-20 z-10 transition-[transform, box-shadow] duration-(--duration-default) ease-out " + (notificationVisibility ? "translate-x-0 right-6" : "translate-x-full right-0")}>
				<NotificationWindow open={notificationVisibility} />
			</div>
			<div className={"fixed inset-0 h-full bg-black transition-opacity duration-(--duration-default) " + (menuVisibility || notificationVisibility ? "pointer-events-auto opacity-20" : "pointer-events-none opacity-0")} onClick={() => setAll(false)} onTransitionEnd={updateZ} />
		</RefreshHandler>
	)
}