import { forwardRef, useEffect, useImperativeHandle, useState } from "react"

type ButtonRef = {
	toggle: () => void;
}

type ButtonProps = {
	onChange?: (enabled: number) => void;
	setValue?: number;
	disabled?: boolean;
}

export default forwardRef<ButtonRef, ButtonProps>(function ToggleButton({onChange, setValue = 0, disabled = false}, ref) {
	const [state, setState] = useState<number>(0);

	function toggleState() {
		if (disabled) { return; }
		const newState = state ? 0 : 1
		onChange?.(newState)
		setState(newState)
	}

	useEffect(() => {
		setState(setValue)
	},[setValue])

	useImperativeHandle(ref, () => ({
		toggle: () => toggleState()
	}))

	return (
		<div className={"clickable h-6 w-12 rounded-full p-0.5 flex transition-colors duration-(--duration-default) " + (state ? "bg-(--colour-green)" : "bg-(--colour-grey)")} onClick={toggleState}>
			<div className={"relative h-full aspect-square rounded-full bg-white transition-all duration-default " + (state ? "translate-x-6": "")} />
		</div>
	)
})