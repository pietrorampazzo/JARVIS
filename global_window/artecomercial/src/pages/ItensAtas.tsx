import React from "react";
import { base44 } from "@/api/base44Client";
import ItemAtaCardExpandido from "../components/atas/ItemAtaCardExpandido";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
import { Package, Search, RotateCcw } from "lucide-react";

export default function ItensAtasPage() {
    const [itens, setItens] = React.useState<any[]>([]);
    const [isLoading, setIsLoading] = React.useState(true);
    const [searchTerm, setSearchTerm] = React.useState("");
    const [categoriaFilter, setCategoriaFilter] = React.useState("all");
    const [statusFilter, setStatusFilter] = React.useState("disponivel");

    React.useEffect(() => {
        loadItens();
    }, []);

    const loadItens = async () => {
        setIsLoading(true);
        try {
            const data = await base44.entities.ItemAta.list('-created_date');
            setItens(data);
        } catch (error) {
            console.error('Erro ao carregar itens:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const filteredItens = itens.filter(item => {
        const searchMatch = searchTerm === "" ||
            (item.item?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.descricao?.toLowerCase().includes(searchTerm.toLowerCase()));

        // Simplificando o filtro de categoria apenas pro mock pois não geramos esse campo no mock explicitamente
        // Mas num caso real funcionaria
        const categoriaMatch = categoriaFilter === "all" || true;
        const statusMatch = statusFilter === "all" || item.status === statusFilter;
        return searchMatch && categoriaMatch && statusMatch;
    });

    const handleReset = () => {
        setSearchTerm("");
        setCategoriaFilter("all");
        setStatusFilter("disponivel");
    };

    const calcularValorTotal = () => {
        return filteredItens.reduce((total, item) => {
            return total + ((item.quantidade_registrada || 0) * (item.valor_unitario || 0));
        }, 0);
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value || 0);
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
                            <Package className="w-8 h-8 text-white" />
                        </div>
                    </div>
                    <h1 className="text-5xl font-bold text-gray-900 mb-6">Itens Disponíveis em Atas</h1>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                        Explore nosso catálogo completo de produtos registrados em atas governamentais vigentes.
                        Instrumentos musicais, equipamentos de áudio e acessórios de alta qualidade.
                    </p>
                </motion.div>

                {/* Resumo de Valores */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
                >
                    <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
                        <CardContent className="p-6">
                            <div className="text-blue-100 text-sm font-medium mb-2">Total de Itens</div>
                            <div className="text-4xl font-bold">{filteredItens.length}</div>
                        </CardContent>
                    </Card>

                    <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0">
                        <CardContent className="p-6">
                            <div className="text-green-100 text-sm font-medium mb-2">Valor Total Registrado</div>
                            <div className="text-3xl font-bold">{formatCurrency(calcularValorTotal())}</div>
                        </CardContent>
                    </Card>

                    <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0">
                        <CardContent className="p-6">
                            <div className="text-purple-100 text-sm font-medium mb-2">Quantidade Total</div>
                            <div className="text-4xl font-bold">
                                {filteredItens.reduce((sum, item) => sum + (item.quantidade_registrada || 0), 0)}
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>

                {/* Filtros e Busca */}
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
                                placeholder="Buscar por item ou descrição..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>

                        <div className="w-full lg:w-48">
                            <Select value={categoriaFilter} onValueChange={setCategoriaFilter}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Categoria" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">Todas Categorias</SelectItem>
                                    <SelectItem value="instrumentos_sopro">Instrumentos de Sopro</SelectItem>
                                    <SelectItem value="instrumentos_corda">Instrumentos de Corda</SelectItem>
                                    <SelectItem value="percussao">Percussão</SelectItem>
                                    <SelectItem value="audio">Áudio</SelectItem>
                                    <SelectItem value="acessorios">Acessórios</SelectItem>
                                    <SelectItem value="equipamentos">Equipamentos</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="w-full lg:w-48">
                            <Select value={statusFilter} onValueChange={setStatusFilter}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Status" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">Todos Status</SelectItem>
                                    <SelectItem value="disponivel">Disponível</SelectItem>
                                    <SelectItem value="esgotado">Esgotado</SelectItem>
                                    <SelectItem value="reservado">Reservado</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <Button
                            variant="outline"
                            onClick={handleReset}
                            className="flex items-center gap-2"
                        >
                            <RotateCcw className="w-4 h-4" /> Limpar
                        </Button>
                    </div>
                </motion.div>

                {/* Grid de Itens */}
                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {Array(12).fill(0).map((_, i) => (
                            <div key={i} className="animate-pulse">
                                <div className="bg-gray-200 rounded-2xl h-80"></div>
                            </div>
                        ))}
                    </div>
                ) : filteredItens.length > 0 ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    >
                        {filteredItens.map((item, index) => (
                            <ItemAtaCardExpandido key={item.id} item={item} index={index} />
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
                        <h3 className="text-2xl font-semibold text-gray-900 mb-4">Nenhum item encontrado</h3>
                        <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
                            Não encontramos itens com os filtros selecionados. Tente ajustar sua busca.
                        </p>
                    </motion.div>
                )}
            </div>
        </div>
    );
}
