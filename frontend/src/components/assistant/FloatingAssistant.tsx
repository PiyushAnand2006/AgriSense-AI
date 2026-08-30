import { useState, useRef, useEffect, type FormEvent } from "react";
import { useI18n } from "@/i18n/I18nProvider";
import { assistantService } from "@/services/assistantService";
import { useToast } from "@/components/ui/Toast";
import { Spinner } from "@/components/ui/primitives";
import { ApiError } from "@/services/apiClient";
import type { AssistantMessage } from "@/types/api";
import { formatDateTime } from "@/utils/format";
import botLogo from "@/assets/ai-assistant-bot.svg";

const SUGGESTED_KEYS = ["q1", "q2", "q3", "q4", "q5"] as const;
const STORAGE_KEY = "agrisense_assistant_pos";

interface Position {
  x: number;
  y: number;
}

export default function FloatingAssistant() {
  const { t } = useI18n();
  const { showToast } = useToast();

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [assistantStatus, setAssistantStatus] = useState<string | null>(null);

  // Position & Drag state
  const [position, setPosition] = useState<Position>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (typeof parsed.x === "number" && typeof parsed.y === "number") {
          return parsed;
        }
      }
    } catch {
      // fallback to default
    }
    // Default initial position on right side
    const initialX = typeof window !== "undefined" ? Math.max(16, window.innerWidth - 86) : 300;
    const initialY = typeof window !== "undefined" ? Math.max(16, window.innerHeight - 150) : 500;
    return { x: initialX, y: initialY };
  });

  const isDraggingRef = useRef(false);
  const dragStartPosRef = useRef<Position>({ x: 0, y: 0 });
  const startButtonPosRef = useRef<Position>({ x: 0, y: 0 });
  const totalMovedDistanceRef = useRef(0);
  const buttonRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages update
  useEffect(() => {
    if (isOpen) {
      endRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  // Adjust position on window resize to ensure button stays on screen
  useEffect(() => {
    const handleResize = () => {
      setPosition((prev) => {
        const maxX = window.innerWidth - 72;
        const maxY = window.innerHeight - 72;
        const nextX = Math.min(Math.max(16, prev.x), Math.max(16, maxX));
        const nextY = Math.min(Math.max(16, prev.y), Math.max(16, maxY));
        return { x: nextX, y: nextY };
      });
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Save position when it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(position));
    } catch {
      // ignore storage errors
    }
  }, [position]);

  // Drag event handlers
  const handlePointerDown = (e: React.PointerEvent) => {
    // Only drag on primary mouse button or touch
    if (e.button !== 0 && e.pointerType === "mouse") return;

    isDraggingRef.current = true;
    dragStartPosRef.current = { x: e.clientX, y: e.clientY };
    startButtonPosRef.current = { ...position };
    totalMovedDistanceRef.current = 0;

    (e.target as HTMLElement).setPointerCapture?.(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDraggingRef.current) return;

    const deltaX = e.clientX - dragStartPosRef.current.x;
    const deltaY = e.clientY - dragStartPosRef.current.y;
    totalMovedDistanceRef.current = Math.hypot(deltaX, deltaY);

    const btnWidth = 64;
    const btnHeight = 64;
    const minX = 12;
    const maxX = window.innerWidth - btnWidth - 12;
    const minY = 12;
    const maxY = window.innerHeight - btnHeight - 12;

    const newX = Math.min(Math.max(minX, startButtonPosRef.current.x + deltaX), maxX);
    const newY = Math.min(Math.max(minY, startButtonPosRef.current.y + deltaY), maxY);

    setPosition({ x: newX, y: newY });
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    if (!isDraggingRef.current) return;
    isDraggingRef.current = false;
    try {
      (e.target as HTMLElement).releasePointerCapture?.(e.pointerId);
    } catch {
      // ignore
    }

    // If moved less than 6 pixels, treat it as a click
    if (totalMovedDistanceRef.current < 6) {
      setIsOpen((prev) => !prev);
    }
  };

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || sending) return;
    setSending(true);
    setInput("");
    const optimisticUser: AssistantMessage = {
      id: Date.now(),
      role: "user",
      content: message,
      createdAt: null,
    };
    setMessages((current) => [...current, optimisticUser]);
    try {
      const result = await assistantService.chat(message, conversationId ?? undefined);
      setConversationId(result.data.conversationId);
      setAssistantStatus(result.data.status);
      setMessages((current) => [...current, result.data.reply]);
    } catch (err) {
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
    <>
      {/* Draggable Floating Assistant Button */}
      <div
        ref={buttonRef}
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          touchAction: "none",
        }}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        className="fixed z-50 flex cursor-grab select-none items-center active:cursor-grabbing"
      >
        <div className="group relative flex items-center">
          {/* Main Round Bot Button */}
          <button
            type="button"
            aria-label="Toggle AI Assistant"
            className={`relative flex h-16 w-16 items-center justify-center rounded-full border-2 border-primary-500 bg-white p-2.5 shadow-2xl transition-transform duration-200 hover:scale-105 active:scale-95 dark:border-primary-400 dark:bg-soil-900 ${
              isOpen ? "ring-4 ring-primary-400/40" : ""
            }`}
          >
            {/* Pulsing Aura */}
            <span className="absolute -inset-1 -z-10 animate-ping rounded-full bg-primary-400/20 duration-1000" />

            {/* Uploaded AI Assistant Bot Logo */}
            <img
              src={botLogo}
              alt="AI Assistant"
              className="h-full w-full object-contain pointer-events-none drop-shadow-sm"
              draggable={false}
            />

            {/* Online Green Badge */}
            <span className="absolute bottom-0.5 right-0.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-emerald-500 shadow-sm dark:border-soil-900" />
          </button>

          {/* Hover Tooltip Pill */}
          {!isOpen && (
            <div className="pointer-events-none absolute right-full mr-3 hidden whitespace-nowrap rounded-xl border border-soil-200 bg-soil-900/90 px-3 py-1.5 text-xs font-bold text-white shadow-lg backdrop-blur transition sm:block dark:border-soil-700 dark:bg-white dark:text-soil-950">
              💬 {t("nav.assistant")}
              <div className="text-[10px] font-normal opacity-80">{t("assistant.note")}</div>
            </div>
          )}
        </div>
      </div>

      {/* Floating Chat Modal / Drawer */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 z-50 flex h-[580px] max-h-[85vh] w-[380px] max-w-[calc(100vw-32px)] flex-col overflow-hidden rounded-3xl border border-soil-200 bg-white/95 shadow-2xl backdrop-blur-xl transition-all duration-300 dark:border-soil-800 dark:bg-soil-900/95 sm:bottom-20 sm:right-6">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-soil-200/80 bg-gradient-to-r from-primary-600 via-primary-700 to-soil-800 px-4 py-3 text-white dark:border-soil-800">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/15 p-1 backdrop-blur">
                <img src={botLogo} alt="" className="h-full w-full object-contain" />
              </div>
              <div>
                <p className="font-display text-sm font-extrabold leading-tight">
                  AgriSense <span className="text-primary-300">AI Assistant</span>
                </p>
                <div className="flex items-center gap-1.5 text-[10px] text-primary-100">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Online · Agro Intelligence</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {assistantStatus && (
                <span className="rounded-full bg-white/20 px-2 py-0.5 text-[10px] font-bold">
                  {assistantStatus === "EXTERNAL_API" ? "🌐 Live" : "📋 Rules"}
                </span>
              )}
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="flex h-7 w-7 items-center justify-center rounded-full text-white/80 transition hover:bg-white/20 hover:text-white"
                aria-label="Close Assistant"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Message List */}
          <div
            className="flex-1 space-y-3 overflow-y-auto p-4 text-xs"
            role="log"
            aria-live="polite"
          >
            {messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-3 py-6 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-50 p-2 dark:bg-primary-950/40">
                  <img src={botLogo} alt="" className="h-full w-full object-contain" />
                </div>
                <div>
                  <p className="font-display text-sm font-bold text-soil-950 dark:text-white">
                    {t("assistant.suggested")}
                  </p>
                  <p className="mt-0.5 text-[11px] text-soil-500 dark:text-soil-400">
                    Ask any agricultural, market, crop health, or fertilizer question:
                  </p>
                </div>
                <div className="flex flex-col gap-1.5 w-full max-w-[280px]">
                  {SUGGESTED_KEYS.map((key) => (
                    <button
                      key={key}
                      type="button"
                      className="rounded-xl border border-soil-200 bg-soil-50 px-3 py-2 text-left text-[11px] font-medium text-soil-700 transition hover:border-primary-500 hover:bg-primary-50 hover:text-primary-700 dark:border-soil-700 dark:bg-soil-800 dark:text-soil-200 dark:hover:border-primary-400 dark:hover:bg-primary-950"
                      onClick={() => void send(t(`assistant.${key}`))}
                    >
                      💡 {t(`assistant.${key}`)}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={`${message.id}-${message.role}`}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
                      message.role === "user"
                        ? "bg-primary-600 text-white"
                        : "bg-soil-100 text-soil-900 dark:bg-soil-800 dark:text-soil-100"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    {message.createdAt && (
                      <p
                        className={`mt-1 text-[9px] ${
                          message.role === "user" ? "text-white/70" : "text-soil-500 dark:text-soil-400"
                        }`}
                      >
                        {formatDateTime(message.createdAt)}
                      </p>
                    )}
                  </div>
                </div>
              ))
            )}
            {sending && (
              <div className="flex justify-start">
                <div className="flex items-center gap-2 rounded-2xl bg-soil-100 px-3.5 py-2 dark:bg-soil-800">
                  <Spinner className="h-3.5 w-3.5 text-primary-600 dark:text-primary-400" />
                  <span className="text-[11px] text-soil-500 dark:text-soil-400">Thinking…</span>
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Bottom Chat Input Form */}
          <form
            onSubmit={submit}
            className="border-t border-soil-200/80 bg-soil-50 p-2.5 dark:border-soil-800 dark:bg-soil-950/60"
          >
            <div className="flex items-center gap-2">
              <input
                id="floating-assistant-input"
                className="input !py-2 !text-xs"
                placeholder={t("assistant.placeholder")}
                value={input}
                onChange={(event) => setInput(event.target.value)}
                disabled={sending}
                autoFocus
              />
              <button
                type="submit"
                className="btn-primary !px-3.5 !py-2 !text-xs shrink-0 font-bold"
                disabled={sending || !input.trim()}
              >
                {t("assistant.send")}
              </button>
            </div>
            <p className="mt-1 text-center text-[10px] text-soil-400 dark:text-soil-500">
              {t("assistant.note")}
            </p>
          </form>
        </div>
      )}
    </>
  );
}
