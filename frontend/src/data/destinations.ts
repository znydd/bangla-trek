/**
 * Predefined destinations in Bangladesh — divisions + popular tourist spots.
 * Used as the canonical list for the destination combobox so that
 * overlap matching works with exact strings (no fuzzy mismatch).
 */
export const BANGLADESH_DESTINATIONS = [
  // Divisions
  "Dhaka",
  "Chattogram",
  "Rajshahi",
  "Khulna",
  "Barishal",
  "Sylhet",
  "Rangpur",
  "Mymensingh",

  // Popular tourist destinations
  "Cox's Bazar",
  "Sundarbans",
  "Saint Martin's Island",
  "Bandarban",
  "Rangamati",
  "Khagrachari",
  "Sajek Valley",
  "Srimangal",
  "Kuakata",
  "Ratargul Swamp Forest",
  "Jaflong",
  "Paharpur",
  "Mahasthangarh",
  "Sonargaon",
  "Lawachara National Park",
  "Tanguar Haor",
  "Nijhum Dwip",
  "Teknaf",
  "Kaptai Lake",
  "Boga Lake",
  "Nafakhum Waterfall",
  "Bichanakandi",
  "Lalakhal",
  "Ratargul",
  "Comilla",
  "Bogura",
] as const;

export type Destination = (typeof BANGLADESH_DESTINATIONS)[number];
