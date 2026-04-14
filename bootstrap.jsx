import React from "react";
import { createRoot } from "react-dom/client";
import CockpitApp from "./App";

const el = document.getElementById("cockpit-root");
if (el) {
  createRoot(el).render(<CockpitApp />);
}