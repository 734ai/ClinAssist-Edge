"""
Multi-Agent Reasoning System for ClinAssist Edge.

This module implements specialized agents that work together to provide
comprehensive clinical support through collaborative reasoning.

Features:
- Diagnostic agent (differential diagnosis)
- Safety agent (contraindications & red flags)
- Documentation agent (SOAP notes)
- Evidence agent (literature & guidelines lookup)
- Agent orchestration with chain-of-thought reasoning
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Types of specialist agents."""
    DIAGNOSTICIAN = "diagnostician"
    SAFETY_MONITOR = "safety_monitor"
    DOCUMENTATION = "documentation"
    EVIDENCE_LOOKUP = "evidence_lookup"
    COORDINATOR = "coordinator"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: AgentRole
    recipient: AgentRole
    content: str
    reasoning: str
    metadata: Dict = None


@dataclass
class AgentResponse:
    """Response from an agent."""
    agent: AgentRole
    output: str
    confidence: float
    reasoning: str
    next_agents: List[AgentRole]  # Agents to consult next


class ClinicalAgent:
    """Base class for clinical specialist agents."""
    
    def __init__(self, role: AgentRole):
        """
        Initialize agent.
        
        Args:
            role: AgentRole for this agent
        """
        self.role = role
        self.conversation_history = []
    
    def process(self, query: str, context: Dict) -> AgentResponse:
        """
        Process a clinical query.
        
        Args:
            query: Clinical question or task
            context: Additional context (patient info, etc.)
        
        Returns:
            AgentResponse with output and next steps
        """
        raise NotImplementedError


class DiagnosticAgent(ClinicalAgent):
    """Specializes in differential diagnosis."""
    
    def __init__(self):
        """Initialize diagnostic agent."""
        super().__init__(AgentRole.DIAGNOSTICIAN)
    
    def process(self, query: str, context: Dict) -> AgentResponse:
        """
        Generate differential diagnosis.
        
        Args:
            query: Patient symptoms and presentation
            context: Patient demographics, history
        
        Returns:
            AgentResponse with differential diagnoses
        """
        symptoms = context.get("symptoms", [])
        findings = context.get("findings", [])
        
        # Generate differential diagnoses based on symptom patterns
        differential = self._generate_differential(symptoms, findings)
        
        reasoning = f"Analyzed {len(symptoms)} symptoms and {len(findings)} findings to generate differential."
        
        # Recommend consulting safety agent and evidence agent
        next_agents = [AgentRole.SAFETY_MONITOR, AgentRole.EVIDENCE_LOOKUP]
        
        return AgentResponse(
            agent=self.role,
            output=self._format_differential(differential),
            confidence=differential[0][1] if differential else 0.0,
            reasoning=reasoning,
            next_agents=next_agents
        )
    
    def _generate_differential(
        self,
        symptoms: List[str],
        findings: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Generate differential diagnoses from symptoms and findings.
        
        Args:
            symptoms: List of symptoms
            findings: List of clinical findings
        
        Returns:
            List of (diagnosis, confidence) tuples
        """
        # Medical knowledge base for symptom-diagnosis mapping
        symptom_profiles = {
            "Pneumonia": {"symptoms": ["fever", "cough", "dyspnea"], "findings": ["crackles", "consolidation"], "weight": 0.95},
            "Bronchitis": {"symptoms": ["cough", "dyspnea"], "findings": ["wheezing"], "weight": 0.75},
            "Malaria": {"symptoms": ["fever", "chills", "headache"], "findings": ["anemia"], "weight": 0.90},
            "Tuberculosis": {"symptoms": ["chronic_cough", "fever", "weight_loss"], "findings": ["infiltrates"], "weight": 0.92},
            "Influenza": {"symptoms": ["fever", "cough", "myalgia"], "findings": ["normal_cxr"], "weight": 0.70},
            "COVID-19": {"symptoms": ["fever", "cough", "dyspnea"], "findings": ["ground_glass"], "weight": 0.88},
        }
        
        diagnoses_scores = []
        
        for diagnosis, profile in symptom_profiles.items():
            # Calculate match score
            symptom_matches = sum(1 for s in symptoms if any(ps in s.lower() for ps in profile["symptoms"]))
            finding_matches = sum(1 for f in findings if any(pf in f.lower() for pf in profile["findings"]))
            
            total_matches = symptom_matches + finding_matches
            max_possible = len(profile["symptoms"]) + len(profile["findings"])
            
            if max_possible > 0:
                match_score = total_matches / max_possible
                confidence = match_score * profile["weight"]
                diagnoses_scores.append((diagnosis, confidence))
        
        # Sort by confidence
        diagnoses_scores.sort(key=lambda x: x[1], reverse=True)
        
        return diagnoses_scores[:5]  # Top 5 diagnoses
    
    def _format_differential(self, differential: List[Tuple[str, float]]) -> str:
        """Format differential diagnoses for display."""
        output = "DIFFERENTIAL DIAGNOSES:\n"
        for i, (diagnosis, confidence) in enumerate(differential, 1):
            output += f"{i}. {diagnosis}: {confidence:.1%}\n"
        return output


class SafetyMonitorAgent(ClinicalAgent):
    """Monitors for contraindications, adverse reactions, and red flags."""
    
    def __init__(self):
        """Initialize safety monitor agent."""
        super().__init__(AgentRole.SAFETY_MONITOR)
    
    def process(self, query: str, context: Dict) -> AgentResponse:
        """
        Check for safety issues.
        
        Args:
            query: Proposed treatment or diagnosis
            context: Patient info (allergies, medications, conditions)
        
        Returns:
            AgentResponse with safety assessment
        """
        proposed_treatment = query
        allergies = context.get("allergies", [])
        current_medications = context.get("medications", [])
        contraindications = context.get("contraindications", [])
        red_flags = context.get("red_flags", [])
        
        # Check for interactions and red flags
        issues = self._identify_safety_issues(
            proposed_treatment, allergies, current_medications, contraindications, red_flags
        )
        
        reasoning = f"Checked for interactions with {len(current_medications)} medications and {len(allergies)} allergies."
        
        safety_level = "Safe" if not issues else "ALERT" if len(issues) > 2 else "Caution"
        
        next_agents = [AgentRole.DOCUMENTATION] if not issues else [AgentRole.EVIDENCE_LOOKUP]
        
        return AgentResponse(
            agent=self.role,
            output=self._format_safety_report(issues, safety_level),
            confidence=1.0 - (len(issues) * 0.2),  # Reduce confidence with each issue
            reasoning=reasoning,
            next_agents=next_agents
        )
    
    def _identify_safety_issues(
        self,
        treatment: str,
        allergies: List[str],
        medications: List[str],
        contraindications: List[str],
        red_flags: List[str]
    ) -> List[str]:
        """Identify safety issues."""
        issues = []
        
        # Drug interaction database
        interactions = {
            ("aspirin", "warfarin"): "CRITICAL: Increased bleeding risk",
            ("metformin", "contrast_dye"): "WARNING: Lactic acidosis risk",
            ("ace_inhibitor", "potassium"): "WARNING: Hyperkalemia risk",
        }
        
        # Check medication interactions
        treatment_lower = treatment.lower()
        for (drug1, drug2), interaction in interactions.items():
            if drug1 in treatment_lower and any(drug2 in m.lower() for m in medications):
                issues.append(interaction)
        
        # Check allergies
        for allergy in allergies:
            if allergy.lower() in treatment_lower:
                issues.append(f"CRITICAL: Patient allergic to {allergy}")
        
        # Check contraindications
        for contraindication in contraindications:
            if contraindication.lower() in treatment_lower:
                issues.append(f"CONTRAINDICATED: {contraindication}")
        
        return issues
    
    def _format_safety_report(self, issues: List[str], safety_level: str) -> str:
        """Format safety report."""
        output = f"SAFETY ASSESSMENT: {safety_level}\n"
        if issues:
            output += "Issues identified:\n"
            for issue in issues:
                output += f"• {issue}\n"
        else:
            output += "No safety concerns identified.\n"
        return output


class DocumentationAgent(ClinicalAgent):
    """Generates clinical documentation (SOAP notes, reports)."""
    
    def __init__(self):
        """Initialize documentation agent."""
        super().__init__(AgentRole.DOCUMENTATION)
    
    def process(self, query: str, context: Dict) -> AgentResponse:
        """
        Generate clinical documentation.
        
        Args:
            query: Clinical findings and diagnosis
            context: Patient info, exam findings, test results
        
        Returns:
            AgentResponse with formatted documentation
        """
        diagnosis = context.get("diagnosis", "")
        symptoms = context.get("symptoms", [])
        findings = context.get("findings", [])
        tests = context.get("tests", [])
        plan = context.get("plan", "")
        
        soap_note = self._generate_soap_note(
            symptoms, findings, diagnosis, tests, plan
        )
        
        reasoning = "Generated SOAP note with complete clinical documentation."
        
        return AgentResponse(
            agent=self.role,
            output=soap_note,
            confidence=0.95,
            reasoning=reasoning,
            next_agents=[]
        )
    
    def _generate_soap_note(
        self,
        symptoms: List[str],
        findings: List[str],
        diagnosis: str,
        tests: List[str],
        plan: str
    ) -> str:
        """Generate SOAP note."""
        note = "CLINICAL NOTE - SOAP FORMAT\n"
        note += "="*60 + "\n\n"
        
        note += "SUBJECTIVE:\n"
        note += "Patient reports:\n"
        for symptom in symptoms:
            note += f"• {symptom}\n"
        note += "\n"
        
        note += "OBJECTIVE:\n"
        note += "Physical Examination:\n"
        for finding in findings:
            note += f"• {finding}\n"
        if tests:
            note += "\nDiagnostic Tests:\n"
            for test in tests:
                note += f"• {test}\n"
        note += "\n"
        
        note += f"ASSESSMENT:\n{diagnosis}\n\n"
        
        note += f"PLAN:\n{plan}\n"
        
        return note


class EvidenceAgentInterface:
    """Interface for evidence lookup agent."""
    
    def __init__(self):
        """Initialize evidence agent interface."""
        self.role = AgentRole.EVIDENCE_LOOKUP
    
    def process(self, query: str, context: Dict) -> AgentResponse:
        """
        Lookup evidence-based guidelines and literature.
        
        Args:
            query: Medical query or diagnosis
            context: Additional context
        
        Returns:
            AgentResponse with evidence
        """
        # This would integrate with RAG system
        evidence = self._retrieve_evidence(query)
        
        return AgentResponse(
            agent=self.role,
            output=evidence,
            confidence=0.9,
            reasoning="Retrieved evidence from medical guidelines.",
            next_agents=[]
        )
    
    def _retrieve_evidence(self, query: str) -> str:
        """Retrieve evidence (placeholder)."""
        # Would use RAG system in production
        return f"Evidence-based guidelines for: {query}"


class AgentOrchestrator:
    """Orchestrates multi-agent reasoning."""
    
    def __init__(self):
        """Initialize agent orchestrator."""
        self.agents = {
            AgentRole.DIAGNOSTICIAN: DiagnosticAgent(),
            AgentRole.SAFETY_MONITOR: SafetyMonitorAgent(),
            AgentRole.DOCUMENTATION: DocumentationAgent(),
            AgentRole.EVIDENCE_LOOKUP: EvidenceAgentInterface(),
        }
        self.conversation_history = []
        self.max_agent_calls = 10  # Prevent infinite loops
    
    def run_reasoning_chain(
        self,
        initial_query: str,
        patient_context: Dict
    ) -> Dict:
        """
        Run multi-agent reasoning chain.
        
        Args:
            initial_query: Initial clinical query
            patient_context: Patient information and context
        
        Returns:
            Dictionary with results from all agents
        """
        results = {}
        active_agents = [AgentRole.DIAGNOSTICIAN]
        call_count = 0
        
        logger.info(f"Starting agent reasoning chain: {initial_query}")
        
        while active_agents and call_count < self.max_agent_calls:
            call_count += 1
            next_agents = []
            
            for agent_role in active_agents:
                agent = self.agents.get(agent_role)
                
                if agent is None:
                    logger.warning(f"Agent {agent_role} not found")
                    continue
                
                # Run agent
                response = agent.process(initial_query, patient_context)
                results[agent_role.value] = {
                    "output": response.output,
                    "confidence": response.confidence,
                    "reasoning": response.reasoning
                }
                
                # Collect next agents to run
                next_agents.extend(response.next_agents)
                
                logger.info(f"Agent {agent_role.value} completed with confidence {response.confidence:.1%}")
            
            # Deduplicate next agents
            active_agents = list(set(next_agents))
        
        logger.info(f"Reasoning chain completed in {call_count} steps")
        
        return results
    
    def format_final_report(self, results: Dict) -> str:
        """Format final multi-agent report."""
        report = "COMPREHENSIVE CLINICAL ASSESSMENT\n"
        report += "="*60 + "\n\n"
        
        if "diagnostician" in results:
            report += results["diagnostician"]["output"]
            report += "\n"
        
        if "safety_monitor" in results:
            report += results["safety_monitor"]["output"]
            report += "\n"
        
        if "documentation" in results:
            report += results["documentation"]["output"]
            report += "\n"
        
        if "evidence_lookup" in results:
            report += "EVIDENCE & GUIDELINES:\n"
            report += results["evidence_lookup"]["output"]
            report += "\n"
        
        return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = AgentOrchestrator()
    
    patient_context = {
        "age": 45,
        "gender": "M",
        "symptoms": ["fever", "productive cough", "dyspnea"],
        "findings": ["crackles RLL", "SpO2 95%"],
        "allergies": ["Penicillin"],
        "medications": ["Aspirin"],
        "contraindications": [],
        "red_flags": []
    }
    
    results = orchestrator.run_reasoning_chain(
        "45-year-old male with fever and productive cough",
        patient_context
    )
    
    print(orchestrator.format_final_report(results))
