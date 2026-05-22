"use client";

import Image from "next/image";
import {
  createContext,
  type PropsWithChildren,
  useCallback,
  useContext,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";

import closeIcon from "../assets/CloseIcon.svg";

const DEFAULT_ERROR_TITLE = "Something went wrong";
const DEFAULT_ERROR_MESSAGE = "Please try again.";
const ERROR_TOAST_AUTO_DISMISS_MS = 3_000;
const ERROR_TOAST_ANIMATION_MS = 200;

export type ErrorToastContent = {
  title?: string;
  message: string;
};

type ErrorToastProps = {
  error: ErrorToastContent;
  onClose: () => void;
};

type ErrorToastContextValue = {
  clearError: () => void;
  showError: (error: unknown) => void;
};

const ErrorToastContext = createContext<ErrorToastContextValue | null>(null);

export function ErrorToastProvider({ children }: PropsWithChildren) {
  const [error, setError] = useState<ErrorToastContent | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const showError = useCallback((nextError: unknown) => {
    setError(normalizeError(nextError));
  }, []);

  const value = useMemo(
    () => ({
      clearError,
      showError,
    }),
    [clearError, showError],
  );

  return (
    <ErrorToastContext.Provider value={value}>
      {children}
      {error ? <ErrorToast error={error} onClose={clearError} /> : null}
    </ErrorToastContext.Provider>
  );
}

export function useErrorToast() {
  const context = useContext(ErrorToastContext);

  if (!context) {
    throw new Error("useErrorToast must be used inside ErrorToastProvider.");
  }

  return context;
}

export function ErrorToast({ error, onClose }: ErrorToastProps) {
  const messageId = useId();
  const titleId = useId();
  const closeTimeoutRef = useRef<number | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const [isProgressRunning, setIsProgressRunning] = useState(false);

  const closeWithAnimation = useCallback(() => {
    if (closeTimeoutRef.current !== null) {
      return;
    }

    setIsVisible(false);
    closeTimeoutRef.current = window.setTimeout(() => {
      closeTimeoutRef.current = null;
      onClose();
    }, ERROR_TOAST_ANIMATION_MS);
  }, [onClose]);

  useEffect(() => {
    const showAnimationFrame = window.requestAnimationFrame(() => {
      setIsVisible(true);
      setIsProgressRunning(true);
    });
    const dismissTimeout = window.setTimeout(
      closeWithAnimation,
      ERROR_TOAST_AUTO_DISMISS_MS,
    );

    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        closeWithAnimation();
      }
    }

    document.addEventListener("keydown", closeOnEscape);
    return () => {
      window.cancelAnimationFrame(showAnimationFrame);
      window.clearTimeout(dismissTimeout);
      if (closeTimeoutRef.current !== null) {
        window.clearTimeout(closeTimeoutRef.current);
      }
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [closeWithAnimation]);

  return (
    <div className="pointer-events-none fixed inset-x-0 top-0 z-50 flex justify-center px-4 py-5 sm:px-6 sm:py-8">
      <section
        role="alert"
        aria-labelledby={titleId}
        aria-describedby={messageId}
        className={`pointer-events-auto relative h-fit w-full max-w-xl overflow-hidden rounded-md border border-[#E58D8D] bg-white shadow-[0_1rem_3rem_rgba(7,17,31,0.26)] transition-transform duration-200 ease-out dark:border-[#E05A5A]/80 dark:bg-[#07111F] ${
          isVisible ? "translate-y-0" : "-translate-y-4"
        }`}
      >
        <div className="h-2 w-full bg-[#D85858]" />
        <div className="flex items-start gap-3 px-4 py-4 sm:px-5 sm:py-5">
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-4">
              <h2
                id={titleId}
                className="text-xl font-semibold text-[#0F2854] dark:text-white sm:text-2xl"
              >
                {error.title || DEFAULT_ERROR_TITLE}
              </h2>
              <button
                type="button"
                aria-label="Dismiss error"
                className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-[#D9EEF7] bg-white transition hover:bg-[#BDE8F5]/45 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#4988C4] dark:border-[#1C4D8D] dark:bg-[#07111F] dark:hover:bg-[#1C4D8D]/55"
                onClick={closeWithAnimation}
              >
                <Image
                  src={closeIcon}
                  alt=""
                  width={16}
                  height={16}
                  className="dark:brightness-0 dark:invert"
                />
              </button>
            </div>
            <p
              id={messageId}
              className="mt-2 whitespace-pre-wrap wrap-break-word text-sm font-medium leading-6 text-[#3D1720] dark:text-[#FFDCDC]"
            >
              {error.message}
            </p>
          </div>
        </div>
        <div className="h-1 w-full bg-[#F3B7B7] dark:bg-[#E05A5A]/25">
          <div
            className={`h-full bg-[#D85858] ${
              isProgressRunning ? "w-full" : "w-0"
            }`}
            style={{
              transitionDuration: `${ERROR_TOAST_AUTO_DISMISS_MS}ms`,
              transitionProperty: "width",
              transitionTimingFunction: "linear",
            }}
          />
        </div>
      </section>
    </div>
  );
}

function normalizeError(error: unknown): ErrorToastContent {
  if (typeof error === "string") {
    return {
      message: error || DEFAULT_ERROR_MESSAGE,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message || DEFAULT_ERROR_MESSAGE,
    };
  }

  if (isErrorToastContent(error)) {
    return {
      title: error.title,
      message: error.message || DEFAULT_ERROR_MESSAGE,
    };
  }

  return {
    message: DEFAULT_ERROR_MESSAGE,
  };
}

function isErrorToastContent(error: unknown): error is ErrorToastContent {
  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    typeof error.message === "string" &&
    (!("title" in error) ||
      error.title === undefined ||
      typeof error.title === "string")
  );
}
