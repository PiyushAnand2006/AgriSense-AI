import { apiClient } from "./apiClient";
import type { CropListing, ListingInput, Page } from "@/types/api";

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

export const marketplaceService = {
  list(query: ListingQuery = {}) {
    return apiClient.get<Page<CropListing>>("/listings", { ...query });
  },
  create(input: ListingInput) {
    return apiClient.post<CropListing>("/listings", input);
  },
  detail(id: string) {
    return apiClient.get<CropListing>(`/listings/${id}`);
  },
  update(id: string, input: Partial<ListingInput> & { status?: string }) {
    return apiClient.patch<CropListing>(`/listings/${id}`, input);
  },
  remove(id: string) {
    return apiClient.delete<void>(`/listings/${id}`);
  },
};
