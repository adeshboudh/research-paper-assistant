'use client';

import { useState } from 'react';
import { Message, QueryMode } from '@/types';
import { queryRag, queryGraphRag, queryConversation } from '@/lib/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ModeSelector from '../ui/ModeSelector';
import { v4 as uuidv4 } from 'uuid';

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [mode, setMode] = useState<QueryMode>('rag');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId] = useState(() => uuidv4());

    const handleSendMessage = async (content: string) => {
        // Add user message
        const userMessage: Message = {
            id: uuidv4(),
            role: 'user',
            content,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        try {
            let assistantContent = '';
            let sources = undefined;
            let graphNodes = undefined;

            // Call appropriate API based on mode
            if (mode === 'rag') {
                const response = await queryRag({
                    question: content,
                    session_id: sessionId,
                    top_k: 5,
                });
                assistantContent = response.answer;
                sources = response.sources;
            } else if (mode === 'graphrag') {
                const response = await queryGraphRag({
                    question: content,
                    session_id: sessionId,
                    top_k: 5,
                    use_graph: true,
                });
                assistantContent = response.answer;
                sources = response.sources;
                graphNodes = response.graph_nodes;
            } else if (mode === 'conversation') {
                const response = await queryConversation({
                    message: content,
                    session_id: sessionId,
                });
                assistantContent = response.reply;
                // For conversation mode, we could also fetch sources via RAG
                // but keeping it simple for now
            }

            // Add assistant message
            const assistantMessage: Message = {
                id: uuidv4(),
                role: 'assistant',
                content: assistantContent,
                sources,
                graph_nodes: graphNodes,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error: any) {
            console.error('Error querying backend:', error);

            // Add error message
            const errorMessage: Message = {
                id: uuidv4(),
                role: 'assistant',
                content: `Sorry, I encountered an error: ${error.response?.data?.detail || error.message}. Please make sure the backend is running.`,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleModeChange = (newMode: QueryMode) => {
        setMode(newMode);
        // Optionally clear messages when switching modes
        // setMessages([]);
    };

    return (
        <div className="flex h-full flex-col bg-slate-50">
            {/* Inner container to keep content centered */}
            <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
                {/* Mode selector */}
                <div className="px-4 pt-4 pb-2 border-b border-slate-200 bg-white">
                    <ModeSelector mode={mode} onChange={handleModeChange} />
                </div>

                {/* Messages */}
                <MessageList messages={messages} />

                {/* Input */}
                <MessageInput
                    onSend={handleSendMessage}
                    disabled={isLoading}
                    placeholder={
                        mode === 'conversation'
                            ? 'Continue the conversation...'
                            : 'Ask a question about this paper or topic...'
                    }
                />
            </div>
        </div>
    );
}
