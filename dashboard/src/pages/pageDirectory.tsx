import {
  faCog,
  faGaugeSimpleHigh,
  faHome,
  faPencilRuler,
  faPlayCircle,
} from "@fortawesome/free-solid-svg-icons";
import { IconDefinition } from "@fortawesome/free-solid-svg-icons";
import CreateGraph from "./createGraph";
import BaseLayout from "./Layout";

export type pageMap = {
  name: string;
  link: string;
  icon: IconDefinition;
  element: any;
};

export const sidebarPageDirectory: Array<pageMap> = [
  {
    name: "Home",
    link: "/",
    icon: faHome,
    element: BaseLayout
  },
  {
    name: "Dashboard",
    link: "/dashboard",
    icon: faGaugeSimpleHigh,
    element: BaseLayout
  },
  {
    name: "Create Graph",
    link: "/graph/create",
    icon: faPencilRuler,
    element: CreateGraph
  },
  {
    name: "Run Graph",
    link: "/graph/run",
    icon: faPlayCircle,
    element: BaseLayout
  },
  {
    name: "Settings",
    link: "/settings",
    icon: faCog,
    element: BaseLayout
  },
];
