import React from "react";
import { motion } from "framer-motion";
import { Award, Users, Clock, Shield, Target, Heart, Building, Globe } from "lucide-react";

export default function SobrePage() {
    const valores = [
        {
            icon: Shield,
            title: "Credibilidade",
            description: "51 anos de tradição e confiança no mercado brasileiro",
        },
        {
            icon: Target,
            title: "Excelência",
            description: "Comprometimento com a mais alta qualidade em produtos e serviços",
        },
        {
            icon: Heart,
            title: "Paixão",
            description: "Amor pela música e dedicação ao desenvolvimento cultural",
        },
        {
            icon: Users,
            title: "Parceria",
            description: "Relacionamentos duradouros com clientes e fornecedores",
        },
    ];

    const timeline = [
        { ano: "2002", evento: "Fundação da Arte Comercial", descricao: "Início das atividades no mercado de instrumentos musicais" },
        { ano: "2004", evento: "Foco em Licitações", descricao: "Especialização no atendimento ao setor público" },
        { ano: "2015", evento: "Expansão Nacional", descricao: "Ampliação do atendimento para todo território brasileiro" },
        { ano: "2025", evento: "Consolidação", descricao: "51 anos de tradição e mais de 20 anos em licitações governamentais" },
    ];

    return (
        <div className="min-h-screen bg-white">
            {/* Hero Section */}
            <section className="py-20 bg-gradient-to-br from-gray-900 to-blue-900 text-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 50 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center"
                    >
                        <h1 className="text-5xl lg:text-6xl font-bold mb-6">Nossa História</h1>
                        <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
                            Dedicados à música e ao desenvolvimento cultural brasileiro desde 2002.
                            Uma trajetória de 51 anos construindo pontes entre arte e educação.
                        </p>
                    </motion.div>
                </div>
            </section>

            {/* Estatísticas */}
            <section className="py-20 bg-gray-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="text-center"
                        >
                            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center">
                                <Clock className="w-8 h-8 text-white" />
                            </div>
                            <div className="text-4xl font-bold text-gray-900 mb-2">51</div>
                            <div className="text-gray-600">Anos de Tradição</div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.1 }}
                            className="text-center"
                        >
                            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center">
                                <Building className="w-8 h-8 text-white" />
                            </div>
                            <div className="text-4xl font-bold text-gray-900 mb-2">20+</div>
                            <div className="text-gray-600">Anos em Licitações</div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            className="text-center"
                        >
                            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center">
                                <Globe className="w-8 h-8 text-white" />
                            </div>
                            <div className="text-4xl font-bold text-gray-900 mb-2">6</div>
                            <div className="text-gray-600">Marcas Mundiais</div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.3 }}
                            className="text-center"
                        >
                            <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl flex items-center justify-center">
                                <Award className="w-8 h-8 text-white" />
                            </div>
                            <div className="text-4xl font-bold text-gray-900 mb-2">100%</div>
                            <div className="text-gray-600">Credibilidade</div>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* Nossa História */}
            <section className="py-20 bg-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid lg:grid-cols-2 gap-16 items-center">
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                        >
                            <h2 className="text-4xl font-bold text-gray-900 mb-6">Tradição que Transcende Gerações</h2>
                            <div className="space-y-6 text-lg text-gray-700 leading-relaxed">
                                <p>
                                    Fundada em 2002, a Arte Comercial nasceu com o propósito de democratizar o acesso aos melhores intrumentos musicais do mundo.
                                    Ao longo de mais de cinco décadas, construímos uma reputação sólida baseada na qualidade, confiabilidade e excelência no atendimento.
                                </p>
                                <p>
                                    Há mais de 20 anos, direcionamos nossa expertise para o atendimento especializado ao setor público, tornando-nos referência em licitações governamentais.
                                </p>
                                <p>
                                    Nossa missão vai além do comércio: contribuímos para o desenvolvimento cultural e educacional do Brasil, fornecendo instrumentos de qualidade internacional.
                                </p>
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, x: 50 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            className="relative"
                        >
                            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-3xl p-8">
                                <div className="space-y-8">
                                    {timeline.map((item, index) => (
                                        <motion.div
                                            key={item.ano}
                                            initial={{ opacity: 0, y: 20 }}
                                            whileInView={{ opacity: 1, y: 0 }}
                                            viewport={{ once: true }}
                                            transition={{ delay: index * 0.1 }}
                                            className="flex items-start space-x-4"
                                        >
                                            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold shrink-0">
                                                {item.ano}
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-semibold text-gray-900 mb-1">{item.evento}</h3>
                                                <p className="text-gray-600">{item.descricao}</p>
                                            </div>
                                        </motion.div>
                                    ))}
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </section>

            {/* Nossos Valores */}
            <section className="py-20 bg-gradient-to-br from-gray-50 to-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl font-bold text-gray-900 mb-6">Nossos Valores</h2>
                        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                            Princípios que guiam nossa conduta e definem nosso compromisso com clientes, parceiros e com o desenvolvimento da música no Brasil.
                        </p>
                    </motion.div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {valores.map((valor, index) => (
                            <motion.div
                                key={valor.title}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: index * 0.1 }}
                                className="text-center group"
                            >
                                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                    <valor.icon className="w-10 h-10 text-white" />
                                </div>
                                <h3 className="text-xl font-semibold text-gray-900 mb-3">{valor.title}</h3>
                                <p className="text-gray-600 leading-relaxed">{valor.description}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Call to Action */}
            <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800 text-white">
                <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                    >
                        <h2 className="text-4xl font-bold mb-6">Faça Parte da Nossa História</h2>
                        <p className="text-xl opacity-90 mb-8 leading-relaxed">
                            Junte-se a dezenas de instituições públicas que confiam na Arte Comercial para fornecer instrumentos de qualidade internacional e contribuir para a educação musical em todo o Brasil.
                        </p>
                    </motion.div>
                </div>
            </section>
        </div>
    );
}
