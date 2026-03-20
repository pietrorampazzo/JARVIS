import { useState } from 'react';
import { Bot, Plus, Edit2, Play, Square, Settings, X, Sparkles } from 'lucide-react';

const initialAgents = [
    {
        id: 'agent-1',
        nome: 'Alice (Closer de Vendas)',
        identidade: 'Vendedora persuasiva e simpática',
        prompt: 'Você é a Alice, uma closer de vendas focada em conversão e empatia com o cliente...',
        cor: 'bg-pink-500',
        modo: 'Full',
        status: 'active',
        leadsHandled: 142,
        conversionRate: '24%',
    },
    {
        id: 'agent-2',
        nome: 'Roberto (SDR)',
        identidade: 'Especialista em qualificação',
        prompt: 'Você é o Roberto, responsável por qualificar leads fazendo perguntas de BANT...',
        cor: 'bg-blue-500',
        modo: 'Prospectando',
        status: 'idle',
        leadsHandled: 89,
        conversionRate: '15%',
    },
    {
        id: 'agent-3',
        nome: 'Carlos (Suporte)',
        identidade: 'Suporte Técnico e CS',
        prompt: 'Você é o Carlos, suporte técnico ágil e cordial, focado em resolver problemas rápido...',
        cor: 'bg-amber-500',
        modo: 'Atendendo',
        status: 'offline',
        leadsHandled: 310,
        conversionRate: 'N/A',
    }
];

export default function Agents() {
    const [agents] = useState(initialAgents);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalMode, setModalMode] = useState<'create' | 'edit' | 'settings'>('create');
    const [selectedAgent, setSelectedAgent] = useState<any>(null);

    const openModal = (mode: 'create' | 'edit' | 'settings', agent: any = null) => {
        setModalMode(mode);
        setSelectedAgent(agent);
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedAgent(null);
    };

    return (
        <div className="flex h-full flex-col">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold dark:text-white">Gestão da Equipe de IA</h1>
                    <p className="text-sm text-slate-500">Configure personas, scripts de vendas e comportamento dos seus agentes virtuais.</p>
                </div>
                <button
                    onClick={() => openModal('create')}
                    className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90">
                    <Plus size={18} /> Novo Agente
                </button>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {agents.map((agent: any) => (
                    <div key={agent.id} className="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all hover:border-primary/30 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900/50">
                        {/* Card Header */}
                        <div className="border-b border-slate-100 p-6 dark:border-slate-800">
                            <div className="mb-4 flex items-center justify-between">
                                <div className={`flex size-12 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800 ${agent.status === 'active' ? 'text-emerald-500 bg-emerald-50 dark:bg-emerald-500/10' : 'text-slate-400'}`}>
                                    <Bot size={24} />
                                </div>
                                <div className={`flex items-center gap-2 rounded-full px-2.5 py-1 text-xs font-bold leading-none ${agent.status === 'active' ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-400' : agent.status === 'idle' ? 'bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'}`}>
                                    <span className="relative flex h-2 w-2">
                                        {agent.status === 'active' && (
                                            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                                        )}
                                        <span className={`relative inline-flex h-2 w-2 rounded-full ${agent.status === 'active' ? 'bg-emerald-500' : agent.status === 'idle' ? 'bg-amber-500' : 'bg-slate-400'}`}></span>
                                    </span>
                                    {agent.status === 'active' ? 'Online' : agent.status === 'idle' ? 'Ocioso' : 'Offline'}
                                </div>
                            </div>
                            <div className="flex items-start justify-between gap-4">
                                <div>
                                    <h3 className="text-lg font-bold text-slate-900 dark:text-white">{agent.nome}</h3>
                                    <p className="text-sm font-medium text-slate-500">{agent.identidade}</p>
                                </div>
                                <div className={`h-6 w-6 shrink-0 rounded-md ${agent.cor} shadow-sm border border-black/5`}></div>
                            </div>

                            <div className="mt-4 flex">
                                <span className="inline-flex items-center rounded-lg bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary dark:bg-primary/20">
                                    Modo: {agent.modo}
                                </span>
                            </div>
                        </div>

                        {/* Card Body */}
                        <div className="p-6">
                            <p className="mb-6 line-clamp-3 text-sm text-slate-500 dark:text-slate-400">
                                "{agent.prompt}"
                            </p>

                            <div className="mb-6 grid grid-cols-2 gap-4 rounded-xl bg-slate-50 p-4 dark:bg-slate-800/50">
                                <div>
                                    <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Leads Atendidos</p>
                                    <p className="text-lg font-bold text-slate-900 dark:text-white">{agent.leadsHandled}</p>
                                </div>
                                <div>
                                    <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Taxa de Conversão</p>
                                    <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">{agent.conversionRate}</p>
                                </div>
                            </div>

                            {/* Card Actions */}
                            <div className="flex items-center justify-between gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => openModal('edit', agent)}
                                        className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300">
                                        <Edit2 size={16} />
                                    </button>
                                    <button
                                        onClick={() => openModal('settings', agent)}
                                        className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-primary dark:hover:bg-slate-800">
                                        <Settings size={16} />
                                    </button>
                                </div>
                                <div className="flex gap-2">
                                    {agent.status === 'active' ? (
                                        <button className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50 text-amber-600 hover:bg-amber-100 dark:bg-amber-500/10 dark:text-amber-400">
                                            <Square size={16} fill="currentColor" />
                                        </button>
                                    ) : (
                                        <button className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400">
                                            <Play size={16} fill="currentColor" />
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Painel Modal do Agente */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm dark:bg-slate-900/80">
                    <div className="w-full max-w-2xl overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-slate-900">
                        {/* Modal Header */}
                        <div className="flex items-center gap-3 border-b border-slate-100 p-4 dark:border-slate-800">
                            <div className="flex-1">
                                <h2 className="text-lg font-bold dark:text-white">
                                    {modalMode === 'create' ? 'Criar Novo Agente de IA' : modalMode === 'edit' ? 'Editar Agente de IA' : 'Configurações Avançadas'}
                                </h2>
                                <p className="text-xs text-slate-500">
                                    {modalMode === 'settings' ? 'Ajuste os parâmetros do modelo e criatividade.' : 'Defina a persona, comportamento e base de conhecimento.'}
                                </p>
                            </div>

                            {modalMode !== 'settings' && (
                                <button title="Gerar Identidade por IA" className="flex items-center justify-center h-8 w-8 rounded-md border border-indigo-200 bg-indigo-50 text-indigo-600 transition-colors hover:bg-indigo-100 dark:border-indigo-500/30 dark:bg-indigo-500/10 dark:text-indigo-400">
                                    <Sparkles size={16} />
                                </button>
                            )}

                            <button
                                onClick={closeModal}
                                className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300">
                                <X size={18} />
                            </button>
                        </div>

                        {/* Modal Body */}
                        <div className="max-h-[75vh] overflow-y-auto p-5">
                            {modalMode !== 'settings' ? (
                                <div className="space-y-4">
                                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                                        <div className="space-y-1.5">
                                            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Nome do Agente</label>
                                            <input
                                                type="text"
                                                defaultValue={selectedAgent?.nome || ''}
                                                placeholder="ex: Alice (Closer de Vendas)"
                                                className="w-full rounded-lg border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                            />
                                        </div>
                                        <div className="space-y-1.5">
                                            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Identidade / Cargo</label>
                                            <input
                                                type="text"
                                                defaultValue={selectedAgent?.identidade || ''}
                                                placeholder="ex: Especialista em Vendas B2B"
                                                className="w-full rounded-lg border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                            />
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                                        <div className="space-y-1.5">
                                            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Modo de Operação</label>
                                            <select
                                                defaultValue={selectedAgent?.modo || 'Full'}
                                                className="w-full rounded-lg border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                            >
                                                <option value="Atendendo">Atendendo (Responde Dúvidas)</option>
                                                <option value="Prospectando">Prospectando (Inicia Conversas)</option>
                                                <option value="Full">Full (Atende, Qualifica e Vende)</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div className="space-y-1.5">
                                        <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">Prompt do Sistema (O Cérebro)</label>
                                        <textarea
                                            defaultValue={selectedAgent?.prompt || ''}
                                            rows={4}
                                            placeholder="Você é um assistente focado em conversão. Sempre pergunte o orçamento..."
                                            className="w-full resize-none rounded-lg border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                        />
                                        <p className="text-[10px] text-slate-500">Este texto define **exatamente** como a IA vai se comportar, argumentar e fechar vendas.</p>
                                    </div>

                                    <div className="space-y-1.5 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-center dark:border-slate-700 dark:bg-slate-800/50">
                                        <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 dark:bg-slate-700">
                                            <Plus size={16} className="text-slate-500 dark:text-slate-400" />
                                        </div>
                                        <h3 className="mt-2 text-xs font-bold text-slate-900 dark:text-white">Base de Conhecimento</h3>
                                        <p className="mt-0.5 text-[10px] text-slate-500">Arraste PDFs, DOCX ou Fotos aqui.</p>
                                        <button className="mt-3 rounded-md bg-white px-3 py-1.5 text-xs font-bold text-slate-700 shadow-sm border border-slate-200 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                                            Selecionar Arquivos
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold dark:text-slate-300">Modelo OpenAI</label>
                                        <select className="w-full rounded-lg border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white">
                                            <option>gpt-4o</option>
                                            <option>gpt-4o-mini</option>
                                            <option>gpt-3.5-turbo</option>
                                        </select>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold dark:text-slate-300">Temperatura (Criatividade)</label>
                                        <input type="range" min="0" max="1" step="0.1" defaultValue="0.7" className="w-full accent-primary" />
                                        <div className="flex justify-between text-xs text-slate-500">
                                            <span>Preciso</span>
                                            <span>Criativo</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="flex items-center justify-end gap-2 border-t border-slate-100 p-4 bg-slate-50 dark:border-slate-800 dark:bg-slate-900/50">
                            <button
                                onClick={closeModal}
                                className="rounded-lg px-4 py-2 text-sm font-bold text-slate-600 transition-colors hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800">
                                Cancelar
                            </button>
                            <button className="rounded-lg bg-primary px-5 py-2 text-sm font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90">
                                Salvar Agente
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
