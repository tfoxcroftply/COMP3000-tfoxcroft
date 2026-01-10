//import { useState } from "react"

export default function Devices() {
	//const [connected,setConnected] = useState(false);
	const test = ["test","test2", "test3"]

	/* function buttonClick(): void {
    console.log("Button click")
		fetch("http://127.0.0.1/api/debug", {method: "POST"})
			.then(response => {
				console.log(response);
				setConnected((response.status === 200) ? true : false);
			})
		} */

  return (
    <>
		{/* <button onClick={buttonClick} className="bg-gray-200 p-1 mb-1 cursor-pointer">Test button</button>
		<h1 className={(connected ? "bg-green-400" : "bg-red-400") + " p-1 max-h-fit max-w-fit"}>{connected ? "Connected" : "Not connected"}</h1> */}
		<div className="flex flex-col space-y-3 mx-auto w-[80vw]">
			{ test.map((element, index) => (
				<div key={element} className="min-h-10 p-3 rounded-2xl outline-2 cursor-pointer **:pointer-events-none bg-white outline-neutral-100 transition-box-shadow duration-100 shadow-sm hover:shadow-md">
					<div className="flex space-x-3 text-xl leading-none">
						<img src="./icons/router_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg" className="h-[1em] w-auto" />
						<h1 className="mt-px">Node {index + 1}</h1>
					</div>
				</div>
			))}
		</div>

    </>
  )
}