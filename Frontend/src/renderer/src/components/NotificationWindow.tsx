import { useContext, useEffect } from "react"

import { NotificationContext } from "@renderer/contexts/NotificationHandler"

export default function NotificationWindow({open} : {open: boolean}) {

	const { notifications, markAllRead } = useContext(NotificationContext)

	const notificationTypes = {
		1: {
			name: "Notification",
			style: "bg-gray-100",
		},
		2: {
			name: "Warning",
			style: "bg-yellow-200/50 outline-yellow-400/50",
		},
		3: {
			name: "Error",
			style: "bg-red-400/50 outline-red-400/50",
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

	// add scrollbar offset management later, should remove "mr-2" if not in overflow
	
	return (
		<div className="flex flex-col space-y-3 min-h-32 max-h-128 mr-2 p-1">
			{ notifications.map(item => (
				<div key={item.id} className={"relative flex flex-col min-h-24 rounded-xl p-2.5 outline-2 outline-(--outline-colour) clickable *:pointer-events-none " + (notificationTypes[item.notification_type].style)}>
					<div className="absolute rounded-full h-5 w-5 right-2 bg-black opacity-10 clickable" />
					<h1 className="font-semibold">{notificationTypes[item.notification_type].name}</h1>
					<h1>{item.text}</h1>
				</div>				
			))}
		</div>

	)
}