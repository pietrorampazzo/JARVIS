import React from "react";
import { Link } from "react-router-dom";
import { createPageUrl } from "@/utils";

import { MapPin, Phone, Mail } from "lucide-react";

export default function Footer() {
    return (
        <footer className="bg-slate-900 text-gray-300 py-16 border-t border-slate-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
                    <div className="col-span-1 md:col-span-2">
                        <div className="mb-6">
                            {/* Logo no Rodapé */}
                            <img
                                src="/images/logo.png"
                                alt="Arte Comercial"
                                className="h-12 w-auto brightness-0 invert opacity-90"
                                onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                    e.currentTarget.nextElementSibling?.classList.remove('hidden');
                                }}
                            />
                            {/* Fallback de texto caso a imagem não carregue */}
                            <span className="hidden text-white text-2xl font-bold tracking-tight">artecomercial</span>
                        </div>
                        <p className="text-sm text-slate-400 mb-8 max-w-md leading-relaxed">
                            Mais de 20 anos em licitações governamentais e 51 anos no mercado de instrumentos musicais e áudio. Tradição e credibilidade no atendimento ao setor público.
                        </p>

                        <ul className="space-y-4 text-sm text-slate-300">
                            <li className="flex items-start">
                                <Phone className="w-5 h-5 mr-3 text-blue-400 mt-0.5" />
                                <a href="https://wa.me/5511994103374" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 transition-colors">
                                    (11) 99410-3374
                                </a>
                            </li>
                            <li className="flex items-start">
                                <Mail className="w-5 h-5 mr-3 text-blue-400 mt-0.5" />
                                <a href="mailto:pietro@artecomercialbrasil.com.br" className="hover:text-blue-400 transition-colors">
                                    pietro@artecomercialbrasil.com.br
                                </a>
                            </li>
                            <li className="flex items-start">
                                <MapPin className="w-5 h-5 mr-3 text-blue-400 mt-0.5" />
                                <span>Avenida Esperança, 808 - CEP: 07095-005<br />São Paulo, SP</span>
                            </li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white font-bold text-lg mb-6">Links Úteis</h4>
                        <ul className="space-y-3 text-sm text-slate-400">
                            <li><Link to={createPageUrl("Home")} className="hover:text-blue-400 transition-colors">Home</Link></li>
                            <li><Link to={createPageUrl("ItensAtas")} className="hover:text-blue-400 transition-colors">Atas Vigentes</Link></li>
                            <li><Link to={createPageUrl("Produtos")} className="hover:text-blue-400 transition-colors">Produtos</Link></li>
                            <li><Link to={createPageUrl("Marcas")} className="hover:text-blue-400 transition-colors">Marcas</Link></li>
                            <li><Link to={createPageUrl("Sobre")} className="hover:text-blue-400 transition-colors">Sobre Nós</Link></li>
                            <li><Link to={createPageUrl("Contato")} className="hover:text-blue-400 transition-colors">Contato</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white font-bold text-lg mb-6">Marcas Oficiais</h4>
                        <ul className="space-y-3 text-sm text-slate-400">
                            <li>Yamaha</li>
                            <li>Tama</li>
                            <li>D'Addario</li>
                            <li>Evans</li>
                            <li>Vandoren</li>
                            <li>Pearl</li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-800 mt-12 pt-8 text-sm text-center">
                    <p>&copy; {new Date().getFullYear()} Arte Comercial Brasil. Todos os direitos reservados.</p>
                </div>
            </div>
        </footer>
    );
}
