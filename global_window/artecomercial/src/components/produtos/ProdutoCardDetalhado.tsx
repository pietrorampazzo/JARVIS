import React from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Package, Plus } from "lucide-react";
import { useCart } from "@/context/CartContext";

export default function ProdutoCardDetalhado({ produto, index }: { produto: any; index: number }) {
    const { addToCart } = useCart();

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
    };

    const handleAdicionar = () => {
        addToCart({
            id: produto.id.toString(),
            nome: `${produto.marca} ${produto.modelo}`,
            preco: produto.preco,
            imagem: produto.imagem,
            marca: produto.marca,
            categoria: produto.categoria || 'Geral'
        }, 1);
    };

    return (
        <Card className="hover:border-blue-300 hover:shadow-xl transition-all duration-300 flex flex-col h-full bg-white overflow-hidden group">
            <div className="relative h-64 overflow-hidden bg-gray-100 flex items-center justify-center p-4">
                {produto.imagem ? (
                    <img
                        src={produto.imagem}
                        alt={produto.modelo}
                        className="object-cover w-full h-full rounded transition-transform duration-500 group-hover:scale-105"
                    />
                ) : (
                    <div className="flex flex-col items-center justify-center text-gray-400">
                        <Package className="w-16 h-16 mb-2" />
                        <span className="text-sm font-medium">Sem Imagem</span>
                    </div>
                )}
                <div className="absolute top-4 right-4">
                    <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md">
                        Estoque: {produto.quantidade}
                    </span>
                </div>
            </div>

            <CardHeader className="bg-white border-b pb-4">
                <div>
                    <span className="text-sm font-semibold text-blue-600 mb-1 block uppercase tracking-wider">{produto.marca}</span>
                    <h3 className="text-2xl font-bold text-gray-900 leading-tight">{produto.modelo}</h3>
                </div>
            </CardHeader>

            <CardContent className="pt-6 flex-grow flex flex-col justify-between space-y-4">
                <p className="text-gray-600 text-sm line-clamp-3">
                    {produto.descricao}
                </p>

                <div className="pt-4 border-t">
                    <p className="text-xs text-gray-500 mb-1">Preço Sugerido</p>
                    <p className="text-3xl font-extrabold text-gray-900 mb-4">{formatCurrency(produto.preco)}</p>
                    <Button
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6"
                        onClick={handleAdicionar}
                    >
                        <Plus className="w-5 h-5 mr-2" />
                        Adicionar à Cotação
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
