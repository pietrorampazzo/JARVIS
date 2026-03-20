import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useCart } from "@/context/CartContext";
import { createPageUrl } from "@/utils";
import { ShoppingCart, Menu, X } from "lucide-react";

export default function Header() {
    const { cartCount, setIsCartOpen } = useCart();
    const location = useLocation();
    const [isMenuOpen, setIsMenuOpen] = React.useState(false);

    const navLinks = [
        { name: "Início", path: createPageUrl("Home") },
        { name: "Atas Vigentes", path: createPageUrl("ItensAtas") },
        { name: "Produtos", path: createPageUrl("Produtos") },
        { name: "Marcas", path: createPageUrl("Marcas") },
        { name: "Sobre Nós", path: createPageUrl("Sobre") },
        { name: "Contato", path: createPageUrl("Contato") },
    ];

    return (
        <header className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-20">
                    <Link to="/" className="flex items-center">
                        {/* Logo real (Aumentado em ~30% a 50%) */}
                        <img
                            src="/images/logo.png"
                            alt="Arte Comercial Brasil"
                            className="h-14 lg:h-16 w-auto object-contain"
                            onError={(e) => {
                                e.currentTarget.style.display = 'none';
                                e.currentTarget.nextElementSibling?.classList.remove('hidden');
                            }}
                        />
                        {/* Fallback de texto caso a imagem não exista ou falhe no carregamento */}
                        <div className="hidden text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 text-transparent bg-clip-text">
                            Arte Comercial
                        </div>
                    </Link>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex flex-1 justify-center space-x-8">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                to={link.path}
                                className={`text-sm font-medium transition-colors hover:text-blue-600 ${location.pathname === link.path ? "text-blue-600" : "text-gray-600"
                                    }`}
                            >
                                {link.name}
                            </Link>
                        ))}
                    </nav>

                    <div className="flex items-center space-x-4">
                        <button
                            className="relative p-2 text-gray-600 hover:text-blue-600 transition-colors cursor-pointer"
                            onClick={() => setIsCartOpen(true)}
                        >
                            <ShoppingCart className="w-6 h-6" />
                            {cartCount > 0 && (
                                <span className="absolute top-0 right-0 -mt-1 -mr-1 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-[10px] font-bold text-white">
                                    {cartCount}
                                </span>
                            )}
                        </button>

                        {/* Mobile menu button */}
                        <button
                            className="md:hidden p-2 text-gray-600"
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                        >
                            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Nav */}
            {isMenuOpen && (
                <div className="md:hidden bg-white border-b">
                    <div className="px-4 py-2 space-y-1">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                to={link.path}
                                onClick={() => setIsMenuOpen(false)}
                                className={`block px-3 py-2 rounded-md text-base font-medium ${location.pathname === link.path
                                    ? "bg-blue-50 text-blue-600"
                                    : "text-gray-600 hover:bg-gray-50 hover:text-blue-600"
                                    }`}
                            >
                                {link.name}
                            </Link>
                        ))}
                    </div>
                </div>
            )}
        </header>
    );
}
