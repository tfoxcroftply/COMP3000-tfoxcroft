import { Line } from "react-chartjs-2"

import "./ChartUtils"

export default function LineGraph({ datasets }) {
    return (
        <Line data={datasets} options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }} />
    )
}

