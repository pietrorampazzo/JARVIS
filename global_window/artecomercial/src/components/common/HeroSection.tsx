import React from "react";
import { Link } from "react-router-dom";
import { Button } from "../ui/button";
import { createPageUrl } from "@/utils";
import { motion } from "framer-motion";
import { ArrowRight, Search } from "lucide-react";

export default function HeroSection() {
    return (
        <section className="relative bg-gradient-to-br from-blue-900 to-gray-900 overflow-hidden text-white">
            <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?ixlib=rb-4.0.3')] blur-sm opacity-20 bg-cover bg-center"></div>
            <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="text-center lg:text-left lg:w-2/3"
                >
                    <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight mb-6">
                        Gestão e Venda de <span className="text-blue-400">Atas Governamentais</span>
                    </h1>
                    <p className="text-xl lg:text-2xl text-gray-300 mb-10 max-w-3xl leading-relaxed">
                        Mais de 51 anos de tradição. Fornecemos instrumentos musicais e equipamentos de áudio para órgãos públicos com excelência e credibilidade.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                        <Button asChild size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-6 rounded-xl">
                            <Link to={createPageUrl("ItensAtas")}>
                                Explorar Atas Vigentes
                                <ArrowRight className="ml-2 w-5 h-5" />
                            </Link>
                        </Button>
                        <Button asChild variant="outline" size="lg" className="border-gray-500 text-black hover:bg-white/10 hover:text-white px-8 py-6 rounded-xl text-lg backdrop-blur-sm">
                            <Link to={createPageUrl("Contato")}>
                                Falar com Consultor
                            </Link>
                        </Button>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
