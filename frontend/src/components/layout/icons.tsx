/** Shared inline SVG icon set (stroke-based, currentColor). */
import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement> & { size?: number };

function base({ size = 20, ...props }: IconProps) {
  return {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.9,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
    ...props,
  };
}

export const DashboardIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <rect x="3" y="3" width="7" height="9" rx="1.5" />
    <rect x="14" y="3" width="7" height="5" rx="1.5" />
    <rect x="14" y="12" width="7" height="9" rx="1.5" />
    <rect x="3" y="16" width="7" height="5" rx="1.5" />
  </svg>
);

export const CropsIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 21v-8" />
    <path d="M12 13c0-3.5-2.5-6-6-6 0 3.5 2.5 6 6 6Z" />
    <path d="M12 13c0-3.5 2.5-6 6-6 0 3.5-2.5 6-6 6Z" />
    <path d="M12 13c0-4-1.5-7-4.5-9" />
  </svg>
);

export const HealthIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M11 3C7 3 4.5 5.8 4.5 9.2c0 4 3 6.8 6.5 6.8 1 0 1.9-.2 2.7-.6l3.6 3.9 2-1.9-3.5-3.8c.9-1.1 1.4-2.5 1.4-4.1C17.2 5.8 15 3 11 3Z" />
    <path d="m9.5 9 1.2 1.4L13 7.6" />
  </svg>
);

export const FertilizerIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 3c-1.5 2-4 3.2-4 6.5C8 12.5 9.8 15 12 15s4-2.5 4-5.5C16 6.2 13.5 5 12 3Z" />
    <path d="M7 21c2-1.5 3.5-2 5-2s3 .5 5 2" />
    <path d="M12 15v4" />
  </svg>
);

export const MarketIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M3 9h18l-1.5 10.5a2 2 0 0 1-2 1.5H6.5a2 2 0 0 1-2-1.5L3 9Z" />
    <path d="M8 9V6a4 4 0 0 1 8 0v3" />
    <path d="m9 13 1.5 3.5L13 12l1.5 4" />
  </svg>
);

export const ScalesIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 3v18" />
    <path d="M5 7h14" />
    <path d="M5 7 2 14h6L5 7Z" />
    <path d="M19 7l-3 7h6l-3-7Z" />
    <path d="M8 21h8" />
  </svg>
);

export const WeatherIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="8" r="4" />
    <path d="M12 2v1.5M12 12.5V14M4.9 4.9l1 1M18.1 4.9l-1 1M2.5 8H4M20 8h1.5" />
    <path d="M7 18h10a3.5 3.5 0 0 0 .5-7 5 5 0 0 0-9.6-1A3.9 3.9 0 0 0 7 18Z" />
  </svg>
);

export const QualityIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m12 3 2.4 4.9 5.4.8-3.9 3.8.9 5.4-4.8-2.5-4.8 2.5.9-5.4L4.2 8.7l5.4-.8L12 3Z" />
  </svg>
);

export const StoreIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 9v11a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9" />
    <path d="M3 9h18l-1-5H4L3 9Z" />
    <path d="M9 21v-6h6v6" />
  </svg>
);

export const ChatIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M21 12a8 8 0 0 1-8 8H4l1.5-3.2A8 8 0 1 1 21 12Z" />
    <path d="M8.5 11h7M8.5 14h4" />
  </svg>
);

export const BellIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" />
    <path d="M10 20a2.2 2.2 0 0 0 4 0" />
  </svg>
);

export const UserIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="8" r="4" />
    <path d="M4 21c1.5-3.5 4.5-5 8-5s6.5 1.5 8 5" />
  </svg>
);

export const SettingsIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="3" />
    <path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.5-2.4 1a7.3 7.3 0 0 0-2-1.2L14 3h-4l-.5 2.6a7.3 7.3 0 0 0-2 1.2l-2.4-1-2 3.5 2 1.5A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.5 2.4-1a7.3 7.3 0 0 0 2 1.2L10 21h4l.5-2.6a7.3 7.3 0 0 0 2-1.2l2.4 1 2-3.5-2-1.5c.1-.4.1-.8.1-1.2Z" />
  </svg>
);

export const LogoutIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <path d="m16 17 5-5-5-5" />
    <path d="M21 12H9" />
  </svg>
);

export const MenuIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 6h16M4 12h16M4 18h16" />
  </svg>
);

export const SunIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
  </svg>
);

export const MoonIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.6 6.6 0 0 0 9.8 9.8Z" />
  </svg>
);

export const UploadIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M12 16V4" />
    <path d="m7 9 5-5 5 5" />
    <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
  </svg>
);

export const CameraIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1Z" />
    <circle cx="12" cy="14" r="3.5" />
  </svg>
);

export const LeafIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M5 19C5 9 11 4 20 4c0 9-5 15-13 15h-2Z" />
    <path d="M5 19c3-5 7-8 11-10" />
  </svg>
);

export const RupeeIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M7 4h10M7 8h10M15 20c-4 0-7-3-7-8" />
    <path d="M7 12h4a4 4 0 0 1 0 8" />
  </svg>
);

export const SproutIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="M7 20h10" />
    <path d="M12 20v-8" />
    <path d="M12 12c-2.5-4-7-4-7 0 0 3 3.5 4 7 0Z" />
    <path d="M12 10c2.5-4 7-4 7 0 0 3-3.5 4-7 0Z" />
  </svg>
);

export const SparklesIcon = (p: IconProps) => (
  <svg {...base(p)}>
    <path d="m12 3 1.8 4.2L18 9l-4.2 1.8L12 15l-1.8-4.2L6 9l4.2-1.8L12 3Z" />
    <path d="M19 16l.9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9L19 16Z" />
  </svg>
);
