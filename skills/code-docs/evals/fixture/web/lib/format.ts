/**
 * Formats a price in euros.
 * @param value Amount in cents.
 * @param locale BCP 47 locale.
 * @returns The formatted price.
 */
export function formatPrice(value: number, locale = "de-DE"): string {
  return new Intl.NumberFormat(locale, { style: "currency", currency: "EUR" }).format(value / 100);
}

export function slug(text: string): string { // expect: DOC-MISSING
  return text.toLowerCase().replace(/\s+/g, "-");
}

/** Joins path parts. */
export const join = (a: string, b: string): string => `${a}/${b}`; // expect-full: DOC-ARGS-MISSING, DOC-RETURNS-MISSING

/**
 * Shortens a text.
 * @param text Input.
 * @param max Old name of the limit.
 */
export function truncate(text: string, limit: number): string { // expect: DOC-PARAM-MISSING, DOC-PARAM-STALE, DOC-RETURNS-MISSING
  return text.slice(0, limit);
}

/**
 * Renders the order card.
 * @param props Card properties.
 */
export default function OrderCard({ id }: { id: number }) {
  return id;
}

/**
 * Logs a message.
 * @param message Text to log.
 */
export async function log(message: string): Promise<void> {
  console.info(message);
}

export const double = n => n * 2; // expect: DOC-MISSING

export class Cart { // expect: DOC-MISSING
  items: string[] = [];
}

function internal(x: number) {
  return x;
}

export const LIMIT = 10;
