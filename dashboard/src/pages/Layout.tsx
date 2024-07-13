import { useContext } from "react";
import { Sidebar, pageMap } from "../components/Sidebar";
import { faCog, faGaugeSimpleHigh } from "@fortawesome/free-solid-svg-icons";
import ThemeContext from "../contexts/theme/ThemeContext";

const sidebarPageDirectory: Array<pageMap> = [
  {
    name: "Dashboard",
    link: "/",
    icon: faGaugeSimpleHigh,
  },
  {
    name: "Settings",
    link: "/",
    icon: faCog,
  },
];

export const Layout = () => {
  const { theme } = useContext(ThemeContext);
  return (
    <div className={theme} style={{ display: "flex  " }}>
      <Sidebar pageDir={sidebarPageDirectory} />
      <div style={{ marginLeft: "250px", padding: "20px", width: "100%" }}>

      </div>
    </div>
  );
};
export default Layout;
