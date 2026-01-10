import { useLocation, useNavigate, Outlet } from "react-router-dom"

export default function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const pageTitles : Record<string,string> = {
    "/home":  "Home",
    "/devices": "Devices",
  }

  const pageTitle = pageTitles[location.pathname] ?? "Page";
  //console.log(location.pathname);

  const toggleSidebar = () => {
    navigate(location.pathname === "/devices" ? "/home" : "/devices") // temporary page switch
  }

  return (
    <div className="p-6 min-h-screen">
        <button className="fixed top-5 left-5 p-2 rounded-full outline-2 outline-neutral-100 cursor-pointer transition-box-shadow duration-100 shadow-sm hover:shadow-md" onClick={toggleSidebar}>
          <img className="h-fit mb-px" src="./icons/menu_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg" />
        </button>
        <div className="title leading-none">{pageTitle}</div>
        <div className="h-px w-full bg-neutral-100 mb-6" />
        <Outlet />
    </div>
  )
}