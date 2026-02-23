# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SENSORA is a neurophysiology-powered fragrance personalization platform for the L'Oreal Brandstorm 2026 competition. It creates bespoke perfume formulations based on emotional states (valence-arousal from text or EEG) and individual body chemistry (pH, skin type, temperature).

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
- **Pages** (`app/`): Landing (`/`), Calibration, Neuro-Brief, Result. All use Framer Motion page transitions.
- **State** (`stores/userProfileStore.ts`): Zustand with localStorage persistence (key: `sensora-user-profile`). Holds calibration, neuro-brief, and formula across page transitions. Exports selector hooks (`useCalibration`, `useNeuroBrief`, `useFormula`) for render optimization.
- **API client** (`lib/api.ts`): Typed fetch wrapper around backend endpoints. Base URL from `NEXT_PUBLIC_API_URL`.
- **Utilities** (`lib/utils.ts`): `cn()` helper (clsx + tailwind-merge), formatting functions, localStorage helpers.
- **Components** (`components/wellness/`): StressProfile, HeartRateMonitor biometric dashboard components.
- **Path alias**: `@/*` maps to `src/*` in tsconfig.

### Frontend Design System
- **Colors**: Sensora Teal (primary, `#10B981`), Gold (accent, `#F59E0B`), Rose (alert, `#F43F5E`), custom gray scale. Defined in `tailwind.config.ts`.
- **Fonts**: Playfair Display (display/headings), DM Sans (body), JetBrains Mono (code). Loaded in `app/layout.tsx`.
- **CSS patterns** (`app/globals.css`): `.wellness-card`, `.aurora-bg`, `.btn-primary`, `.btn-soft`, `.teal-gradient`. Custom keyframes for particle, aurora, heartbeat, wave, breathe animations.

### Backend (`backend/app/`)
- `main.py` - FastAPI entry, CORS config, route registration
- `config.py` - Pydantic settings. Note: `openai_base_url` defaults to `newapi.deepwisdom.ai/v1` (not standard OpenAI)
- `models/` - Pydantic request/response models (`formula.py`, `user_profile.py`)
- `core/ai_service.py` - OpenAI GPT-4o integration for emotion-to-scent analysis (primary engine)
- `core/aether_agent.py` - Local formula orchestrator (fallback when no OpenAI key)
- `core/physio_rag.py` - ChromaDB + sentence-transformers for physiological corrections; keyword matching fallback
- `chemistry/ifra_validator.py` - IFRA 51st Amendment compliance checker
- `chemistry/molecular_calc.py` - RDKit-based LogP and molecular weight calculations
- `chemistry/ingredient_db.py` - JSON ingredient database accessor
- `neuro/eeg_simulator.py` - Text-to-valence-arousal conversion (no EEG hardware required)
- `neuro/ph_analyzer.py` - pH strip image analysis via color matching
- `api/routes/` - REST endpoints: calibration, formulation, payment
- `data/` - JSON data files: 15 ingredients, 13 physio rules, IFRA standards

### Key Design Decisions
- **Stateless backend**: No database or session persistence. Each request is independent; frontend Zustand store carries state between steps.
- **Graceful degradation**: Heavy dependencies (RDKit, sentence-transformers, ChromaDB) have fallbacks for Vercel serverless. OpenAI unavailable -> local AetherAgent. ChromaDB unavailable -> keyword matching.
- **Legacy naming**: Backend config and AI prompts still reference "Aether" in places (pre-rebrand name).
- Formula generation always runs IFRA validation before returning.

## API Endpoints

Base URL: `/api`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/formulation/generate` | Main formula generation (requires profile_id, ph_value, skin_type) |
| POST | `/formulation/validate` | IFRA compliance check |
| POST | `/formulation/eeg-simulate` | Text to valence-arousal |
| GET | `/formulation/ph-simulate/{skin_type}` | Demo pH values by skin type |
| POST | `/formulation/ph-analyze` | Analyze pH strip image (multipart) |
| POST | `/formulation/molecular-analysis` | RDKit molecular properties from SMILES |
| GET | `/formulation/ingredients` | List ingredients (filters: note_type, sustainable_only, family) |
| POST | `/calibration/profile` | Create user profile |

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
- Production: deepscent.vercel.app
- CORS allows `localhost:3000`, `deepscent.vercel.app`, and `*.vercel.app`

## Domain Concepts

- **Valence-Arousal (V-A)**: Circumplex model of affect. Valence (-1 to +1) = pleasantness; Arousal (-1 to +1) = energy level
- **Physio-RAG**: 13 scientific rules that apply physiological corrections (e.g., dry skin -> boost fixatives, oily skin -> reduce heavy musks)
- **IFRA Compliance**: International Fragrance Association 51st Amendment safety standards. Category 1 = fine fragrance concentration limits
- **Note Pyramid**: Top (20%), Middle/Heart (35%), Base (45%) concentration ratios
- **LogP**: Octanol-water partition coefficient. Higher LogP = longer lasting on skin
