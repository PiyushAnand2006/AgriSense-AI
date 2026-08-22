import { apiClient } from "./apiClient";
import type { AssistantChatResponse, Conversation } from "@/types/api";

export const assistantService = {
  chat(message: string, conversationId?: string) {
    return apiClient.post<AssistantChatResponse>("/assistant/chat", {
      message,
      conversationId,
    });
  },
  conversations() {
    return apiClient.get<Pick<Conversation, "id" | "title" | "createdAt">[]>(
      "/assistant/conversations",
    );
  },
  conversation(id: string) {
    return apiClient.get<Conversation>(`/assistant/conversations/${id}`);
  },
};
