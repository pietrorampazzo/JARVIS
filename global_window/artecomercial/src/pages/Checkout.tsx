import React, { useState } from "react";
import { useCart } from "@/context/CartContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import emailjs from "@emailjs/browser";
import { ShoppingCart, CheckCircle, Phone, Mail } from "lucide-react";
import { motion } from "framer-motion";

export default function CheckoutPage() {
    const { cartItens, cartTotal, clearCart } = useCart();
    const [enviado, setEnviado] = useState(false);
    const [enviando, setEnviando] = useState(false);
    const [formData, setFormData] = useState({
        nome_completo: "",
        empresa_orgao: "",
        cnpj: "",
        email: "",
        telefone: "",
        estado: "",
        cidade: "",
        mensagem: "",
    });

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL",
        }).format(value || 0);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setEnviando(true);

        // Formatação HTML simples da lista de mercadorias
        const linhasPedido = cartItens.map(i => `• ${i.quantidade}x ${i.nome} (${formatCurrency(i.preco)})`);
        const strPedidoHtml = linhasPedido.join('\n');

        try {
            // Em produção, as keys abaixo devem vir do env (ex: import.meta.env.VITE_EMAILJS_SERVICE_ID)
            // Aqui criamos a base para você preencher os tokens oficiais da sua conta EmailJS
            const params = {
                nome_contato: formData.nome_completo,
                empresa_orgao: formData.empresa_orgao,
                cnpj: formData.cnpj,
                email_contato: formData.email,
                telefone: formData.telefone,
                localizacao: `${formData.cidade} - ${formData.estado}`,
                mensagem: formData.mensagem || "Sem observações adicionais.",
                resumo_pedido: strPedidoHtml,
                valor_estimado: formatCurrency(cartTotal)
            };

            console.log("Payload Montado para E-mail:", params);

            // IMPORTANTE: Adicione suas credenciais do EmailJS logo abaixo
            await emailjs.send(
                import.meta.env.VITE_EMAILJS_SERVICE_ID || 'arte_loja_b2g',
                import.meta.env.VITE_EMAILJS_TEMPLATE_ID || 'template_4a1tns7',
                params,
                import.meta.env.VITE_EMAILJS_PUBLIC_KEY || 'PC5Xxu5-YE-XxJ4Hy'
            );

            setEnviado(true);
            clearCart();
        } catch (error: any) {
            console.error("Falha detalhada EmailJS:", error?.text ? error.text : error);
            alert(`Ocorreu um erro no envio. Detalhes (Logs): ${error?.text || 'Falha de Conexão com EmailJS'}`);
        } finally {
            setEnviando(false);
        }
    };

    if (enviado) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-green-50 to-white py-12 flex items-center justify-center">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="max-w-2xl mx-auto px-4 text-center"
                >
                    <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                        <CheckCircle className="w-12 h-12 text-green-600" />
                    </div>
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Solicitação Enviada com Sucesso!</h1>
                    <p className="text-xl text-gray-600 mb-8">
                        Recebemos sua solicitação de cotação. Nossa equipe entrará em contato em breve.
                    </p>
                    <div className="bg-blue-50 rounded-xl p-6 mb-8">
                        <h3 className="font-semibold text-gray-900 mb-4">Contate nosso Departamento de Licitações:</h3>
                        <div className="space-y-3">
                            <div className="flex items-center justify-center gap-2">
                                <Mail className="w-5 h-5 text-blue-600" />
                                <a href="mailto:pietro@artecomercialbrasil.com.br" className="text-blue-600 hover:underline">
                                    pietro@artecomercialbrasil.com.br
                                </a>
                            </div>
                            <div className="flex items-center justify-center gap-2">
                                <Phone className="w-5 h-5 text-blue-600" />
                                <a href="https://wa.me/5511994103374" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                    (11) 99410-3374
                                </a>
                            </div>
                        </div>
                    </div>
                    <Button onClick={() => (window.location.href = "/")} className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg">
                        Voltar ao Início
                    </Button>
                </motion.div>
            </div>
        );
    }

    if (cartItens.length === 0) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white py-12 flex items-center justify-center">
                <div className="text-center">
                    <ShoppingCart className="w-24 h-24 mx-auto text-gray-300 mb-6" />
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">Carrinho Vazio</h2>
                    <p className="text-gray-600 mb-8">Adicione produtos ao carrinho para solicitar cotação</p>
                    <Button onClick={() => (window.location.href = "/produtos")} className="bg-blue-600 hover:bg-blue-700 text-white">
                        Ver Produtos
                    </Button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-gray-50 to-white py-12">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">Finalizar Solicitação de Cotação</h1>
                    <p className="text-xl text-gray-600">Preencha os dados abaixo para receber sua cotação personalizada</p>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Formulário */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Dados para Contato</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleSubmit} className="space-y-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <Label htmlFor="nome_completo">Nome Completo *</Label>
                                            <Input
                                                id="nome_completo"
                                                name="nome_completo"
                                                value={formData.nome_completo}
                                                onChange={handleInputChange}
                                                required
                                                className="mt-1"
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="empresa_orgao">Empresa/Órgão (UASG) *</Label>
                                            <Input
                                                id="empresa_orgao"
                                                name="empresa_orgao"
                                                value={formData.empresa_orgao}
                                                onChange={handleInputChange}
                                                required
                                                className="mt-1"
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="cnpj">CNPJ Empresa/Órgão (UASG) *</Label>
                                            <Input
                                                id="cnpj"
                                                name="cnpj"
                                                value={formData.cnpj}
                                                onChange={handleInputChange}
                                                required
                                                placeholder="00.000.000/0000-00"
                                                className="mt-1"
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="email">E-mail *</Label>
                                            <Input
                                                id="email"
                                                name="email"
                                                type="email"
                                                value={formData.email}
                                                onChange={handleInputChange}
                                                required
                                                className="mt-1"
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="telefone">Telefone *</Label>
                                            <Input
                                                id="telefone"
                                                name="telefone"
                                                type="tel"
                                                value={formData.telefone}
                                                onChange={handleInputChange}
                                                required
                                                placeholder="(11) 99999-9999"
                                                className="mt-1"
                                            />
                                        </div>
                                        <div>
                                            <Label htmlFor="estado">Estado *</Label>
                                            <Input
                                                id="estado"
                                                name="estado"
                                                value={formData.estado}
                                                onChange={handleInputChange}
                                                required
                                                className="mt-1"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <Label htmlFor="cidade">Cidade *</Label>
                                            <Input
                                                id="cidade"
                                                name="cidade"
                                                value={formData.cidade}
                                                onChange={handleInputChange}
                                                required
                                                className="mt-1"
                                            />
                                        </div>
                                        <div className="md:col-span-2">
                                            <Label htmlFor="mensagem">Mensagem</Label>
                                            <Textarea
                                                id="mensagem"
                                                name="mensagem"
                                                value={formData.mensagem}
                                                onChange={handleInputChange}
                                                placeholder="Gostaria de fazer alguma solicitação customizada à Arte? Escreva nesse campo"
                                                rows={4}
                                                className="mt-1"
                                            />
                                        </div>
                                    </div>

                                    <div className="bg-blue-50 rounded-lg p-4">
                                        <h3 className="font-semibold text-gray-900 mb-2">Contate nosso Departamento de Licitações:</h3>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex items-center gap-2">
                                                <Mail className="w-4 h-4 text-blue-600" />
                                                <a href="mailto:pietro@artecomercialbrasil.com.br" className="text-blue-600 hover:underline">
                                                    pietro@artecomercialbrasil.com.br
                                                </a>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Phone className="w-4 h-4 text-blue-600" />
                                                <a href="https://wa.me/5511994103374" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                                    (11) 99410-3374
                                                </a>
                                            </div>
                                        </div>
                                    </div>

                                    <Button
                                        type="submit"
                                        className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg"
                                        disabled={enviando}
                                    >
                                        {enviando ? "Enviando..." : "Enviar Solicitação"}
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Resumo do Pedido */}
                    <div>
                        <Card className="sticky top-24">
                            <CardHeader>
                                <CardTitle>Resumo da Cotação</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4 mb-6 max-h-96 overflow-y-auto pr-2">
                                    {cartItens.map((item) => (
                                        <div key={item.id} className="border-b pb-4">
                                            <h4 className="font-medium text-sm text-gray-900 mb-1">{item.nome}</h4>
                                            <div className="flex justify-between text-sm text-gray-600">
                                                <span>Qtd: {item.quantidade}</span>
                                                {item.preco && (
                                                    <span>{formatCurrency(item.preco * item.quantidade)}</span>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="border-t pt-4 space-y-2">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Total de itens:</span>
                                        <span className="font-medium">{cartItens.reduce((t, i) => t + i.quantidade, 0)}</span>
                                    </div>
                                    <div className="flex justify-between text-lg font-bold">
                                        <span>Valor Total:</span>
                                        <span className="text-blue-600">{formatCurrency(cartTotal)}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
