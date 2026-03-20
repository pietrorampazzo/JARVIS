import React, { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import ProdutoCardDetalhado from "../components/produtos/ProdutoCardDetalhado";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { Search, Music, RotateCcw } from "lucide-react";

export default function ProdutosPage() {
    const [produtos, setProdutos] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // Filtros
    const [searchTerm, setSearchTerm] = useState("");
    const [marcaFilter, setMarcaFilter] = useState("all");

    useEffect(() => {
        loadProdutos();
    }, []);

    const loadProdutos = async () => {
        setIsLoading(true);
        try {
            const data = await base44.entities.Produto.list('-created_date');
            setProdutos(data);
        } catch (error) {
            console.error('Erro ao carregar produtos:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Gerar lista única de marcas baseada nos produtos mockados
    const marcasUnicas = Array.from(new Set(produtos.map(p => p.marca)));

    // Aplicar filtros
    const filteredProdutos = produtos.filter(produto => {
        const searchMatch = searchTerm === "" ||
            (produto.modelo?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                produto.descricao?.toLowerCase().includes(searchTerm.toLowerCase()));

        const marcaMatch = marcaFilter === "all" || produto.marca === marcaFilter;

        return searchMatch && marcaMatch;
    });

    const handleReset = () => {
        setSearchTerm("");
        setMarcaFilter("all");
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <div className="flex items-center justify-center mb-6">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center">
                            <Music className="w-8 h-8 text-white" />
                        </div>
                    </div>
                    <h1 className="text-5xl font-bold text-gray-900 mb-6">Catálogo de Produtos</h1>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                        Aqui você encontra todos os instrumentos musicais, equipamentos de áudio e acessórios do nosso catálogo.
                        Adicione ao seu orçamento e solicite uma cotação.
                    </p>
                </motion.div>

                {/* Barra de Filtros */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-8"
                >
                    <div className="flex flex-col lg:flex-row gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <Input
                                type="text"
                                placeholder="Buscar por modelo ou descrição..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>

                        <div className="w-full lg:w-48">
                            <Select
                                value={marcaFilter}
                                onChange={(e) => setMarcaFilter(e.target.value)}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Marca" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">Todas as Marcas</SelectItem>
                                    {marcasUnicas.map(marca => (
                                        <SelectItem key={marca} value={marca}>{marca}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <Button
                            variant="outline"
                            onClick={handleReset}
                            className="flex items-center gap-2"
                        >
                            <RotateCcw className="w-4 h-4" /> Limpar Filtros
                        </Button>
                    </div>
                </motion.div>

                {/* Grid de Produtos */}
                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {Array(8).fill(0).map((_, i) => (
                            <div key={i} className="animate-pulse">
                                <div className="bg-gray-200 rounded-2xl h-96"></div>
                            </div>
                        ))}
                    </div>
                ) : filteredProdutos.length > 0 ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
                    >
                        {filteredProdutos.map((produto, index) => (
                            <ProdutoCardDetalhado key={produto.id} produto={produto} index={index} />
                        ))}
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3 }}
                        className="text-center py-20"
                    >
                        <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
                            <Search className="w-12 h-12 text-gray-400" />
                        </div>
                        <h3 className="text-2xl font-semibold text-gray-900 mb-4">Nenhum produto encontrado</h3>
                        <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
                            Não encontramos produtos com os filtros selecionados. Tente ajustar sua busca.
                        </p>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
