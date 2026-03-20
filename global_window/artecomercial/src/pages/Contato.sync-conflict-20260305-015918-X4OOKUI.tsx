import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { motion } from "framer-motion";
import { Mail, Phone, MapPin, Clock, FileText, Users, Send } from "lucide-react";

export default function ContatoPage() {
    const [formData, setFormData] = React.useState({
        nome: "",
        email: "",
        telefone: "",
        orgao: "",
        tipo_solicitacao: "",
        mensagem: ""
    });
    const [isSubmitting, setIsSubmitting] = React.useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        // Simular envio
        setTimeout(() => {
            setIsSubmitting(false);
            alert("Mensagem enviada com sucesso! Entraremos em contato em breve.");
            setFormData({
                nome: "",
                email: "",
                telefone: "",
                orgao: "",
                tipo_solicitacao: "",
                mensagem: ""
            });
        }, 2000);
    };

    const handleInputChange = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const informacoesContato = [
        {
            icon: Phone,
            title: "Telefone",
            info: "(11) 99410-3374",
            descricao: "Segunda a sexta, 8h às 18h"
        },
        {
            icon: Mail,
            title: "E-mail",
            info: "pietro@artecomercialbrasil.com.br",
            descricao: "Resposta em até 24h úteis"
        },
        {
            icon: MapPin,
            title: "Endereço",
            info: "São Paulo, SP",
            descricao: "Atendimento personalizado"
        },
        {
            icon: Clock,
            title: "Horário",
            info: "Segunda a Sexta",
            descricao: "8:00 às 18:00"
        }
    ];

    const tiposSolicitacao = [
        "Consulta sobre Atas Vigentes",
        "Solicitação de Proposta",
        "Informações sobre Produtos",
        "Suporte Técnico",
        "Parceria Comercial",
        "Outros"
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white py-20 text-gray-900 font-sans">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">

                {/* Destaque Atendimento Especializado */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-center mb-16 flex flex-col items-center"
                >
                    <Users className="w-16 h-16 text-blue-600 mb-4" />
                    <h3 className="text-2xl font-semibold text-gray-900 mb-2">Atendimento Especializado</h3>
                    <p className="text-gray-600 max-w-lg">
                        Equipe com mais de 20 anos de experiência em licitações governamentais
                    </p>
                </motion.div>

                {/* Informações de Contato */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                    {informacoesContato.map((item, index) => (
                        <motion.div
                            key={item.title}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 + index * 0.1 }}
                            className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6 flex flex-col items-center text-center hover:border-blue-500/50 transition-colors"
                        >
                            <div className="w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center mb-4 shrink-0">
                                <item.icon className="w-6 h-6 text-blue-600" />
                            </div>
                            <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                            <p className="text-blue-600 font-medium mb-1 break-words w-full text-sm">{item.info}</p>
                            <p className="text-sm text-gray-500">{item.descricao}</p>
                        </motion.div>
                    ))}
                </div>

                {/* Formulário de Contato */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="bg-white p-8 rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100"
                >
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                            <FileText className="w-6 h-6 text-blue-600" /> Envie sua Mensagem
                        </h2>
                        <p className="text-gray-600 mt-2">Preencha o formulário abaixo e nossa equipe entrará em contato em breve.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Nome Completo *</label>
                                <Input
                                    type="text"
                                    value={formData.nome}
                                    onChange={(e) => handleInputChange('nome', e.target.value)}
                                    placeholder="Seu nome completo"
                                    required
                                    className="bg-gray-50 border-gray-200 text-gray-900 focus:border-blue-500 h-12"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">E-mail *</label>
                                <Input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => handleInputChange('email', e.target.value)}
                                    placeholder="seu@email.com"
                                    required
                                    className="bg-gray-50 border-gray-200 text-gray-900 focus:border-blue-500 h-12"
                                />
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Telefone</label>
                                <Input
                                    type="tel"
                                    value={formData.telefone}
                                    onChange={(e) => handleInputChange('telefone', e.target.value)}
                                    placeholder="(11) 99999-9999"
                                    className="bg-gray-50 border-gray-200 text-gray-900 focus:border-blue-500 h-12"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Órgão/Instituição</label>
                                <Input
                                    type="text"
                                    value={formData.orgao}
                                    onChange={(e) => handleInputChange('orgao', e.target.value)}
                                    placeholder="Nome do órgão ou instituição"
                                    className="bg-gray-50 border-gray-200 text-gray-900 focus:border-blue-500 h-12"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Solicitação *</label>
                            <Select value={formData.tipo_solicitacao} onValueChange={(value) => handleInputChange('tipo_solicitacao', value)}>
                                <SelectTrigger className="bg-gray-50 border-gray-200 text-gray-900 h-12">
                                    <SelectValue placeholder="Selecione o tipo de solicitação" />
                                </SelectTrigger>
                                <SelectContent className="bg-white border-gray-200 text-gray-900">
                                    {tiposSolicitacao.map(tipo => (
                                        <SelectItem key={tipo} value={tipo} className="focus:bg-gray-100 cursor-pointer">
                                            {tipo}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Mensagem *</label>
                            <Textarea
                                value={formData.mensagem}
                                onChange={(e) => handleInputChange('mensagem', e.target.value)}
                                placeholder="Descreva sua solicitação ou dúvida..."
                                rows={5}
                                required
                                className="bg-gray-50 border-gray-200 text-gray-900 focus:border-blue-500 resize-none"
                            />
                        </div>

                        <div className="flex justify-end pt-4">
                            <Button
                                type="submit"
                                disabled={isSubmitting}
                                className="bg-blue-600 hover:bg-blue-700 text-white h-12 px-8 text-lg rounded-xl shadow-lg shadow-blue-200"
                            >
                                {isSubmitting ? (
                                    <div className="flex items-center gap-2">
                                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Enviando...
                                    </div>
                                ) : (
                                    <div className="flex items-center gap-3">
                                        <Send className="w-5 h-5" /> Enviar Mensagem
                                    </div>
                                )}
                            </Button>
                        </div>
                    </form>
                </motion.div>
            </div>
        </div>
    );
}
