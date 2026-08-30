import { useState, type ReactNode } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthProvider";
import { useI18n } from "@/i18n/I18nProvider";
import { useCropSelection } from "@/store/CropContext";
import { useNotifications } from "@/store/NotificationContext";
import { useTheme } from "@/store/ThemeContext";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { Drawer } from "@/components/ui/primitives";
import { initials } from "@/utils/format";
import {
  BellIcon,
  CropsIcon,
  DashboardIcon,
  FertilizerIcon,
  HealthIcon,
  LogoutIcon,
  MarketIcon,
  MenuIcon,
  MoonIcon,
  ScalesIcon,
  SettingsIcon,
  SproutIcon,
  StoreIcon,
  SunIcon,
  UserIcon,
  WeatherIcon,
} from "./icons";
import logo from "@/assets/logo.svg";
import FloatingAssistant from "@/components/assistant/FloatingAssistant";

interface NavItem {
  to: string;
  label: string;
  icon: (props: { size?: number }) => ReactNode;
}

export default function AppLayout() {
  const { t, language, setLanguage } = useI18n();
  const { user, logout } = useAuth();
  const { setMode, isDark } = useTheme();
  const { season, setSeason } = useCropSelection();
  const { unreadCount } = useNotifications();
  const online = useOnlineStatus();
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const navItems: NavItem[] = [
    { to: "/dashboard", label: t("nav.dashboard"), icon: DashboardIcon },
    { to: "/crops", label: t("nav.crops"), icon: CropsIcon },
    { to: "/crop-recommendation", label: t("nav.cropRecommendation"), icon: SproutIcon },
    { to: "/health", label: t("nav.health"), icon: HealthIcon },
    { to: "/fertilizer", label: t("nav.fertilizer"), icon: FertilizerIcon },
    { to: "/market", label: t("nav.market"), icon: MarketIcon },
    { to: "/recommendation", label: t("nav.recommendation"), icon: ScalesIcon },
    { to: "/weather", label: t("nav.weather"), icon: WeatherIcon },
    { to: "/marketplace", label: t("nav.marketplace"), icon: StoreIcon },
  ];

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const navList = (
    <nav aria-label="Main" className="flex flex-col gap-1">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) => `nav-link ${isActive ? "nav-link-active" : ""}`}
          onClick={() => setDrawerOpen(false)}
        >
          <item.icon size={19} />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );

  const seasonSwitcher = (
    <div>
      <p className="mb-1.5 px-1 text-xs font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
        {t("season.title")}
      </p>
      <div className="grid grid-cols-2 gap-1 rounded-xl bg-soil-100 p-1 dark:bg-soil-800">
        {(["RABI", "ZAID"] as const).map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setSeason(s)}
            className={`rounded-lg px-2 py-1.5 text-xs font-bold transition-colors ${
              season === s
                ? "bg-white text-primary-700 shadow-sm dark:bg-soil-950 dark:text-primary-300"
                : "text-soil-500 hover:text-soil-800 dark:text-soil-400 dark:hover:text-soil-200"
            }`}
          >
            {t(`season.${s}`)}
          </button>
        ))}
      </div>
    </div>
  );

  const userBlock = user && (
    <div className="rounded-xl border border-soil-200/80 bg-soil-50 p-3 dark:border-soil-800 dark:bg-soil-950/60">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-600 text-sm font-bold text-white">
          {initials(user.name)}
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-soil-950 dark:text-white">{user.name}</p>
          <p className="truncate text-xs text-soil-500 dark:text-soil-400">{user.email}</p>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2">
        <NavLink to="/profile" className="btn-secondary !py-2 !text-xs" onClick={() => setDrawerOpen(false)}>
          <UserIcon size={16} />
          {t("nav.profile")}
        </NavLink>
        <button type="button" className="btn-secondary !py-2 !text-xs" onClick={handleLogout}>
          <LogoutIcon size={16} />
          {t("nav.logout")}
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen lg:flex">
      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col justify-between overflow-y-auto border-r border-soil-200/80 bg-white p-4 dark:border-soil-800 dark:bg-soil-900 lg:flex">
        <div className="space-y-6">
          <NavLink to="/dashboard" className="flex items-center gap-2.5 px-1 pt-1">
            <img src={logo} alt="" className="h-9 w-9" />
            <div>
              <p className="font-display text-base font-extrabold leading-tight text-soil-950 dark:text-white">
                AgriSense <span className="text-primary-600 dark:text-primary-400">AI</span>
              </p>
              <p className="text-[11px] leading-tight text-soil-500 dark:text-soil-400">
                {t("app.tagline")}
              </p>
            </div>
          </NavLink>
          {seasonSwitcher}
          {navList}
        </div>
        {userBlock}
      </aside>

      {/* Mobile drawer */}
      <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)} label="Navigation">
        <div className="space-y-6">
          <div className="flex items-center gap-2.5 px-1">
            <img src={logo} alt="" className="h-9 w-9" />
            <p className="font-display text-base font-extrabold text-soil-950 dark:text-white">
              AgriSense <span className="text-primary-600 dark:text-primary-400">AI</span>
            </p>
          </div>
          {seasonSwitcher}
          {navList}
        </div>
        <div className="mt-6">{userBlock}</div>
      </Drawer>

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top bar */}
        <header className="sticky top-0 z-30 border-b border-soil-200/80 bg-white/85 backdrop-blur dark:border-soil-800 dark:bg-soil-900/85">
          <div className="flex items-center gap-2 px-4 py-3 sm:px-6">
            <button
              type="button"
              className="btn-ghost !px-2.5 lg:hidden"
              aria-label="Open menu"
              onClick={() => setDrawerOpen(true)}
            >
              <MenuIcon size={22} />
            </button>

            <div className="lg:hidden">
              <p className="font-display text-sm font-extrabold text-soil-950 dark:text-white">
                AgriSense <span className="text-primary-600 dark:text-primary-400">AI</span>
              </p>
            </div>

            <div className="ml-auto flex items-center gap-1.5">
              <button
                type="button"
                className="btn-ghost !px-2.5 !text-xs !font-bold"
                onClick={() => setLanguage(language === "en" ? "hi" : "en")}
                aria-label="Toggle language"
              >
                {language === "en" ? "हिं" : "EN"}
              </button>
              <button
                type="button"
                className="btn-ghost !px-2.5"
                aria-label="Toggle dark mode"
                onClick={() => setMode(isDark ? "light" : "dark")}
              >
                {isDark ? <SunIcon size={19} /> : <MoonIcon size={19} />}
              </button>
              <NavLink
                to="/notifications"
                className="btn-ghost relative !px-2.5"
                aria-label={t("nav.notifications")}
              >
                <BellIcon size={19} />
                {unreadCount > 0 && (
                  <span className="absolute right-1 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </NavLink>
              <NavLink to="/profile" className="btn-ghost !px-2.5 lg:hidden" aria-label={t("nav.profile")}>
                <SettingsIcon size={19} />
              </NavLink>
            </div>
          </div>
          {!online && (
            <p className="bg-accent-500 px-4 py-1 text-center text-xs font-semibold text-white sm:px-6">
              {t("common.offlineBanner")}
            </p>
          )}
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6 sm:py-8">
          <Outlet />
        </main>
      </div>

      {/* Draggable Floating AI Assistant */}
      <FloatingAssistant />
    </div>
  );
}
