import Cookies from "js-cookie";
import { createI18n } from "vue-i18n";

interface LocaleData {
  name: string;
  fallback: string | null;
}

const FALLBACK_LOCALE = "en";
const ALL_LOCALES: { [id: string]: LocaleData } = {
  en: {
    name: "🇬🇧 English",
    fallback: null,
  },
  de: {
    name: "🇩🇪 Deutsch",
    fallback: "en",
  },
};

function getLocaleTag() {
  return i18n.global.locale;
}

function getSystemLocale() {
  let rawLocale;
  if (navigator.languages != undefined) {
    rawLocale = navigator.languages[0];
  } else {
    rawLocale = navigator.language;
  }

  if (rawLocale == null) {
    return null;
  }

  return rawLocale.replace(/-.*/, "");
}

function initialLocale() {
  const storedLocale = Cookies.get("client-locale");
  if (storedLocale != null && storedLocale in ALL_LOCALES) {
    return storedLocale;
  }

  const systemLocale = getSystemLocale();
  if (systemLocale != null && systemLocale in ALL_LOCALES) {
    return systemLocale;
  }

  return FALLBACK_LOCALE;
}

const i18n = createI18n({
  locale: initialLocale(),
});

async function ensureLocaleLoaded(locale: string) {
  const messages = await import(/* webpackChunkName: "locale-[request]" */ `./locales/${locale}.json`);
  i18n.global.setLocaleMessage(locale, messages);
}

async function updateLocale(locale: string) {
  if (locale == undefined || !(locale in ALL_LOCALES)) {
    throw "Unknown locale " + locale;
  }

  const localeData = ALL_LOCALES[locale];
  if (localeData.fallback != null) {
    await ensureLocaleLoaded(localeData.fallback);
    i18n.global.fallbackLocale = localeData.fallback;
  }
  await ensureLocaleLoaded(locale);
  i18n.global.locale = locale;

  Cookies.set("client-locale", locale, { sameSite: "lax" });
}

export { updateLocale, getLocaleTag, i18n, ALL_LOCALES };
