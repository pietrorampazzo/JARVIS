import * as React from "react"
import { cn } from "@/utils"

const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
    ({ className, children, ...props }, ref) => (
        <div className="relative">
            <select
                ref={ref}
                className={cn(
                    "flex h-10 w-full appearance-none rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                    className
                )}
                {...props}
            >
                {children}
            </select>
            <div className="pointer-events-none absolute right-3 top-2.5">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 opacity-50"><path d="m6 9 6 6 6-6" /></svg>
            </div>
        </div>
    )
)
Select.displayName = "Select"

const SelectTrigger = ({ children }: { children: React.ReactNode }) => <>{children}</>
const SelectValue = ({ placeholder }: { placeholder?: string }) => <option value="" disabled hidden>{placeholder}</option>
const SelectContent = ({ children }: { children: React.ReactNode }) => <>{children}</>
const SelectItem = ({ children, value }: { children: React.ReactNode; value: string }) => <option value={value}>{children}</option>

// Simplificada a interface do Select para usar a tag <select> nativa, já que nas referências estavam sendo usados como um componente composto padrão Shadcn
export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem }
