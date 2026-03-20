import { Link } from 'react-router-dom';
import { Bot, Zap, Users, ArrowRight } from 'lucide-react';

export default function Landing() {
    return (
        <div className="min-h-screen bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100">

            {/* Navbar */}
            <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-md px-6 py-4 dark:border-slate-800 dark:bg-slate-900/80 sticky top-0 z-50">
                <div className="mx-auto flex max-w-7xl items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-white">
                            <Bot size={20} />
                        </div>
                        <span className="text-xl font-bold">Wappi</span>
                    </div>
                    <div className="flex gap-4">
                        <Link to="/auth" className="rounded-lg px-4 py-2 font-semibold text-slate-600 hover:text-primary dark:text-slate-300">
                            Entrar
                        </Link>
                        <Link to="/auth" className="rounded-lg bg-primary px-5 py-2 font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90">
                            Começar Grátis
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="mx-auto max-w-7xl px-6 py-24 text-center">
                <div className="mx-auto max-w-3xl">
                    <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary">
                        <Zap size={16} /> Automação de vendas no WhatsApp
                    </div>
                    <h1 className="mb-6 text-5xl font-extrabold tracking-tight md:text-7xl">
                        Seu time de vendas por <br /><span className="text-primary">Inteligência Artificial</span>
                    </h1>
                    <p className="mb-10 text-xl text-slate-600 dark:text-slate-400">
                        Agentes de IA que prospectam, qualificam e vendem pelo WhatsApp automaticamente. CRM com Kanban que se move sozinho. Resultados reais, sem esforço manual.
                    </p>
                    <div className="flex justify-center gap-4">
                        <Link to="/auth" className="flex items-center gap-2 rounded-xl bg-primary px-8 py-4 font-bold text-white shadow-xl shadow-primary/20 transition-all hover:bg-primary/90 hover:-translate-y-1">
                            Começar Agora <ArrowRight size={20} />
                        </Link>
                        <Link to="#features" className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-8 py-4 font-bold text-slate-700 shadow-sm transition-all hover:bg-slate-50 hover:-translate-y-1 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800">
                            Ver Recursos
                        </Link>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="mx-auto max-w-7xl px-6 py-24 border-t border-slate-200 dark:border-slate-800">
                <h2 className="mb-16 text-center text-3xl font-bold">Everything you need to scale</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

                    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                        <div className="mb-4 flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                            <Bot size={24} />
                        </div>
                        <h3 className="mb-2 text-xl font-bold">Autonomous Agents</h3>
                        <p className="text-slate-500">Train AI personas that speak your brand's voice and follow your custom sales playbooks.</p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                        <div className="mb-4 flex size-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-500">
                            <Zap size={24} />
                        </div>
                        <h3 className="mb-2 text-xl font-bold">Real-time Kanban</h3>
                        <p className="text-slate-500">Watch your leads automatically move through the pipeline via Socket.io as the AI negotiates.</p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                        <div className="mb-4 flex size-12 items-center justify-center rounded-xl bg-purple-500/10 text-purple-500">
                            <Users size={24} />
                        </div>
                        <h3 className="mb-2 text-xl font-bold">Group Extraction</h3>
                        <p className="text-slate-500">Instantly pull leads from WhatsApp groups and drop them into automated prospecting sequences.</p>
                    </div>

                </div>
            </section>

        </div>
    );
}
