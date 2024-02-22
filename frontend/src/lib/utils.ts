import { type ClassValue, clsx } from ".pnpm/clsx@2.1.0/node_modules/clsx";
import { twMerge } from ".pnpm/tailwind-merge@2.2.1/node_modules/tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
