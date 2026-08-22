import { useState } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { useAuth } from "@/auth/AuthProvider";
import { useTheme } from "@/store/ThemeContext";
import { authService } from "@/services/authService";
import { clearApiCache } from "@/services/apiClient";
import { useToast } from "@/components/ui/Toast";
import { ApiError } from "@/services/apiClient";
import { initials } from "@/utils/format";

export default function ProfilePage() {
  const { t, language, setLanguage } = useI18n();
  const { user, updateUser, logout } = useAuth();
  const { mode, setMode } = useTheme();
  const { showToast } = useToast();

  const [form, setForm] = useState({
    name: user?.name ?? "",
    phone: user?.profile?.phone ?? "",
    village: user?.profile?.village ?? "",
    district: user?.profile?.district ?? "",
    state: user?.profile?.state ?? "",
    farmSizeAcres: user?.profile?.farmSizeAcres?.toString() ?? "",
  });
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (saving) return;
    setSaving(true);
    try {
      const result = await authService.updateProfile({
        name: form.name,
        farmSizeAcres: form.farmSizeAcres ? Number(form.farmSizeAcres) : undefined,
      });
      updateUser({
        ...result.data,
        profile: result.data.profile
          ? {
              ...result.data.profile,
              village: form.village || result.data.profile.village,
              district: form.district || result.data.profile.district,
              state: form.state || result.data.profile.state,
              phone: form.phone || result.data.profile.phone,
            }
          : null,
      });
      showToast(t("profile.saved"), "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-extrabold">{t("profile.title")}</h1>

      {/* Identity */}
      <div className="card flex flex-wrap items-center gap-4 p-6">
        <span className="flex h-16 w-16 items-center justify-center rounded-full bg-primary-600 text-xl font-bold text-white">
          {initials(user?.name ?? "?")}
        </span>
        <div>
          <p className="font-display text-lg font-bold">{user?.name}</p>
          <p className="text-sm text-soil-500 dark:text-soil-400">{user?.email}</p>
        </div>
      </div>

      {/* Farm details form */}
      <section className="card space-y-4 p-6" aria-label={t("profile.farmDetails")}>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
          {t("profile.farmDetails")}
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {(
            [
              ["name", t("auth.name")],
              ["phone", "Phone"],
              ["village", t("auth.village")],
              ["district", t("auth.district")],
              ["state", t("auth.state")],
              ["farmSizeAcres", t("crops.farmSize")],
            ] as const
          ).map(([field, label]) => (
            <div key={field}>
              <label htmlFor={`profile-${field}`} className="label">
                {label}
              </label>
              <input
                id={`profile-${field}`}
                type={field === "farmSizeAcres" ? "number" : "text"}
                step={field === "farmSizeAcres" ? "0.5" : undefined}
                className="input"
                value={form[field]}
                onChange={(event) => setForm((current) => ({ ...current, [field]: event.target.value }))}
              />
            </div>
          ))}
        </div>
        <button type="button" className="btn-primary" onClick={() => void save()} disabled={saving}>
          {t("common.save")}
        </button>
      </section>

      {/* Settings: theme + language */}
      <section className="card space-y-5 p-6" aria-label={t("settings.title")}>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-soil-500 dark:text-soil-400">
          {t("settings.appearance")}
        </h2>
        <div className="flex flex-wrap items-center gap-6">
          <div>
            <p className="label">{t("settings.theme")}</p>
            <div className="flex gap-1 rounded-xl bg-soil-100 p-1 dark:bg-soil-800">
              {(["light", "dark", "system"] as const).map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setMode(option)}
                  aria-pressed={mode === option}
                  className={`rounded-lg px-3 py-1.5 text-xs font-bold transition-colors ${
                    mode === option
                      ? "bg-white text-primary-700 shadow-sm dark:bg-soil-950 dark:text-primary-300"
                      : "text-soil-500 hover:text-soil-800 dark:text-soil-400 dark:hover:text-soil-200"
                  }`}
                >
                  {t(`settings.theme${option.charAt(0).toUpperCase()}${option.slice(1)}`)}
                </button>
              ))}
            </div>
          </div>
          <div>
            <p className="label">{t("settings.language")}</p>
            <div className="flex gap-1 rounded-xl bg-soil-100 p-1 dark:bg-soil-800">
              {(["en", "hi"] as const).map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setLanguage(option)}
                  aria-pressed={language === option}
                  className={`rounded-lg px-3 py-1.5 text-xs font-bold transition-colors ${
                    language === option
                      ? "bg-white text-primary-700 shadow-sm dark:bg-soil-950 dark:text-primary-300"
                      : "text-soil-500 hover:text-soil-800 dark:text-soil-400 dark:hover:text-soil-200"
                  }`}
                >
                  {option === "en" ? "English" : "हिंदी"}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-soil-200 pt-4 dark:border-soil-800">
          <p className="label">{t("settings.data")}</p>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => {
              clearApiCache();
              showToast(t("settings.clearCache"), "success");
            }}
          >
            {t("settings.clearCache")}
          </button>
        </div>

        <div className="border-t border-soil-200 pt-4 dark:border-soil-800">
          <button type="button" className="btn-secondary !text-red-600 dark:!text-red-400" onClick={() => void logout()}>
            {t("nav.logout")}
          </button>
        </div>
      </section>
    </div>
  );
}
