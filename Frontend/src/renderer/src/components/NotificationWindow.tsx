import { useContext, useEffect } from "react"

import { NotificationContext } from "@renderer/contexts/NotificationHandler"

import deleteIcon from "../assets/icons/delete_24dp_F1F1F1_FILL0_wght400_GRAD0_opsz24.svg"
export default function NotificationWindow({open} : {open: boolean}) {

	const { notifications, markAllRead, deleteNotification } = useContext(NotificationContext)

	const notificationTypes = {
		1: {
			name: "Notification",
			style: "bg-gray-200",
		},
		2: {
			name: "Warning",
			style: "bg-yellow-100",
		},
		3: {
			name: "Error",
			style: "bg-red-300",
		},
	}

	useEffect(() => {
		const update = async function() {
			if (open === true) {
				try {
					markAllRead()
				} catch (err) {
					console.log(err)
				}
			}
		}
		update()
	},[open])
	
	return (
		<div className="flex flex-col space-y-3 min-h-16 max-h-128 p-1 overflow-y-auto max-h-lg ">
			<div className="flex h-8">
				<h1 className="text-center text-xl h-8 mt-1 justify-center grow leading-none pt-px">Notifications</h1>
			</div>

			<div className={"h-24 flex flex-col justify-center " + (notifications.length > 0 ? "hidden" : "")}>
				<h1 className="text-center">No notifications found</h1>
			</div>

			{ notifications.map(item => (
				<div key={item.id} className={"relative flex flex-col"}>
					<div className="absolute h-6 w-6 top-1.5 right-1.5 p-0 opacity-50 pointer-events-auto clickable shadow-none" onClick={() => deleteNotification(item.id)}>
						<img src={deleteIcon} className="w-full h-full rounded-md pointer-events-auto transition-colors duration-default bg-black/0 hover:bg-black/20"/>
					</div>
					<div className={"rounded-md p-2.5 min-h-24 " + (notificationTypes[item.notification_type].style)}>
						<h1 className="font-semibold">{notificationTypes[item.notification_type].name}</h1>
						<h1>{item.text}</h1>
					</div>
				</div>				

			))}
		</div>
	)
}