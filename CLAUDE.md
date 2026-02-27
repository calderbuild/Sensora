# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SENSORA is a neurophysiology-powered fragrance personalization platform for the L'Oreal Brandstorm 2026 competition. It creates bespoke perfume formulations based on emotional states (valence-arousal from text or EEG) and individual body chemistry (pH, skin type, temperature).

This is an MVP/demo: 15 ingredients, 13 physio rules, no real EEG hardware. Designed to showcase technology within competition constraints.

## Development Commands

### Frontend (Next.js 14 + TypeScript)
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start dev server (localhost:3000)
npm run build        # Production build
npm run lint         # ESLint check
```

### Backend (FastAPI + Python 3.11+)
```bash
cd backend
pip install -r requirements.txt           # Minimal deps (Vercel-compatible)
pip install -r requirements-full.txt      # Full deps (local dev with RDKit, ChromaDB)
uvicorn app.main:app --reload             # Start dev server (localhost:8000)
```

No test suite exists yet. pytest is in requirements-full.txt for future use.

## Architecture

### Data Flow
```
User Input -> Calibration (pH/skin/temp) -> Neuro-Brief (text -> valence-arousal)
           -> AI Service (OpenAI) or AetherAgent (local fallback)
           -> Physio-RAG Corrections -> IFRA Validation -> Formula Output
```

### Frontend (`frontend/src/`)
- **Pages** (`app/`): Landing (`/`), Calibration (`/calibration`), Neuro-Brief (`/neuro-brief`), Result (`/result`). All use Framer Motion page transitions.
- **State** (`stores/userProfileStore.ts`): Zustand with localStorage persistence (key: `sensora-user-profile`). Holds calibration, neuro-brief, and formula across page transitions. Exports selector hooks (`useCalibration`, `useNeuroBrief`, `useFormula`) for render optimization.
- **API client** (`lib/api.ts`): Typed fetch wrapper around backend endpoints. Base URL from `NEXT_PUBLIC_API_URL`. Auto-strips trailing slashes. Custom `ApiError` class with status/statusText/message.
- **Utilities** (`lib/utils.ts`): `cn()` helper (clsx + tailwind-merge), `getMoodLabel()`/`getScentFamilies()` for V-A mapping, math helpers (`clamp`, `lerp`, `mapRange`), safe localStorage wrappers.
- **Components** (`components/wellness/`): StressProfile, HeartRateMonitor -- these are **UI-only demo components** that don't send data to the backend.
- **Path alias**: `@/*` maps to `src/*` in tsconfig.

### Frontend Design System
- **Colors**: Sensora Teal (primary, `#10B981`), Gold (accent, `#F59E0B`), Rose (alert, `#F43F5E`), custom gray scale. Defined in `tailwind.config.ts`.
- **Fonts**: Playfair Display (display/headings), DM Sans (body), JetBrains Mono (code). Loaded in `app/layout.tsx`.
- **CSS patterns** (`app/globals.css`): `.wellness-card`, `.aurora-bg`, `.btn-primary`, `.btn-soft`, `.teal-gradient`. Custom keyframes for particle, aurora, heartbeat, wave, breathe animations.

### Backend (`backend/app/`)
- `main.py` - FastAPI entry, CORS config, route registration
- `config.py` - Pydantic settings. Note: `openai_base_url` defaults to `newapi.deepwisdom.ai/v1` (DeepWisdom proxy, not standard OpenAI)
- `models/` - Pydantic request/response models (`formula.py`, `user_profile.py`)
- `core/ai_service.py` - OpenAI GPT-4o integration for emotion-to-scent analysis (primary engine)
- `core/aether_agent.py` - Local formula orchestrator (fallback when no OpenAI key)
- `core/physio_rag.py` - ChromaDB + sentence-transformers for physiological corrections; keyword matching fallback
- `chemistry/ifra_validator.py` - IFRA 51st Amendment compliance checker
- `chemistry/molecular_calc.py` - RDKit-based LogP and molecular weight calculations
- `chemistry/ingredient_db.py` - JSON ingredient database accessor (singleton)
- `neuro/eeg_simulator.py` - Text-to-valence-arousal via keyword matching (no EEG hardware)
- `neuro/ph_analyzer.py` - pH strip image analysis via RGB color distance matching
- `api/routes/` - REST endpoints: calibration, formulation, payment

### Key Design Decisions
- **Stateless backend**: No database or session persistence. Each request is independent; frontend Zustand store carries state between steps.
- **Graceful degradation**: Heavy dependencies (RDKit, sentence-transformers, ChromaDB) have try-except fallbacks for Vercel serverless. OpenAI unavailable -> local AetherAgent. ChromaDB unavailable -> keyword matching. RDKit unavailable -> dummy molecular values.
- **Module-level singletons**: `IngredientDatabase`, `IFRAValidator`, `EEGSimulator`, `PhysioRAG` are all instantiated at module level. Works for stateless serverless but limits testability.
- **IFRA validation is advisory**: Violations are reported in response but don't block formula delivery. Formula generation always runs IFRA validation before returning.
- **Legacy naming**: Backend config (`app_name = "Aether"`), AI prompts, and `frontend/package.json` (`name: "aether-frontend"`) still reference the pre-rebrand name.

## API Endpoints

Base URL: `/api`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Root: returns app name, version, status |
| GET | `/health` | Health check |
| POST | `/calibration/profile` | Create user profile |
| POST | `/formulation/generate` | Main formula generation (requires profile_id, ph_value, skin_type) |
| POST | `/formulation/validate` | IFRA compliance check |
| POST | `/formulation/eeg-simulate` | Text to valence-arousal |
| GET | `/formulation/ph-simulate/{skin_type}` | Demo pH values (hardcoded per skin type) |
| POST | `/formulation/ph-analyze` | Analyze pH strip image (multipart) |
| POST | `/formulation/molecular-analysis` | RDKit molecular properties from SMILES |
| GET | `/formulation/ingredients` | List ingredients (filters: note_type, sustainable_only, family) |

FastAPI auto-generates Swagger docs at `/docs` when running locally.

## Environment Variables

### Backend (`backend/.env`)
```
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://newapi.deepwisdom.ai/v1   # DeepWisdom proxy, not standard OpenAI
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PAYPAL_CLIENT_ID=...
```

## Deployment

- Frontend: Vercel (Next.js), config at `frontend/vercel.json`
- Backend: Vercel serverless (Python), entry point at `backend/api/index.py`, config at `backend/vercel.json`
- Alternative: Railway via `backend/Dockerfile` + `railway.toml`
- Frontend production: sensora-app.vercel.app
- Backend production: sensora-api.vercel.app
- CORS allows `localhost:3000`, `sensora-app.vercel.app`, and `*.vercel.app`

## Gotchas

- **Zustand persistence is partial**: `isGenerating` and `error` state don't persist to localStorage -- only calibration, neuroBrief, formula, and currentStep do.
- **Result page has sample formula fallback**: If `formula` is null in Zustand store, the result page renders hardcoded sample data for demo purposes.
- **Mood quadrant Y-axis is inverted on screen**: High arousal renders at top of canvas but internally uses +1. Valence is -1 (left) to +1 (right).
- **Note pyramid ratios are hardcoded**: Always 20% top, 35% middle, 45% base. No per-user or per-formula customization.
- **EEG simulator is keyword-based**: Maps words like "happy" (+0.3 valence), "intense" (+0.3 arousal) to circumplex coordinates. No actual signal processing.
- **pH simulator returns hardcoded values**: `GET /ph-simulate/{skin_type}` returns mock pH, not real sensor readings.
- **Framer Motion transitions are component-level**: Not enforced at router level. Browser back button doesn't trigger exit animations.
- **Pydantic models on backend mirror TypeScript interfaces on frontend but are not auto-generated**: Changes to one must be manually reflected in the other.

## Domain Concepts

- **Valence-Arousal (V-A)**: Circumplex model of affect. Valence (-1 to +1) = pleasantness; Arousal (-1 to +1) = energy level
- **Physio-RAG**: 13 rules in `backend/data/physio_rules.json` that apply physiological corrections (e.g., pH < 4.5 -> reduce aldehydes by 0.85x due to Schiff base formation; dry skin -> boost fixatives)
- **IFRA Compliance**: International Fragrance Association 51st Amendment safety standards. Category 1 = fine fragrance. Bans HICC/Lyral outright; restricts coumarin to 0.8%, methyl eugenol to 0.0002%. Allergen declaration threshold: 0.1% for Category 1.
- **Note Pyramid**: Top (20%), Middle/Heart (35%), Base (45%) concentration ratios
- **LogP**: Octanol-water partition coefficient (Crippen method via RDKit). Higher LogP = more lipophilic = longer lasting on skin. Typically >3.5 for base notes.
- **Ingredient database**: 15 entries in `backend/data/ingredients.json`, each with SMILES, note_type, family, logp, sustainability_score (0-10), ifra_restricted flag, max_concentration
