export default function Toast({text, show, onClick} : {text: string | undefined, show: boolean, onClick: () => void}) {

	return (
		<div className="absolute w-full h-full flex flex-col justify-end pointer-events-none">
			<div className={"relative w-fit min-w-32 h-12 flex flex-col p-4 justify-center ml-auto mr-auto mb-12 bg-red-300 rounded-2xl clickable transition-opacity duration-default " + (show ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none")} onClick={onClick}>
				<h1 className="text-center text-md">{text}</h1>
			</div>
		</div>
	)
}