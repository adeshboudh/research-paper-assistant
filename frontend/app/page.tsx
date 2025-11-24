'use client';

import { useState } from 'react';
import ChatInterface from '@/components/chat/ChatInterface';
import PdfUploader from '@/components/upload/PdfUploader';
import { MessageSquare, UploadCloud } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'upload'>('chat');

  return (
    <div className="flex-1 flex justify-center px-4 py-4 md:py-8">
      <div className="w-full max-w-6xl flex flex-col gap-4">
        {/* Top bar */}
        <header className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
              Research Paper Assistant
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Ask questions, explore graphs, and upload papers to analyze.
            </p>
          </div>

          <div className="inline-flex rounded-full border border-slate-200 bg-white shadow-sm overflow-hidden">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-2 px-4 py-2 text-sm ${activeTab === 'chat'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
                }`}
            >
              <MessageSquare size={16} />
              <span>Chat</span>
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex items-center gap-2 px-4 py-2 text-sm ${activeTab === 'upload'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:bg-slate-100'
                }`}
            >
              <UploadCloud size={16} />
              <span>Upload Paper</span>
            </button>
          </div>
        </header>

        {/* Main content card */}
        <main className="flex-1">
          {activeTab === 'chat' ? (
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden h-[calc(100vh-12rem)]">
              <ChatInterface />
            </div>
          ) : (
            <div className="rounded-2xl border border-slate-200 bg-white shadow-sm p-6 h-[calc(100vh-12rem)] overflow-y-auto">
              <PdfUploader />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
