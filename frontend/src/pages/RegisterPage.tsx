import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/auth/AuthProvider";
import { useI18n } from "@/i18n/I18nProvider";
import { useToast } from "@/components/ui/Toast";
import { Spinner } from "@/components/ui/primitives";
import { ApiError } from "@/services/apiClient";
import logo from "@/assets/logo.svg";

export default function RegisterPage() {
  const { t } = useI18n();
  const { register } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    village: "",
    district: "",
    state: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = (field: keyof typeof form) => (value: string) =>
    setForm((current) => ({ ...current, [field]: value }));

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      await register(form);
      showToast(t("dashboard.title"), "success");
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("common.error"));
    } finally {
      setSubmitting(false);
    }
  };

  const fields: { id: keyof typeof form; label: string; type?: string; required?: boolean }[] = [
    { id: "name", label: t("auth.name"), required: true },
    { id: "email", label: t("auth.email"), type: "email", required: true },
    { id: "password", label: t("auth.password"), type: "password", required: true },
    { id: "village", label: t("auth.village") },
    { id: "district", label: t("auth.district") },
    { id: "state", label: t("auth.state"), required: true },
  ];

  return (
    <div className="flex min-h-screen items-center justify-center bg-soil-50 px-4 py-10 dark:bg-soil-950">
      <div className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center gap-3 text-center">
          <img src={logo} alt="" className="h-14 w-14" />
          <div>
            <h1 className="font-display text-2xl font-extrabold text-soil-950 dark:text-white">
              {t("auth.registerTitle")}
            </h1>
            <p className="mt-1 text-sm text-soil-500 dark:text-soil-400">
              {t("auth.registerSubtitle")}
            </p>
          </div>
        </div>

        <form onSubmit={submit} className="card space-y-4 p-6" noValidate>
          {fields.map((field) => (
            <div key={field.id}>
              <label htmlFor={`register-${field.id}`} className="label">
                {field.label}
              </label>
              <input
                id={`register-${field.id}`}
                type={field.type ?? "text"}
                className="input"
                required={field.required}
                value={form[field.id]}
                onChange={(event) => update(field.id)(event.target.value)}
              />
            </div>
          ))}

          {error && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm font-medium text-red-700 dark:bg-red-900/30 dark:text-red-300">
              {error}
            </p>
          )}

          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? <Spinner className="h-4 w-4" /> : t("auth.registerSubmit")}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-soil-600 dark:text-soil-300">
          {t("auth.hasAccount")}{" "}
          <Link to="/login" className="font-semibold text-primary-700 hover:underline dark:text-primary-300">
            {t("auth.loginSubmit")}
          </Link>
        </p>
      </div>
    </div>
  );
}
