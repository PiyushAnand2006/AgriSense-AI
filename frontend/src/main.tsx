import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "@/App";
import { ThemeProvider } from "@/store/ThemeContext";
import { I18nProvider } from "@/i18n/I18nProvider";
import { AuthProvider } from "@/auth/AuthProvider";
import { CropProvider } from "@/store/CropContext";
import { NotificationProvider } from "@/store/NotificationContext";
import { ToastProvider } from "@/components/ui/Toast";
import "@/index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <I18nProvider>
          <AuthProvider>
            <NotificationProvider>
              <CropProvider>
                <ToastProvider>
                  <App />
                </ToastProvider>
              </CropProvider>
            </NotificationProvider>
          </AuthProvider>
        </I18nProvider>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
);
