import { useState, useEffect, useCallback } from 'react';
import { Smartphone, QrCode, RefreshCw, CheckCircle2, AlertCircle, ExternalLink, Square, Shield } from 'lucide-react';

interface StatusData {
    status: string;
    timestamp?: string;
    message?: string;
    processRunning?: boolean;
}

export default function WhatsApp() {
    const [qrTimestamp, setQrTimestamp] = useState(Date.now());
    const [statusData, setStatusData] = useState<StatusData | null>(null);
    const [isStarting, setIsStarting] = useState(false);
    const [showPanel, setShowPanel] = useState(false);

    const fetchStatus = useCallback(() => {
        fetch('http://localhost:3001/status')
            .then(res => res.json())
            .then(data => {
                setStatusData(data);
                setQrTimestamp(Date.now());
            })
            .catch(() => {
                fetch('/whatsapp-status.json')
                    .then(r => r.json())
                    .then(d => setStatusData(d))
                    .catch(() => setStatusData(null));
            });
    }, []);

    // Polling a cada 3 segundos quando o painel estiver aberto
    useEffect(() => {
        if (!showPanel) return;
        fetchStatus();
        const interval = setInterval(fetchStatus, 3000);
        return () => clearInterval(interval);
    }, [fetchStatus, showPanel]);

    const handleStart = async () => {
        setIsStarting(true);
        try {
            const res = await fetch('http://localhost:3001/start', { method: 'POST' });
            const data = await res.json();
            console.log('Start:', data);
            setTimeout(fetchStatus, 1000);
        } catch {
            alert('Não foi possível iniciar.\nCertifique-se que o servidor local está rodando:\n\ncd whatsapp-local\nnode server.js');
        } finally {
            setIsStarting(false);
        }
    };

    const handleStop = async () => {
        try {
            await fetch('http://localhost:3001/stop', { method: 'POST' });
            fetchStatus();
        } catch (e) {
            console.error(e);
        }
    };

    const status = statusData?.status ?? 'IDLE';
    const isRunning = statusData?.processRunning;
    const isConnected = status === 'CONNECTED';
    const hasQR = status === 'QR_AVAILABLE';

    const getStatusConfig = () => {
        switch (status) {
            case 'CONNECTED': return { label: 'Conectado', color: 'text-emerald-600', bg: 'bg-emerald-100', icon: CheckCircle2, spin: false };
            case 'QR_AVAILABLE': return { label: 'Escaneie o QR', color: 'text-amber-600', bg: 'bg-amber-100', icon: QrCode, spin: false };
            case 'WAITING_QR': return { label: 'Abrindo Chrome...', color: 'text-blue-600', bg: 'bg-blue-100', icon: RefreshCw, spin: true };
            case 'STARTING': return { label: 'Iniciando...', color: 'text-blue-600', bg: 'bg-blue-100', icon: RefreshCw, spin: true };
            case 'ERROR': return { label: 'Erro', color: 'text-rose-600', bg: 'bg-rose-100', icon: AlertCircle, spin: false };
            default: return { label: isRunning ? 'Rodando' : 'Desconectado', color: 'text-slate-500', bg: 'bg-slate-100', icon: Smartphone, spin: false };
        }
    };

    const cfg = getStatusConfig();

    return (
        <div className="flex h-full flex-col gap-6 overflow-y-auto pb-8">
            {/* Page Header */}
            <div>
                <h1 className="text-2xl font-bold dark:text-white">Conexão WhatsApp</h1>
                <p className="text-sm text-slate-500">Escolha como o Wappi deve se conectar ao seu WhatsApp.</p>
            </div>

            {/* Connection Cards */}
            <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

                {/* Card 1 — WhatsApp Local */}
                <div className={`flex flex-col rounded-2xl border-2 p-6 shadow-sm transition-all ${showPanel ? 'border-primary/50 bg-primary/5 dark:bg-primary/10' : 'border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900/50'}`}>
                    <div className="mb-3 flex size-12 items-center justify-center rounded-2xl bg-orange-100 dark:bg-orange-500/20">
                        <RefreshCw size={22} className="text-orange-500" />
                    </div>
                    <h3 className="mb-1 font-bold dark:text-white">WhatsApp Local</h3>
                    <p className="mb-4 text-xs text-slate-500 dark:text-slate-400 flex-1">
                        Bot local (Playwright). Roda direto no servidor local para máxima fidelidade.
                    </p>
                    {isConnected ? (
                        <button
                            onClick={handleStop}
                            className="w-full rounded-xl border border-rose-200 bg-rose-50 py-2.5 text-sm font-bold text-rose-600 hover:bg-rose-100 transition-all"
                        >
                            Desconectar
                        </button>
                    ) : (
                        <button
                            onClick={() => { setShowPanel(true); handleStart(); }}
                            disabled={isStarting}
                            className="w-full rounded-xl bg-orange-500 py-2.5 text-sm font-bold text-white shadow-lg shadow-orange-500/20 hover:bg-orange-600 disabled:opacity-60 transition-all"
                        >
                            {isStarting ? 'Abrindo...' : 'Usar Bot Local'}
                        </button>
                    )}
                </div>

                {/* Card 2 — Evolution API */}
                <div className="flex flex-col rounded-2xl border-2 border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                    <div className="mb-3 flex size-12 items-center justify-center rounded-2xl bg-green-100 dark:bg-green-500/20">
                        <Smartphone size={22} className="text-green-600" />
                    </div>
                    <h3 className="mb-1 font-bold dark:text-white">Evolution API</h3>
                    <p className="mb-4 text-xs text-slate-500 dark:text-slate-400 flex-1">
                        Conexão em nuvem via QR Code. Estável e performática.
                    </p>
                    <button className="w-full rounded-xl bg-primary py-2.5 text-sm font-bold text-white shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all">
                        Conectar QR Code
                    </button>
                </div>

                {/* Card 3 — API Oficial */}
                <div className="flex flex-col rounded-2xl border-2 border-slate-200 bg-white p-6 shadow-sm opacity-60 dark:border-slate-800 dark:bg-slate-900/50">
                    <div className="mb-3 flex size-12 items-center justify-center rounded-2xl bg-slate-100 dark:bg-slate-800">
                        <Shield size={22} className="text-slate-500" />
                    </div>
                    <h3 className="mb-1 font-bold dark:text-white">API Oficial</h3>
                    <p className="mb-4 text-xs text-slate-500 dark:text-slate-400 flex-1">
                        Meta Business Cloud API. Para escala industrial.
                    </p>
                    <button disabled className="w-full rounded-xl border border-slate-200 py-2.5 text-sm font-semibold text-slate-400 dark:border-slate-700">
                        Em Breve
                    </button>
                </div>
            </div>

            {/* QR Code Panel — expandido ao clicar em "Usar Bot Local" */}
            {showPanel && (
                <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900/50">
                    {/* Panel Header */}
                    <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800">
                        <div className="flex items-center gap-3">
                            <h3 className="font-bold dark:text-white">WhatsApp Local — Pareamento</h3>
                            <span className={`flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${cfg.color} ${cfg.bg}`}>
                                <cfg.icon size={12} className={cfg.spin ? 'animate-spin' : ''} />
                                {cfg.label}
                            </span>
                        </div>
                        <div className="flex items-center gap-3">
                            {statusData?.timestamp && (
                                <p className="text-xs text-slate-400">
                                    Atualizado às {new Date(statusData.timestamp).toLocaleTimeString()}
                                </p>
                            )}
                            {isRunning && !isConnected && (
                                <button
                                    onClick={handleStop}
                                    className="flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-100"
                                >
                                    <Square size={12} /> Parar
                                </button>
                            )}
                            <button
                                onClick={() => setShowPanel(false)}
                                className="text-xs text-slate-400 hover:text-slate-600"
                            >
                                ✕ Fechar
                            </button>
                        </div>
                    </div>

                    {/* Panel Body */}
                    <div className="flex flex-col items-start gap-8 p-6 md:flex-row">

                        {/* QR Code area */}
                        <div className="shrink-0">
                            <div className="relative flex size-[220px] items-center justify-center overflow-hidden rounded-2xl border-2 border-slate-100 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
                                {isConnected ? (
                                    <div className="flex flex-col items-center gap-3 p-4 text-center">
                                        <CheckCircle2 size={52} className="text-emerald-500" />
                                        <p className="text-sm font-bold text-emerald-600">WhatsApp Conectado!</p>
                                        <p className="text-xs text-slate-500">Agente ativo e recebendo mensagens.</p>
                                    </div>
                                ) : hasQR ? (
                                    <img
                                        key={qrTimestamp}
                                        src={`/qr.png?t=${qrTimestamp}`}
                                        alt="WhatsApp QR Code"
                                        className="h-full w-full object-contain p-2"
                                    />
                                ) : (
                                    <div className="flex flex-col items-center gap-3 p-4 text-center">
                                        {(status === 'WAITING_QR' || status === 'STARTING' || isStarting) ? (
                                            <RefreshCw size={40} className="animate-spin text-primary/60" />
                                        ) : (
                                            <QrCode size={40} className="text-slate-300" />
                                        )}
                                        <p className="text-sm font-semibold text-slate-500">
                                            {isStarting ? 'Abrindo Chrome...' : 'QR aparecerá aqui'}
                                        </p>
                                        <p className="text-xs text-slate-400">O Chrome abrirá em alguns instantes</p>
                                    </div>
                                )}
                            </div>
                            {hasQR && (
                                <p className="mt-2 text-center text-xs text-slate-400">Atualiza a cada 3 segundos</p>
                            )}
                        </div>

                        {/* Instructions */}
                        <div className="flex-1 space-y-4">
                            <div className="rounded-xl border border-blue-100 bg-blue-50 p-4 dark:border-blue-500/20 dark:bg-blue-500/10">
                                <h4 className="mb-2 text-sm font-bold text-blue-900 dark:text-blue-400">Como escanear</h4>
                                <ol className="space-y-2 text-xs text-blue-700 dark:text-blue-300">
                                    {[
                                        'O Chrome abrirá automaticamente com o WhatsApp Web',
                                        'Aguarde o QR Code aparecer acima (alguns segundos)',
                                        'Abra o WhatsApp no seu celular',
                                        'Toque em Mais opções → Dispositivos conectados',
                                        'Toque em Conectar um dispositivo e aponte para o QR acima',
                                    ].map((step, i) => (
                                        <li key={i} className="flex items-start gap-2">
                                            <span className="mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full bg-blue-200 text-[10px] font-bold text-blue-800 dark:bg-blue-500/30 dark:text-blue-300">
                                                {i + 1}
                                            </span>
                                            {step}
                                        </li>
                                    ))}
                                </ol>
                            </div>

                            {status === 'ERROR' && statusData?.message && (
                                <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 dark:border-rose-500/20 dark:bg-rose-500/10">
                                    <div className="flex items-start gap-2 text-rose-700 dark:text-rose-400">
                                        <AlertCircle size={16} className="mt-0.5 shrink-0" />
                                        <div>
                                            <p className="text-sm font-bold">Erro detectado</p>
                                            <p className="text-xs">{statusData.message}</p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {!isRunning && !isConnected && status === 'IDLE' && (
                                <div className="rounded-xl border border-amber-100 bg-amber-50 p-3 dark:border-amber-500/20 dark:bg-amber-500/10">
                                    <p className="mb-1 text-xs font-semibold text-amber-700">⚡ Servidor local não detectado. Execute:</p>
                                    <code className="block rounded bg-amber-100 px-2 py-1.5 text-xs text-amber-800 dark:bg-amber-500/20 dark:text-amber-300">
                                        cd whatsapp-local &amp;&amp; node server.js
                                    </code>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Help Banner */}
            <div className="flex items-center justify-between rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-3 dark:border-emerald-500/20 dark:bg-emerald-500/10">
                <div className="flex items-center gap-3 text-sm text-emerald-800 dark:text-emerald-400">
                    <QrCode size={18} />
                    <span><strong>Precisa de ajuda com a conexão?</strong> Consulte nossa documentação técnica sobre as diferenças entre as APIs.</span>
                </div>
                <ExternalLink size={16} className="shrink-0 text-emerald-600 dark:text-emerald-400" />
            </div>
        </div>
    );
}
