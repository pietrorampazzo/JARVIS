import React from 'react';
import { Bot, Bell, LayoutDashboard, Settings as SettingsIcon, Users, MessageSquare, Smartphone } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const location = useLocation();

    return (
        <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100">

            {/* Top Nav Bar */}
            <header className="sticky top-0 z-50 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3 dark:border-slate-800 dark:bg-background-dark">
                <div className="flex items-center gap-4">
                    <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-white">
                        <Bot size={20} />
                    </div>
                    <h2 className="text-lg font-bold leading-tight tracking-tight text-slate-900 dark:text-white">Wappi</h2>
                </div>

                <div className="flex flex-1 items-center justify-end gap-6">
                    <nav className="hidden items-center gap-6 md:flex">
                        <Link to="/dashboard" className={`text-sm font-medium transition-colors ${location.pathname === '/dashboard' ? 'border-b-2 border-primary py-1 font-bold text-primary' : 'text-slate-600 hover:text-primary dark:text-slate-300'}`}>Dashboard</Link>
                        <Link to="/kanban" className={`text-sm font-medium transition-colors ${location.pathname === '/kanban' ? 'border-b-2 border-primary py-1 font-bold text-primary' : 'text-slate-600 hover:text-primary dark:text-slate-300'}`}>CRM Kanban</Link>
                        <Link to="/settings" className={`text-sm font-medium transition-colors ${location.pathname === '/settings' ? 'border-b-2 border-primary py-1 font-bold text-primary' : 'text-slate-600 hover:text-primary dark:text-slate-300'}`}>Configurações</Link>
                    </nav>

                    <div className="flex gap-2 border-l border-slate-200 pl-6 dark:border-slate-800">
                        <button className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 text-slate-600 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700">
                            <Bell size={20} />
                        </button>
                        <div className="flex h-10 w-10 items-center justify-center rounded-full border border-primary/30 bg-primary/20">
                            <img src="https://ui-avatars.com/api/?name=Wappi+User&background=1FAD53&color=fff" alt="User Profile" className="rounded-full" />
                        </div>
                    </div>
                </div>
            </header>

            <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-8 p-6 md:flex-row md:p-8 overflow-hidden">

                {/* Global Sidebar Navigation */}
                <aside className="hidden w-full flex-col gap-2 md:w-64 md:flex shrink-0 border-r border-slate-200 dark:border-slate-800 pr-6">

                    <Link to="/dashboard" className={`flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-all ${location.pathname === '/dashboard' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}>
                        <LayoutDashboard size={18} />
                        <span>Dashboard</span>
                    </Link>

                    <Link to="/kanban" className={`flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-all ${location.pathname === '/kanban' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}>
                        <Bot size={18} />
                        <span>Kanban CRM</span>
                    </Link>

                    <Link to="/agents" className={`flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-all ${location.pathname === '/agents' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}>
                        <Bot size={18} />
                        <span>Agentes de IA</span>
                    </Link>

                    <Link to="/inbox" className={`flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-all ${location.pathname === '/inbox' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}>
                        <MessageSquare size={18} />
                        <span>Conversas</span>
                    </Link>

                    <Link to="/contacts" className={`flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-all ${location.pathname === '/contacts' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}>
                        <Users size={18} />
                        <span>Contatos</span>
                    </Link>

                    <Link to="/whatsapp" className={`flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-all ${location.pathname === '/whatsapp' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}>
                        <Smartphone size={18} />
                        <span>WhatsApp</span>
                    </Link>

                    <Link to="/settings" className={`flex items-center gap-3 rounded-xl px-4 py-3 font-medium transition-all ${location.pathname === '/settings' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}>
                        <SettingsIcon size={18} />
                        <span>Configurações</span>
                    </Link>

                </aside>

                <div className="flex-1 overflow-hidden">
                    {children}
                </div>
            </main>
        </div>
    );
}
