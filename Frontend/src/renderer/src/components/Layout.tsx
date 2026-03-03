import { useContext, useEffect, useState } from "react";
import { useLocation, useNavigate, Outlet, matchPath } from "react-router-dom"

import { NotificationContext } from "@renderer/contexts/NotificationHandler"

import Connection from "../components/Connection";

import menuIcon from "../assets/icons/menu_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import backIcon from "../assets/icons/arrow_back_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import notificationIcon from "../assets/icons/notifications_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import homeIcon from "../assets/icons/home_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"
import logsIcon from "../assets/icons/analytics_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"
import nodeIcon from "../assets/icons/router_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg"
import settingsIcon from "../assets/icons/settings_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"
import NotificationWindow from "./NotificationWindow";

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
		{path: "/devices", name: "Devices", icon: nodeIcon, offset: true, inMenu: true},
		{path: "/device-edit/:id", name: "Modify device", icon: undefined, offset: false, inMenu: false},
		{path: "/settings", name: "Settings", icon: settingsIcon, offset: false, inMenu: true},
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
		console.log(location.pathname)
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
				const newPath = location.pathname.substring(0, location.pathname.lastIndexOf("/"))
				console.log(newPath)
				navigate(newPath)
			}
		}
	}

	useEffect(() => { // for back button checking
		setBackVisibility(backIsValid())
	},[location.pathname])

	return (
		<div>
			<Connection />
			<div className="p-6 min-h-screen">
				<div className="h-14 flex flex-col">
					<div className={"fixed flex top-5 left-5 space-x-5 right-5 pointer-events-none " + (menuZOffset ? "z-30" : "z-0")}>
						<button className="clickable menu-button-container" onClick={toggleMenu}>
							<img className="menu-button" src={menuIcon} />
						</button>
						{ backVisibility && 
							<button className="clickable menu-button-container" onClick={goBack}>
								<img className="menu-button" src={backIcon} />
							</button>
						}

					</div>
					<div className={"fixed flex top-5 left-20 space-x-5 right-5 pointer-events-none " + (notificationZOffset ? "z-30" : "z-0") }>
						<button className={"clickable menu-button-container ml-auto transition-colors duration-(--duration-long) " + (read ? "" : "outline-(--colour-red)")} onClick={toggleNotifications}>
							<img className="menu-button" src={notificationIcon} />
						</button>
					</div>
					<div className="title leading-none mt-auto">{pageTitle}</div>
					
				</div>
				<div className="h-px w-full bg-neutral-100 mb-6" />
				<div className="px-6">
					<Outlet />
				</div>

			</div>
			<div className={"absolute left-0 top-0 w-72 h-full pt-14 z-20 overflow-hidden bg-white transition-[transform, box-shadow] duration-(--duration-default) ease-out " + (menuVisibility ? "translate-x-0 shadow-2xl" : "-translate-x-full shadow-none") }>
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
			<div className={"fixed top-0 w-96 h-fit p-3 bg-white rounded-2xl shadow-md mt-20 z-10 transition-[transform, box-shadow] duration-(--duration-default) ease-out " + (notificationVisibility ? "translate-x-0 right-6" : "translate-x-full right-0")}>
				<div className="overflow-auto max-h-lg">
					<NotificationWindow open={notificationVisibility} />
				</div>
			</div>
			<div className={"fixed inset-0 h-full bg-black transition-opacity duration-(--duration-default) " + (menuVisibility || notificationVisibility ? "pointer-events-auto opacity-20" : "pointer-events-none opacity-0")} onClick={() => setAll(false)} onTransitionEnd={updateZ} />
		</div>
	)
}