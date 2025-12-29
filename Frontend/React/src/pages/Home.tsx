import "../components/Chart"
import { Line } from "react-chartjs-2"

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
      <h1 className="title">Dashboard</h1>
      <div>
        <Line data={test} options={{
          plugins: {
          legend: {
          display: false
        }
        }}} />
      </div>
    </>

  )
}
