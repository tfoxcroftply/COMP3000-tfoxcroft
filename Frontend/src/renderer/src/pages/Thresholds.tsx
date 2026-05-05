import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"

import { ConnectionContext } from "../contexts/ConnectionHandler";

type thresholdType = {
	id: number,
	name: string,
	value: number,
	threshold_type: string,
	enabled: number,
	triggered: number
	last_trigger: number | undefined
}

export default function Thresholds() {
	const navigate = useNavigate();

	const { getPath } = useContext(ConnectionContext);

	const [thresholds, setThresholds] = useState<thresholdType[]>([]);
	const [loaded, setLoaded] = useState(false);

	useEffect(() => {
		const load = async function() {
			const response = await fetch(getPath("/api/thresholds-get-all"))
			if (response.ok) {
				const data = await response.json()
				let found: thresholdType[] = []

				for (const threshold of data.data) { // { id : { data } }
					found.push({ id: threshold.id, name: threshold.name, value: threshold.value, threshold_type: threshold.threshold_type, enabled: threshold.enabled, triggered: threshold.triggered, last_trigger: threshold.last_trigger})
				}

				setThresholds(found);
			}
		}

		const main = async function() {
			await load()
			setLoaded(true)
		}

		main()
	},[])

	if (!loaded) { return; }

	return (
		<div className="flex flex-col space-y-3 centre-page-container">

			<h1 className={"text-xl leading-none text-center " + (thresholds?.length > 0  ? "hidden" : "mb-6")}>
				No thresholds found. Create a threshold below.
			</h1>
			
			<div className={"flex flex-col space-y-3  " + (thresholds?.length > 0  ? "" : "hidden")}>
				{thresholds.map(element => (
					<div key={element.id} className="button-entry button-entry-style clickable" onClick={() => navigate("/thresholds/" + element.id)}>
						<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
							<h1 className="mt-px">{element.name}</h1>
							<div className={"h-4 w-4 rounded-full align-bottom m-auto mr-2 " + (element.triggered === 1 ? "bg-(--colour-red)" : "bg-(--colour-grey)")}/>
						</div>
					</div>
				))}
			</div>

			<div className="button-entry button-entry-style clickable" onClick={() => navigate("/thresholds/-1")}>
				<div className="flex space-x-3 w-full h-fit text-xl leading-none mt-auto mb-auto">
					<h1 className="mt-px w-full text-center">
						+ Add new threshold
					</h1>
				</div>
			</div>
		</div>
	)
}