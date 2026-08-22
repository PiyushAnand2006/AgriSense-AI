import { useEffect, useRef, useState, type FormEvent } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { assistantService } from "@/services/assistantService";
import { useToast } from "@/components/ui/Toast";
import { Spinner } from "@/components/ui/primitives";
import { ApiError } from "@/services/apiClient";
import type { AssistantMessage } from "@/types/api";
import { formatDateTime } from "@/utils/format";

const SUGGESTED_KEYS = ["q1", "q2", "q3", "q4", "q5"] as const;

export default function AssistantPage() {
  const { t } = useI18n();
  const { showToast } = useToast();
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [assistantStatus, setAssistantStatus] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || sending) return;
    setSending(true);
    setInput("");
    const optimisticUser: AssistantMessage = { id: Date.now(), role: "user", content: message, createdAt: null };
    setMessages((current) => [...current, optimisticUser]);
    try {
      const result = await assistantService.chat(message, conversationId ?? undefined);
      setConversationId(result.data.conversationId);
      setAssistantStatus(result.data.status);
      setMessages((current) => [...current, result.data.reply]);
    } catch (err) {
      // Revert optimistic message on failure.
      setMessages((current) => current.filter((m) => m.id !== optimisticUser.id));
      setInput(message);
      showToast(err instanceof ApiError ? err.message : t("common.error"), "error");
    } finally {
      setSending(false);
    }
  };

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void send(input);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="font-display text-2xl font-extrabold">{t("assistant.title")}</h1>
        {assistantStatus && (
          <span className="chip bg-soil-100 text-soil-600 dark:bg-soil-800 dark:text-soil-300">
            {assistantStatus === "EXTERNAL_API" ? "🌐 API" : "📋 RULES"}
          </span>
        )}
      </div>

      {/* Conversation */}
      <div
        className="card flex-1 space-y-3 overflow-y-auto p-5"
        role="log"
        aria-label={t("assistant.title")}
        aria-live="polite"
      >
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <p className="font-display text-lg font-bold">{t("assistant.suggested")}</p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTED_KEYS.map((key) => (
                <button
                  key={key}
                  type="button"
                  className="chip border border-soil-200 hover:border-primary-400 hover:text-primary-700 dark:border-soil-700 dark:hover:text-primary-300"
                  onClick={() => void send(t(`assistant.${key}`))}
                >
                  {t(`assistant.${key}`)}
                </button>
              ))}
            </div>
            <p className="text-xs text-soil-500 dark:text-soil-400">{t("assistant.note")}</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={`${message.id}-${message.role}`}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  message.role === "user"
                    ? "bg-primary-600 text-white"
                    : "bg-soil-100 text-soil-900 dark:bg-soil-800 dark:text-soil-100"
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.createdAt && (
                  <p className={`mt-1 text-[10px] ${message.role === "user" ? "text-white/70" : "text-soil-500 dark:text-soil-400"}`}>
                    {formatDateTime(message.createdAt)}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
        {sending && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-soil-100 px-4 py-3 dark:bg-soil-800">
              <Spinner className="h-4 w-4 text-soil-500" />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <form onSubmit={submit} className="card flex items-center gap-3 p-3">
        <label htmlFor="assistant-input" className="sr-only">
          {t("assistant.placeholder")}
        </label>
        <input
          id="assistant-input"
          className="input flex-1"
          placeholder={t("assistant.placeholder")}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={sending}
        />
        <button type="submit" className="btn-primary" disabled={sending || !input.trim()}>
          {t("assistant.send")}
        </button>
      </form>
      <p className="text-center text-xs text-soil-500 dark:text-soil-400">{t("assistant.note")}</p>
    </div>
  );
}
