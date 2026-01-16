"""
IFRA Compliance Validator.
Validates fragrance formulas against IFRA 51st Amendment standards.
"""

import json
from dataclasses import dataclass
from typing import Optional

from app.config import settings


@dataclass
class IFRAViolation:
    """A single IFRA compliance violation."""
    ingredient_name: str
    cas_number: Optional[str]
    violation_type: str  # "banned", "over_limit", "allergen_declaration"
    current_concentration: float
    max_allowed: float
    severity: str  # "critical", "warning", "info"
    recommendation: str


@dataclass
class IFRAReport:
    """Complete IFRA compliance report for a formula."""
    is_compliant: bool
    violations: list[IFRAViolation]
    allergens_to_declare: list[dict]
    total_allergen_load: float
    product_category: str
    summary: str


class IFRAValidator:
    """
    Validates fragrance formulas against IFRA standards.

    Checks:
    1. Banned substances (zero tolerance)
    2. Restricted substances (max concentration limits)
    3. Allergen declaration requirements
    4. Phototoxicity limits for citrus oils
    5. Total allergen load
    """

    def __init__(self):
        self._standards: dict = {}
        self._loaded = False

    def _load_standards(self):
        """Load IFRA standards from JSON."""
        if self._loaded:
            return

        standards_path = settings.data_dir / "ifra_standards.json"

        if not standards_path.exists():
            self._standards = {"restricted_substances": [], "allergens_declaration_required": [], "phototoxicity_limits": []}
            self._loaded = True
            return

        with open(standards_path, 'r', encoding='utf-8') as f:
            self._standards = json.load(f)

        self._loaded = True

    def validate_formula(
        self,
        ingredients: list[dict],
        product_category: str = "cat1"
    ) -> IFRAReport:
        """
        Validate a formula against IFRA standards.

        Args:
            ingredients: List of dicts with 'name', 'concentration', optional 'cas'
            product_category: "cat1" (leave-on) or "cat2" (rinse-off)

        Returns:
            IFRAReport with compliance status and any violations
        """
        self._load_standards()

        violations = []
        allergens_to_declare = []
        total_allergen_load = 0.0

        # Build lookup maps
        restricted_map = {s['name'].lower(): s for s in self._standards.get('restricted_substances', [])}
        allergen_map = {a['name'].lower(): a for a in self._standards.get('allergens_declaration_required', [])}
        phototox_map = {p['name'].lower(): p for p in self._standards.get('phototoxicity_limits', [])}

        # Check each ingredient
        for ing in ingredients:
            name = ing.get('name', '')
            name_lower = name.lower()
            concentration = ing.get('concentration', 0)
            cas = ing.get('cas')

            # Check restricted substances
            if name_lower in restricted_map:
                restricted = restricted_map[name_lower]
                max_conc = restricted.get('max_concentration_cat1', 0)

                if max_conc == 0:
                    # Banned substance
                    violations.append(IFRAViolation(
                        ingredient_name=name,
                        cas_number=restricted.get('cas'),
                        violation_type="banned",
                        current_concentration=concentration,
                        max_allowed=0,
                        severity="critical",
                        recommendation=f"Remove {name} - banned under IFRA. {restricted.get('reason', '')}"
                    ))
                elif concentration > max_conc:
                    # Over limit
                    violations.append(IFRAViolation(
                        ingredient_name=name,
                        cas_number=restricted.get('cas'),
                        violation_type="over_limit",
                        current_concentration=concentration,
                        max_allowed=max_conc,
                        severity="critical",
                        recommendation=f"Reduce {name} to max {max_conc}%. {restricted.get('reason', '')}"
                    ))

            # Check phototoxicity limits
            for phototox_name, phototox in phototox_map.items():
                if phototox_name in name_lower or name_lower in phototox_name:
                    max_conc = phototox.get('max_concentration_cat1', 100)
                    if concentration > max_conc:
                        violations.append(IFRAViolation(
                            ingredient_name=name,
                            cas_number=None,
                            violation_type="phototoxicity",
                            current_concentration=concentration,
                            max_allowed=max_conc,
                            severity="critical",
                            recommendation=f"Reduce {name} to max {max_conc}% for phototoxicity. {phototox.get('reason', '')}"
                        ))

            # Check allergen declaration
            for allergen_name, allergen in allergen_map.items():
                if allergen_name in name_lower or name_lower in allergen_name:
                    threshold = allergen.get('threshold_cat1', 0.001)

                    # Check if banned
                    if threshold == 0:
                        violations.append(IFRAViolation(
                            ingredient_name=name,
                            cas_number=allergen.get('cas'),
                            violation_type="banned",
                            current_concentration=concentration,
                            max_allowed=0,
                            severity="critical",
                            recommendation=f"Remove {name} - banned allergen"
                        ))
                    elif concentration >= threshold:
                        # Must be declared
                        allergens_to_declare.append({
                            "name": name,
                            "cas": allergen.get('cas'),
                            "concentration": concentration,
                            "threshold": threshold
                        })
                        total_allergen_load += concentration

        # Check total allergen load
        allergen_limits = self._standards.get('total_allergen_limits', {}).get('cat1_leave_on', {})
        max_total = allergen_limits.get('max_total_percentage', 1.0)

        if total_allergen_load > max_total:
            violations.append(IFRAViolation(
                ingredient_name="Total Allergens",
                cas_number=None,
                violation_type="allergen_load",
                current_concentration=total_allergen_load,
                max_allowed=max_total,
                severity="warning",
                recommendation=f"Total allergen load {total_allergen_load:.2f}% exceeds {max_total}% recommendation"
            ))

        # Determine compliance
        critical_violations = [v for v in violations if v.severity == "critical"]
        is_compliant = len(critical_violations) == 0

        # Generate summary
        if is_compliant and not violations:
            summary = "Formula is fully IFRA compliant with no issues detected."
        elif is_compliant:
            summary = f"Formula is compliant with {len(violations)} warning(s). {len(allergens_to_declare)} allergen(s) require declaration."
        else:
            summary = f"Formula has {len(critical_violations)} critical violation(s) that must be resolved for IFRA compliance."

        return IFRAReport(
            is_compliant=is_compliant,
            violations=violations,
            allergens_to_declare=allergens_to_declare,
            total_allergen_load=total_allergen_load,
            product_category=product_category,
            summary=summary
        )

    def get_max_concentration(self, ingredient_name: str, product_category: str = "cat1") -> Optional[float]:
        """
        Get maximum allowed concentration for an ingredient.

        Args:
            ingredient_name: Name of the ingredient
            product_category: "cat1" or "cat2"

        Returns:
            Max concentration percentage, or None if not restricted
        """
        self._load_standards()

        name_lower = ingredient_name.lower()

        # Check restricted substances
        for restricted in self._standards.get('restricted_substances', []):
            if restricted['name'].lower() == name_lower:
                return restricted.get('max_concentration_cat1', None)

        # Check phototoxicity limits
        for phototox in self._standards.get('phototoxicity_limits', []):
            if phototox['name'].lower() in name_lower:
                return phototox.get('max_concentration_cat1', None)

        return None  # Not restricted

    def is_allergen(self, ingredient_name: str) -> bool:
        """Check if an ingredient is a declared allergen."""
        self._load_standards()

        name_lower = ingredient_name.lower()

        for allergen in self._standards.get('allergens_declaration_required', []):
            if allergen['name'].lower() in name_lower or name_lower in allergen['name'].lower():
                return True

        return False


# Singleton instance
ifra_validator = IFRAValidator()
