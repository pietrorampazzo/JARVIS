importReactfrom"react";

import { base44 } from"@/api/base44Client";

importAtaCardDetalhadofrom"../components/atas/AtaCardDetalhado";

importAtaFiltersfrom"../components/atas/AtaFilters";

import { motion } from"framer-motion";

import { FileText, Search } from"lucide-react";

exportdefaultfunctionAtasPage() {

  const [atas, setAtas] = React.useState([]);

  const [isLoading, setIsLoading] = React.useState(true);

  const [tipoFilter, setTipoFilter] = React.useState("all");

  const [statusFilter, setStatusFilter] = React.useState("all");

  React.useEffect(() => {

    loadAtas();

  }, []);

  const loadAtas = async () => {

    setIsLoading(true);

    try {

    const data = await base44.entities.Ata.list('-created_date');

    setAtas(data);

    } catch (error) {

    console.error('Erro ao carregar atas:', error);

    } finally {

    setIsLoading(false);

    }

  };

  const filteredAtas = atas.filter(ata => {

    const tipoMatch = tipoFilter === "all" || ata.tipo === tipoFilter;

    const statusMatch = statusFilter === "all" || ata.status === statusFilter;

    return tipoMatch && statusMatch;

  });

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

    `<div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center">`

    `<FileText className="w-8 h-8 text-white" />`

    `</div>`

    `</div>`

    `<h1 className="text-5xl font-bold text-gray-900 mb-6">`

    AtasGovernamentaisVigentes

    `</h1>`

    `<p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">`

    Explore nossas atas ativas de órgãos municipais, estaduais e federais.

    Encontre oportunidades para sua instituição com produtos de alta qualidade e credibilidade comprovada.

    `</p>`

    </motion.div>

    {/* Filtros */}

    <motion.div

    initial={{ opacity: 0, y: 20 }}

    animate={{ opacity: 1, y: 0 }}

    transition={{ delay: 0.2 }}

    >

    <AtaFilters

    tipoFilter={tipoFilter}

    setTipoFilter={setTipoFilter}

    statusFilter={statusFilter}

    setStatusFilter={setStatusFilter}

    totalAtas={filteredAtas.length}

    />

    </motion.div>

    {/* Conteúdo */}

    {isLoading ? (

    `<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">`

    {Array(9).fill(0).map((_, i) => (

    <div key={i} className="animate-pulse">

    `<div className="bg-gray-200 rounded-2xl h-72"></div>`

    `</div>`

    ))}

    `</div>`

    ) : filteredAtas.length > 0 ? (

    <motion.div

    initial={{ opacity: 0 }}

    animate={{ opacity: 1 }}

    transition={{ delay: 0.3 }}

    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8"

    >

    {filteredAtas.map((ata, index) => (

    <AtaCardDetalhado key={ata.id} ata={ata} index={index} />

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

    `<Search className="w-12 h-12 text-gray-400" />`

    `</div>`

    `<h3 className="text-2xl font-semibold text-gray-900 mb-4">`

    Nenhuma ata encontrada

    `</h3>`

    `<p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">`

    Não encontramos atas com os filtros selecionados. Tente ajustar os filtros ou remover algumas restrições.

    `</p>`

    </motion.div>

    )}

    `</div>`

    `</div>`

  );

}
