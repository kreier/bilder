# Stage plan

The important distinction is:

> The six stages are the project's high-level development roadmap. 2A/2B/2C are sub-phases inside Stage 2.

So I would currently represent it like this:

| Stage  | Name                                     | Current status  |
| ------ | ---------------------------------------- | --------------- |
| **1**  | Foundation / Schema / Scanner groundwork | **Completed**   |
| **2**  | Deterministic Catalog                    | **In progress** |
| **2A** | Architecture & Data Model                | **Frozen**      |
| **2B** | Data Inspector                           | **Next**        |
| **2C** | Deterministic Catalog/Scanner            | **After 2B**    |
| **3**  | Identity & Relationship Analysis         | Later           |
| **4**  | Metadata / Semantic Intelligence         | Later           |
| **5**  | User-facing Application / Search         | Later           |
| **6**  | AI-assisted / Advanced Intelligence      | Later           |

There is one nuance: the exact names of Stages 3–6 should probably be checked against our original six-stage plan before we treat this table as authoritative. I don't want to accidentally replace the terminology we established earlier with my reconstructed names.

So I would not update the roadmap documents with those Stage 3–6 names yet. The solid part is:

```text
Stage 1
   ↓
Stage 2
   ├── 2A Architecture & Data Model
   ├── 2B Data Inspector
   └── 2C Deterministic Catalog/Scanner
   ↓
Stage 3
   ↓
Stage 4
   ↓
Stage 5
   ↓
Stage 6
```

And I think the 2A → 2B → 2C refinement is actually a good improvement: we haven't changed the six-stage roadmap; we've made Stage 2 more explicit.
