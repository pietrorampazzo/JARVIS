import React from "react";
import { Button } from "../ui/button";

export default function AtaFilters({
    tipoFilter,
    setTipoFilter,
    statusFilter,
    setStatusFilter,
    totalAtas
}: {
    tipoFilter: string;
    setTipoFilter: (tipo: string) => void;
    statusFilter: string;
    setStatusFilter: (status: string) => void;
    totalAtas: number;
}) {
    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex flex-col md:flex-row gap-6 items-center justify-between">
                <div className="flex flex-wrap gap-4">
                    <div className="space-y-2">
                        <span className="text-sm font-medium text-gray-500 uppercase tracking-widest">Esfera</span>
                        <div className="flex gap-2">
                            <Button
                                variant={tipoFilter === "all" ? "default" : "outline"}
                                onClick={() => setTipoFilter("all")}
                                className={tipoFilter === "all" ? "bg-blue-600 hover:bg-blue-700 text-white" : ""}
                                size="sm"
                            >
                                Todas
                            </Button>
                            <Button
                                variant={tipoFilter === "Federal" ? "default" : "outline"}
                                onClick={() => setTipoFilter("Federal")}
                                className={tipoFilter === "Federal" ? "bg-blue-600 hover:bg-blue-700 text-white" : ""}
                                size="sm"
                            >
                                Federal
                            </Button>
                            <Button
                                variant={tipoFilter === "Estadual" ? "default" : "outline"}
                                onClick={() => setTipoFilter("Estadual")}
                                className={tipoFilter === "Estadual" ? "bg-blue-600 hover:bg-blue-700 text-white" : ""}
                                size="sm"
                            >
                                Estadual
                            </Button>
                            <Button
                                variant={tipoFilter === "Municipal" ? "default" : "outline"}
                                onClick={() => setTipoFilter("Municipal")}
                                className={tipoFilter === "Municipal" ? "bg-blue-600 hover:bg-blue-700 text-white" : ""}
                                size="sm"
                            >
                                Municipal
                            </Button>
                        </div>
                    </div>

                    <div className="space-y-2 border-l pl-4 border-gray-200">
                        <span className="text-sm font-medium text-gray-500 uppercase tracking-widest">Status</span>
                        <div className="flex gap-2">
                            <Button
                                variant={statusFilter === "all" ? "default" : "outline"}
                                onClick={() => setStatusFilter("all")}
                                className={statusFilter === "all" ? "bg-gray-800 text-white hover:bg-gray-900" : ""}
                                size="sm"
                            >
                                Todos
                            </Button>
                            <Button
                                variant={statusFilter === "vigente" ? "default" : "outline"}
                                onClick={() => setStatusFilter("vigente")}
                                className={statusFilter === "vigente" ? "bg-green-600 hover:bg-green-700 text-white" : ""}
                                size="sm"
                            >
                                Vigentes
                            </Button>
                        </div>
                    </div>
                </div>

                <div className="text-sm text-gray-500 flex items-center gap-2 bg-gray-50 px-4 py-2 rounded-lg">
                    <span className="font-semibold text-gray-900 text-lg">{totalAtas}</span>
                    atas encontradas
                </div>
            </div>
        </div>
    );
}
