// Mirrors api/src/kmg_api/schemas/*.py
// Keep field names aligned with the FastAPI schemas — these flow over the proxy unchanged.

export type UUID = string
export type ISODate = string

// ───── Workspace ─────
export interface Workspace {
  id: UUID
  tenant_id: UUID
  name: string
  slug: string
  status: string
  settings: Record<string, unknown>
  created_at: ISODate
  updated_at: ISODate
}
export interface WorkspaceListResponse {
  workspaces: Workspace[]
  total: number
}
export interface CreateWorkspaceRequest {
  name: string
  slug: string
  settings?: Record<string, unknown>
}
export interface UpdateWorkspaceRequest {
  name?: string
  settings?: Record<string, unknown>
}

// ───── Source ─────
export interface Source {
  id: UUID
  tenant_id: UUID
  workspace_id: UUID
  source_type: string
  title: string
  uri: string | null
  content_hash: string | null
  status: string
  metadata: Record<string, unknown>
  created_at: ISODate
  updated_at: ISODate
}
export interface SourceListResponse {
  sources: Source[]
  total: number
}
export interface CreateSourceRequest {
  source_type: string
  title: string
  pipeline_id?: string
  uri?: string | null
  metadata?: Record<string, unknown>
}
export interface CreateSourceResponse {
  source_id: UUID
  version_id: UUID
  job_id: UUID
}
export interface PresignedUploadRequest {
  source_type: string
  title: string
  pipeline_id?: string
  metadata?: Record<string, unknown>
}
export interface PresignedUploadResponse {
  source_id: UUID
  version_id: UUID
  upload_url: string
  expires_in: number
}
export interface ConfirmUploadRequest {
  source_id: UUID
  version_id: UUID
}
export interface ConfirmUploadResponse {
  job_id: UUID
  status: string
}
export interface SourceVersion {
  id: UUID
  source_id: UUID
  parser_version: string | null
  raw_object_key: string
  content_hash: string | null
  created_at: ISODate
}
export interface JobStatus {
  id: UUID
  status: 'pending' | 'running' | 'completed' | 'failed' | string
  stage:
    | 'parsing'
    | 'segmenting'
    | 'chunking'
    | 'chunk_embedding'
    | 'wiki_generation'
    | 'wiki_internal_linking'
    | 'backlink_indexing'
    | 'wiki_revision_created'
    | 'wiki_embedding'
    | 'graph_node_creation'
    | 'graph_edge_creation'
    | 'wiki_graph_linking'
    | 'vector_sync'
    | 'completed'
    | string
    | null
  progress: number
  error: string | null
  created_at: ISODate
  updated_at: ISODate
}

// ───── Wiki ─────
export type FreshnessStatus = 'fresh' | 'stale' | 'outdated' | string
export interface WikiPage {
  id: UUID
  tenant_id: UUID
  workspace_id: UUID
  slug: string
  title: string
  page_type: string
  markdown: string
  summary: string | null
  freshness_status: FreshnessStatus
  source_count: number
  chunk_count: number
  graph_node_count: number
  metadata: Record<string, unknown>
  created_at: ISODate
  updated_at: ISODate
}
export interface WikiPageListResponse {
  pages: WikiPage[]
  total: number
}
export interface UpdateWikiPageRequest {
  markdown?: string
  summary?: string
  title?: string
}
export interface WikiBacklink {
  id: UUID
  wiki_page_id: UUID
  referring_wiki_page_id: UUID
  context_snippet: string | null
}
export interface WikiRevision {
  id: UUID
  wiki_page_id: UUID
  revision_number: number
  markdown: string
  author_type: string
  change_summary: string | null
  created_at: ISODate
}
export interface WikiEvidence {
  id: UUID
  wiki_page_id: UUID
  chunk_id: UUID
  source_id: UUID
  source_version_id: UUID
  evidence_role: string
  confidence: number
  quote: string | null
}
export interface Chunk {
  id: UUID
  tenant_id: UUID
  workspace_id: UUID
  source_id: UUID
  source_version_id: UUID
  segment_id: UUID
  chunk_index: number
  text: string
  content_hash: string | null
  status: string
  metadata: Record<string, unknown>
  created_at: ISODate
  updated_at: ISODate
}

// ───── Graph ─────
export interface GraphNode {
  id: UUID
  tenant_id: UUID
  workspace_id: UUID
  node_type: string
  canonical_name: string
  description: string | null
  aliases: string[]
  confidence: number
  status: string
  primary_wiki_page_id: UUID | null
  metadata: Record<string, unknown>
  created_at: ISODate
  updated_at: ISODate
}
export interface GraphEdge {
  id: UUID
  subject_type: string
  subject_id: UUID
  predicate: string
  object_type: string
  object_id: UUID
  confidence: number
  weight: number
  status: string
  created_at: ISODate
}
export interface GraphNodeListResponse {
  nodes: GraphNode[]
  total: number
}
export interface GraphEdgeListResponse {
  edges: GraphEdge[]
  total: number
}
export interface GraphExploreResponse {
  center_node: GraphNode
  edges: GraphEdge[]
  connected_nodes: GraphNode[]
}

// ───── Search & Chat ─────
export type SearchScope = 'current_project' | 'all_projects' | 'shared_projects'
export interface SearchRequest {
  query: string
  scope?: SearchScope
  record_types?: string[]
  limit?: number
}
export interface SearchResultItem {
  id: UUID
  record_type: string
  score: number
  title?: string | null
  slug?: string | null
  snippet?: string | null
  workspace_id: UUID
  metadata?: Record<string, unknown>
}
export interface SearchResponse {
  query: string
  results: SearchResultItem[]
  answer?: string | null
  citations: Array<Record<string, unknown>>
  total_found: number
  confidence?: number | null
  follow_up_suggestions: string[]
}
export interface ChatRequest {
  query: string
  scope?: SearchScope
  conversation_id?: UUID | null
}
export interface ChatResponse {
  answer: string
  citations: Array<Record<string, unknown>>
  confidence?: number | null
  conversation_id: UUID
  follow_up_suggestions: string[]
}

// ───── Canvas ─────
export interface Canvas {
  id: UUID
  tenant_id: UUID
  workspace_id: UUID
  title: string
  layout: Record<string, unknown>
  metadata: Record<string, unknown>
  created_at: ISODate
  updated_at: ISODate
}
export interface CanvasItem {
  id: UUID
  canvas_id: UUID
  item_type: 'wiki_page' | 'graph_node' | 'source' | 'chunk' | 'sticky_note' | string
  target_id: UUID | null
  x: number
  y: number
  width: number
  height: number
  style: Record<string, unknown>
  created_at: ISODate
}
export interface CanvasEdge {
  id: UUID
  canvas_id: UUID
  from_item_id: UUID
  to_item_id: UUID
  label: string | null
  edge_type: string | null
  style: Record<string, unknown>
  created_at: ISODate
}
export interface CanvasDetailResponse {
  canvas: Canvas
  items: CanvasItem[]
  edges: CanvasEdge[]
}
export interface CanvasListResponse {
  canvases: Canvas[]
  total: number
}
export interface CreateCanvasRequest {
  title: string
  layout?: Record<string, unknown>
  metadata?: Record<string, unknown>
}
export interface UpdateCanvasRequest {
  title?: string
  layout?: Record<string, unknown>
}
export interface CanvasItemRequest {
  item_type: string
  target_id?: UUID | null
  x?: number
  y?: number
  width?: number
  height?: number
  style?: Record<string, unknown>
}
export interface CanvasEdgeRequest {
  from_item_id: UUID
  to_item_id: UUID
  label?: string
  edge_type?: string
  style?: Record<string, unknown>
}
export interface AiOrganizeResponse {
  items_moved: number
  edges_added: number
  groups: Array<Record<string, unknown>>
}
