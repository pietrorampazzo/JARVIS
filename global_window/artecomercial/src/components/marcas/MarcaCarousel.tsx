import React from "react";
import { motion } from "framer-motion";

export default function MarcaCarousel({ marcas }: { marcas: any[] }) {
    return (
        <section className="py-24 bg-white overflow-hidden">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12 text-center">
                <h2 className="text-2xl font-semibold text-gray-500 uppercase tracking-widest">
                    Marcas que Representamos
                </h2>
            </div>
            <div className="relative flex overflow-x-hidden group">
                <div className="flex animate-marquee space-x-16 px-8 items-center">
                    {[...marcas, ...marcas, ...marcas].map((marca, i) => (
                        <div key={`${marca.id}-${i}`} className="flex-shrink-0 grayscale hover:grayscale-0 opacity-50 hover:opacity-100 transition-all duration-300 cursor-pointer w-48 h-24 flex items-center justify-center">
                            {marca.logo_url ? (
                                <img
                                    src={marca.logo_url}
                                    alt={marca.nome}
                                    className={`max-w-full object-contain transition-transform duration-300 ${['Vandoren', 'Evans'].includes(marca.nome)
                                            ? 'scale-[1.8] h-full'
                                            : 'max-h-16'
                                        } ${marca.nome === 'Tama' ? 'invert' : ''}`}
                                />
                            ) : (
                                <div className="text-3xl font-bold text-gray-400">{marca.nome}</div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
