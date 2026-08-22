/**
 * Central feature flags.
 *
 * The backend is the source of truth for which integrations are active
 * (see GET /api/v1/system — `integrations`). These frontend flags control
 * UI affordances only.
 */
export const features = {
  cropCatalog: true,
  diseaseInfo: true,
  pestInfo: true,
  treatmentInfo: true,
  fertilizerGuidance: true,
  marketPrices: true,
  marketTrends: true,
  sellHoldRules: true,
  healthRecords: true,
  marketplace: true,
  assistant: true,
  weatherIntegration: true,
  offlineSupport: true,
} as const;

export type FeatureKey = keyof typeof features;
