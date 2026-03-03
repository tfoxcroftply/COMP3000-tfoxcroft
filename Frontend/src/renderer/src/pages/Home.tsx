import { Line } from "react-chartjs-2"

import "../components/Chart"

const test = {
	labels: ["test1","test2"],
	datasets: [
		{
			label: "test",
			data: [0,1],
		}
	]
}

export default function Home() {
	return (
		<div>
			<div className="flex justify-center">
				<div className="mx-auto w-full max-w-[80vw]">
					<Line data={test} options={{
						responsive: true,
						maintainAspectRatio: false,
						plugins: {
							legend: {
								display: false
							}
						}
					}} />
				</div>
			</div>
			<div className="grid gap-4 grid-cols-2" >
				<div className="clickable button-entry-style h-16">
					<h1>Average temperature</h1>
				</div>
				<div className="clickable button-entry-style h-16">
					<h1>Max</h1>
					<h1>Min</h1>
				</div>
				<div className="clickable button-entry-style h-16">
					<h1>Threshold alerts</h1>
					<h1>None</h1>
				</div>
			</div>
		</div>
	)
}
