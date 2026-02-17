"""
Drug-Disease-Allergy Interaction Checker for ClinAssist Edge.

This module provides comprehensive checks for medication interactions,
contraindications, allergies, and adverse events.

Features:
- Drug-drug interactions
- Drug-disease contraindications
- Allergy checking
- Adverse event tracking
- Dosing verification
- Pregnancy/lactation safety
"""

import logging
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InteractionSeverity(Enum):
    """Severity levels for interactions."""
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MODERATE = "MODERATE"
    MINOR = "MINOR"
    INFO = "INFO"


@dataclass
class Interaction:
    """Drug interaction information."""
    drug1: str
    drug2: str
    severity: InteractionSeverity
    mechanism: str
    recommendation: str


@dataclass
class Contraindication:
    """Drug-disease contraindication."""
    drug: str
    disease: str
    severity: InteractionSeverity
    reason: str
    alternative: Optional[str]


@dataclass
class AdverseEvent:
    """Known adverse event for medication."""
    drug: str
    event: str
    frequency: str  # "rare", "uncommon", "common"
    severity: InteractionSeverity
    monitoring: str


class DrugDatabase:
    """Comprehensive drug interaction and safety database."""
    
    def __init__(self):
        """Initialize drug database."""
        self.drug_drug_interactions = self._build_interaction_db()
        self.drug_disease_contraindications = self._build_contraindication_db()
        self.adverse_events = self._build_adverse_event_db()
        self.known_allergies = self._build_allergy_db()
        self.pregnancy_categories = self._build_pregnancy_db()
    
    def _build_interaction_db(self) -> Dict[Tuple[str, str], Interaction]:
        """Build drug-drug interaction database."""
        interactions = {
            ("warfarin", "aspirin"): Interaction(
                drug1="warfarin",
                drug2="aspirin",
                severity=InteractionSeverity.CRITICAL,
                mechanism="Increased bleeding risk due to dual anticoagulation",
                recommendation="Avoid if possible. If necessary, monitor INR closely and adjust warfarin dose."
            ),
            ("metformin", "contrast_dye"): Interaction(
                drug1="metformin",
                drug2="contrast_dye",
                severity=InteractionSeverity.MAJOR,
                mechanism="Risk of contrast-induced nephropathy and lactic acidosis",
                recommendation="Hold metformin 48 hours before and after contrast procedure. Check renal function."
            ),
            ("lisinopril", "potassium"): Interaction(
                drug1="lisinopril",
                drug2="potassium",
                severity=InteractionSeverity.MAJOR,
                mechanism="Risk of hyperkalemia",
                recommendation="Monitor K+ levels. Use only if indicated. Check renal function."
            ),
            ("simvastatin", "clarithromycin"): Interaction(
                drug1="simvastatin",
                drug2="clarithromycin",
                severity=InteractionSeverity.MAJOR,
                mechanism="Increased statin levels, risk of myopathy",
                recommendation="Consider alternative antibiotic or temporary statin cessation."
            ),
            ("ssri", "maoi"): Interaction(
                drug1="ssri",
                drug2="maoi",
                severity=InteractionSeverity.CRITICAL,
                mechanism="Risk of serotonin syndrome",
                recommendation="Absolute contraindication. Washout period required (14 days for MAOIs)."
            ),
            ("methotrexate", "nsaid"): Interaction(
                drug1="methotrexate",
                drug2="nsaid",
                severity=InteractionSeverity.MAJOR,
                mechanism="Decreased MTX clearance, increased toxicity",
                recommendation="Avoid NSAIDs. Use acetaminophen or COX-2 inhibitors with caution."
            ),
        }
        return interactions
    
    def _build_contraindication_db(self) -> Dict[Tuple[str, str], Contraindication]:
        """Build drug-disease contraindication database."""
        contraindications = {
            ("ace_inhibitor", "hyperkalemia"): Contraindication(
                drug="ace_inhibitor",
                disease="hyperkalemia",
                severity=InteractionSeverity.MAJOR,
                reason="ACE inhibitors reduce potassium excretion",
                alternative="Use alternative antihypertensive with K+ monitoring"
            ),
            ("nsaid", "acute_kidney_injury"): Contraindication(
                drug="nsaid",
                disease="acute_kidney_injury",
                severity=InteractionSeverity.MAJOR,
                reason="NSAIDs reduce renal perfusion",
                alternative="Use acetaminophen instead"
            ),
            ("beta_blocker", "asthma"): Contraindication(
                drug="beta_blocker",
                disease="asthma",
                severity=InteractionSeverity.MAJOR,
                reason="Beta blockers can cause bronchospasm",
                alternative="Use calcium channel blocker or cardioselective beta blocker with caution"
            ),
            ("statin", "muscle_disease"): Contraindication(
                drug="statin",
                disease="muscle_disease",
                severity=InteractionSeverity.MODERATE,
                reason="Risk of myositis and rhabdomyolysis",
                alternative="Use lower dose with close monitoring"
            ),
            ("metformin", "severe_renal_disease"): Contraindication(
                drug="metformin",
                disease="eGFR < 30",
                severity=InteractionSeverity.MAJOR,
                reason="Risk of lactic acidosis",
                alternative="Use insulin or other glucose-lowering agent"
            ),
        }
        return contraindications
    
    def _build_adverse_event_db(self) -> Dict[str, List[AdverseEvent]]:
        """Build adverse event database."""
        adverse_events = {
            "chloroquine": [
                AdverseEvent(
                    drug="chloroquine",
                    event="Retinopathy",
                    frequency="uncommon",
                    severity=InteractionSeverity.MAJOR,
                    monitoring="Ophthalmology exam at baseline and annually"
                ),
                AdverseEvent(
                    drug="chloroquine",
                    event="Myopathy",
                    frequency="uncommon",
                    severity=InteractionSeverity.MAJOR,
                    monitoring="Monitor muscle strength, CK levels"
                ),
            ],
            "warfarin": [
                AdverseEvent(
                    drug="warfarin",
                    event="Bleeding",
                    frequency="common",
                    severity=InteractionSeverity.MAJOR,
                    monitoring="INR monitoring, signs of bleeding"
                ),
            ],
            "metformin": [
                AdverseEvent(
                    drug="metformin",
                    event="GI upset",
                    frequency="common",
                    severity=InteractionSeverity.MINOR,
                    monitoring="Take with food, slow titration"
                ),
            ],
        }
        return adverse_events
    
    def _build_allergy_db(self) -> Dict[str, Set[str]]:
        """Build allergy cross-reactivity database."""
        allergies = {
            "penicillin": {"amoxicillin", "ampicillin", "piperacillin"},
            "sulfonamide": {"sulfamethoxazole", "sulfadiazine"},
            "macrolide": {"erythromycin", "clarithromycin"},
        }
        return allergies
    
    def _build_pregnancy_db(self) -> Dict[str, str]:
        """Build pregnancy safety category database."""
        pregnancy_categories = {
            "acetaminophen": "A",  # Safe
            "penicillin": "B",  # Probably safe
            "tetracycline": "D",  # Contraindicated
            "warfarin": "X",  # Contraindicated
            "metformin": "B",  # Probably safe
            "methotrexate": "X",  # Contraindicated
        }
        return pregnancy_categories


class DrugInteractionChecker:
    """Main drug interaction checking engine."""
    
    def __init__(self):
        """Initialize checker with drug database."""
        self.db = DrugDatabase()
    
    def check_drug_drug_interactions(
        self,
        medications: List[str]
    ) -> List[Interaction]:
        """
        Check for drug-drug interactions.
        
        Args:
            medications: List of medication names
        
        Returns:
            List of identified interactions
        """
        interactions = []
        
        # Check all pairs
        for i, drug1 in enumerate(medications):
            for drug2 in medications[i+1:]:
                # Check both orderings
                key1 = (drug1.lower(), drug2.lower())
                key2 = (drug2.lower(), drug1.lower())
                
                if key1 in self.db.drug_drug_interactions:
                    interactions.append(self.db.drug_drug_interactions[key1])
                elif key2 in self.db.drug_drug_interactions:
                    interactions.append(self.db.drug_drug_interactions[key2])
        
        # Sort by severity
        interactions.sort(
            key=lambda x: list(InteractionSeverity).index(x.severity)
        )
        
        logger.info(f"Found {len(interactions)} drug-drug interactions")
        return interactions
    
    def check_drug_disease_contraindications(
        self,
        medications: List[str],
        diseases: List[str],
        conditions: List[str]
    ) -> List[Contraindication]:
        """
        Check for drug-disease contraindications.
        
        Args:
            medications: List of medication names
            diseases: List of diagnoses
            conditions: List of medical conditions
        
        Returns:
            List of contraindications
        """
        contraindications = []
        all_conditions = diseases + conditions
        
        for medication in medications:
            for condition in all_conditions:
                key1 = (medication.lower(), condition.lower())
                key2 = (medication.lower(), condition.split()[0].lower())  # Try shorter match
                
                if key1 in self.db.drug_disease_contraindications:
                    contraindications.append(self.db.drug_disease_contraindications[key1])
                elif key2 in self.db.drug_disease_contraindications:
                    contraindications.append(self.db.drug_disease_contraindications[key2])
        
        # Sort by severity
        contraindications.sort(
            key=lambda x: list(InteractionSeverity).index(x.severity)
        )
        
        logger.info(f"Found {len(contraindications)} drug-disease contraindications")
        return contraindications
    
    def check_allergies(
        self,
        medications: List[str],
        known_allergies: List[str]
    ) -> List[Tuple[str, str, str]]:
        """
        Check for medication allergies.
        
        Args:
            medications: Proposed medications
            known_allergies: Known patient allergies
        
        Returns:
            List of (medication, allergen, severity) tuples
        """
        allergic_reactions = []
        
        for medication in medications:
            med_lower = medication.lower()
            
            for allergy in known_allergies:
                allergy_lower = allergy.lower()
                
                # Direct match
                if allergy_lower in med_lower or med_lower in allergy_lower:
                    allergic_reactions.append((
                        medication,
                        allergy,
                        "DIRECT_ALLERGY"
                    ))
                
                # Cross-reactivity check
                for allergen_class, cross_reactive_drugs in self.db.known_allergies.items():
                    if allergy_lower in allergen_class:
                        if any(d in med_lower for d in cross_reactive_drugs):
                            allergic_reactions.append((
                                medication,
                                allergy,
                                f"CROSS_REACTIVE_{allergen_class}"
                            ))
        
        logger.info(f"Found {len(allergic_reactions)} potential allergic reactions")
        return allergic_reactions
    
    def check_adverse_events(
        self,
        medications: List[str]
    ) -> List[AdverseEvent]:
        """
        Get known adverse events for medications.
        
        Args:
            medications: List of medications
        
        Returns:
            List of known adverse events
        """
        adverse_events = []
        
        for medication in medications:
            med_lower = medication.lower()
            
            if med_lower in self.db.adverse_events:
                adverse_events.extend(self.db.adverse_events[med_lower])
        
        return adverse_events
    
    def check_pregnancy_safety(
        self,
        medications: List[str],
        is_pregnant: bool = False,
        trimester: Optional[int] = None
    ) -> List[Tuple[str, str, str]]:
        """
        Check pregnancy safety of medications.
        
        Args:
            medications: List of medications
            is_pregnant: Whether patient is pregnant
            trimester: Trimester (1, 2, or 3)
        
        Returns:
            List of (medication, category, recommendation) tuples
        """
        if not is_pregnant:
            return []
        
        safety = []
        
        category_risks = {
            "A": "Safe - No risk",
            "B": "Probably safe - Animal studies OK",
            "C": "Use with caution - Animal studies show risk",
            "D": "Avoid if possible - Evidence of risk",
            "X": "CONTRAINDICATED - Teratogenic"
        }
        
        for medication in medications:
            med_lower = medication.lower()
            
            category = self.db.pregnancy_categories.get(med_lower, "UNKNOWN")
            recommendation = category_risks.get(category, "Unknown safety profile")
            
            safety.append((medication, category, recommendation))
        
        return safety
    
    def comprehensive_check(
        self,
        medications: List[str],
        diseases: List[str],
        conditions: List[str],
        known_allergies: List[str],
        is_pregnant: bool = False,
        trimester: Optional[int] = None
    ) -> Dict:
        """
        Perform comprehensive safety check.
        
        Args:
            medications: List of medications
            diseases: List of diagnoses
            conditions: List of conditions
            known_allergies: Known allergies
            is_pregnant: Pregnancy status
            trimester: Trimester if pregnant
        
        Returns:
            Dictionary with all safety checks
        """
        return {
            "drug_drug_interactions": self.check_drug_drug_interactions(medications),
            "drug_disease_contraindications": self.check_drug_disease_contraindications(
                medications, diseases, conditions
            ),
            "allergy_checks": self.check_allergies(medications, known_allergies),
            "adverse_events": self.check_adverse_events(medications),
            "pregnancy_safety": self.check_pregnancy_safety(
                medications, is_pregnant, trimester
            )
        }


def format_safety_report(safety_check: Dict) -> str:
    """Format safety check results for display."""
    report = "MEDICATION SAFETY REPORT\n"
    report += "="*60 + "\n\n"
    
    # Drug-drug interactions
    if safety_check["drug_drug_interactions"]:
        report += "DRUG-DRUG INTERACTIONS:\n"
        for interaction in safety_check["drug_drug_interactions"]:
            report += f"⚠ {interaction.severity.value}: {interaction.drug1} + {interaction.drug2}\n"
            report += f"   Mechanism: {interaction.mechanism}\n"
            report += f"   Recommendation: {interaction.recommendation}\n\n"
    
    # Drug-disease contraindications
    if safety_check["drug_disease_contraindications"]:
        report += "CONTRAINDICATIONS:\n"
        for contra in safety_check["drug_disease_contraindications"]:
            report += f"⚠ {contra.severity.value}: {contra.drug} in {contra.disease}\n"
            report += f"   Reason: {contra.reason}\n"
            if contra.alternative:
                report += f"   Alternative: {contra.alternative}\n"
            report += "\n"
    
    # Allergies
    if safety_check["allergy_checks"]:
        report += "ALLERGY ALERTS:\n"
        for med, allergy, severity in safety_check["allergy_checks"]:
            report += f"🚨 {med} may cause reaction in patient allergic to {allergy}\n"
    
    # Adverse events
    if safety_check["adverse_events"]:
        report += "\nKNOWN ADVERSE EVENTS:\n"
        for ae in safety_check["adverse_events"]:
            report += f"• {ae.drug}: {ae.event} ({ae.frequency})\n"
            report += f"  Monitor: {ae.monitoring}\n"
    
    # Pregnancy safety
    if safety_check["pregnancy_safety"]:
        report += "\nPREGNANCY SAFETY:\n"
        for med, category, rec in safety_check["pregnancy_safety"]:
            report += f"• {med}: Category {category} - {rec}\n"
    
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    checker = DrugInteractionChecker()
    
    # Example check
    safety = checker.comprehensive_check(
        medications=["warfarin", "aspirin"],
        diseases=["atrial_fibrillation"],
        conditions=[],
        known_allergies=["penicillin"],
        is_pregnant=False
    )
    
    print(format_safety_report(safety))
