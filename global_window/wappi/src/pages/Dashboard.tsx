import {
    LineChart,
    Line,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { Users, MessageSquare, TrendingUp, DollarSign, Bot, ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

const conversionData = [
    { name: 'Seg', leads: 45, conversions: 12 },
    { name: 'Ter', leads: 52, conversions: 15 },
    { name: 'Qua', leads: 38, conversions: 10 },
    { name: 'Qui', leads: 65, conversions: 22 },
    { name: 'Sex', leads: 48, conversions: 14 },
    { name: 'Sáb', leads: 25, conversions: 5 },
    { name: 'Dom', leads: 20, conversions: 4 },
];

const messagesData = [
    { name: '08:00', sent: 120, received: 110 },
    { name: '10:00', sent: 350, received: 340 },
    { name: '12:00', sent: 200, received: 190 },
    { name: '14:00', sent: 480, received: 450 },
    { name: '16:00', sent: 520, received: 500 },
    { name: '18:00', sent: 300, received: 280 },
];

const KpiCard = ({ title, value, change, isPositive, icon: Icon }: any) => (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400">{title}</h3>
            <div className="flex size-10 items-center justify-center rounded-xl bg-slate-50 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                <Icon size={20} />
            </div>
        </div>
        <div className="flex items-end gap-4">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">{value}</h2>
            <div className={`mb-1 flex items-center gap-1 text-sm font-semibold ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
                {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                {change}%
            </div>
        </div>
    </div>
);

export default function Dashboard() {
    return (
        <div className="flex h-full flex-col gap-6 overflow-y-auto pb-8">
            <div className="flex flex-col gap-2">
                <h1 className="text-2xl font-bold dark:text-white">Dashboard Geral</h1>
                <p className="text-sm text-slate-500">Métricas de performance dos seus agentes e funil de vendas.</p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <KpiCard title="Total de Leads (Mês)" value="1,248" change={12.5} isPositive={true} icon={Users} />
                <KpiCard title="Taxa de Conversão" value="18.2%" change={2.4} isPositive={true} icon={TrendingUp} />
                <KpiCard title="Mensagens Trocadas" value="45.2k" change={5.1} isPositive={true} icon={MessageSquare} />
                <KpiCard title="Receita Projetada" value="R$ 142k" change={1.2} isPositive={false} icon={DollarSign} />
            </div>

            {/* Main Charts */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

                {/* AI Performance Area Chart */}
                <div className="col-span-1 lg:col-span-2 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="mb-6 flex items-center justify-between">
                        <div>
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Desempenho de Aquisição</h3>
                            <p className="text-sm text-slate-500">Leads capturados vs convertidos na semana</p>
                        </div>
                        <select className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm font-medium text-slate-700 focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                            <option>Esta Semana</option>
                            <option>Mês Passado</option>
                        </select>
                    </div>

                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={conversionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorLeads" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#94a3b8" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorConversions" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#1FAD53" stopOpacity={0.4} />
                                        <stop offset="95%" stopColor="#1FAD53" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                    cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '4 4' }}
                                />
                                <Area type="monotone" dataKey="leads" name="Novos Leads" stroke="#94a3b8" strokeWidth={2} fillOpacity={1} fill="url(#colorLeads)" />
                                <Area type="monotone" dataKey="conversions" name="Convertidos" stroke="#1FAD53" strokeWidth={3} fillOpacity={1} fill="url(#colorConversions)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Agent Activity Bar Chart */}
                <div className="col-span-1 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="mb-6">
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Carga de Mensagens</h3>
                        <p className="text-sm text-slate-500">Volume processado hoje</p>
                    </div>

                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={messagesData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                                <Tooltip
                                    cursor={{ fill: '#f1f5f9' }}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                />
                                <Bar dataKey="received" name="Recebidas" fill="#cbd5e1" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="sent" name="Enviadas pela IA" fill="#1FAD53" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

                {/* Active Agents */}
                <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="mb-6 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Bot className="text-primary" size={20} />
                            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Status dos Agentes</h3>
                        </div>
                        <span className="flex items-center gap-1.5 rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400">
                            <span className="relative flex h-2 w-2">
                                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                            </span>
                            3 Online
                        </span>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between rounded-xl border border-slate-100 p-4 dark:border-slate-800">
                            <div className="flex items-center gap-3">
                                <div className="flex size-10 items-center justify-center rounded-lg bg-pink-100 text-pink-600 dark:bg-pink-500/20">A</div>
                                <div>
                                    <p className="font-bold text-slate-900 dark:text-white">Alice (Closer)</p>
                                    <p className="text-xs text-slate-500">Fechamentos e Objeções</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="font-bold text-slate-900 dark:text-white">142</p>
                                <p className="text-xs text-slate-500">Chats Ativos</p>
                            </div>
                        </div>

                        <div className="flex items-center justify-between rounded-xl border border-slate-100 p-4 dark:border-slate-800">
                            <div className="flex items-center gap-3">
                                <div className="flex size-10 items-center justify-center rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-500/20">R</div>
                                <div>
                                    <p className="font-bold text-slate-900 dark:text-white">Roberto (SDR)</p>
                                    <p className="text-xs text-slate-500">Qualificação Inicial</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="font-bold text-slate-900 dark:text-white">204</p>
                                <p className="text-xs text-slate-500">Chats Ativos</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Activity Timeline */}
                <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="mb-6 flex items-center gap-2">
                        <Activity className="text-primary" size={20} />
                        <h3 className="text-lg font-bold text-slate-900 dark:text-white">Atividade Recente</h3>
                    </div>

                    <div className="relative border-l border-slate-200 ml-4 pl-6 space-y-6 dark:border-slate-800">
                        <div className="relative">
                            <span className="absolute -left-[33px] flex h-4 w-4 items-center justify-center rounded-full bg-white ring-4 ring-white dark:bg-slate-900 dark:ring-slate-900">
                                <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                            </span>
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">Novo Lead Convertido: Empresa Alpha</p>
                            <p className="text-xs text-slate-500">Há 5 minutos pela Alice</p>
                        </div>
                        <div className="relative">
                            <span className="absolute -left-[33px] flex h-4 w-4 items-center justify-center rounded-full bg-white ring-4 ring-white dark:bg-slate-900 dark:ring-slate-900">
                                <span className="h-2 w-2 rounded-full bg-slate-300 dark:bg-slate-700"></span>
                            </span>
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">Upload de Conhecimento Concluído</p>
                            <p className="text-xs text-slate-500">Base "Objeções 2026.pdf" indexada. Há 45 min</p>
                        </div>
                        <div className="relative">
                            <span className="absolute -left-[33px] flex h-4 w-4 items-center justify-center rounded-full bg-white ring-4 ring-white dark:bg-slate-900 dark:ring-slate-900">
                                <span className="h-2 w-2 rounded-full bg-rose-500"></span>
                            </span>
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">Intervenção Humana Solicitada</p>
                            <p className="text-xs text-slate-500">Lead "Carlos Souza" transferido para Inbox. Há 2 horas</p>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    );
}
