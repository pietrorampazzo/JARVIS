import { useState, useEffect } from 'react';
import { Key, Webhook, User, Eye, EyeOff, Copy, QrCode, Smartphone, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Settings() {
    const [showEvolutionKey, setShowEvolutionKey] = useState(false);
    const [showOpenAiKey, setShowOpenAiKey] = useState(false);
    const [qrTimestamp, setQrTimestamp] = useState(Date.now());
    const [whatsappStatus, setWhatsappStatus] = useState<any>(null);

    const [apiKeys, setApiKeys] = useState({
        evolutionUrl: 'https://evolution.wappi-instance.com',
        evolutionKey: 'sk-evolution-876234987123498',
        openAiKey: 'sk-proj-492384729384729384'
    });

    const [webhooks] = useState({
        incoming: 'https://app.wappi.ai/webhook/v1/messages',
        status: 'https://app.wappi.ai/webhook/v1/status'
    });

    const [profile, setProfile] = useState({
        name: 'Alexander Rossi',
        email: 'alex@rossi-sales.io'
    });

    useEffect(() => {
        const interval = setInterval(() => {
            setQrTimestamp(Date.now());
            fetch('/whatsapp-status.json')
                .then(res => res.json())
                .then(data => setWhatsappStatus(data))
                .catch(() => setWhatsappStatus(null));
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text);
        alert('Copiado para a área de transferência!');
    };

    const getStatusDisplay = () => {
        if (!whatsappStatus) return { label: 'Desconectado', color: 'text-slate-500', icon: Smartphone };
        switch (whatsappStatus.status) {
            case 'CONNECTED': return { label: 'Conectado', color: 'text-emerald-500', icon: CheckCircle2 };
            case 'QR_AVAILABLE': return { label: 'QR Code Disponível', color: 'text-amber-500', icon: QrCode };
            case 'WAITING_QR': return { label: 'Aguardando QR...', color: 'text-blue-500', icon: RefreshCw };
            case 'ERROR': return { label: 'Erro na Conexão', color: 'text-rose-500', icon: AlertCircle };
            default: return { label: 'Processando...', color: 'text-slate-500', icon: RefreshCw };
        }
    };

    const statusInfo = getStatusDisplay();

    return (
        <>
            <div className="mb-6">
                <h1 className="text-2xl font-bold dark:text-white">System Settings</h1>
                <p className="text-sm text-slate-500">Manage technical environment</p>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 space-y-8">

                {/* WhatsApp Local Section */}
                <section id="whatsapp-local" className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                    <div className="flex items-center justify-between border-b border-slate-200 p-6 dark:border-slate-800">
                        <div>
                            <h2 className="text-lg font-bold dark:text-white">WhatsApp Local</h2>
                            <p className="text-sm text-slate-500">Vincule sua conta do WhatsApp diretamente via Browser Local.</p>
                        </div>
                        <Smartphone className="text-slate-400" size={24} />
                    </div>

                    <div className="p-6">
                        <div className="flex flex-col items-center gap-6 md:flex-row md:items-start">
                            <div className="relative flex aspect-square w-full max-w-[250px] items-center justify-center overflow-hidden rounded-2xl border-2 border-slate-100 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
                                {whatsappStatus?.status === 'QR_AVAILABLE' ? (
                                    <img
                                        src={`/qr.png?t=${qrTimestamp}`}
                                        alt="WhatsApp QR Code"
                                        className="h-full w-full object-contain p-2"
                                    />
                                ) : (
                                    <div className="flex flex-col items-center gap-3 text-center p-6">
                                        <statusInfo.icon className={`size-12 ${statusInfo.label === 'Aguardando QR...' ? 'animate-spin' : ''} ${statusInfo.color}`} />
                                        <p className={`text-sm font-bold ${statusInfo.color}`}>{statusInfo.label}</p>
                                        <p className="text-xs text-slate-500">Inicie o script local para gerar o QR Code.</p>
                                    </div>
                                )}
                            </div>

                            <div className="flex-1 space-y-4">
                                <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-500/10">
                                    <h4 className="mb-1 text-sm font-bold text-blue-800 dark:text-blue-400">Instruções de Pareamento</h4>
                                    <ol className="list-decimal pl-4 text-xs space-y-2 text-blue-700 dark:text-blue-300">
                                        <li>Certifique-se que o motor do WhatsApp Local está rodando em sua máquina.</li>
                                        <li>Abra o WhatsApp no seu celular.</li>
                                        <li>Toque em Mais opções (Android) ou Configurações (iPhone).</li>
                                        <li>Toque em Dispositivos conectados e, em seguida, em Conectar um dispositivo.</li>
                                        <li>Aponte seu celular para esta tela para capturar o código acima.</li>
                                    </ol>
                                </div>

                                <div className="flex items-center gap-3 text-sm">
                                    <div className={`p-2 rounded-full bg-slate-100 dark:bg-slate-800 ${statusInfo.color}`}>
                                        <statusInfo.icon size={18} />
                                    </div>
                                    <div>
                                        <p className="font-bold dark:text-white">Status: {statusInfo.label}</p>
                                        <p className="text-xs text-slate-500">Última atualização: {whatsappStatus ? new Date(whatsappStatus.timestamp).toLocaleTimeString() : 'Nunca'}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* API Keys Section */}
                <section id="api-keys" className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                    <div className="flex items-center justify-between border-b border-slate-200 p-6 dark:border-slate-800">
                        <div>
                            <h2 className="text-lg font-bold dark:text-white">API Configuration</h2>
                            <p className="text-sm text-slate-500">Securely connect Wappi to your WhatsApp and AI providers.</p>
                        </div>
                        <Key className="text-slate-400" size={24} />
                    </div>

                    <div className="space-y-6 p-6">
                        <div className="grid grid-cols-1 gap-6">

                            <div className="space-y-2">
                                <label className="text-sm font-semibold dark:text-slate-300">Evolution API URL</label>
                                <input
                                    type="text"
                                    value={apiKeys.evolutionUrl}
                                    onChange={(e) => setApiKeys({ ...apiKeys, evolutionUrl: e.target.value })}
                                    className="w-full rounded-lg border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-semibold dark:text-slate-300">Evolution API Key</label>
                                <div className="relative">
                                    <input
                                        type={showEvolutionKey ? "text" : "password"}
                                        value={apiKeys.evolutionKey}
                                        onChange={(e) => setApiKeys({ ...apiKeys, evolutionKey: e.target.value })}
                                        className="w-full rounded-lg border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                    <button
                                        onClick={() => setShowEvolutionKey(!showEvolutionKey)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-primary">
                                        {showEvolutionKey ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-semibold dark:text-slate-300">OpenAI API Key</label>
                                <div className="relative">
                                    <input
                                        type={showOpenAiKey ? "text" : "password"}
                                        value={apiKeys.openAiKey}
                                        onChange={(e) => setApiKeys({ ...apiKeys, openAiKey: e.target.value })}
                                        className="w-full rounded-lg border-slate-200 bg-slate-50 px-4 py-3 pr-12 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                    <button
                                        onClick={() => setShowOpenAiKey(!showOpenAiKey)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-primary">
                                        {showOpenAiKey ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                            </div>

                        </div>
                        <div className="flex justify-end pt-4">
                            <button className="rounded-lg bg-primary py-2.5 px-6 font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90">
                                Save API Changes
                            </button>
                        </div>
                    </div>
                </section>

                {/* Webhooks Section */}
                <section id="webhooks" className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                    <div className="flex items-center justify-between border-b border-slate-200 p-6 dark:border-slate-800">
                        <div>
                            <h2 className="text-lg font-bold dark:text-white">Webhook Endpoints</h2>
                            <p className="text-sm text-slate-500">Configure where your Evolution instance sends message events.</p>
                        </div>
                        <Webhook className="text-slate-400" size={24} />
                    </div>

                    <div className="space-y-6 p-6">
                        <div className="grid grid-cols-1 gap-6">

                            <div className="space-y-2">
                                <label className="text-sm font-semibold dark:text-slate-300">Incoming Messages URL</label>
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        readOnly
                                        value={webhooks.incoming}
                                        className="flex-1 rounded-lg border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                    <button
                                        onClick={() => handleCopy(webhooks.incoming)}
                                        className="rounded-lg border border-slate-200 px-4 py-2 text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800">
                                        <Copy size={18} />
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-semibold dark:text-slate-300">Connection Status URL</label>
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        readOnly
                                        value={webhooks.status}
                                        className="flex-1 rounded-lg border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                    />
                                    <button
                                        onClick={() => handleCopy(webhooks.status)}
                                        className="rounded-lg border border-slate-200 px-4 py-2 text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-800">
                                        <Copy size={18} />
                                    </button>
                                </div>
                            </div>

                        </div>
                    </div>
                </section>

                {/* Profile Section */}
                <section id="profile" className="mb-12 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                    <div className="flex items-center justify-between border-b border-slate-200 p-6 dark:border-slate-800">
                        <div>
                            <h2 className="text-lg font-bold dark:text-white">Account Profile</h2>
                            <p className="text-sm text-slate-500">Manage your administrative contact information.</p>
                        </div>
                        <User className="text-slate-400" size={24} />
                    </div>

                    <div className="space-y-6 p-6">
                        <div className="mb-4 flex items-center gap-6">
                            <div className="group relative flex size-20 cursor-pointer items-center justify-center overflow-hidden rounded-2xl border-2 border-dashed border-slate-300 bg-slate-100 dark:border-slate-700 dark:bg-slate-800">
                                <img src="https://ui-avatars.com/api/?name=Alexander+Rossi&background=136dec&color=fff&size=128" alt="Profile" className="absolute inset-0 h-full w-full object-cover opacity-50 transition-opacity group-hover:opacity-30" />
                                <span className="z-10 text-slate-400 transition-colors group-hover:text-primary">+ Photo</span>
                            </div>
                            <div>
                                <h3 className="font-bold dark:text-white">{profile.name}</h3>
                                <p className="text-sm text-slate-500">Admin Account • Pro Plan</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                            <div className="space-y-2">
                                <label className="text-sm font-semibold dark:text-slate-300">Full Name</label>
                                <input
                                    type="text"
                                    value={profile.name}
                                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                                    className="w-full rounded-lg border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-semibold dark:text-slate-300">Email Address</label>
                                <input
                                    type="email"
                                    value={profile.email}
                                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                    className="w-full rounded-lg border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-primary focus:ring-primary dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                                />
                            </div>
                        </div>

                        <div className="flex justify-end pt-4">
                            <button className="mr-3 rounded-lg bg-slate-100 py-2.5 px-6 font-bold text-slate-900 transition-all hover:bg-slate-200 dark:bg-slate-800 dark:text-white dark:hover:bg-slate-700">
                                Reset Form
                            </button>
                            <button className="rounded-lg bg-primary py-2.5 px-6 font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90">
                                Save Profile
                            </button>
                        </div>
                    </div>
                </section>

            </div>
        </>
    );
}
