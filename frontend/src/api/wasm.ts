import initSqlJs, { type Database } from "sql.js";
import type { LatestScan, Overview } from "./client";

let dbInstance: Database | null = null;
let initPromise: Promise<Database> | null = null;

/**
 * Initialize sql.js and load the in-memory database from bilder.db.
 */
export async function getWasmDatabase(): Promise<Database> {
  if (dbInstance) {
    return dbInstance;
  }

  if (initPromise) {
    return initPromise;
  }

  initPromise = (async () => {
    const baseUrl = import.meta.env.BASE_URL.endsWith("/")
      ? import.meta.env.BASE_URL
      : `${import.meta.env.BASE_URL}/`;

    // 1. Initialize SQL.js engine with local WASM binary
    const SQL = await initSqlJs({
      locateFile: (file) => `${baseUrl}${file}`,
    });

    // 2. Fetch the database binary
    const dbUrl = `${baseUrl}bilder.db`;
    const response = await fetch(dbUrl);
    if (!response.ok) {
      throw new Error(`Failed to load database from ${dbUrl}: ${response.status} ${response.statusText}`);
    }

    const buffer = await response.arrayBuffer();
    const db = new SQL.Database(new Uint8Array(buffer));
    dbInstance = db;
    return db;
  })();

  return initPromise;
}

function getCount(db: Database, table: string): number {
  try {
    const result = db.exec(`SELECT count(*) FROM ${table}`);
    if (result.length > 0 && result[0].values.length > 0) {
      return Number(result[0].values[0][0]);
    }
  } catch (err) {
    console.warn(`Could not count table ${table}:`, err);
    return 0;
  }
  return 0;
}

/**
 * Executes queries against in-browser SQLite matching the FastAPI /api/overview endpoint.
 */
export async function getWasmOverview(): Promise<Overview> {
  const db = await getWasmDatabase();

  const counts = {
    sources: getCount(db, "source"),
    scan_sessions: getCount(db, "scan_session"),
    file_versions: getCount(db, "file_version"),
    source_copies: getCount(db, "source_copy"),
    file_observations: getCount(db, "file_observation"),
  };

  let latest_scan: LatestScan | null = null;
  try {
    const scanQuery = `
      SELECT
          scan_session.id,
          scan_session.started_at,
          scan_session.completed_at,
          scan_session.status,
          scan_session.scan_root,
          scan_session.scanner_version,
          source.name AS source_name
      FROM scan_session
      JOIN source
          ON source.id = scan_session.source_id
      ORDER BY scan_session.id DESC
      LIMIT 1
    `;

    const scanResult = db.exec(scanQuery);
    if (scanResult.length > 0 && scanResult[0].values.length > 0) {
      const cols = scanResult[0].columns;
      const row = scanResult[0].values[0];
      const scanObj: Record<string, any> = {};
      cols.forEach((col, idx) => {
        scanObj[col] = row[idx];
      });
      latest_scan = scanObj as LatestScan;
    }
  } catch (err) {
    console.warn("Could not retrieve latest scan session:", err);
  }

  return {
    database: "bilder.db (In-Browser SQLite WASM)",
    counts,
    latest_scan,
  };
}

/**
 * Health check for the in-browser WASM engine.
 */
export async function getWasmHealth(): Promise<{ status: string; application: string; mode: string }> {
  await getWasmDatabase();
  return {
    status: "ok",
    application: "bilder",
    mode: "in-browser-sqlite",
  };
}
