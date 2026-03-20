
importReactfrom"react";

import { base44 } from"@/api/base44Client";

import { Card, CardContent, CardHeader } from"@/components/ui/card";

import { Button } from"@/components/ui/button";

import { motion } from"framer-motion";

import { ExternalLink, Award, Globe } from"lucide-react";

exportdefaultfunctionMarcasPage() {

  const [marcas, setMarcas] = React.useState([]);

  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {

    loadMarcas();

  }, []);

  const loadMarcas = async () => {

    setIsLoading(true);

    try {

    const data = await base44.entities.Marca.list();

    setMarcas(data);

    } catch (error) {

    console.error('Erro ao carregar marcas:', error);

    } finally {

    setIsLoading(false);

    }

  };

  return (

    `<div className="min-h-screen bg-gradient-to-br from-gray-50 to-white py-12">`

    `<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">`

    {/* Header */}

    <motion.div

    initial={{ opacity: 0, y: 30 }}

    animate={{ opacity: 1, y: 0 }}

    className="text-center mb-12"

    >

    `<div className="flex items-center justify-center mb-6">`

    <img

    src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68a73ee4f163ee9631b6ccc6/8d71721c1_ARTE_LOGO.png"

    alt="Arte Comercial"

    className="h-24 w-auto object-contain"

    />

    `</div>`

    `<h1 className="text-5xl font-bold text-gray-900 mb-6">`

    MarcasRepresentadas

    `</h1>`

    `<p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">`

    Somos representantes oficiais das principais marcas mundiais de instrumentos musicais e equipamentos de áudio.

    Tradição, qualidade e inovação em cada produto.

    `</p>`

    </motion.div>

    {/* Grid de Marcas */}

    {isLoading ? (

    `<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">`

    {Array(6).fill(0).map((_, i) => (

    <div key={i} className="animate-pulse">

    `<div className="bg-gray-200 rounded-2xl h-64"></div>`

    `</div>`

    ))}

    `</div>`

    ) : marcas.length > 0 ? (

    <motion.div

    initial={{ opacity: 0 }}

    animate={{ opacity: 1 }}

    transition={{ delay: 0.2 }}

    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"

    >

    {marcas.map((marca, index) => (

    <motion.div

    key={marca.id}

    initial={{ opacity: 0, y: 30 }}

    animate={{ opacity: 1, y: 0 }}

    transition={{ duration: 0.5, delay: index * 0.1 }}

    >

    `<Card className="group hover:shadow-2xl transition-all duration-500 border-0 bg-white/90 backdrop-blur-sm h-full">`

    `<CardHeader className="text-center pb-6">`

    `<div className="w-full h-32 flex items-center justify-center mb-6 bg-gray-50 rounded-xl">`

    {marca.logo_url ? (

    <img

    src={marca.logo_url}

    alt={marca.nome}

    className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-300"

    />

    ) : (

    `<div className="text-3xl font-bold text-gray-400">`

    {marca.nome}

    `</div>`

    )}

    `</div>`

    `<h3 className="text-2xl font-bold text-gray-900 mb-2">`

    {marca.nome}

    `</h3>`

    {marca.categoria_principal && (

    `<p className="text-sm text-gray-500 uppercase tracking-wider font-medium">`

    {marca.categoria_principal}

    `</p>`

    )}

    `</CardHeader>`

    `<CardContent className="pt-0">`

    {marca.descricao && (

    `<p className="text-gray-600 mb-6 leading-relaxed">`

    {marca.descricao}

    `</p>`

    )}

    {marca.site_oficial && (

    <Button

    variant="outline"

    className="w-full group-hover:bg-blue-50 group-hover:border-blue-200 transition-colors duration-300"

    asChild

    >

    <a href={marca.site_oficial} target="_blank" rel="noopener noreferrer">

    `<Globe className="w-4 h-4 mr-2" />`

    VisitarSiteOficial

    `<ExternalLink className="w-4 h-4 ml-2" />`

    `</a>`

    `</Button>`

    )}

    `</CardContent>`

    `</Card>`

    </motion.div>

    ))}

    </motion.div>

    ) : (

    <motion.div

    initial={{ opacity: 0, scale: 0.9 }}

    animate={{ opacity: 1, scale: 1 }}

    transition={{ delay: 0.3 }}

    className="text-center py-20"

    >

    `<div className="w-24 h-24 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">`

    `<Award className="w-12 h-12 text-gray-400" />`

    `</div>`

    `<h3 className="text-2xl font-semibold text-gray-900 mb-4">`

    Nenhuma marca encontrada

    `</h3>`

    `<p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">`

    As informações das marcas representadas serão carregadas em breve.

    `</p>`

    </motion.div>

    )}

    {/* Seção de Credenciais */}

    <motion.div

    initial={{ opacity: 0, y: 30 }}

    whileInView={{ opacity: 1, y: 0 }}

    viewport={{ once: true }}

    className="mt-20 bg-gradient-to-r from-blue-600 to-blue-800 rounded-3xl p-12 text-white text-center"

    >

    `<h2 className="text-3xl font-bold mb-4">`

    Representação OficialAutorizada

    `</h2>`

    `<p className="text-xl opacity-90 max-w-3xl mx-auto">`

    Como representantes oficiais, garantimos produtos originais, suporte técnico especializado

    e condições especiais para atendimento ao setor público através de nossas atas governamentais.

    `</p>`

    </motion.div>

    `</div>`

    `</div>`

  );

}
