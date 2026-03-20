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
                <CardHeader className="bg-gradient-to-br from-gray-50 to-gray-100/50 rounded-t-xl border-b pb-4">
                    <div className="flex justify-between items-start mb-2">
                        <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded flex items-center gap-1">
                            <FileText className="w-3 h-3" />
                            Ata Vigente
                        </span>
                        <span className="text-sm text-gray-500 font-medium">#{item.id}</span>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 line-clamp-2 mt-2 group-hover:text-blue-600 transition-colors">
                        {item.nome}
                    </h3>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col pt-6">
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
