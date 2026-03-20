importReactfrom"react";

import { Button } from"@/components/ui/button";

import { Card, CardContent, CardHeader, CardTitle } from"@/components/ui/card";

import { Input } from"@/components/ui/input";

import { Textarea } from"@/components/ui/textarea";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from"@/components/ui/select";

import { motion } from"framer-motion";

import { Mail, Phone, MapPin, Clock, FileText, Users, Send } from"lucide-react";

exportdefaultfunctionContatoPage() {

  const [formData, setFormData] = React.useState({

    nome: "",

    email: "",

    telefone: "",

    orgao: "",

    tipo_solicitacao: "",

    mensagem: ""

  });

  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleSubmit = async (e) => {

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

  const handleInputChange = (field, value) => {

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

    `<div className="min-h-screen bg-gradient-to-br from-gray-50 to-white py-12">`

    `<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">`

    {/* Header */}

    <motion.div

    initial={{ opacity: 0, y: 30 }}

    animate={{ opacity: 1, y: 0 }}

    className="text-center mb-12"

    >

    `<h1 className="text-5xl font-bold text-gray-900 mb-6">`

    Entre em Contato

    `</h1>`

    `<p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">`

    Nossa equipe especializada está pronta para atender suas necessidades em licitações governamentais

    e fornecer as melhores soluções em instrumentos musicais e equipamentos de áudio.

    `</p>`

    </motion.div>

    `<div className="grid lg:grid-cols-3 gap-12">`

    {/* Informações de Contato */}

    <motion.div

    initial={{ opacity: 0, x: -30 }}

    animate={{ opacity: 1, x: 0 }}

    transition={{ delay: 0.2 }}

    className="lg:col-span-1"

    >

    `<Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm mb-8">`

    `<CardHeader>`

    `<CardTitle className="text-2xl text-center mb-6">`

    Informações de Contato

    `</CardTitle>`

    `</CardHeader>`

    `<CardContent className="space-y-6">`

    {informacoesContato.map((item, index) => (

    <motion.div

    key={item.title}

    initial={{ opacity: 0, y: 20 }}

    animate={{ opacity: 1, y: 0 }}

    transition={{ delay: 0.3 + index * 0.1 }}

    className="flex items-start space-x-4"

    >

    `<div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shrink-0">`

    <item.icon className="w-6 h-6 text-white" />

    `</div>`

    `<div>`

    `<h3 className="font-semibold text-gray-900 mb-1">`{item.title}`</h3>`

    `<p className="text-blue-600 font-medium">`{item.info}`</p>`

    `<p className="text-sm text-gray-500">`{item.descricao}`</p>`

    `</div>`

    </motion.div>

    ))}

    `</CardContent>`

    `</Card>`

    {/* Destaques */}

    <motion.div

    initial={{ opacity: 0, y: 20 }}

    animate={{ opacity: 1, y: 0 }}

    transition={{ delay: 0.6 }}

    className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-2xl p-6 text-white"

    >

    `<div className="text-center">`

    `<Users className="w-12 h-12 mx-auto mb-4 opacity-80" />`

    `<h3 className="text-lg font-semibold mb-2">`AtendimentoEspecializado`</h3>`

    `<p className="text-sm opacity-90">`

    Equipe com mais de 20 anos de experiência em licitações governamentais

    `</p>`

    `</div>`

    </motion.div>

    </motion.div>

    {/* Formulário de Contato */}

    <motion.div

    initial={{ opacity: 0, x: 30 }}

    animate={{ opacity: 1, x: 0 }}

    transition={{ delay: 0.4 }}

    className="lg:col-span-2"

    >

    `<Card className="shadow-xl border-0 bg-white/90 backdrop-blur-sm">`

    `<CardHeader>`

    `<CardTitle className="text-2xl flex items-center gap-2">`

    `<FileText className="w-6 h-6 text-blue-600" />`

    Formulário de Contato

    `</CardTitle>`

    `<p className="text-gray-600">`

    Preencha o formulário abaixo e nossa equipe entrará em contato em breve

    `</p>`

    `</CardHeader>`

    `<CardContent>`

    <form onSubmit={handleSubmit} className="space-y-6">

    `<div className="grid grid-cols-1 md:grid-cols-2 gap-6">`

    `<div>`

    `<label className="block text-sm font-medium text-gray-700 mb-2">`

    NomeCompleto *

    `</label>`

    <Input

    type="text"

    value={formData.nome}

    onChange={(e) => handleInputChange('nome', e.target.value)}

    placeholder="Seu nome completo"

    required

    />

    `</div>`

    `<div>`

    `<label className="block text-sm font-medium text-gray-700 mb-2">`

    E-mail *

    `</label>`

    <Input

    type="email"

    value={formData.email}

    onChange={(e) => handleInputChange('email', e.target.value)}

    placeholder="seu@email.com"

    required

    />

    `</div>`

    `</div>`

    `<div className="grid grid-cols-1 md:grid-cols-2 gap-6">`

    `<div>`

    `<label className="block text-sm font-medium text-gray-700 mb-2">`

    Telefone

    `</label>`

    <Input

    type="tel"

    value={formData.telefone}

    onChange={(e) => handleInputChange('telefone', e.target.value)}

    placeholder="(11) 99999-9999"

    />

    `</div>`

    `<div>`

    `<label className="block text-sm font-medium text-gray-700 mb-2">`

    Órgão/Instituição

    `</label>`

    <Input

    type="text"

    value={formData.orgao}

    onChange={(e) => handleInputChange('orgao', e.target.value)}

    placeholder="Nome do órgão ou instituição"

    />

    `</div>`

    `</div>`

    `<div>`

    `<label className="block text-sm font-medium text-gray-700 mb-2">`

    Tipo de Solicitação *

    `</label>`

    <Select value={formData.tipo_solicitacao} onValueChange={(value) => handleInputChange('tipo_solicitacao', value)}>

    `<SelectTrigger>`

    `<SelectValue placeholder="Selecione o tipo de solicitação" />`

    `</SelectTrigger>`

    `<SelectContent>`

    {tiposSolicitacao.map(tipo => (

    <SelectItem key={tipo} value={tipo}>{tipo}`</SelectItem>`

    ))}

    `</SelectContent>`

    `</Select>`

    `</div>`

    `<div>`

    `<label className="block text-sm font-medium text-gray-700 mb-2">`

    Mensagem *

    `</label>`

    <Textarea

    value={formData.mensagem}

    onChange={(e) => handleInputChange('mensagem', e.target.value)}

    placeholder="Descreva sua solicitação ou dúvida..."

    rows={5}

    required

    />

    `</div>`

    <Button

    type="submit"

    disabled={isSubmitting}

    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 text-lg"

    >

    {isSubmitting ? (

    `<div className="flex items-center gap-2">`

    `<div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />`

    Enviando...

    `</div>`

    ) : (

    `<div className="flex items-center gap-2">`

    `<Send className="w-5 h-5" />`

    EnviarMensagem

    `</div>`

    )}

    `</Button>`

    `</form>`

    `</CardContent>`

    `</Card>`

    </motion.div>

    `</div>`

    {/* Informações Adicionais */}

    <motion.div

    initial={{ opacity: 0, y: 30 }}

    whileInView={{ opacity: 1, y: 0 }}

    viewport={{ once: true }}

    className="mt-16 text-center"

    >

    `<div className="bg-gradient-to-br from-gray-900 to-blue-900 rounded-3xl p-12 text-white">`

    `<h2 className="text-3xl font-bold mb-4">`

    Compromisso com a Excelência

    `</h2>`

    `<p className="text-xl opacity-90 max-w-3xl mx-auto">`

    Há mais de 80 anos construindo pontes entre a música e a educação.

    Nossa experiência em licitações governamentais garante processos transparentes

    e produtos de qualidade internacional para o setor público.

    `</p>`

    `</div>`

    </motion.div>

    `</div>`

    `</div>`

  );

}
