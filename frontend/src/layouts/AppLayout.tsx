import type { ReactNode } from "react";

interface AppLayoutProps {
    children: ReactNode;
}

const primaryNavigation = [
    "Overview",
    "Browse",
    "Search",
    "Timeline",
    "Collections",
];

const informationNavigation = [
    "Scans",
    "Database",
    "Diagnostics",
    "System",
];

function AppLayout({ children }: AppLayoutProps) {
    return (
        <div
            style={{
                minHeight: "100vh",
                display: "flex",
                background: "#f5f6f8",
                color: "#202124",
                fontFamily:
                    "system-ui, -apple-system, BlinkMacSystemFont, " +
                    '"Segoe UI", sans-serif',
            }}
        >
            <aside
                style={{
                    width: "230px",
                    flexShrink: 0,
                    background: "#ffffff",
                    borderRight: "1px solid #dfe1e5",
                    padding: "24px 16px",
                    boxSizing: "border-box",
                }}
            >
                <div
                    style={{
                        fontSize: "24px",
                        fontWeight: 700,
                        marginBottom: "32px",
                        padding: "0 12px",
                    }}
                >
                    bilder
                </div>

                <nav>
                    <NavigationSection items={primaryNavigation} />

                    <div
                        style={{
                            marginTop: "28px",
                            marginBottom: "8px",
                            padding: "0 12px",
                            fontSize: "11px",
                            fontWeight: 700,
                            textTransform: "uppercase",
                            letterSpacing: "0.08em",
                            color: "#73777d",
                        }}
                    >
                        Information
                    </div>

                    <NavigationSection items={informationNavigation} />
                </nav>
            </aside>

            <main
                style={{
                    flex: 1,
                    minWidth: 0,
                    padding: "32px 40px",
                    boxSizing: "border-box",
                }}
            >
                {children}
            </main>
        </div>
    );
}

interface NavigationSectionProps {
    items: string[];
}

function NavigationSection({
    items,
}: NavigationSectionProps) {
    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                gap: "4px",
            }}
        >
            {items.map((item) => {
                const active = item === "Overview";

                return (
                    <a
                        key={item}
                        href="#"
                        style={{
                            display: "block",
                            padding: "9px 12px",
                            borderRadius: "7px",
                            textDecoration: "none",
                            fontSize: "14px",
                            fontWeight: active ? 600 : 400,
                            color: active ? "#202124" : "#5f6368",
                            background: active
                                ? "#e8eaed"
                                : "transparent",
                        }}
                    >
                        {item}
                    </a>
                );
            })}
        </div>
    );
}

export default AppLayout;