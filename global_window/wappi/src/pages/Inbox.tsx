import { useState } from 'react';
import { Search, MoreVertical, Paperclip, Smile, Mic, Send, Bot, Check, CheckCheck } from 'lucide-react';

const initialChats = [
    {
        id: '1',
        name: 'Maria Silva',
        pfp: 'https://ui-avatars.com/api/?name=Maria+Silva&background=Random',
        lastMessage: 'Vou querer o pacote premium.',
        timestamp: '14:23',
        unread: 2,
        isAgent: true,
        agentName: 'Alice',
        agentColor: 'bg-pink-500'
    },
    {
        id: '2',
        name: 'João Souza',
        pfp: 'https://ui-avatars.com/api/?name=Joao+Souza&background=Random',
        lastMessage: 'Qual o valor do envio para SP?',
        timestamp: '11:45',
        unread: 0,
        isAgent: true,
        agentName: 'Roberto',
        agentColor: 'bg-blue-500'
    },
    {
        id: '3',
        name: 'Carlos Empreendimentos',
        pfp: 'https://ui-avatars.com/api/?name=Carlos+Emp&background=Random',
        lastMessage: 'Ok, combinado.',
        timestamp: 'Ontem',
        unread: 0,
        isAgent: false
    }
];

const initialMessages = {
    '1': [
        { id: '1', text: 'Olá! Como posso ajudar você hoje?', sender: 'agent', timestamp: '14:20', status: 'read' },
        { id: '2', text: 'Estou avaliando as opções de assinatura do serviço.', sender: 'user', timestamp: '14:21', status: 'read' },
        { id: '3', text: 'Maravilha! O pacote premium é o mais indicado pelas suas necessidades.', sender: 'agent', timestamp: '14:22', status: 'read' },
        { id: '4', text: 'Vou querer o pacote premium.', sender: 'user', timestamp: '14:23', status: 'delivered' },
    ],
    '2': [
        { id: '1', text: 'Olá, gostaria de saber sobre valores.', sender: 'user', timestamp: '11:40', status: 'read' },
        { id: '2', text: 'Claro! Temos planos a partir de R$ 97.', sender: 'agent', timestamp: '11:42', status: 'read' },
        { id: '3', text: 'Qual o valor do envio para SP?', sender: 'user', timestamp: '11:45', status: 'delivered' }
    ],
    '3': [
        { id: '1', text: 'O contrato foi enviado.', sender: 'agent', timestamp: 'Ontem', status: 'read' },
        { id: '2', text: 'Ok, combinado.', sender: 'user', timestamp: 'Ontem', status: 'read' }
    ]
};

export default function Inbox() {
    const [chats, setChats] = useState(initialChats);
    const [messagesByChat, setMessagesByChat] = useState<Record<string, any[]>>(initialMessages);
    const [selectedChatId, setSelectedChatId] = useState<string>('1');
    const [messageInput, setMessageInput] = useState('');

    const selectedChat = chats.find(c => c.id === selectedChatId);
    const currentMessages = messagesByChat[selectedChatId] || [];

    const handleSendMessage = () => {
        if (!messageInput.trim() || !selectedChatId) return;

        const newMessage = {
            id: Date.now().toString(),
            text: messageInput.trim(),
            sender: 'agent', // You (the human taking over) sending from the business side
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            status: 'sent',
            isHuman: true // Flag to show it was sent by human, not AI
        };

        setMessagesByChat(prev => ({
            ...prev,
            [selectedChatId]: [...(prev[selectedChatId] || []), newMessage]
        }));

        // Update chat list to show last message
        setChats(prev => prev.map(c =>
            c.id === selectedChatId
                ? { ...c, lastMessage: newMessage.text, timestamp: newMessage.timestamp, unread: 0 }
                : c
        ));

        setMessageInput('');
    };

    return (
        <div className="flex h-full flex-col">
            <div className="mb-4">
                <h1 className="text-2xl font-bold dark:text-white">Conversas</h1>
                <p className="text-sm text-slate-500">Caixa de entrada unificada de atendimento.</p>
            </div>

            {/* Main Chat Container - WhatsApp Layout */}
            <div className="flex flex-1 overflow-hidden min-h-[600px] rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">

                {/* Left Sidebar - Chat List */}
                <div className="flex w-full flex-col border-r border-slate-200 dark:border-slate-800 md:w-80 lg:w-96 shrink-0">
                    {/* Sidebar Header */}
                    <div className="flex items-center justify-between bg-slate-50 p-4 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                        <div className="relative w-full">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                            <input
                                type="text"
                                placeholder="Pesquisar ou começar nova conversa"
                                className="w-full rounded-lg border-none bg-white py-2 pl-10 pr-4 text-sm text-slate-900 shadow-sm focus:ring-2 focus:ring-primary dark:bg-slate-800 dark:text-white dark:placeholder-slate-500"
                            />
                        </div>
                    </div>

                    {/* Chat List */}
                    <div className="flex-1 overflow-y-auto">
                        {chats.map(chat => (
                            <div
                                key={chat.id}
                                onClick={() => {
                                    setSelectedChatId(chat.id);
                                    // mark as read
                                    if (chat.unread > 0) {
                                        setChats(prev => prev.map(c => c.id === chat.id ? { ...c, unread: 0 } : c));
                                    }
                                }}
                                className={`flex cursor-pointer items-center gap-3 border-b border-slate-100 p-4 transition-colors hover:bg-slate-50 dark:border-slate-800/50 dark:hover:bg-slate-800/50 ${selectedChatId === chat.id ? 'bg-slate-100 dark:bg-slate-800' : ''}`}
                            >
                                <img src={chat.pfp} alt={chat.name} className="h-12 w-12 rounded-full object-cover" />
                                <div className="flex flex-1 flex-col overflow-hidden">
                                    <div className="flex items-center justify-between">
                                        <h3 className="truncate font-semibold text-slate-900 dark:text-white">{chat.name}</h3>
                                        <span className="text-xs text-slate-500">{chat.timestamp}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <p className="truncate text-sm text-slate-500 dark:text-slate-400">{chat.lastMessage}</p>
                                        {chat.unread > 0 && (
                                            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-white">
                                                {chat.unread}
                                            </span>
                                        )}
                                    </div>
                                    {chat.isAgent && (
                                        <div className="mt-1 flex items-center gap-1">
                                            <Bot size={10} className="text-slate-400" />
                                            <span className={`text-[10px] font-medium text-slate-500 ${chat.agentColor ? chat.agentColor.replace('bg-', 'text-') : ''}`}>
                                                IA: {chat.agentName}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right Area - Active Chat */}
                {selectedChat ? (
                    <div className="flex flex-1 flex-col bg-[#efeae2] dark:bg-[#0b141a]"> {/* WhatsApp default background colors */}

                        {/* Chat Header */}
                        <div className="flex items-center justify-between bg-white px-4 py-3 shadow-sm dark:bg-slate-900 z-10 border-b border-slate-200 dark:border-slate-800">
                            <div className="flex items-center gap-3">
                                <img src={selectedChat.pfp} alt={selectedChat.name} className="h-10 w-10 rounded-full" />
                                <div>
                                    <h2 className="font-semibold text-slate-900 dark:text-white">{selectedChat.name}</h2>
                                    <p className="text-xs text-slate-500">visto por último hoje às 14:23</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4 text-slate-500">
                                <button className="hover:text-slate-700 dark:hover:text-slate-300">
                                    <Search size={20} />
                                </button>
                                <button className="hover:text-slate-700 dark:hover:text-slate-300">
                                    <MoreVertical size={20} />
                                </button>
                            </div>
                        </div>

                        {/* Chat Messages Area */}
                        <div className="flex-1 overflow-y-auto p-6 bg-cover bg-center" style={{ backgroundImage: "url('https://whatsapp-clone-web.netlify.app/bg-chat-tile-light.png')", opacity: 0.8 }}>
                            <div className="flex flex-col gap-2">
                                {/* Date Divider */}
                                <div className="flex justify-center mb-4">
                                    <span className="rounded-lg bg-white/90 px-3 py-1 text-xs text-slate-500 shadow-sm dark:bg-slate-800/90 dark:text-slate-400">
                                        HOJE
                                    </span>
                                </div>

                                {currentMessages.map(msg => (
                                    <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-start' : 'justify-end'}`}>
                                        <div className={`relative max-w-[75%] rounded-lg px-3 py-2 text-sm shadow-sm ${msg.sender === 'agent' ? 'bg-[#d9fdd3] text-slate-900 dark:bg-[#005c4b] dark:text-slate-100 rounded-tr-none' : 'bg-white text-slate-900 dark:bg-[#202c33] dark:text-slate-100 rounded-tl-none'}`}>

                                            {msg.sender === 'agent' && selectedChat.isAgent && !msg.isHuman && (
                                                <div className={`mb-1 flex items-center gap-1 text-[10px] font-bold ${selectedChat.agentColor ? selectedChat.agentColor.replace('bg-', 'text-') : 'text-primary'}`}>
                                                    <Bot size={10} />
                                                    {selectedChat.agentName}
                                                </div>
                                            )}

                                            {msg.sender === 'agent' && msg.isHuman && (
                                                <div className="mb-1 flex items-center gap-1 text-[10px] font-bold text-slate-500 dark:text-slate-400">
                                                    Você (Humano)
                                                </div>
                                            )}

                                            <span className="break-words">{msg.text}</span>

                                            <div className="float-right ml-3 mt-1 flex items-end gap-1 text-[10px] text-slate-500 dark:text-slate-400">
                                                <span>{msg.timestamp}</span>
                                                {msg.sender === 'agent' && (
                                                    msg.status === 'read' ? <CheckCheck size={14} className="text-[#53bdeb]" /> : <Check size={14} />
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Chat Input Area */}
                        <div className="flex items-end gap-2 bg-slate-50 px-4 py-3 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
                            <button className="flex h-10 w-10 shrink-0 items-center justify-center text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300">
                                <Smile size={24} />
                            </button>
                            <button className="flex h-10 w-10 shrink-0 items-center justify-center text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300">
                                <Paperclip size={22} />
                            </button>

                            <div className="flex-1">
                                <input
                                    type="text"
                                    value={messageInput}
                                    onChange={(e) => setMessageInput(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') handleSendMessage();
                                    }}
                                    placeholder="Digite uma mensagem"
                                    className="w-full rounded-xl border-none bg-white px-4 py-2.5 text-sm text-slate-900 shadow-sm focus:ring-0 dark:bg-slate-800 dark:text-white"
                                />
                            </div>

                            {messageInput.trim().length > 0 ? (
                                <button onClick={handleSendMessage} className="flex h-10 w-10 shrink-0 items-center justify-center text-primary hover:text-primary/80">
                                    <Send size={24} />
                                </button>
                            ) : (
                                <button className="flex h-10 w-10 shrink-0 items-center justify-center text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300">
                                    <Mic size={24} />
                                </button>
                            )}
                        </div>

                    </div>
                ) : (
                    <div className="flex flex-1 items-center justify-center bg-[#f0f2f5] dark:bg-[#222e35]">
                        <div className="text-center text-slate-500 dark:text-slate-400 max-w-sm">
                            <h3 className="mt-4 text-xl font-light text-slate-700 dark:text-slate-300">Wappi Web</h3>
                            <p className="mt-2 text-sm leading-relaxed">Selecione um contato na lista à esquerda para começar a conversar ou assumir o controle do agente de IA.</p>
                        </div>
                    </div>
                )}
            </div>

        </div>
    );
}
