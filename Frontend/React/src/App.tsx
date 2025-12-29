import { Route, Routes } from "react-router-dom"

import Layout from "./components/Layout"

import Loading from "./pages/Loading"
import Home from "./pages/Home"
import Devices from "./pages/Devices"

export default function App() {
  return (
    <div className="min-h-screen w-full flex flex-col overflow-hidden">
      <Routes>
        <Route path="/" element={<Loading />}/>
        <Route element={<Layout />}>
          <Route path="/home" element={<Home />}/>
          <Route path="/devices" element={<Devices />}/>
        </Route>
      </Routes>
    </div>
  )
}