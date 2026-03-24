import LineGraph from "@renderer/components/LineGraph"

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
		<div className="h-full">
			<div className="flex justify-center h-full">
				<div className="mx-auto w-full max-w-[80vw] h-72">
					<LineGraph datasets={test} />
				</div>
			</div>
			<div className="flex justify-center space-x-4 h-full *:flex-1" >
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
