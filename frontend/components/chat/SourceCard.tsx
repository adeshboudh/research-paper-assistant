'use client';

import { SourceInfo, GraphNode } from '@/types';
import { FileText, Database } from 'lucide-react';

interface SourceCardProps {
    sources?: SourceInfo[];
    graphNodes?: GraphNode[];
}

export default function SourceCard({ sources, graphNodes }: SourceCardProps) {
    if ((!sources || sources.length === 0) && (!graphNodes || graphNodes.length === 0)) {
        return null;
    }

    return (
        <div className="mt-3 space-y-3">
            {/* Text Sources */}
            {sources && sources.length > 0 && (
                <div>
                    <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        <FileText size={16} />
                        <span>Sources ({sources.length})</span>
                    </div>
                    <div className="space-y-2">
                        {sources.map((source, idx) => (
                            <div
                                key={idx}
                                className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md text-sm"
                            >
                                <div className="flex justify-between items-start gap-2 mb-1">
                                    <span className="font-medium text-blue-900 dark:text-blue-300">
                                        {source.paper_id}
                                    </span>
                                    {source.relevance_score && (
                                        <span className="text-xs bg-blue-200 dark:bg-blue-800 px-2 py-1 rounded">
                                            {(source.relevance_score * 100).toFixed(0)}% match
                                        </span>
                                    )}
                                </div>
                                <p className="text-gray-700 dark:text-gray-300 line-clamp-3">
                                    {source.snippet}
                                </p>
                                {source.page && (
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                        Page {source.page}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Graph Nodes */}
            {graphNodes && graphNodes.length > 0 && (
                <div>
                    <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        <Database size={16} />
                        <span>Knowledge Graph ({graphNodes.length})</span>
                    </div>
                    <div className="space-y-2">
                        {graphNodes.map((node, idx) => (
                            <div
                                key={idx}
                                className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-md text-sm"
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-xs bg-purple-200 dark:bg-purple-800 px-2 py-1 rounded font-medium">
                                        {node.node_type}
                                    </span>
                                </div>
                                <div className="text-gray-700 dark:text-gray-300">
                                    {node.properties.title && (
                                        <div className="font-medium">{node.properties.title}</div>
                                    )}
                                    {node.properties.authors && (
                                        <div className="text-xs text-gray-600 dark:text-gray-400">
                                            {node.properties.authors}
                                        </div>
                                    )}
                                    {node.properties.year && (
                                        <div className="text-xs text-gray-500 dark:text-gray-400">
                                            Year: {node.properties.year}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
