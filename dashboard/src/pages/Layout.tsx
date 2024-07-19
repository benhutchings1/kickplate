import React, { useContext } from "react";
import { Sidebar } from "../components/Sidebar";
import ThemeContext from "../contexts/theme/ThemeContext";
import { sidebarPageDirectory } from "./pageDirectory";

interface Props {
  children?;
}

export const BaseLayout = (props: Props) => {
  const { theme } = useContext(ThemeContext);

  return (
    <div className={ theme }>
    <div className="container-fluid">
      <div className="row flex-nowrap">
        <div className="canvas-sidebar col-2 text-center">
          <Sidebar pageDir={sidebarPageDirectory} />
        </div>
        <div className="canvas-main col-10">
          <div style={{padding: 20}}>
            {props.children}
          </div>
        </div>
      </div>
    </div>
    </div>
  );
};
export default BaseLayout;
