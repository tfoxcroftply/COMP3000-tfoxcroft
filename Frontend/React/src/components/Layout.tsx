import { useLocation, Outlet, useNavigate } from "react-router-dom"

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const toggleSidebar = () => {
    navigate(location.pathname === "/devices" ? "/home" : "/devices") // temporary page switch
  }

  return (
    <div className="p-6">
        <button className="fixed top-5 left-5 p-2 rounded-full outline-0 hover:outline-3 duration-100 outline-neutral-300 transition-all cursor-pointer" onClick={toggleSidebar}>
          <img className="h-fit" src="./icons/menu.svg" />
        </button>
        <Outlet />
    </div>
  )
}