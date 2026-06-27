import { promises as fs } from "fs";
import path from "path";
import type { DataStore } from "../types";
import { seedData } from "./seed";

const DATA_DIR = path.join(process.cwd(), "data");
const STORE_PATH = path.join(DATA_DIR, "store.json");

async function ensureStore(): Promise<DataStore> {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true });
    const raw = await fs.readFile(STORE_PATH, "utf-8");
    return JSON.parse(raw) as DataStore;
  } catch {
    const initial = seedData();
    await fs.writeFile(STORE_PATH, JSON.stringify(initial, null, 2));
    return initial;
  }
}

async function writeStore(store: DataStore): Promise<void> {
  await fs.mkdir(DATA_DIR, { recursive: true });
  await fs.writeFile(STORE_PATH, JSON.stringify(store, null, 2));
}

export async function readLocalStore(): Promise<DataStore> {
  return ensureStore();
}

export async function updateLocalStore(
  updater: (store: DataStore) => DataStore
): Promise<DataStore> {
  const store = await ensureStore();
  const updated = updater(store);
  await writeStore(updated);
  return updated;
}
