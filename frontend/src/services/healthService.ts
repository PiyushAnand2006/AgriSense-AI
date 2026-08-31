/**
 * Health API — image uploads + farmer-logged health records.
 *
 * Farmers browse disease/pest information via diseaseService/pestService
 * and log their own field observations here.
 */
import { apiClient } from "./apiClient";
import type { HealthRecord, HealthRecordInput, RecordType } from "@/types/api";

export interface UploadResult {
  url: string;
}

export const healthService = {
  uploadImage: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.postForm<UploadResult>("/uploads", formData);
  },

  records: (cropId: string, recordType?: RecordType) =>
    apiClient.get<HealthRecord[]>(`/crops/${cropId}/records`, {
      recordType,
    }),

  logRecord: (cropId: string, input: HealthRecordInput) =>
    apiClient.post<HealthRecord>(`/crops/${cropId}/records`, input),

  deleteRecord: (cropId: string, recordId: string) =>
    apiClient.delete<void>(`/crops/${cropId}/records/${recordId}`),
};
