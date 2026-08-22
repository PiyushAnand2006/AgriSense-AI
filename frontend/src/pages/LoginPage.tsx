import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthProvider";
import { useI18n } from "@/i18n/I18nProvider";
import { useToast } from "@/components/ui/Toast";
import { Spinner } from "@/components/ui/primitives";
import { ApiError } from "@/services/apiClient";
import logo from "@/assets/logo.svg";

export default function LoginPage() {
  const { t } = useI18n();
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      showToast(t("dashboard.title"), "success");
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  };

  const useDemo = () => {
    setEmail("demo@agrisense.ai");
    setPassword("Demo@1234");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-soil-50 px-4 py-10 dark:bg-soil-950">
      <div className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center gap-3 text-center">
          <img src={logo} alt="" className="h-14 w-14" />
          <div>
            <h1 className="font-display text-2xl font-extrabold text-soil-950 dark:text-white">
              {t("auth.loginTitle")}
            </h1>
            <p className="mt-1 text-sm text-soil-500 dark:text-soil-400">
              {t("auth.loginSubtitle")}
            </p>
          </div>
        </div>

        <form onSubmit={submit} className="card space-y-4 p-6" noValidate>
          <div>
            <label htmlFor="login-email" className="label">
              {t("auth.email")}
            </label>
            <input
              id="login-email"
              type="email"
              className="input"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>
          <div>
            <label htmlFor="login-password" className="label">
              {t("auth.password")}
            </label>
            <input
              id="login-password"
              type="password"
              className="input"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
            <p className="mt-1 text-xs text-soil-500 dark:text-soil-400">{t("auth.passwordHint")}</p>
          </div>

          {error && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:bg-red-900/30 dark:text-red-300">
              {error}
            </p>
          )}

          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? <Spinner className="h-4 w-4" /> : t("auth.loginSubmit")}
          </button>

          <button type="button" className="btn-secondary w-full" onClick={useDemo}>
            {t("auth.demoAccount")}
          </button>
          <p className="text-center text-xs text-soil-500 dark:text-soil-400">{t("auth.demoHint")}</p>
        </form>

        <p className="mt-4 text-center text-sm text-soil-600 dark:text-soil-300">
          {t("auth.noAccount")}{" "}
          <Link to="/register" className="font-semibold text-primary-700 hover:underline dark:text-primary-300">
            {t("auth.registerSubmit")}
          </Link>
        </p>
      </div>
    </div>
  );
}
