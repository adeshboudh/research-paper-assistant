'use client';

import { Message } from '@/types';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import SourceCard from './SourceCard';

interface MessageListProps {
    messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
    if (messages.length === 0) {
        return (
            <div className="flex-1 flex items-center justify-center text-slate-500">
                <div className="text-center space-y-2">
                    <Bot size={40} className="mx-auto mb-2 opacity-70" />
                    <p className="text-base font-medium">Start a conversation</p>
                    <p className="text-xs md:text-sm">
                        Ask about a concept, a paper you uploaded, or a topic like “GraphRAG vs RAG”.
                    </p>
                </div>
            </div>
        );
    }


    return (
        <div className="flex-1 overflow-y-auto custom-scrollbar space-y-6 p-6">
            {messages.map((message) => (
                <div
                    key={message.id}
                    className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                >
                    {message.role === 'assistant' && (
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                            <Bot size={20} className="text-white" />
                        </div>
                    )}

                    <div
                        className={`max-w-3xl ${message.role === 'user'
                            ? 'bg-blue-600 text-white rounded-2xl rounded-tr-sm'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-2xl rounded-tl-sm'
                            } px-4 py-3 shadow-md`}
                    >
                        <div className="prose prose-sm dark:prose-invert max-w-none">
                            {message.role === 'user' ? (
                                <p className="m-0">{message.content}</p>
                            ) : (
                                <ReactMarkdown>{message.content}</ReactMarkdown>
                            )}
                        </div>

                        {/* Show sources for assistant messages */}
                        {message.role === 'assistant' && (
                            <SourceCard
                                sources={message.sources}
                                graphNodes={message.graph_nodes}
                            />
                        )}

                        <div className="text-xs opacity-60 mt-2">
                            {message.timestamp.toLocaleTimeString()}
                        </div>
                    </div>

                    {message.role === 'user' && (
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                            <User size={20} className="text-white" />
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
