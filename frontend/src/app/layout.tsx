import "@/styles/globals.css";
import "katex/dist/katex.min.css";

import type { Metadata } from "next";
import Script from "next/script";

import { ThemeProvider } from "@/components/theme-provider";
import { I18nProvider } from "@/core/i18n/context";
import { detectLocaleServer } from "@/core/i18n/server";

export const metadata: Metadata = {
  title: "DeerFlow",
  description: "A LangChain-based framework for building super agents.",
};

const performanceMeasureGuard = `
  (function () {
    const perf = window.performance;
    if (!perf || typeof perf.measure !== "function") {
      return;
    }
    const originalMeasure = perf.measure.bind(perf);
    perf.measure = function (...args) {
      try {
        return originalMeasure(...args);
      } catch (error) {
        const message =
          typeof error?.message === "string" ? error.message : "";
        if (message.includes("negative time stamp")) {
          return null;
        }
        throw error;
      }
    };
  })();
`;

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const locale = await detectLocaleServer();
  return (
    <html lang={locale} suppressContentEditableWarning suppressHydrationWarning>
      <body>
        <Script
          id="performance-measure-guard"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{ __html: performanceMeasureGuard }}
        />
        <ThemeProvider attribute="class" enableSystem disableTransitionOnChange>
          <I18nProvider initialLocale={locale}>{children}</I18nProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
