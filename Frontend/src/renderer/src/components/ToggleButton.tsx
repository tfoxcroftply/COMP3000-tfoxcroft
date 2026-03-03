import { forwardRef, useEffect, useImperativeHandle, useState } from "react"

type ButtonHandler = {
	toggle: () => void;
}

type ButtonProps = {
	onChange?: (on: boolean) => void;
	setValue?: number;
}

export default forwardRef<ButtonHandler, ButtonProps>(function ToggleButton({onChange, setValue}, ref) {
	const [state, setState] = useState(false);

	function toggleState() {
		const newState = !state
		onChange?.(newState)
		setState(newState)
	}

	useEffect(() => {
		setState(setValue === 1 ? true : false)
	},[setValue])


	useImperativeHandle(ref, () => ({
		toggle: () => toggleState()
	}))

	return (
		<div className={"clickable h-6 w-12 rounded-full p-0.5 flex transition-colors duration-default " + (state ? "bg-(--colour-green)" : "bg-(--colour-grey)")} onClick={toggleState}>
			<div className={"relative h-full aspect-square rounded-full bg-white transition-all duration-default " + (state ? "translate-x-6": "")} />
		</div>
	)
})