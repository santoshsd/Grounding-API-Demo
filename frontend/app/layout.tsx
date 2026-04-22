import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";

export const metadata: Metadata = {
  title: "Grounding API Comparison",
  description: "Side-by-side comparison of grounding-capable LLM APIs.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <Script id="posthog-init" strategy="afterInteractive">
          {`
            !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+" (stub)"},o="init bs ws capture calculateEventProperties je Fe getFeatureFlag getFeatureFlagPayload getRemoteConfig isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset debug changePersonId createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing startSessionRecording stopSessionRecording sessionRecordingStarted loadToolbar captureException".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
            posthog.init('phc_xdQkboG6UafFXxDPWLHFiZQWH3C7xGyYPjtqqqCRKh8b', {
              api_host: 'https://t.s13i.me',
              defaults: '2026-01-30',
              capture_exceptions: true,
              cross_subdomain_cookie: true,
            });
          `}
        </Script>
        <header className="border-b border-[var(--border)] px-6 py-4 flex items-center justify-between">
          <Link href="/" className="font-semibold text-lg">
            Grounding API Comparison
          </Link>
          <nav className="flex gap-4 text-sm text-[var(--muted)]">
            <Link href="/" className="hover:text-[var(--fg)]">Run</Link>
            <Link href="/compare" className="hover:text-[var(--fg)]">Compare</Link>
          </nav>
        </header>
        <main className="p-6 max-w-[1400px] mx-auto">{children}</main>
      </body>
    </html>
  );
}
