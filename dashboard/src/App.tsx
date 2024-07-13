import { Component } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./pages/Layout";
import ThemeContextProvider from "./contexts/theme/ThemeContextProvider";
// Bootstrap Bundles
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min";

class App extends Component {
  render() {
    return (
      <ThemeContextProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}></Route>
          </Routes>
        </BrowserRouter>
      </ThemeContextProvider>
    );
  }
}

export default App;
