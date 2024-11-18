import Switch from "react-switch";
import { Component, ReactNode } from "react";
import Cookies from "js-cookie";

interface Props {
  theme: string;
  setTheme: Function;
}

interface State {
  checked: boolean;
}

export default class ThemeToggleSwitch extends Component<Props, State> {
  constructor(props: Props) {
    super(props);

    // Check for theme cookie
    const storedTheme = Cookies.get("theme");
    this.state = {
      checked: storedTheme == null ? false : storedTheme === "light",
    };
    this.handleChange = this.handleChange.bind(this);
  }

  handleChange(checked: boolean) {
    const theme = checked ? "light" : "dark";
    Cookies.set("theme", theme);
    this.props.setTheme(theme);
    this.setState({ checked });
  }

  render(): ReactNode {
    return <Switch onChange={this.handleChange} checked={this.state.checked} />;
  }
}
