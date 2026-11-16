/**
 * languages.js - har tool ki language dropdown yahin se aati hai.
 * Nayi language = neeche ek line add karo.
 * `value` wahi naam hai jo AI ko prompt mein jaata hai.
 */
const INDIAN = [
  "Hindi", "Hinglish", "Punjabi", "Gujarati", "Marathi", "Bengali",
  "Tamil", "Telugu", "Kannada", "Malayalam", "Odia", "Assamese",
  "Urdu", "Nepali", "Sanskrit",
];

const INTERNATIONAL = [
  "English", "Japanese", "German", "French", "Spanish", "Portuguese",
  "Italian", "Russian", "Chinese (Simplified)", "Korean", "Arabic",
  "Turkish", "Dutch", "Indonesian", "Thai", "Vietnamese",
];

const toOption = (name, group) => ({ value: name, label: `${name} (${group})` });

// Summary / Draft: Hinglish bhi chalega
export const LANGUAGE_OPTIONS = [
  ...INDIAN.map((l) => toOption(l, "Indian")),
  ...INTERNATIONAL.map((l) => toOption(l, "International")),
];

// Translation: Hinglish asli language nahi hai, isliye hata di
export const TRANSLATE_OPTIONS = LANGUAGE_OPTIONS.filter((o) => o.value !== "Hinglish");