'use client';

import { QueryMode } from '@/types';

interface ModeSelectorProps {
    mode: QueryMode;
    onChange: (mode: QueryMode) => void;
}

export default function ModeSelector({ mode, onChange }: ModeSelectorProps) {
    const modes: { value: QueryMode; label: string; description: string }[] = [
        {
            value: 'rag',
            label: 'RAG',
            description: 'Semantic search',
        },
        {
            value: 'graphrag',
            label: 'GraphRAG',
            description: 'Vector + graph',
        },
        {
            value: 'conversation',
            label: 'Conversation',
            description: 'Chat with memory',
        },
    ];

    return (
        <div className="inline-flex rounded-full bg-slate-100 p-1 text-xs md:text-sm">
            {modes.map((m) => {
                const active = mode === m.value;
                return (
                    <button
                        key={m.value}
                        onClick={() => onChange(m.value)}
                        className={`px-3 md:px-4 py-2 rounded-full transition-colors flex flex-col md:flex-row md:items-center md:gap-1 ${active
                                ? 'bg-white text-slate-900 shadow-sm'
                                : 'text-slate-500 hover:text-slate-800'
                            }`}
                    >
                        <span className="font-medium">{m.label}</span>
                        <span className="hidden md:inline text-[11px] opacity-70">
                            {m.description}
                        </span>
                    </button>
                );
            })}
        </div>
    );
}
