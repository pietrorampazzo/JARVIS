import React from "react";
import { Card, CardHeader, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { FileText, Calendar, DollarSign, Building } from "lucide-react";

export default function AtaCardDetalhado({ ata, index }: { ata: any; index: number }) {
    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value || 0);
    };

    const formatDate = (dateStr: string) => {
        if (!dateStr) return "-";
        const d = new Date(dateStr);
        return new Intl.DateTimeFormat('pt-BR').format(d);
    };

    return (
        <Card className="hover:border-blue-300 hover:shadow-lg transition-all duration-300">
            <CardHeader className="bg-gray-50 border-b">
                <div className="flex justify-between items-start">
                    <div>
                        <span className={`text-xs font-semibold px-2 py-1 rounded mb-2 inline-block ${ata.status === 'vigente' ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-800'}`}>
                            {ata.status === 'vigente' ? 'Vigente' : 'Expirada'}
                        </span>
                        <h3 className="text-xl font-bold text-gray-900">Ata Nº {ata.numero}</h3>
                    </div>
                    <FileText className="w-6 h-6 text-gray-400" />
                </div>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
                <div className="flex items-start gap-3">
                    <Building className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                        <p className="text-sm font-medium text-gray-500">Órgão Gerenciador</p>
                        <p className="text-base text-gray-900">{ata.orgao}</p>
                        <p className="text-sm text-gray-500">Nível: {ata.tipo}</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4 bg-blue-50/50 p-4 rounded-lg">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <Calendar className="w-4 h-4 text-gray-500" />
                            <span className="text-sm font-medium text-gray-500">Validade</span>
                        </div>
                        <p className="font-semibold text-gray-900">{formatDate(ata.data_vencimento)}</p>
                    </div>
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <DollarSign className="w-4 h-4 text-gray-500" />
                            <span className="text-sm font-medium text-gray-500">Valor Total Estimado</span>
                        </div>
                        <p className="font-bold text-blue-600">{formatCurrency(ata.valor_total)}</p>
                    </div>
                </div>

                <Button className="w-full mt-4" variant="outline">Ver Itens Registrados</Button>
            </CardContent>
        </Card>
    );
}
