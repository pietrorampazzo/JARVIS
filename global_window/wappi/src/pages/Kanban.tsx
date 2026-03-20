import { useState } from 'react';
import type { DropResult } from '@hello-pangea/dnd';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { MoreVertical, MessageCircle, Bot, X, Sparkles, Paperclip, CheckSquare, Calendar, User, Phone, Mail, Clock, ChevronDown, Plus } from 'lucide-react';

// Fake Data for CRM
const initialData = {
    columns: {
        'col-1': {
            id: 'col-1',
            title: 'Lead',
            taskIds: ['task-1', 'task-2'],
        },
        'col-2': {
            id: 'col-2',
            title: 'Cadencia',
            taskIds: ['task-3'],
        },
        'col-3': {
            id: 'col-3',
            title: 'Conectado',
            taskIds: ['task-4'],
        },
        'col-4': {
            id: 'col-4',
            title: 'Qualificado',
            taskIds: ['task-5'],
        },
        'col-5': {
            id: 'col-5',
            title: 'Ganho',
            taskIds: [],
        },
        'col-6': {
            id: 'col-6',
            title: 'Perdido',
            taskIds: [],
        },
    },
    tasks: {
        'task-1': {
            id: 'task-1', name: 'Laura Oliveira', phone: '+55 11 9999-8888', email: 'laura@email.com', value: 'R$ 4.500', agent: 'Alice (Closer)',
            description: 'Lead muito engajada, demonstrou interesse real no pacote premium durante a última conversa. Precisa de aprovação do sócio.',
            deadline: '10 Mar 2026',
            checklist: [{ id: 1, text: 'Enviar proposta PDF', done: true }, { id: 2, text: 'Agendar reunião com sócio', done: false }],
            attachments: [{ name: 'Briefing_Laura.pdf', size: '2.4 MB', type: 'pdf' }]
        },
        'task-2': {
            id: 'task-2', name: 'Carlos Ribeiro', phone: '+55 21 8888-7777', email: 'carlos.r@empresa.com', value: 'R$ 1.200', agent: 'Roberto (SDR)',
            description: 'Curioso sobre integrações. Ainda na fase de descoberta.',
            deadline: 'Sem prazo',
            checklist: [],
            attachments: []
        },
        'task-3': {
            id: 'task-3', name: 'Empresa X', phone: '+55 31 7777-6666', email: 'contato@empresax.com', value: 'R$ 12.000', agent: 'Alice (Closer)',
            description: 'B2B Enterprise. Ciclo de venda será longo. Focam muito em segurança e conformidade.',
            deadline: '30 Abr 2026',
            checklist: [{ id: 1, text: 'Assinar NDA', done: true }, { id: 2, text: 'Apresentação Técnica', done: false }, { id: 3, text: 'Drafitar Contrato', done: false }],
            attachments: [{ name: 'Cenários_B2B.docx', size: '1.1 MB', type: 'doc' }, { name: 'Logo_EmpresaX.png', size: '400 KB', type: 'img' }]
        },
        'task-4': {
            id: 'task-4', name: 'Juliana Costa', phone: '+55 41 6666-5555', email: 'jucosta@gmail.com', value: 'R$ 800', agent: 'Roberto (SDR)',
            description: 'Orçamento apertado, mas gostou muito do produto. Tentar upsell num plano anual com desconto.',
            deadline: '05 Mar 2026',
            checklist: [{ id: 1, text: 'Follow-up via WhatsApp', done: false }],
            attachments: []
        },
        'task-5': {
            id: 'task-5', name: 'Marcos Silva', phone: '+55 51 5555-4444', email: 'marcos@silvaimoveis.net', value: 'R$ 3.000', agent: 'Alice (Closer)',
            description: 'Precisa conectar com o ERP atual (Bling). Dúvidas técnicas sobre API.',
            deadline: '15 Mar 2026',
            checklist: [{ id: 1, text: 'Consultar com devs sobre API', done: true }, { id: 2, text: 'Enviar docs da API', done: false }],
            attachments: []
        },
    },
    columnOrder: ['col-1', 'col-2', 'col-3', 'col-4', 'col-5', 'col-6'],
};

export default function Kanban() {
    const [data, setData] = useState(initialData);
    const [selectedTask, setSelectedTask] = useState<any | null>(null);
    const [newItemText, setNewItemText] = useState('');
    const [isAddingItem, setIsAddingItem] = useState(false);
    const [isEditingDesc, setIsEditingDesc] = useState(false);
    const [descText, setDescText] = useState('');
    const [isCreatingLead, setIsCreatingLead] = useState(false);
    const [newLeadData, setNewLeadData] = useState({ name: '', phone: '', email: '', company: '' });

    const updateTask = (taskId: string, updates: any) => {
        setData(prev => ({
            ...prev,
            tasks: {
                ...prev.tasks,
                [taskId]: {
                    ...prev.tasks[taskId as keyof typeof prev.tasks],
                    ...updates
                }
            }
        }));
        if (selectedTask?.id === taskId) {
            setSelectedTask((prev: any) => ({ ...prev, ...updates }));
        }
    };

    const toggleChecklist = (checklistId: number) => {
        if (!selectedTask) return;
        const newChecklist = selectedTask.checklist.map((item: any) =>
            item.id === checklistId ? { ...item, done: !item.done } : item
        );
        updateTask(selectedTask.id, { checklist: newChecklist });
    };

    const addChecklistItem = () => {
        if (!selectedTask || !newItemText.trim()) return;
        const newItem = {
            id: Date.now(),
            text: newItemText,
            done: false
        };
        const newChecklist = [...(selectedTask.checklist || []), newItem];
        updateTask(selectedTask.id, { checklist: newChecklist });
        setNewItemText('');
        setIsAddingItem(false);
    };

    const handleSaveDesc = () => {
        if (!selectedTask) return;
        updateTask(selectedTask.id, { description: descText });
        setIsEditingDesc(false);
    };

    const onDragEnd = (result: DropResult) => {
        const { destination, source, draggableId } = result;

        if (!destination) return;
        if (destination.droppableId === source.droppableId && destination.index === source.index) return;

        const start = data.columns[source.droppableId as keyof typeof data.columns];
        const finish = data.columns[destination.droppableId as keyof typeof data.columns];

        if (start === finish) {
            const newTaskIds = Array.from(start.taskIds);
            newTaskIds.splice(source.index, 1);
            newTaskIds.splice(destination.index, 0, draggableId);

            const newColumn = { ...start, taskIds: newTaskIds };
            setData((prev) => ({ ...prev, columns: { ...prev.columns, [newColumn.id]: newColumn } }));
            return;
        }

        const startTaskIds = Array.from(start.taskIds);
        startTaskIds.splice(source.index, 1);
        const newStart = { ...start, taskIds: startTaskIds };

        const finishTaskIds = Array.from(finish.taskIds);
        finishTaskIds.splice(destination.index, 0, draggableId);
        const newFinish = { ...finish, taskIds: finishTaskIds };

        setData((prev) => ({
            ...prev,
            columns: {
                ...prev.columns,
                [newStart.id]: newStart,
                [newFinish.id]: newFinish,
            },
        }));
    };

    return (
        <div className="h-full flex flex-col">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold dark:text-white">CRM Pipeline</h1>
                    <p className="text-sm text-slate-500">Autonomous WhatsApp Agent flow</p>
                </div>
                <button
                    onClick={() => setIsCreatingLead(true)}
                    className="rounded-lg bg-primary px-4 py-2 font-bold text-white shadow-lg shadow-primary/20 hover:bg-primary/90"
                >
                    + Kanban
                </button>
            </div>

            <div className="flex-1 overflow-x-auto pb-4">
                <DragDropContext onDragEnd={onDragEnd}>
                    <div className="flex h-full items-start gap-6">
                        {data.columnOrder.map((columnId) => {
                            const column = data.columns[columnId as keyof typeof data.columns];
                            const tasks = column.taskIds.map((taskId) => data.tasks[taskId as keyof typeof data.tasks]);

                            return (
                                <div key={column.id} className="flex min-w-[320px] max-w-[320px] flex-col rounded-xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-800 dark:bg-slate-900/50 h-full">
                                    <div className="mb-4 flex items-center justify-between">
                                        <h3 className="font-bold text-slate-700 dark:text-slate-200">
                                            {column.title} <span className="ml-2 rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-400">{tasks.length}</span>
                                        </h3>
                                        <button className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"><MoreVertical size={16} /></button>
                                    </div>

                                    <Droppable droppableId={column.id}>
                                        {(provided, snapshot) => (
                                            <div
                                                {...provided.droppableProps}
                                                ref={provided.innerRef}
                                                className={`flex-1 overflow-y-auto space-y-3 transition-colors ${snapshot.isDraggingOver ? 'bg-slate-100 dark:bg-slate-800/80 rounded-lg' : ''}`}
                                            >
                                                {tasks.map((task, index) => (
                                                    <Draggable key={task.id} draggableId={task.id} index={index}>
                                                        {(provided, snapshot) => (
                                                            <div
                                                                ref={provided.innerRef}
                                                                {...provided.draggableProps}
                                                                {...provided.dragHandleProps}
                                                                onClick={() => setSelectedTask(task)}
                                                                className={`rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow dark:border-slate-700 dark:bg-slate-800 cursor-pointer ${snapshot.isDragging ? 'shadow-lg ring-2 ring-primary ring-offset-2 dark:ring-offset-slate-900' : 'hover:border-primary/50'}`}
                                                            >
                                                                <div className="mb-2 flex items-start justify-between">
                                                                    <h4 className="font-bold text-slate-900 dark:text-white">{task.name}</h4>
                                                                    <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{task.value}</span>
                                                                </div>

                                                                <p className="mb-3 text-sm text-slate-500">{task.phone}</p>

                                                                <div className="flex items-center justify-between border-t border-slate-100 pt-3 dark:border-slate-700">
                                                                    <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                                                                        <Bot size={14} className="text-primary" />
                                                                        <span>{task.agent}</span>
                                                                    </div>
                                                                    <div className="flex items-center gap-3">
                                                                        {task.checklist && task.checklist.length > 0 && (
                                                                            <div className="flex items-center gap-1 text-slate-400">
                                                                                <CheckSquare size={13} />
                                                                                <span className="text-xs">{task.checklist.filter((c: any) => c.done).length}/{task.checklist.length}</span>
                                                                            </div>
                                                                        )}
                                                                        {task.attachments && task.attachments.length > 0 && (
                                                                            <div className="flex items-center gap-1 text-slate-400">
                                                                                <Paperclip size={13} />
                                                                                <span className="text-xs">{task.attachments.length}</span>
                                                                            </div>
                                                                        )}
                                                                        <button className="text-slate-400 hover:text-primary"><MessageCircle size={16} /></button>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </Draggable>
                                                ))}
                                                {provided.placeholder}
                                            </div>
                                        )}
                                    </Droppable>
                                </div>
                            );
                        })}
                    </div>
                </DragDropContext>
            </div>

            {/* Lead Details Modal (Trello Style) */}
            {selectedTask && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
                    <div
                        className="relative flex w-full max-w-5xl max-h-[90vh] flex-col rounded-2xl bg-[#F4F5F7] shadow-2xl dark:bg-slate-900 overflow-hidden"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 dark:border-slate-800 dark:bg-slate-900 shrink-0">
                            <div className="flex items-center gap-4">
                                <div className="rounded-lg bg-primary/10 p-2 text-primary">
                                    <User size={24} />
                                </div>
                                <div>
                                    <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{selectedTask.name}</h2>
                                    <p className="text-sm text-slate-500">Na lista <span className="underline decoration-slate-300 underline-offset-2">Negociação</span></p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedTask(null)}
                                className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
                            >
                                <X size={24} />
                            </button>
                        </div>

                        {/* Body */}
                        <div className="flex flex-1 flex-col md:flex-row overflow-y-auto">

                            {/* Left Column (Main Content) */}
                            <div className="flex-1 space-y-8 p-6 lg:p-8">

                                {/* CRM Fields Info Box */}
                                <div className="flex flex-wrap items-center gap-6 rounded-xl bg-white p-4 shadow-sm border border-slate-200 dark:bg-slate-800 dark:border-slate-700">
                                    <div className="flex-1 min-w-[200px]">
                                        <p className="mb-1 text-xs font-semibold text-slate-500">TELEFONE</p>
                                        <div className="flex items-center gap-2 font-medium text-slate-900 dark:text-white">
                                            <Phone size={16} className="text-slate-400" /> {selectedTask.phone}
                                        </div>
                                    </div>
                                    <div className="flex-1 min-w-[200px]">
                                        <p className="mb-1 text-xs font-semibold text-slate-500">E-MAIL</p>
                                        <div className="flex items-center gap-2 font-medium text-slate-900 dark:text-white">
                                            <Mail size={16} className="text-slate-400" /> {selectedTask.email}
                                        </div>
                                    </div>
                                    <div className="flex-1 min-w-[200px]">
                                        <p className="mb-1 text-xs font-semibold text-slate-500">VALOR/PROPOSTA</p>
                                        <div className="flex items-center gap-2 font-bold text-emerald-600 dark:text-emerald-400 text-lg">
                                            {selectedTask.value}
                                        </div>
                                    </div>
                                </div>

                                {/* AI Description */}
                                <div>
                                    <div className="mb-3 flex items-center gap-2 text-slate-800 dark:text-slate-200">
                                        <Sparkles size={20} className="text-amber-500" />
                                        <h3 className="text-lg font-bold">Resumo do Cliente (Gerado por IA)</h3>
                                    </div>
                                    {isEditingDesc ? (
                                        <div className="space-y-2">
                                            <textarea
                                                className="w-full rounded-xl border border-amber-300 bg-amber-50/50 p-4 text-sm leading-relaxed text-slate-700 focus:border-amber-500 focus:ring-1 focus:ring-amber-500 dark:border-amber-500/30 dark:bg-slate-800 dark:text-slate-200 min-h-[100px]"
                                                value={descText}
                                                onChange={(e) => setDescText(e.target.value)}
                                                autoFocus
                                            />
                                            <div className="flex justify-end gap-2">
                                                <button onClick={() => setIsEditingDesc(false)} className="px-3 py-1.5 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200">Cancelar</button>
                                                <button onClick={handleSaveDesc} className="rounded bg-amber-500 px-3 py-1.5 text-sm font-bold text-white hover:bg-amber-600">Salvar Resumo</button>
                                            </div>
                                        </div>
                                    ) : (
                                        <div
                                            onClick={() => { setIsEditingDesc(true); setDescText(selectedTask.description); }}
                                            className="rounded-xl border border-slate-200 bg-amber-50/50 p-4 text-sm leading-relaxed text-slate-700 cursor-text hover:border-amber-300 transition-colors dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-amber-500/30"
                                        >
                                            {selectedTask.description || 'Adicione um resumo sobre este cliente...'}
                                        </div>
                                    )}
                                </div>

                                {/* Attachments */}
                                <div>
                                    <div className="mb-3 flex items-center gap-2 text-slate-800 dark:text-slate-200">
                                        <Paperclip size={20} />
                                        <h3 className="text-lg font-bold">Anexos</h3>
                                    </div>
                                    <div className="flex flex-wrap gap-4">
                                        {selectedTask.attachments && selectedTask.attachments.map((file: any, idx: number) => (
                                            <div key={idx} className="flex min-w-[200px] items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 shadow-sm hover:bg-slate-50 cursor-pointer transition-colors dark:border-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700">
                                                <div className={`flex h-10 w-10 items-center justify-center rounded bg-slate-100 font-bold uppercase text-slate-500 dark:bg-slate-700 ${file.type === 'pdf' ? 'text-red-500 bg-red-50 dark:bg-red-500/10' : ''}`}>
                                                    {file.type}
                                                </div>
                                                <div className="flex-1 overflow-hidden">
                                                    <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">{file.name}</p>
                                                    <p className="text-xs text-slate-500">{file.size} - Adicionado ontem</p>
                                                </div>
                                            </div>
                                        ))}
                                        <button className="flex min-h-[66px] items-center justify-center gap-2 rounded-lg border-2 border-dashed border-slate-300 bg-transparent px-4 py-3 text-sm font-medium text-slate-500 hover:border-primary hover:text-primary hover:bg-primary/5 transition-all dark:border-slate-700 dark:text-slate-400">
                                            <Plus size={16} /> Adicionar Anexo (PDF, Img, Doc)
                                        </button>
                                    </div>
                                </div>

                                {/* Checklist / Tasks */}
                                <div>
                                    <div className="mb-3 flex items-center justify-between">
                                        <div className="flex items-center gap-2 text-slate-800 dark:text-slate-200">
                                            <CheckSquare size={20} />
                                            <h3 className="text-lg font-bold">Tarefas / Checklist</h3>
                                        </div>
                                        <span className="text-sm font-medium text-slate-500">
                                            {selectedTask.checklist ? `${Math.round((selectedTask.checklist.filter((c: any) => c.done).length / selectedTask.checklist.length) * 100 || 0)}% Concluído` : '0%'}
                                        </span>
                                    </div>

                                    {selectedTask.checklist && selectedTask.checklist.length > 0 && (
                                        <div className="mb-4 h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
                                            <div
                                                className="h-full bg-primary transition-all duration-500"
                                                style={{ width: `${(selectedTask.checklist.filter((c: any) => c.done).length / selectedTask.checklist.length) * 100}%` }}
                                            />
                                        </div>
                                    )}

                                    <div className="space-y-2">
                                        {selectedTask.checklist && selectedTask.checklist.map((item: any) => (
                                            <div key={item.id} className="flex items-center gap-3 rounded-lg border border-transparent p-2 hover:bg-slate-100 dark:hover:bg-slate-800/50">
                                                <input
                                                    type="checkbox"
                                                    checked={item.done}
                                                    onChange={() => toggleChecklist(item.id)}
                                                    className="h-4 w-4 cursor-pointer rounded border-slate-300 text-primary focus:ring-primary dark:border-slate-600 dark:bg-slate-700"
                                                />
                                                <span
                                                    onClick={() => toggleChecklist(item.id)}
                                                    className={`text-sm cursor-pointer select-none ${item.done ? 'text-slate-400 line-through dark:text-slate-500' : 'text-slate-700 font-medium dark:text-slate-300'}`}
                                                >
                                                    {item.text}
                                                </span>
                                            </div>
                                        ))}

                                        {isAddingItem ? (
                                            <div className="flex items-center gap-2 mt-2">
                                                <input
                                                    type="text"
                                                    autoFocus
                                                    placeholder="Digite a nova tarefa..."
                                                    value={newItemText}
                                                    onChange={(e) => setNewItemText(e.target.value)}
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter') addChecklistItem();
                                                        if (e.key === 'Escape') setIsAddingItem(false);
                                                    }}
                                                    className="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                                />
                                                <button onClick={addChecklistItem} className="rounded bg-primary px-3 py-1.5 text-sm font-bold text-white hover:bg-primary/90">Salvar</button>
                                                <button onClick={() => setIsAddingItem(false)} className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"><X size={16} /></button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => { setIsAddingItem(true); setNewItemText(''); }}
                                                className="mt-2 text-sm font-medium text-slate-500 hover:text-slate-700 underline underline-offset-2"
                                            >
                                                Adicionar item...
                                            </button>
                                        )}
                                    </div>
                                </div>

                            </div>

                            {/* Right Column (Sidebar) */}
                            <div className="w-full md:w-64 shrink-0 bg-slate-50 border-l border-slate-200 p-6 dark:bg-slate-900/50 dark:border-slate-800">

                                <div className="space-y-6">
                                    <div>
                                        <p className="mb-2 text-xs font-bold uppercase text-slate-500">Agente Responsável</p>
                                        <div className="flex items-center gap-2 rounded-lg bg-white p-3 shadow-sm border border-slate-200 dark:bg-slate-800 dark:border-slate-700">
                                            <Bot size={18} className="text-primary" />
                                            <span className="text-sm font-bold text-slate-900 dark:text-white">{selectedTask.agent}</span>
                                        </div>
                                    </div>

                                    <div>
                                        <p className="mb-2 text-xs font-bold uppercase text-slate-500">Prazo / Deadline</p>
                                        <div className={`flex items-center justify-between rounded-lg p-3 shadow-sm border text-sm font-bold ${selectedTask.deadline !== 'Sem prazo' ? 'bg-rose-50 border-rose-200 text-rose-700 dark:bg-rose-500/10 dark:border-rose-500/30 dark:text-rose-400' : 'bg-white border-slate-200 text-slate-600 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400'}`}>
                                            <div className="flex items-center gap-2">
                                                <Calendar size={16} />
                                                <span>{selectedTask.deadline}</span>
                                            </div>
                                            <ChevronDown size={14} className="opacity-50" />
                                        </div>
                                    </div>

                                    <div>
                                        <p className="mb-2 text-xs font-bold uppercase text-slate-500">Ações Rápidas</p>
                                        <div className="flex flex-col gap-2">
                                            <button className="flex w-full items-center gap-2 rounded bg-slate-200/50 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700/80">
                                                <MessageCircle size={16} /> Conversar no Inbox
                                            </button>
                                            <button className="flex w-full items-center gap-2 rounded bg-slate-200/50 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700/80">
                                                <Clock size={16} /> Ver Histórico
                                            </button>
                                            <button className="flex w-full items-center gap-2 rounded bg-slate-200/50 px-3 py-2 text-sm font-medium text-rose-600 hover:bg-rose-100 dark:bg-slate-800 dark:text-rose-400 dark:hover:bg-rose-500/10 mt-4">
                                                Arquivar Lead
                                            </button>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Create Lead Modal */}
            {isCreatingLead && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <div className="mb-6 flex items-center justify-between">
                            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Adicionar ao Kanban</h2>
                            <button onClick={() => setIsCreatingLead(false)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"><X size={20} /></button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Nome Completo</label>
                                <input
                                    type="text"
                                    value={newLeadData.name}
                                    onChange={(e) => setNewLeadData({ ...newLeadData, name: e.target.value })}
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    placeholder="Ex: Carlos Silva"
                                />
                            </div>
                            <div>
                                <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Empresa (Opcional)</label>
                                <input
                                    type="text"
                                    value={newLeadData.company}
                                    onChange={(e) => setNewLeadData({ ...newLeadData, company: e.target.value })}
                                    className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">Telefone (WhatsApp)</label>
                                    <input
                                        type="text"
                                        value={newLeadData.phone}
                                        onChange={(e) => setNewLeadData({ ...newLeadData, phone: e.target.value })}
                                        className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                        placeholder="+55 11 99999-9999"
                                    />
                                </div>
                                <div>
                                    <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300">E-mail</label>
                                    <input
                                        type="email"
                                        value={newLeadData.email}
                                        onChange={(e) => setNewLeadData({ ...newLeadData, email: e.target.value })}
                                        className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-2 text-sm focus:border-primary focus:ring-1 focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 flex justify-end gap-3">
                            <button onClick={() => setIsCreatingLead(false)} className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">Cancelar</button>
                            <button
                                onClick={() => {
                                    // Dummy create action for preview
                                    alert('Lead criado! (Mock)');
                                    setIsCreatingLead(false);
                                    setNewLeadData({ name: '', phone: '', email: '', company: '' });
                                }}
                                className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white shadow-lg shadow-primary/20 hover:bg-primary/90"
                            >
                                Criar Lead
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
