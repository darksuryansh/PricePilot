

  import { createRoot } from "react-dom/client";
  import App from "./App.tsx";
  import "./index.css";
  import { AuthProvider } from "./contexts/AuthContext";
  import { Analytics } from "@vercel/analytics/next"

  createRoot(document.getElementById("root")!).render(
    <AuthProvider>
      <App />
      <Analytics/>
    </AuthProvider>
  );
  
  