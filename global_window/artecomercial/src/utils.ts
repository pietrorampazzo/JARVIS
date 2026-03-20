import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Rotas utilitárias, caso as rotas fiquem dinâmicas no futuro
export function createPageUrl(page: string) {
  const map: Record<string, string> = {
    "Home": "/",
    "ItensAtas": "/atas",
    "Produtos": "/produtos", // Opcional, talvez usar a mesma página de atas para produtos
    "Marcas": "/marcas",
    "Sobre": "/sobre",
    "Contato": "/contato",
    "Checkout": "/checkout"
  };
  return map[page] || "/";
}
