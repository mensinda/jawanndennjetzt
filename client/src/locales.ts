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
  return i18n.global.locale.value;
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
  const storedLocale = window.localStorage.getItem("client-locale");
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
  legacy: false,
  locale: initialLocale(),
  warnHtmlMessage: false,
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
    i18n.global.fallbackLocale.value = localeData.fallback;
  }
  await ensureLocaleLoaded(locale);
  i18n.global.locale.value = locale;

  window.localStorage.setItem("client-locale", locale);
}

export { updateLocale, getLocaleTag, i18n, ALL_LOCALES };
