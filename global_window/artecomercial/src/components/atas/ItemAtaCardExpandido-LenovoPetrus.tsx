import React from "react";
import { Card, CardHeader, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { motion } from "framer-motion";
import { useCart } from "@/context/CartContext";
import { FileText, Package, Plus } from "lucide-react";

export default function ItemAtaCardExpandido({ item, index }: { item: any; index: number }) {
    const { addToCart } = useCart();

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1 }}
            className="h-full"
        >
            <Card className="h-full flex flex-col hover:border-blue-300 hover:shadow-xl transition-all duration-300 bg-white group">
                <CardHeader className="p-0 overflow-hidden rounded-t-xl border-b bg-gray-50">
                    <div className="relative aspect-video group-hover:scale-105 transition-transform duration-500">
                        <img
                            src={item.imagem_url || "/images/produtos/placeholder.jpg"}
                            alt={item.nome}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                                (e.target as HTMLImageElement).src = "/images/produtos/placeholder.jpg";
                            }}
                        />
                        <div className="absolute top-2 right-2 flex gap-2">
                            <span className="bg-white/90 backdrop-blur-sm text-gray-500 text-[10px] font-medium px-2 py-0.5 rounded shadow-sm">
                                #{item.id}
                            </span>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col pt-4">
                    <div className="flex items-center gap-1.5 mb-2">
                        <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 uppercase tracking-wider">
                            <FileText className="w-2.5 h-2.5" />
                            Ata Vigente
                        </span>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors leading-tight">
                        {item.nome}
                    </h3>
                    <p className="text-gray-600 text-sm mb-6 line-clamp-3">
                        {item.descricao}
                    </p>
                    <div className="mt-auto space-y-4">
                        <div className="flex items-center justify-between text-sm bg-gray-50 p-3 rounded-lg">
                            <span className="text-gray-500">Marca/Fabricante</span>
                            <span className="font-semibold text-gray-900">{item.marca_nome || "Diversas"}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-gray-500 mb-1">Valor Unitário</p>
                                <p className="text-2xl font-bold text-blue-600">
                                    {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(item.valor_unitario || 0)}
                                </p>
                            </div>
                        </div>
                        <Button
                            onClick={() => addToCart({ id: item.id.toString(), nome: item.nome, preco: item.valor_unitario, marca: item.marca_nome || 'Diversas', categoria: item.categoria || 'Geral', imagem: item.imagem_url || '' }, 1)}
                            className="w-full bg-gray-900 hover:bg-black text-white py-6"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Adicionar à Cotação
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
