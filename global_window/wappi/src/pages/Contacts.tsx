import { useState, useMemo, useRef } from 'react';
import { Search, Plus, Filter, Download, MoreHorizontal, ChevronDown, ChevronUp, CheckSquare, Bot, Mail, Phone, Clock, X, Save } from 'lucide-react';

const initialContacts = [
    {
        id: '1',
        name: 'Maria Silva',
        company: 'Empresa Alpha',
        email: 'maria.silva@alpha.com',
        phone: '+55 11 98765-4321',
        owner: 'Alice (Closer)',
        status: 'Conectado',
        lastActivity: 'Hoje às 14:23',
    },
    {
        id: '2',
        name: 'João Souza',
        company: 'Souza Tech',
        email: 'joao.souza@tech.com',
        phone: '+55 21 91234-5678',
        owner: 'Roberto (SDR)',
        status: 'Cadencia',
        lastActivity: 'Ontem',
    },
    {
        id: '3',
        name: 'Carlos Empreendimentos',
        company: 'Empreendimentos CE',
        email: 'contato@ce.com.br',
        phone: '+55 31 99999-1111',
        owner: 'Nenhum',
        status: 'Lead',
        lastActivity: '2 de Mar, 2026',
    },
    {
        id: '4',
        name: 'Ana Oliveira',
        company: 'Oliveira & Cia',
        email: 'ana@oliveira.com',
        phone: '+55 41 98888-2222',
        owner: 'Alice (Closer)',
        status: 'Ganho',
        lastActivity: '28 de Fev, 2026',
    },
    {
        id: '5',
        name: 'Paulo Santos',
        company: 'Santos Logística',
        email: 'paulo.log@santos.net',
        phone: '+55 51 97777-3333',
        owner: 'Carlos (Suporte)',
        status: 'Perdido',
        lastActivity: '15 de Fev, 2026',
    }
];

export default function Contacts() {
    const [contacts, setContacts] = useState(initialContacts);
    const [selectedRows, setSelectedRows] = useState<string[]>([]);
    const [activeTab, setActiveTab] = useState<'all' | 'my'>('all');
    const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc' | 'desc' } | null>(null);
    const [editingContact, setEditingContact] = useState<any | null>(null);
    const [isCreatingContact, setIsCreatingContact] = useState(false);
    const [showFilters, setShowFilters] = useState(false);
    const [newContactData, setNewContactData] = useState({ name: '', phone: '', email: '', company: '' });
    const fileInputRef = useRef<HTMLInputElement>(null);

    const updateContact = (id: string, updates: any) => {
        setContacts(prev => prev.map(c => c.id === id ? { ...c, ...updates } : c));
    };

    const handleSaveEdit = () => {
        if (editingContact) {
            updateContact(editingContact.id, editingContact);
            setEditingContact(null);
        }
    };

    const sortedContacts = useMemo(() => {
        let sortableContacts = [...contacts];
        if (sortConfig !== null) {
            sortableContacts.sort((a: any, b: any) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? -1 : 1;
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? 1 : -1;
                }
                return 0;
            });
        }
        return sortableContacts;
    }, [sortConfig]);

    const requestSort = (key: string) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const getSortIcon = (key: string) => {
        if (!sortConfig || sortConfig.key !== key) {
            return <ChevronDown size={14} className="text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity" />;
        }
        return sortConfig.direction === 'asc' ? <ChevronUp size={14} className="text-primary" /> : <ChevronDown size={14} className="text-primary" />;
    };

    const toggleRow = (id: string) => {
        if (selectedRows.includes(id)) {
            setSelectedRows(selectedRows.filter(rowId => rowId !== id));
        } else {
            setSelectedRows([...selectedRows, id]);
        }
    };

    const toggleAll = () => {
        if (selectedRows.length === sortedContacts.length) {
            setSelectedRows([]);
        } else {
            setSelectedRows(sortedContacts.map(c => c.id));
        }
    };

    const getStatusStyle = (status: string) => {
        switch (status) {
            case 'Lead': return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400';
            case 'Cadencia': return 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400';
            case 'Conectado': return 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400';
            case 'Qualificado': return 'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400';
            case 'Ganho': return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400';
            case 'Perdido': return 'bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-400';
            default: return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400';
        }
    };

    return (
        <div className="flex h-full flex-col">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold dark:text-white">Contatos</h1>
                    <p className="text-sm text-slate-500">Gestão completa da base de leads e clientes.</p>
                </div>
                <div className="flex gap-3">
                    <input
                        type="file"
                        ref={fileInputRef}
                        accept=".xlsx, .xls, .csv"
                        className="hidden"
                        onChange={(e) => {
                            if (e.target.files && e.target.files.length > 0) {
                                alert(`Arquivo ${e.target.files[0].name} selecionado para importação (Simulação).`);
                            }
                        }}
                    />
                    <button onClick={() => fileInputRef.current?.click()} className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 font-semibold text-slate-700 shadow-sm transition-all hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                        <Download size={16} /> Importar Arquivo (.xlsx)
                    </button>
                    <button onClick={() => setIsCreatingContact(true)} className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90">
                        <Plus size={18} /> Criar Contato
                    </button>
                </div>
            </div>

            <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
                {/* CRM Controls & Tools */}
                <div className="border-b border-slate-200 p-4 dark:border-slate-800">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex border-b border-slate-200 dark:border-slate-700">
                            <button
                                onClick={() => setActiveTab('all')}
                                className={`px-4 py-2 text-sm font-semibold transition-colors ${activeTab === 'all' ? 'border-b-2 border-primary text-primary' : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'}`}
                            >
                                Todos os Contatos
                            </button>
                            <button
                                onClick={() => setActiveTab('my')}
                                className={`px-4 py-2 text-sm font-semibold transition-colors ${activeTab === 'my' ? 'border-b-2 border-primary text-primary' : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'}`}
                            >
                                Meus Contatos
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center justify-between gap-4">
                        <div className="flex flex-1 items-center gap-3">
                            <div className="relative w-full max-w-sm">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                                <input
                                    type="text"
                                    placeholder="Pesquisar nome, telefone, empresa..."
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-4 text-sm text-slate-900 shadow-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800/50 dark:text-white"
                                />
                            </div>
                            <button
                                onClick={() => setShowFilters(!showFilters)}
                                className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium shadow-sm transition-colors ${showFilters ? 'bg-primary/10 border-primary text-primary dark:bg-primary/20 dark:text-primary-light' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300'}`}
                            >
                                <Filter size={16} />
                                Filtros Avançados {showFilters ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                            </button>
                        </div>
                        {selectedRows.length > 0 && (
                            <div className="flex items-center gap-3 rounded-lg bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400 shadow-sm border border-indigo-100 dark:border-indigo-500/20">
                                <span>{selectedRows.length} selecionado(s)</span>
                                <div className="h-4 w-px bg-indigo-200 dark:bg-indigo-500/30"></div>
                                <select
                                    className="bg-transparent border-none text-sm font-semibold focus:ring-0 p-0 text-indigo-700 dark:text-indigo-400 cursor-pointer outline-none"
                                    onChange={(e) => {
                                        if (e.target.value !== '') {
                                            const newOwner = e.target.value;
                                            setContacts(prev => prev.map(c => selectedRows.includes(c.id) ? { ...c, owner: newOwner } : c));
                                            setSelectedRows([]);
                                            e.target.value = '';
                                        }
                                    }}
                                    defaultValue=""
                                >
                                    <option value="" disabled>Ações em Massa...</option>
                                    <optgroup label="Atribuir Proprietário">
                                        <option value="Nenhum">Limpar Proprietário</option>
                                        <option value="Alice (Closer)">Para: Alice (Closer)</option>
                                        <option value="Roberto (SDR)">Para: Roberto (SDR)</option>
                                        <option value="Carlos (Suporte)">Para: Carlos (Suporte)</option>
                                    </optgroup>
                                </select>
                            </div>
                        )}
                    </div>

                    {/* Advanced Filters Panel */}
                    {showFilters && (
                        <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50 grid grid-cols-1 md:grid-cols-4 gap-4 animate-in slide-in-from-top-2 fade-in">
                            <div>
                                <label className="mb-1 block text-xs font-semibold text-slate-500 dark:text-slate-400">Proprietário (Responsável)</label>
                                <select className="w-full rounded-lg border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
                                    <option value="all">Qualquer Agente</option>
                                    <option value="Alice (Closer)">Alice (Closer)</option>
                                    <option value="Roberto (SDR)">Roberto (SDR)</option>
                                    <option value="Nenhum">Não Atribuído</option>
                                </select>
                            </div>
                            <div>
                                <label className="mb-1 block text-xs font-semibold text-slate-500 dark:text-slate-400">Fase do Funil (Status)</label>
                                <select className="w-full rounded-lg border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
                                    <option value="all">Todas as Fases</option>
                                    <option value="Lead">Lead</option>
                                    <option value="Cadencia">Cadencia</option>
                                    <option value="Conectado">Conectado</option>
                                    <option value="Qualificado">Qualificado</option>
                                    <option value="Ganho">Ganho / Cliente</option>
                                    <option value="Perdido">Perdido</option>
                                </select>
                            </div>
                            <div>
                                <label className="mb-1 block text-xs font-semibold text-slate-500 dark:text-slate-400">Última Atividade</label>
                                <select className="w-full rounded-lg border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200">
                                    <option value="any">A qualquer momento</option>
                                    <option value="today">Hoje</option>
                                    <option value="yesterday">Ontem</option>
                                    <option value="last7days">Últimos 7 dias</option>
                                </select>
                            </div>
                            <div className="flex items-end gap-2">
                                <button className="flex flex-1 items-center justify-center rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100">Aplicar</button>
                                <button onClick={() => setShowFilters(false)} className="flex items-center justify-center rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">Limpar</button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Data Table */}
                <div className="flex-1 overflow-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="sticky top-0 z-10 bg-slate-50 text-xs uppercase text-slate-500 shadow-sm dark:bg-slate-800/80 dark:text-slate-400">
                            <tr>
                                <th scope="col" className="px-6 py-4">
                                    <button onClick={toggleAll} className="text-slate-400 hover:text-primary">
                                        <CheckSquare size={18} className={selectedRows.length === sortedContacts.length && sortedContacts.length > 0 ? 'text-primary' : ''} />
                                    </button>
                                </th>
                                <th scope="col" className="px-6 py-4 font-semibold group cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" onClick={() => requestSort('name')}>
                                    <div className="flex items-center gap-1">NOME / EMPRESA {getSortIcon('name')}</div>
                                </th>
                                <th scope="col" className="px-6 py-4 font-semibold group cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" onClick={() => requestSort('email')}>
                                    <div className="flex items-center gap-1">CONTATO {getSortIcon('email')}</div>
                                </th>
                                <th scope="col" className="px-6 py-4 font-semibold group cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" onClick={() => requestSort('status')}>
                                    <div className="flex items-center gap-1">STATUS DO LEAD {getSortIcon('status')}</div>
                                </th>
                                <th scope="col" className="px-6 py-4 font-semibold group cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" onClick={() => requestSort('owner')}>
                                    <div className="flex items-center gap-1">PROPRIETÁRIO {getSortIcon('owner')}</div>
                                </th>
                                <th scope="col" className="px-6 py-4 font-semibold group cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors" onClick={() => requestSort('lastActivity')}>
                                    <div className="flex items-center gap-1">ÚLTIMA ATIVIDADE {getSortIcon('lastActivity')}</div>
                                </th>
                                <th scope="col" className="px-6 py-4 font-semibold"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 bg-white dark:divide-slate-800 dark:bg-slate-900">
                            {sortedContacts.map((contact) => (
                                <tr key={contact.id} className="transition-colors hover:bg-slate-50/80 dark:hover:bg-slate-800/40">
                                    <td className="px-6 py-4">
                                        <button onClick={() => toggleRow(contact.id)} className="text-slate-300 hover:text-primary dark:text-slate-600">
                                            <CheckSquare size={18} className={selectedRows.includes(contact.id) ? 'text-primary' : ''} />
                                        </button>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <img src={`https://ui-avatars.com/api/?name=${encodeURIComponent(contact.name)}&background=Random`} className="h-9 w-9 rounded-full" />
                                            <div>
                                                <p className="font-semibold text-slate-900 dark:text-white hover:text-primary cursor-pointer hover:underline" onClick={() => setEditingContact(contact)}>{contact.name}</p>
                                                <p className="text-xs text-slate-500">{contact.company}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-col gap-1">
                                            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                                                <Phone size={14} className="text-slate-400" />
                                                <span className="text-xs">{contact.phone}</span>
                                            </div>
                                            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                                                <Mail size={14} className="text-slate-400" />
                                                <span className="text-xs">{contact.email}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusStyle(contact.status)}`}>
                                            {contact.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            {contact.owner !== 'Nenhum' && <Bot size={16} className="text-primary" />}
                                            <select
                                                value={contact.owner}
                                                onChange={(e) => updateContact(contact.id, { owner: e.target.value })}
                                                className="bg-transparent text-sm font-medium text-slate-700 focus:ring-0 dark:text-slate-300 dark:bg-slate-900 border-none p-0 cursor-pointer w-full focus:outline-none"
                                            >
                                                <option value="Nenhum">Não atribuído</option>
                                                <option value="Alice (Closer)">Alice (Closer)</option>
                                                <option value="Roberto (SDR)">Roberto (SDR)</option>
                                                <option value="Carlos (Suporte)">Carlos (Suporte)</option>
                                            </select>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2 text-slate-500">
                                            <Clock size={14} />
                                            <span className="text-xs">{contact.lastActivity}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-300">
                                            <MoreHorizontal size={18} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Footer / Pagination */}
                <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-6 py-4 dark:border-slate-800 dark:bg-slate-900/50">
                    <span className="text-sm text-slate-500">Mostrando 1 a 5 de 42 contatos</span>
                    <div className="flex items-center gap-2">
                        <button className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-500 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800">
                            Anterior
                        </button>
                        <button className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                            Próxima
                        </button>
                    </div>
                </div>
            </div>

            {/* Edit Contact Modal */}
            {editingContact && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <div className="mb-6 flex items-center justify-between">
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Editar Contato</h2>
                            <button onClick={() => setEditingContact(null)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"><X size={20} /></button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Nome Completo</label>
                                <input
                                    type="text"
                                    value={editingContact.name}
                                    onChange={(e) => setEditingContact({ ...editingContact, name: e.target.value })}
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Empresa</label>
                                <input
                                    type="text"
                                    value={editingContact.company}
                                    onChange={(e) => setEditingContact({ ...editingContact, company: e.target.value })}
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Telefone</label>
                                    <input
                                        type="text"
                                        value={editingContact.phone}
                                        onChange={(e) => setEditingContact({ ...editingContact, phone: e.target.value })}
                                        className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                </div>
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">E-mail</label>
                                    <input
                                        type="email"
                                        value={editingContact.email}
                                        onChange={(e) => setEditingContact({ ...editingContact, email: e.target.value })}
                                        className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Status do Lead</label>
                                <select
                                    value={editingContact.status}
                                    onChange={(e) => setEditingContact({ ...editingContact, status: e.target.value })}
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                >
                                    <option value="Lead">Lead</option>
                                    <option value="Cadencia">Cadencia</option>
                                    <option value="Conectado">Conectado</option>
                                    <option value="Qualificado">Qualificado</option>
                                    <option value="Ganho">Ganho</option>
                                    <option value="Perdido">Perdido</option>
                                </select>
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end gap-3">
                            <button onClick={() => setEditingContact(null)} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">Cancelar</button>
                            <button onClick={handleSaveEdit} className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white shadow-lg shadow-primary/20 hover:bg-primary/90">
                                <Save size={16} /> Salvar Alterações
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Create Contact Modal */}
            {isCreatingContact && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <div className="mb-6 flex items-center justify-between">
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Criar Novo Contato</h2>
                            <button onClick={() => setIsCreatingContact(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"><X size={20} /></button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Nome Completo</label>
                                <input
                                    type="text"
                                    value={newContactData.name}
                                    onChange={(e) => setNewContactData({ ...newContactData, name: e.target.value })}
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    placeholder="Ex: Ana Oliveira"
                                />
                            </div>
                            <div>
                                <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Empresa</label>
                                <input
                                    type="text"
                                    value={newContactData.company}
                                    onChange={(e) => setNewContactData({ ...newContactData, company: e.target.value })}
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Telefone (WahtsApp)</label>
                                    <input
                                        type="text"
                                        value={newContactData.phone}
                                        onChange={(e) => setNewContactData({ ...newContactData, phone: e.target.value })}
                                        className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                        placeholder="+55 11 99999-9999"
                                    />
                                </div>
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">E-mail</label>
                                    <input
                                        type="email"
                                        value={newContactData.email}
                                        onChange={(e) => setNewContactData({ ...newContactData, email: e.target.value })}
                                        className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end gap-3">
                            <button onClick={() => setIsCreatingContact(false)} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">Cancelar</button>
                            <button
                                onClick={() => {
                                    alert('Contato Criado!');
                                    setIsCreatingContact(false);
                                    setNewContactData({ name: '', phone: '', email: '', company: '' });
                                }}
                                className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white shadow-lg shadow-primary/20 hover:bg-primary/90"
                            >
                                Criar Contato
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
