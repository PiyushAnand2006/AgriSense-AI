import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "@/auth/AuthProvider";
import { Spinner } from "@/components/ui/primitives";
import AppLayout from "@/components/layout/AppLayout";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import CropsPage from "@/pages/CropsPage";
import HealthPage from "@/pages/HealthPage";
import FertilizerPage from "@/pages/FertilizerPage";
import MarketPage from "@/pages/MarketPage";
import RecommendationPage from "@/pages/RecommendationPage";
import CropRecommendationPage from "@/pages/CropRecommendationPage";
import WeatherPage from "@/pages/WeatherPage";
import MarketplacePage from "@/pages/MarketplacePage";
import AssistantPage from "@/pages/AssistantPage";
import NotificationsPage from "@/pages/NotificationsPage";
import ProfilePage from "@/pages/ProfilePage";

function Protected() {
  const { user, initializing } = useAuth();
  if (initializing) {
    return (
      <div className="flex min-h-screen items-center justify-center text-primary-600">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <AppLayout />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<Protected />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/crops" element={<CropsPage />} />
        <Route path="/health" element={<HealthPage />} />
        <Route path="/fertilizer" element={<FertilizerPage />} />
        <Route path="/market" element={<MarketPage />} />
        <Route path="/crop-recommendation" element={<CropRecommendationPage />} />
        <Route path="/recommendation" element={<RecommendationPage />} />
        <Route path="/weather" element={<WeatherPage />} />
        <Route path="/marketplace" element={<MarketplacePage />} />
        <Route path="/assistant" element={<AssistantPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
