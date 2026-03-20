import React from "react";
import { base44 } from "@/api/base44Client";
import HeroSection from "../components/common/HeroSection";
import ItemAtaCardExpandido from "../components/atas/ItemAtaCardExpandido";
import ProdutoCardDetalhado from "../components/produtos/ProdutoCardDetalhado";
import MarcaCarousel from "../components/marcas/MarcaCarousel";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { ArrowRight, Award, Users, Clock, Shield } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
    const [itensRecentes, setItensRecentes] = React.useState<any[]>([]);
    const [produtosDestaque, setProdutosDestaque] = React.useState<any[]>([]);
    const [marcas, setMarcas] = React.useState<any[]>([]);
    const [isLoading, setIsLoading] = React.useState(true);
    const [isExpanded, setIsExpanded] = React.useState(false);

    React.useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [itensData, produtosData, marcasData] = await Promise.all([
                base44.entities.ItemAta.list('-created_date', 6),
                base44.entities.Produto.list('-created_date', 24),
                base44.entities.Marca.list()
            ]);
            setItensRecentes(itensData);
            setProdutosDestaque(produtosData);
            setMarcas(marcasData);
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const diferenciais = [
        {
            icon: Clock,
            title: "20+ Anos em Licitações",
            description: "Experiência consolidada no atendimento ao setor público"
        },
        {
            icon: Award,
            title: "51 Anos de Tradição",
            description: "Mais de cinco décadas dedicadas ao mercado musical"
        },
        {
            icon: Shield,
            title: "Credibilidade Comprovada",
            description: "Fornecedor confiável para órgãos governamentais"
        },
        {
            icon: Users,
            title: "Atendimento Especializado",
            description: "Equipe especializada em processos licitatórios"
        }
    ];

    return (
        <div className="min-h-screen bg-white">
            {/* Hero Section */}
            <HeroSection />

            {/* Seção de Diferenciais */}
            <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 50 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            Por que escolher a Arte Comercial?
                        </h2>
                        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                            Combinamos décadas de experiência com as melhores práticas do mercado para oferecer soluções completas ao setor público
                        </p>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {diferenciais.map((item, index) => (
                            <motion.div
                                key={item.title}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="text-center group"
                            >
                                <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                    <item.icon className="w-8 h-8 text-white" />
                                </div>
                                <h3 className="text-xl font-semibold text-gray-900 mb-3">{item.title}</h3>
                                <p className="text-gray-600">{item.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Seção de Itens Recentes */}
            <section className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="flex items-center justify-between mb-12"
                    >
                        <div>
                            <h2 className="text-4xl font-bold text-gray-900 mb-4">
                                Itens em Atas Governamentais
                            </h2>
                            <p className="text-xl text-gray-600">
                                Produtos registrados em atas vigentes prontos para aquisição
                            </p>
                        </div>
                        <Link to={createPageUrl("ItensAtas")}>
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 hidden lg:flex items-center gap-2">
                                Ver Todos os Itens
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </Link>
                    </motion.div>

                    {isLoading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {Array(6).fill(0).map((_, i) => (
                                <div key={i} className="animate-pulse">
                                    <div className="bg-gray-200 rounded-2xl h-96"></div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {itensRecentes.map((item, index) => (
                                <ItemAtaCardExpandido key={item.id} item={item} index={index} />
                            ))}
                        </div>
                    )}

                    <div className="text-center mt-12">
                        <Link to={createPageUrl("ItensAtas")}>
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
                                Ver Todos os Itens
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Seção de Produtos em Destaque */}
            <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="flex items-center justify-between mb-12"
                    >
                        <div>
                            <h2 className="text-4xl font-bold text-gray-900 mb-4">
                                Produtos em Destaque
                            </h2>
                            <p className="text-xl text-gray-600">
                                Instrumentos e equipamentos disponíveis em nossas atas governamentais
                            </p>
                        </div>
                        <Link to={createPageUrl("Produtos")}>
                            <Button variant="outline" className="px-6 py-3 hidden lg:flex items-center gap-2">
                                Ver Todos os Produtos
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </Link>
                    </motion.div>

                    {isLoading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {Array(8).fill(0).map((_, i) => (
                                <div key={i} className="animate-pulse">
                                    <div className="bg-gray-200 rounded-2xl h-80"></div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {produtosDestaque.slice(0, isExpanded ? 24 : 8).map((produto, index) => (
                                <ProdutoCardDetalhado key={produto.id} produto={produto} index={index} />
                            ))}
                        </div>
                    )}

                    <div className="text-center mt-12 flex flex-col sm:flex-row items-center justify-center gap-4">
                        {!isExpanded && produtosDestaque.length > 8 && (
                            <Button
                                variant="outline"
                                className="px-8 py-3 bg-white text-gray-900 border-gray-300 hover:bg-gray-50"
                                onClick={() => setIsExpanded(true)}
                            >
                                Ver Mais Produtos
                            </Button>
                        )}
                        <Link to={createPageUrl("Produtos")}>
                            <Button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white">
                                Ir para o Catálogo Completo
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Seção de Marcas */}
            {marcas.length > 0 && <MarcaCarousel marcas={marcas} />}
        </div>
    );
}
