import { getWasmHealth, getWasmOverview } from "./wasm";

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// In production on GitHub Pages (when no custom backend URL is specified) or if explicitly requested, default to WASM
const FORCE_WASM =
    import.meta.env.VITE_FORCE_WASM === "true" ||
    (import.meta.env.PROD && !import.meta.env.VITE_API_BASE_URL);

export interface LatestScan {
    id: number;
    started_at: string;
    completed_at: string | null;
    status: string;
    scan_root: string;
    scanner_version: string;
    source_name: string;
}

export interface Overview {
    database: string;
    counts: {
        sources: number;
        scan_sessions: number;
        file_versions: number;
        source_copies: number;
        file_observations: number;
    };
    latest_scan: LatestScan | null;
}

async function request<T>(path: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`);

    if (!response.ok) {
        throw new Error(
            `API request failed: ${response.status} ${response.statusText}`,
        );
    }

    return response.json() as Promise<T>;
}

export async function getOverview(): Promise<Overview> {
    if (FORCE_WASM) {
        return getWasmOverview();
    }

    try {
        return await request<Overview>("/api/overview");
    } catch (err) {
        console.warn(
            "FastAPI backend not reachable, falling back to in-browser SQLite WASM:",
            err,
        );
        return getWasmOverview();
    }
}

export async function getHealth(): Promise<{
    status: string;
    application: string;
    mode?: string;
}> {
    if (FORCE_WASM) {
        return getWasmHealth();
    }

    try {
        return await request("/api/health");
    } catch (err) {
        console.warn(
            "FastAPI backend not reachable, falling back to in-browser SQLite WASM:",
            err,
        );
        return getWasmHealth();
    }
}