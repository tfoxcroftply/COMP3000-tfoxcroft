import { Line } from "react-chartjs-2"

import "../components/Chart"

const test = {
    labels: ["test","test"],
    datasets: [
        {
          label: "test",
          data: [0,1],
        }
    ]
}

export default function Home() {
  return (
    <>
      <div>
        <Line data={test} options={{
          plugins: {
            legend: {
              display: false
            }
          }
        }} />
      </div>
    </>

  )
}
