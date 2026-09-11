const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

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

export function getOverview(): Promise<Overview> {
    return request<Overview>("/api/overview");
}

export function getHealth(): Promise<{
    status: string;
    application: string;
}> {
    return request("/api/health");
}