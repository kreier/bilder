import { useEffect, useState } from "react";

import {
    getOverview,
    type Overview as OverviewData,
} from "../api/client";

function Overview() {
    const [data, setData] = useState<OverviewData | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        getOverview()
            .then(setData)
            .catch((err: unknown) => {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError("Could not load the catalogue overview.");
                }
            });
    }, []);

    if (error) {
        return (
            <section>
                <h1>Overview</h1>

                <div
                    style={{
                        padding: "16px",
                        borderRadius: "8px",
                        background: "#fce8e6",
                        color: "#a50e0e",
                        marginTop: "24px",
                    }}
                >
                    <strong>Could not connect to Bilder.</strong>
                    <p style={{ marginBottom: 0 }}>
                        {error}
                    </p>
                </div>
            </section>
        );
    }

    if (!data) {
        return (
            <section>
                <h1>Overview</h1>
                <p>Loading catalogue information…</p>
            </section>
        );
    }

    const { counts, latest_scan } = data;

    return (
        <section>
            <div
                style={{
                    marginBottom: "32px",
                }}
            >
                <h1
                    style={{
                        margin: 0,
                        fontSize: "32px",
                        lineHeight: 1.2,
                    }}
                >
                    Overview
                </h1>

                <p
                    style={{
                        marginTop: "8px",
                        color: "#5f6368",
                    }}
                >
                    Current state of the Bilder catalogue.
                </p>
            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns:
                        "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: "16px",
                    marginBottom: "32px",
                }}
            >
                <StatisticCard
                    label="Sources"
                    value={counts.sources}
                />

                <StatisticCard
                    label="File versions"
                    value={counts.file_versions}
                />

                <StatisticCard
                    label="Source copies"
                    value={counts.source_copies}
                />

                <StatisticCard
                    label="Observations"
                    value={counts.file_observations}
                />

                <StatisticCard
                    label="Scans"
                    value={counts.scan_sessions}
                />
            </div>

            <section
                style={{
                    background: "#ffffff",
                    border: "1px solid #dfe1e5",
                    borderRadius: "10px",
                    padding: "24px",
                }}
            >
                <h2
                    style={{
                        marginTop: 0,
                        fontSize: "18px",
                    }}
                >
                    Latest scan
                </h2>

                {latest_scan ? (
                    <dl
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "max-content 1fr",
                            gap: "8px 24px",
                            margin: 0,
                        }}
                    >
                        <dt>Session</dt>
                        <dd style={{ margin: 0 }}>
                            #{latest_scan.id}
                        </dd>

                        <dt>Source</dt>
                        <dd style={{ margin: 0 }}>
                            {latest_scan.source_name}
                        </dd>

                        <dt>Status</dt>
                        <dd style={{ margin: 0 }}>
                            {latest_scan.status}
                        </dd>

                        <dt>Started</dt>
                        <dd style={{ margin: 0 }}>
                            {latest_scan.started_at}
                        </dd>

                        <dt>Completed</dt>
                        <dd style={{ margin: 0 }}>
                            {latest_scan.completed_at ?? "—"}
                        </dd>

                        <dt>Root</dt>
                        <dd
                            style={{
                                margin: 0,
                                fontFamily:
                                    "ui-monospace, SFMono-Regular, Menlo, monospace",
                                overflowWrap: "anywhere",
                            }}
                        >
                            {latest_scan.scan_root}
                        </dd>

                        <dt>Scanner</dt>
                        <dd style={{ margin: 0 }}>
                            {latest_scan.scanner_version}
                        </dd>
                    </dl>
                ) : (
                    <p>
                        No scans have been recorded yet.
                    </p>
                )}
            </section>

            <section
                style={{
                    marginTop: "24px",
                    color: "#5f6368",
                    fontSize: "13px",
                }}
            >
                Database:{" "}
                <code>{data.database}</code>
            </section>
        </section>
    );
}

interface StatisticCardProps {
    label: string;
    value: number;
}

function StatisticCard({
    label,
    value,
}: StatisticCardProps) {
    return (
        <div
            style={{
                background: "#ffffff",
                border: "1px solid #dfe1e5",
                borderRadius: "10px",
                padding: "20px",
            }}
        >
            <div
                style={{
                    fontSize: "13px",
                    color: "#5f6368",
                    marginBottom: "8px",
                }}
            >
                {label}
            </div>

            <div
                style={{
                    fontSize: "28px",
                    fontWeight: 650,
                }}
            >
                {value.toLocaleString()}
            </div>
        </div>
    );
}

export default Overview;