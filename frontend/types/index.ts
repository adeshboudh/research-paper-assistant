// API Request Types
export interface RagRequest {
  question: string;
  session_id?: string;
  top_k?: number;
}

export interface GraphRagRequest {
  question: string;
  session_id?: string;
  top_k?: number;
  use_graph?: boolean;
}

export interface ConversationRequest {
  message: string;
  session_id: string;
}

// API Response Types
export interface SourceInfo {
  paper_id: string;
  title: string;
  snippet: string;
  page?: number;
  relevance_score?: number;
}

export interface GraphNode {
  node_type: string;
  properties: Record<string, any>;
}

export interface RagResponse {
  answer: string;
  sources: SourceInfo[];
  session_id: string;
}

export interface GraphRagResponse {
  answer: string;
  sources: SourceInfo[];
  graph_nodes: GraphNode[];
  session_id: string;
}

export interface ConversationResponse {
  reply: string;
  session_id: string;
  context_used: number;
}

// UI Types
export type QueryMode = 'rag' | 'graphrag' | 'conversation';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceInfo[];
  graph_nodes?: GraphNode[];
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  messages: Message[];
  mode: QueryMode;
}
