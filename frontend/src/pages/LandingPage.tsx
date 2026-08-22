import { Link } from "react-router-dom";
import { useI18n } from "@/i18n/I18nProvider";
import { useAuth } from "@/auth/AuthProvider";
import heroField from "@/assets/hero-field.svg";
import illHealth from "@/assets/ill-health.svg";
import illMarket from "@/assets/ill-market.svg";
import illSellHold from "@/assets/ill-sellhold.svg";
import logo from "@/assets/logo.svg";
import {
  ChatIcon,
  HealthIcon,
  LeafIcon,
  MarketIcon,
  QualityIcon,
  RupeeIcon,
  ScalesIcon,
  StoreIcon,
  WeatherIcon,
} from "@/components/layout/icons";

export default function LandingPage() {
  const { t } = useI18n();
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-soil-50 dark:bg-soil-950">
      {/* Nav */}
      <header className="sticky top-0 z-30 border-b border-soil-200/60 bg-soil-50/90 backdrop-blur dark:border-soil-800 dark:bg-soil-950/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-2.5">
            <img src={logo} alt="" className="h-9 w-9" />
            <p className="font-display text-lg font-extrabold text-soil-950 dark:text-white">
              AgriSense <span className="text-primary-600 dark:text-primary-400">AI</span>
            </p>
          </div>
          <nav className="flex items-center gap-2">
            {user ? (
              <Link to="/dashboard" className="btn-primary">
                {t("nav.dashboard")}
              </Link>
            ) : (
              <>
                <Link to="/login" className="btn-secondary">
                  {t("nav.login")}
                </Link>
                <Link to="/register" className="btn-primary">
                  {t("nav.register")}
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-14 sm:px-6 lg:grid-cols-2 lg:py-20">
        <div className="animate-fade-in-up">
          <p className="chip mb-4 bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-200">
            <LeafIcon size={14} />
            {t("app.tagline")}
          </p>
          <h1 className="text-balance font-display text-4xl font-extrabold leading-tight tracking-tight text-soil-950 dark:text-white sm:text-5xl">
            {t("landing.heroTitle")}
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-soil-600 dark:text-soil-300">
            {t("landing.heroSubtitle")}
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to={user ? "/dashboard" : "/login"} className="btn-primary !px-6 !py-3 !text-base">
              {t("landing.heroCtaPrimary")}
            </Link>
            <a href="#how" className="btn-secondary !px-6 !py-3 !text-base">
              {t("landing.heroCtaSecondary")}
            </a>
          </div>
          <p className="mt-4 text-xs text-soil-500 dark:text-soil-400">{t("landing.footerNote")}</p>
        </div>
        <img
          src={heroField}
          alt=""
          className="mx-auto w-full max-w-md drop-shadow-xl animate-fade-in"
          loading="eager"
        />
      </section>

      {/* Problems */}
      <section className="border-y border-soil-200/60 bg-white py-14 dark:border-soil-800 dark:bg-soil-900">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <h2 className="section-title text-center">{t("landing.problemTitle")}</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {[
              { icon: HealthIcon, title: t("landing.problem1Title"), body: t("landing.problem1Body"), art: illHealth },
              { icon: MarketIcon, title: t("landing.problem2Title"), body: t("landing.problem2Body"), art: illMarket },
              { icon: ScalesIcon, title: t("landing.problem3Title"), body: t("landing.problem3Body"), art: illSellHold },
            ].map((item) => (
              <div key={item.title} className="card p-6">
                <img src={item.art} alt="" className="mx-auto h-28" loading="lazy" />
                <h3 className="mt-4 font-display text-lg font-bold text-soil-950 dark:text-white">
                  {item.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-soil-600 dark:text-soil-300">{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
        <h2 className="section-title text-center">{t("landing.howTitle")}</h2>
        <ol className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((n) => (
            <li key={n} className="card relative p-6">
              <span className="absolute -top-3 left-6 flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 font-display text-sm font-extrabold text-white shadow-glow">
                {n}
              </span>
              <h3 className="mt-3 font-display text-base font-bold text-soil-950 dark:text-white">
                {t(`landing.howStep${n}Title`)}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-soil-600 dark:text-soil-300">
                {t(`landing.howStep${n}Body`)}
              </p>
            </li>
          ))}
        </ol>
      </section>

      {/* Features */}
      <section className="border-y border-soil-200/60 bg-white py-14 dark:border-soil-800 dark:bg-soil-900">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <h2 className="section-title text-center">{t("landing.featuresTitle")}</h2>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { icon: HealthIcon, title: t("landing.feature1"), body: t("landing.feature1Body") },
              { icon: LeafIcon, title: t("landing.feature2"), body: t("landing.feature2Body") },
              { icon: RupeeIcon, title: t("landing.feature3"), body: t("landing.feature3Body") },
              { icon: WeatherIcon, title: t("landing.feature4"), body: t("landing.feature4Body") },
              { icon: StoreIcon, title: t("landing.feature5"), body: t("landing.feature5Body") },
              { icon: ChatIcon, title: t("landing.feature6"), body: t("landing.feature6Body") },
            ].map((feature) => (
              <div key={feature.title} className="card flex gap-4 p-5">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
                  <feature.icon size={22} />
                </span>
                <div>
                  <h3 className="font-display text-base font-bold text-soil-950 dark:text-white">
                    {feature.title}
                  </h3>
                  <p className="mt-1 text-sm leading-relaxed text-soil-600 dark:text-soil-300">
                    {feature.body}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
        <div className="grid items-center gap-8 lg:grid-cols-2">
          <h2 className="section-title">{t("landing.benefitsTitle2")}</h2>
          <ul className="grid gap-4 sm:grid-cols-2">
            {[1, 2, 3, 4].map((n) => (
              <li key={n} className="card p-4">
                <p className="font-semibold text-soil-950 dark:text-white">
                  <QualityIcon size={16} className="mb-0.5 mr-1.5 inline text-accent-500" />
                  {t(`landing.benefit${n}`)}
                </p>
                <p className="mt-1 text-sm text-soil-600 dark:text-soil-300">
                  {t(`landing.benefit${n}Body`)}
                </p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-primary-700 py-14 dark:bg-primary-900">
        <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
          <h2 className="font-display text-3xl font-extrabold text-white">{t("landing.ctaTitle")}</h2>
          <p className="mx-auto mt-3 max-w-xl text-primary-100">{t("landing.ctaBody")}</p>
          <Link to="/login" className="btn-accent mt-7 !px-7 !py-3 !text-base">
            {t("landing.ctaButton")}
          </Link>
        </div>
      </section>

      <footer className="border-t border-soil-200/60 py-6 text-center text-xs text-soil-500 dark:border-soil-800 dark:text-soil-400">
        <p>
          AgriSense AI — {t("landing.footerNote")}
        </p>
      </footer>
    </div>
  );
}
