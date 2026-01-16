"""
Formulation API endpoints.
Handles perfume formula generation, IFRA validation, and physiological analysis.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from app.core.ai_service import ai_analyzer
from app.core.aether_agent import create_agent, AetherAgent
from app.chemistry.ifra_validator import ifra_validator
from app.chemistry.molecular_calc import calculate_logp, get_full_properties
from app.chemistry.ingredient_db import ingredient_db
from app.neuro.eeg_simulator import eeg_simulator
from app.neuro.ph_analyzer import ph_analyzer
from app.config import settings

router = APIRouter()


# ============== Request/Response Models ==============

class FormulationRequest(BaseModel):
    """Request model for generating a personalized perfume formula."""
    profile_id: str = Field(..., description="User profile ID from calibration")
    ph_value: float = Field(..., ge=3.0, le=9.0)
    skin_type: str = Field(..., pattern="^(Dry|Normal|Oily|dry|normal|oily)$")
    temperature: float = Field(default=36.5, ge=35.0, le=40.0)
    prompt: Optional[str] = Field(None, description="Natural language scent description")
    valence: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Mood valence score")
    arousal: Optional[float] = Field(None, ge=0.0, le=1.0, description="Mood arousal score")
    allergies: Optional[list[str]] = Field(default=[], description="Known allergens to avoid")


class Ingredient(BaseModel):
    """Single ingredient in a formula."""
    name: str
    smiles: str
    concentration: float
    note_type: str
    logp: float
    molecular_weight: Optional[float] = None
    is_sustainable: bool
    source: str
    sustainability_score: Optional[int] = None


class FormulaResponse(BaseModel):
    """Response model for generated formula."""
    formula_id: str
    name: str
    description: str
    ingredients: list[Ingredient]
    note_pyramid: dict
    longevity_score: float
    projection_score: float
    sustainability_score: float
    ifra_compliant: bool
    ifra_report: Optional[dict] = None
    physio_corrections_applied: list[str]
    emotional_profile: Optional[dict] = None


class ValidationRequest(BaseModel):
    """Request model for IFRA compliance validation."""
    ingredients: list[Ingredient]
    product_category: str = Field(default="cat1", pattern="^(cat1|cat2)$")


class ValidationResponse(BaseModel):
    """Response model for IFRA validation."""
    compliant: bool
    violations: list[dict]
    warnings: list[str]
    allergens_to_declare: list[dict]
    allergen_total: float
    max_allergen_limit: float
    summary: str


class EEGSimulationRequest(BaseModel):
    """Request for EEG simulation from text."""
    text_input: str = Field(..., min_length=3)
    quadrant: Optional[str] = Field(None, pattern="^(happy|excited|calm|sad)$")


class EEGSimulationResponse(BaseModel):
    """EEG simulation result."""
    valence: float
    arousal: float
    confidence: float
    emotion_label: str
    raw_alpha: float
    raw_beta: float
    raw_theta: float


class PHAnalysisResponse(BaseModel):
    """pH analysis result."""
    ph_value: float
    confidence: float
    color_detected: str
    method: str
    error: Optional[str] = None


class MolecularAnalysisRequest(BaseModel):
    """Request for molecular property analysis."""
    smiles: str = Field(..., min_length=1)


class MolecularAnalysisResponse(BaseModel):
    """Molecular property analysis result."""
    smiles: str
    valid: bool
    logp: Optional[float] = None
    molecular_weight: Optional[float] = None
    volatility_class: Optional[str] = None
    tpsa: Optional[float] = None
    error_message: Optional[str] = None


# ============== Endpoints ==============

@router.post("/generate", response_model=FormulaResponse)
async def generate_formula(request: FormulationRequest):
    """
    Generate a personalized perfume formula based on physiological profile.

    Uses AI-powered analysis combined with Physio-RAG corrections and
    RDKit molecular calculations for optimal personalization.
    """
    # Generate EEG-derived valence/arousal if not provided but prompt given
    emotional_profile = None
    if request.prompt and (request.valence is None or request.arousal is None):
        eeg_signal = eeg_simulator.simulate_from_text(request.prompt)
        valence = eeg_signal.valence
        arousal = eeg_signal.arousal
        emotional_profile = {
            "valence": valence,
            "arousal": arousal,
            "emotion_label": eeg_signal.emotion_label,
            "confidence": eeg_signal.confidence,
            "source": "text_simulation"
        }
    else:
        valence = request.valence or 0.3
        arousal = request.arousal or 0.5
        if request.valence is not None:
            emotional_profile = {
                "valence": valence,
                "arousal": arousal,
                "source": "user_provided"
            }

    # Try AI-powered generation first
    if settings.openai_api_key:
        try:
            result = await ai_analyzer.full_analysis(
                emotional_input=request.prompt or "A balanced, elegant fragrance",
                valence=valence,
                arousal=arousal,
                ph=request.ph_value,
                skin_type=request.skin_type.lower(),
                temperature=request.temperature
            )

            formula_data = result.get("formula", {})
            recommendation = result.get("recommendation", {})

            # Build ingredients with RDKit calculations
            ingredients = []
            for ing in formula_data.get("ingredients", []):
                name = ing.get("name", "Unknown")
                smiles = _find_smiles_for_ingredient(name)
                mol_props = get_full_properties(smiles) if smiles else None

                ingredients.append(Ingredient(
                    name=name,
                    smiles=smiles or "",
                    concentration=ing.get("percentage", 5.0),
                    note_type=ing.get("note_type", "middle"),
                    logp=mol_props.logp if mol_props and mol_props.logp else 0.0,
                    molecular_weight=mol_props.molecular_weight if mol_props else None,
                    is_sustainable=True,
                    source="natural",
                    sustainability_score=8
                ))

            # IFRA validation
            ifra_report = ifra_validator.validate_formula([
                {"name": i.name, "concentration": i.concentration}
                for i in ingredients
            ])

            # Calculate note pyramid
            note_pyramid = _calculate_note_pyramid(ingredients)

            return FormulaResponse(
                formula_id=str(uuid.uuid4()),
                name=formula_data.get("name", "Aether Custom"),
                description=formula_data.get("description", recommendation.get("mood_interpretation", "")),
                ingredients=ingredients,
                note_pyramid=note_pyramid,
                longevity_score=_estimate_longevity(ingredients),
                projection_score=_estimate_projection(ingredients),
                sustainability_score=formula_data.get("sustainability_score", 0.8) * 10,
                ifra_compliant=ifra_report.is_compliant,
                ifra_report={
                    "summary": ifra_report.summary,
                    "allergens_to_declare": ifra_report.allergens_to_declare,
                    "total_allergen_load": ifra_report.total_allergen_load
                },
                physio_corrections_applied=formula_data.get("physio_adjustments", []),
                emotional_profile=emotional_profile
            )

        except Exception:
            pass  # Fall through to local generation

    # Local generation using AetherAgent
    return _generate_local_formula(request, valence, arousal, emotional_profile)


def _generate_local_formula(
    request: FormulationRequest,
    valence: float,
    arousal: float,
    emotional_profile: Optional[dict]
) -> FormulaResponse:
    """Generate formula using local AetherAgent and Physio-RAG."""
    agent = create_agent(
        ph=request.ph_value,
        skin_type=request.skin_type.capitalize(),
        temperature=request.temperature,
        allergies=request.allergies or []
    )

    # Generate formula with local engine
    formula = agent.generate_formula(
        scent_preferences=_extract_preferences(request.prompt) if request.prompt else None,
        valence=valence,
        arousal=arousal
    )

    # Convert to response format with RDKit enrichment
    ingredients = []
    for fi in formula.ingredients:
        ing = fi.ingredient
        mol_props = get_full_properties(ing.smiles)

        ingredients.append(Ingredient(
            name=ing.name,
            smiles=ing.smiles,
            concentration=fi.concentration,
            note_type=ing.note_type,
            logp=mol_props.logp if mol_props.valid else ing.logp,
            molecular_weight=mol_props.molecular_weight if mol_props.valid else ing.molecular_weight,
            is_sustainable=ing.is_sustainable,
            source=ing.source,
            sustainability_score=ing.sustainability_score
        ))

    # IFRA validation
    ifra_report = ifra_validator.validate_formula([
        {"name": i.name, "concentration": i.concentration}
        for i in ingredients
    ])

    # Generate name based on emotional quadrant
    formula_name = _generate_formula_name(valence, arousal, request.prompt)

    return FormulaResponse(
        formula_id=formula.formula_id,
        name=formula_name,
        description=formula.description or "A personalized fragrance crafted for your unique chemistry.",
        ingredients=ingredients,
        note_pyramid=formula.note_pyramid,
        longevity_score=_estimate_longevity(ingredients),
        projection_score=_estimate_projection(ingredients),
        sustainability_score=formula.sustainability_score,
        ifra_compliant=ifra_report.is_compliant,
        ifra_report={
            "summary": ifra_report.summary,
            "allergens_to_declare": ifra_report.allergens_to_declare,
            "total_allergen_load": ifra_report.total_allergen_load
        },
        physio_corrections_applied=formula.corrections_applied,
        emotional_profile=emotional_profile
    )


@router.post("/validate", response_model=ValidationResponse)
async def validate_formula(request: ValidationRequest):
    """
    Validate a formula against IFRA safety standards.

    Uses the full IFRA 51st Amendment database for compliance checking.
    """
    ingredients_data = [
        {"name": ing.name, "concentration": ing.concentration}
        for ing in request.ingredients
    ]

    report = ifra_validator.validate_formula(
        ingredients_data,
        product_category=request.product_category
    )

    violations = [
        {
            "ingredient": v.ingredient_name,
            "type": v.violation_type,
            "current": v.current_concentration,
            "max_allowed": v.max_allowed,
            "severity": v.severity,
            "recommendation": v.recommendation
        }
        for v in report.violations
    ]

    warnings = [v["recommendation"] for v in violations if v["severity"] == "warning"]

    return ValidationResponse(
        compliant=report.is_compliant,
        violations=violations,
        warnings=warnings,
        allergens_to_declare=report.allergens_to_declare,
        allergen_total=report.total_allergen_load,
        max_allergen_limit=1.0,
        summary=report.summary
    )


@router.post("/eeg-simulate", response_model=EEGSimulationResponse)
async def simulate_eeg(request: EEGSimulationRequest):
    """
    Simulate EEG-derived valence-arousal from text input.

    For demo purposes - analyzes emotional content of text to generate
    plausible EEG-like valence/arousal scores.
    """
    if request.quadrant:
        signal = eeg_simulator.simulate_random(quadrant=request.quadrant)
    else:
        signal = eeg_simulator.simulate_from_text(request.text_input)

    return EEGSimulationResponse(
        valence=signal.valence,
        arousal=signal.arousal,
        confidence=signal.confidence,
        emotion_label=signal.emotion_label,
        raw_alpha=signal.raw_alpha,
        raw_beta=signal.raw_beta,
        raw_theta=signal.raw_theta
    )


@router.post("/ph-analyze", response_model=PHAnalysisResponse)
async def analyze_ph_image(file: UploadFile = File(...)):
    """
    Analyze pH test strip image to extract pH value.

    Accepts JPEG or PNG images of pH test strips.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await file.read()
    result = ph_analyzer.analyze_image(contents)

    return PHAnalysisResponse(
        ph_value=result.ph_value,
        confidence=result.confidence,
        color_detected=result.color_detected,
        method=result.method,
        error=result.error
    )


@router.get("/ph-simulate/{skin_type}", response_model=PHAnalysisResponse)
async def simulate_ph(skin_type: str):
    """
    Simulate pH reading based on skin type for demo purposes.

    Skin types: dry, normal, oily
    """
    if skin_type.lower() not in ["dry", "normal", "oily"]:
        raise HTTPException(status_code=400, detail="Skin type must be dry, normal, or oily")

    result = ph_analyzer.simulate_from_skin_type(skin_type)

    return PHAnalysisResponse(
        ph_value=result.ph_value,
        confidence=result.confidence,
        color_detected=result.color_detected,
        method=result.method,
        error=result.error
    )


@router.post("/molecular-analysis", response_model=MolecularAnalysisResponse)
async def analyze_molecule(request: MolecularAnalysisRequest):
    """
    Analyze molecular properties from SMILES string using RDKit.

    Returns LogP, molecular weight, volatility classification, and more.
    """
    props = get_full_properties(request.smiles)

    return MolecularAnalysisResponse(
        smiles=props.smiles,
        valid=props.valid,
        logp=props.logp,
        molecular_weight=props.molecular_weight,
        volatility_class=props.volatility_class,
        tpsa=props.tpsa,
        error_message=props.error_message
    )


@router.get("/ingredients")
async def list_ingredients(
    note_type: Optional[str] = None,
    sustainable_only: bool = False,
    family: Optional[str] = None
):
    """
    List available fragrance ingredients from database.

    Filters available: note_type (top/middle/base), sustainable_only, family
    """
    ingredients = ingredient_db.get_all()

    if note_type:
        ingredients = [i for i in ingredients if i.note_type == note_type.lower()]

    if sustainable_only:
        ingredients = [i for i in ingredients if i.is_sustainable]

    if family:
        ingredients = [i for i in ingredients if i.family.lower() == family.lower()]

    return [
        {
            "id": i.id,
            "name": i.name,
            "smiles": i.smiles,
            "note_type": i.note_type,
            "family": i.family,
            "logp": i.logp,
            "is_sustainable": i.is_sustainable,
            "source": i.source,
            "sustainability_score": i.sustainability_score,
            "descriptors": i.descriptors
        }
        for i in ingredients
    ]


# ============== Helper Functions ==============

def _find_smiles_for_ingredient(name: str) -> Optional[str]:
    """Find SMILES string for an ingredient by name."""
    name_lower = name.lower()
    for ing in ingredient_db.get_all():
        if ing.name.lower() in name_lower or name_lower in ing.name.lower():
            return ing.smiles
    return None


def _calculate_note_pyramid(ingredients: list[Ingredient]) -> dict:
    """Calculate note type proportions."""
    top_total = sum(i.concentration for i in ingredients if i.note_type == "top")
    mid_total = sum(i.concentration for i in ingredients if i.note_type in ["middle", "heart"])
    base_total = sum(i.concentration for i in ingredients if i.note_type == "base")
    total = top_total + mid_total + base_total or 1

    return {
        "top": round(100 * top_total / total, 1),
        "middle": round(100 * mid_total / total, 1),
        "base": round(100 * base_total / total, 1)
    }


def _estimate_longevity(ingredients: list[Ingredient]) -> float:
    """Estimate fragrance longevity based on ingredient properties."""
    if not ingredients:
        return 5.0

    # Higher LogP = better longevity
    avg_logp = sum(i.logp * i.concentration for i in ingredients) / sum(i.concentration for i in ingredients)
    base_score = 5.0 + (avg_logp - 2.5) * 1.5

    # More base notes = better longevity
    base_ratio = sum(i.concentration for i in ingredients if i.note_type == "base") / sum(i.concentration for i in ingredients)
    base_bonus = base_ratio * 3.0

    return min(10.0, max(1.0, base_score + base_bonus))


def _estimate_projection(ingredients: list[Ingredient]) -> float:
    """Estimate fragrance projection (sillage) based on ingredient properties."""
    if not ingredients:
        return 5.0

    # More top notes = better projection initially
    top_ratio = sum(i.concentration for i in ingredients if i.note_type == "top") / sum(i.concentration for i in ingredients)
    top_bonus = top_ratio * 4.0

    # Higher concentration = better projection
    total_conc = sum(i.concentration for i in ingredients)
    conc_factor = min(2.0, total_conc / 20.0)

    return min(10.0, max(1.0, 4.0 + top_bonus + conc_factor))


def _extract_preferences(prompt: str) -> list[str]:
    """Extract scent preferences from natural language prompt."""
    preferences = []
    keywords = {
        "fresh": ["fresh", "clean", "crisp"],
        "floral": ["flower", "floral", "rose", "jasmine", "lily"],
        "woody": ["wood", "woody", "cedar", "sandalwood", "forest"],
        "citrus": ["citrus", "lemon", "orange", "bergamot", "lime"],
        "sweet": ["sweet", "vanilla", "caramel", "honey"],
        "spicy": ["spicy", "pepper", "cinnamon", "warm"],
        "earthy": ["earth", "moss", "rain", "petrichor"]
    }

    prompt_lower = prompt.lower()
    for category, words in keywords.items():
        if any(word in prompt_lower for word in words):
            preferences.append(category)

    return preferences


def _generate_formula_name(valence: float, arousal: float, prompt: Optional[str]) -> str:
    """Generate poetic formula name based on emotional profile."""
    if prompt:
        prompt_lower = prompt.lower()
        if "morning" in prompt_lower or "fresh" in prompt_lower:
            return "Dawn Whisper"
        elif "night" in prompt_lower or "evening" in prompt_lower:
            return "Midnight Reverie"
        elif "rain" in prompt_lower or "petrichor" in prompt_lower:
            return "After the Rain"
        elif "garden" in prompt_lower or "flower" in prompt_lower:
            return "Secret Garden"
        elif "ocean" in prompt_lower or "sea" in prompt_lower:
            return "Ocean Drift"
        elif "forest" in prompt_lower or "wood" in prompt_lower:
            return "Forest Path"

    # Fallback to V-A quadrant names
    if valence >= 0:
        if arousal >= 0.5:
            return "Radiant Energy"
        else:
            return "Serene Bliss"
    else:
        if arousal >= 0.5:
            return "Bold Intensity"
        else:
            return "Deep Contemplation"
