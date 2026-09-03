/**
 * Central API type definitions.
 *
 * These mirror the backend's camelCase wire format exactly. The frontend
 * consumes only these standardized shapes — never raw third-party formats
 * (the backend owns external API normalization).
 */

export type Season = "RABI" | "KHARIF" | "ZAID";
export type Severity = "LOW" | "MODERATE" | "HIGH";
export type Risk = "LOW" | "MEDIUM" | "HIGH";
export type ListingStatus = "ACTIVE" | "SOLD" | "EXPIRED";
export type PlantingStatus = "ACTIVE" | "HARVESTED" | "ARCHIVED";
export type RecordType = "DISEASE" | "PEST";
export type TrendDirection = "UP" | "DOWN" | "FLAT";
export type TrendLabel = "UPWARD" | "DOWNWARD" | "FLAT";

// --- Seasons -----------------------------------------------------------------

export interface SeasonInfo {
  id: string; // "rabi" | "kharif" | "zaid"
  name: string;
  label: string;
}

export interface SeasonCrops {
  season: SeasonInfo;
  crops: Crop[];
}

// --- Crops -------------------------------------------------------------------

export interface Crop {
  id: string;
  name: string;
  season: Season;
  scientificName?: string | null;
  imageUrl: string;
  description: string;
  growingPeriodDays?: number | null;
  sowingWindow?: string | null;
  harvestWindow?: string | null;
  supported: boolean;
}

export interface FarmerCrop {
  id: string;
  cropId: string;
  crop: Crop | null;
  season: Season;
  plantingDate?: string | null;
  expectedHarvestDate?: string | null;
  farmSize?: number | null;
  location?: string | null;
  status: PlantingStatus;
  createdAt?: string | null;
}

export interface FarmerCropInput {
  cropId: string;
  plantingDate?: string;
  expectedHarvestDate?: string;
  farmSize?: number;
  location?: string;
}

// --- Disease / pest / treatment information (educational) ----------------------

export interface KnowledgeBase {
  symptoms: string[];
  recommendedAction: string;
  treatment: string;
  organicAlternatives: string;
  prevention: string[];
  sourceNote: string;
}

export interface DiseaseInfo {
  id: string; // slug e.g. "leaf-rust"
  name: string;
  cropIds: string[];
  knowledge: KnowledgeBase;
}

export interface PestInfo {
  id: string; // slug e.g. "aphid"
  name: string;
  cropIds: string[];
  knowledge: KnowledgeBase;
}

export interface Treatment {
  id: string; // slug e.g. "leaf-rust-treatment"
  targetType: "DISEASE" | "PEST";
  targetName: string;
  recommendedAction: string;
  chemicalGuidance: string;
  organicAlternatives: string;
  prevention: string[];
  sourceNote: string;
}

// --- Fertilizers (rule-based guidance) ----------------------------------------

export interface FertilizerInfo {
  id: string;
  name: string;
  category: string;
  growthStages: string[];
  guidance: string;
  sourceNote: string;
}

export interface FertilizerGuidanceRequest {
  cropId: string;
  growthStage: string;
  soilCondition: string;
  npk?: string;
}

export interface FertilizerGuidance {
  crop: string;
  growthStage: string;
  soilCondition: string;
  recommendedCategory: string;
  recommendedFertilizerId: string;
  applicationTiming: string;
  soilNote: string;
  guidance: string;
  sourceNote: string;
}

// --- ML-Based Fertilizer Prediction (XGBoost) --------------------------------

export interface MLFertilizerPredictionRequest {
  crop: string;
  season: string;
  soilType: string;
  nitrogen: number;
  phosphorous: number;
  potassium: number;
  temperature: number;
  humidity: number;
  moisture: number;
}

export interface FertilizerProbabilityItem {
  fertilizer: string;
  probability: number;
}

export interface FertilizerNutrientProfile {
  npkRatio: string;
  primaryFunction: string;
  applicationAdvice: string;
}

export interface FertilizerInputSummary {
  crop: string;
  season: string;
  soilType: string;
  nitrogen: number;
  phosphorous: number;
  potassium: number;
  temperature: number;
  humidity: number;
  moisture: number;
}

export interface MLFertilizerPredictionResponse {
  status: string;
  prediction: string;
  confidence: number;
  confidencePct: number;
  profile?: FertilizerNutrientProfile | null;
  inputSummary?: FertilizerInputSummary | null;
  probabilities: FertilizerProbabilityItem[];
  disclaimer: string;
}

export interface FertilizerPresetItem {
  id: string;
  title: string;
  description: string;
  values: MLFertilizerPredictionRequest;
}

export interface MLFertilizerModelInfo {
  modelName: string;
  modelType: string;
  testAccuracy: number;
  totalClasses: number;
  classes: string[];
  features: string[];
  supportedCrops: Record<string, string[]>;
  supportedSoils: string[];
  supportedSeasons: string[];
}

// --- Farmer-logged health records (observations, not predictions) ---------------

export interface HealthRecord {
  id: string;
  cropId: string;
  cropName: string;
  recordType: RecordType;
  name: string;
  severity: Severity;
  imageUrl: string;
  notes: string;
  createdAt?: string | null;
}

export interface HealthRecordInput {
  recordType: RecordType;
  name: string;
  severity: Severity;
  imageUrl?: string;
  notes?: string;
}

// --- Market (normalized mandi structure) ----------------------------------------

export interface Market {
  id: string;
  name: string;
  city: string;
  state: string;
}

export interface PricePoint {
  date: string;
  minPrice: number;
  maxPrice: number;
  modalPrice: number;
  unit: string;
}

export interface PriceSummary {
  cropId: string;
  cropName: string;
  marketId: string;
  marketName: string;
  currentPrice: number;
  minPrice: number;
  maxPrice: number;
  modalPrice: number;
  unit: string;
  previousPrice: number;
  change: number;
  changePct: number;
  trend7d: number;
  trend14d: number;
  trend30d: number;
  lastUpdated: string;
  source: string; // "mandi-api" | "mandi-db"
}

export interface PriceHistory {
  cropId: string;
  cropName: string;
  marketId: string;
  marketName: string;
  currentPrice: number;
  history: PricePoint[];
  trends: { trend7d: number; trend14d: number; trend30d: number };
  source: string;
}

export interface MarketTrend {
  cropId: string;
  cropName: string;
  marketId: string;
  marketName: string;
  days: number;
  currentPrice: number;
  startPrice: number;
  change: number;
  changePct: number;
  direction: TrendDirection;
  trend7d: number;
  trend14d: number;
  trend30d: number;
  history: PricePoint[];
  note: string;
}

// --- Weather (standardized regardless of provider) --------------------------------

export interface WeatherDay {
  date: string;
  temperatureC: number;
  humidityPct: number;
  rainProbability: number;
  windKph: number;
  condition: string;
}

export interface WeatherAlert {
  severity: "INFO" | "WARNING" | "CRITICAL";
  title: string;
  message: string;
}

export interface LocationSearchResult {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  admin1?: string;
  country?: string;
  countryCode?: string;
}

export interface WeatherResponse {
  location: string;
  lat: number | null;
  lon: number | null;
  today: WeatherDay;
  forecast: WeatherDay[];
  alerts: WeatherAlert[];
  source: string; // "weather-api" | "weather-local"
}

// --- Sell / Hold (rule-based decision support) ------------------------------------

export interface SellHoldRequest {
  cropId: string;
  marketId?: string;
  quantity: number;
  storageDays: number;
  storageCost?: number;
  riskTolerance?: "LOW" | "MEDIUM" | "HIGH";
}

export interface SellHoldResult {
  recommendation: "SELL" | "HOLD";
  reason: string;
  currentPrice: number;
  trend: TrendLabel;
  trendChangePct: number;
  projectedPrice: number;
  storageCost: number;
  expectedAdditionalReturn: number;
  risk: Risk;
  cropId: string;
  cropName: string;
  marketId: string;
  marketName: string;
  quantity: number;
  storageDays: number;
  disclaimer: string;
}

// --- Marketplace -------------------------------------------------------------------

export interface CropListing {
  id: string;
  farmerId: string;
  farmerName: string;
  cropId: string;
  cropName: string;
  quantity: number;
  unit: string;
  askingPrice: number;
  qualityGrade?: string | null;
  location?: string | null;
  status: ListingStatus;
  createdAt?: string | null;
}

export interface ListingInput {
  cropId: string;
  quantity: number;
  unit: string;
  askingPrice: number;
  qualityGrade?: string;
  location?: string;
}

export interface ListingQuery {
  search?: string;
  cropId?: string;
  grade?: string;
  status?: string;
  maxPrice?: number;
  sort?: string;
  page?: number;
  pageSize?: number;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// --- Notifications / assistant ------------------------------------------------------

export interface NotificationItem {
  id: string;
  type: string;
  title: string;
  message: string;
  isRead: boolean;
  createdAt?: string | null;
}

export interface NotificationList {
  items: NotificationItem[];
  unreadCount: number;
}

export interface AssistantMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  createdAt?: string | null;
}

export interface AssistantChatResponse {
  conversationId: string;
  reply: AssistantMessage;
  status: string; // "RULE_BASED" | "EXTERNAL_API"
}

export interface Conversation {
  id: string;
  title: string;
  createdAt?: string | null;
  messages: AssistantMessage[];
}

// --- Dashboard aggregation -----------------------------------------------------------

export interface HealthScorePoint {
  date: string;
  score: number;
  name?: string | null;
  severity?: Severity | null;
}

export interface DashboardSummary {
  crop: Crop;
  season: Season;
  healthScore: number;
  healthScoreLabel: string;
  latestRecord: HealthRecord | null;
  marketId: string;
  marketName: string;
  marketPrice: number;
  marketSource: string;
  marketTrend: MarketTrend | null;
  recommendation: "SELL" | "HOLD" | null;
  recommendationRisk: Risk | null;
  expectedAdditionalReturn: number | null;
  healthHistory: HealthScorePoint[];
  weather: WeatherDay | null;
  weatherSource: string | null;
  unreadNotifications: number;
  warnings: string[];
}

// --- Auth / profile --------------------------------------------------------------------

export interface FarmerProfile {
  id: string;
  phone?: string | null;
  village?: string | null;
  district?: string | null;
  state?: string | null;
  language: string;
  farmSizeAcres?: number | null;
}

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt?: string | null;
  profile: FarmerProfile | null;
}

export interface AuthResponse {
  token: string;
  tokenType: string;
  expiresInDays: number;
  user: User;
}

export interface SystemStatus {
  status: string;
  app: string;
  version: string;
  integrations: {
    weatherApi: boolean;
    mandiApi: boolean;
    assistantApi: boolean;
    redisCache: boolean;
  };
  features: Record<string, boolean>;
}

// --- ML Crop Recommendation --------------------------------------------------

export interface CropRecommendationInput {
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
}

export interface CropAlternative {
  crop: string;
  cropLabel: string;
  probability: number;
}

export interface AgronomicGuide {
  season: string;
  waterRequirement: string;
  soilType: string;
  growthDurationDays: string;
  fertilizerTip: string;
  advisoryNote: string;
  icon: string;
}

export interface CropRecommendationResult {
  recommendedCrop: string;
  cropLabel: string;
  confidence: number;
  alternatives: CropAlternative[];
  agronomicGuide: AgronomicGuide;
  modelName: string;
  modelAccuracy: number;
  inputParameters: Record<string, number>;
}

export interface ModelInfo {
  modelName: string;
  modelType: string;
  testAccuracy: number;
  crossValScore: number;
  totalClasses: number;
  classes: string[];
  features: string[];
}

export interface PresetItem {
  id: string;
  title: string;
  description: string;
  values: CropRecommendationInput;
}
