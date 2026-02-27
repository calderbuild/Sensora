# SENSORA

**Fragrance That Feels You**

> L'Oréal Brandstorm 2026 — Crafting the Future of Luxury Fragrance

SENSORA is a neurophysiology-powered fragrance personalization platform. It creates bespoke perfume formulations based on emotional states (valence-arousal) and individual body chemistry (pH, skin type, temperature).

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Bio-Calibration│────▶│   Neuro-Brief   │────▶│  AI Formulation │
│  pH / Skin Type │     │  Text → V-A Map │     │  + Physio-RAG   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Skin Chemistry  │     │ Emotional Tone  │     │ IFRA-Compliant  │
│   Profiling     │     │   Extraction    │     │    Formula      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**User Journey:**
1. **Calibrate** — Input skin pH, type, and body temperature
2. **Describe** — Natural language prompt + mood quadrant positioning
3. **Generate** — AI creates personalized formula with physiological corrections
4. **Order** — Secure checkout, bespoke 30ml formula delivered

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Zustand |
| Backend | FastAPI, Python 3.11+ |
| AI/ML | OpenAI GPT-4o, Sentence-Transformers |
| Chemistry | RDKit (LogP, MW), IFRA 51st Amendment |
| Database | ChromaDB (vector store), JSON (ingredients) |

## Quick Start

**Frontend**
```bash
cd frontend
npm install
npm run dev    # localhost:3000
```

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload    # localhost:8000
```

**Environment Variables**
```bash
# backend/.env
OPENAI_API_KEY=sk-...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PAYPAL_CLIENT_ID=...
```

## Project Structure

```
Sensora/
├── frontend/                 # Next.js application
│   ├── src/app/             # Pages: /, /calibration, /neuro-brief, /result
│   ├── src/stores/          # Zustand state management
│   └── src/lib/api.ts       # Backend API client
│
├── backend/                  # FastAPI application
│   ├── app/core/            # AetherAgent, Physio-RAG, AI service
│   ├── app/chemistry/       # IFRA validator, molecular calculations
│   ├── app/neuro/           # EEG simulator, pH analyzer
│   ├── app/api/routes/      # REST endpoints
│   └── data/                # 15 ingredients, 13 physio rules
│
└── docs/                     # Competition materials
```

## Core Technologies

**Physio-RAG (Retrieval-Augmented Generation)**
- 13 scientific rules for fragrance-skin interaction
- Adjusts formulations based on pH, skin type, temperature
- Example: Dry skin → boost fixatives; Oily skin → reduce heavy musks

**IFRA Compliance**
- Validates against IFRA 51st Amendment standards
- Category 1 (fine fragrance) concentration limits
- Automated safety checking before formula output

**Valence-Arousal Mapping**
- Circumplex model: Valence (-1 to +1), Arousal (-1 to +1)
- Maps emotional descriptors to scent families
- High valence + low arousal → calming florals; Low valence + high arousal → intense spices

## Deployment

- **Frontend**: Vercel (Next.js auto-detection)
- **Backend**: Vercel Serverless via `backend/api/index.py`
- **Production**: sensora-delta.vercel.app

## Competition Alignment

| Criterion | Implementation |
|-----------|----------------|
| Innovative | First platform combining EEG-ready emotional input with skin chemistry |
| Sustainable | Sustainability scoring for each ingredient |
| Tech-Driven | Full-stack AI: NLP → Physio-RAG → molecular validation |
| Inclusive | Works across all skin types, no hardware required for basic use |
| Feasible | Working prototype with payment integration |
| Scalable | Cloud-native architecture, API-first design |

## Team

Sensora Team — L'Oréal Brandstorm 2026

## License

MIT
