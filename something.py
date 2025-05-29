#!/usr/bin/env python3
"""
AI Agent Hackathon - Healthcare Treatment Analysis System
Fixed implementation using AWS Strands SDK
"""

import os
import json
import logging
import boto3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from dataclasses import dataclass

# Strands imports
from strands import Agent, tool
from strands.models import BedrockModel

# Additional imports for file handling
import PyPDF2
import docx
from bs4 import BeautifulSoup
import mammoth
import pandas as pd

# Configure logging
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

@dataclass
class TreatmentData:
    """Data structure for treatment information"""
    treatment_id: str
    source: str
    raw_content: str
    structured_content: str = ""
    risk_assessment: str = ""
    revenue_analysis: str = ""

@dataclass
class ProcessingResults:
    """Container for all processing results"""
    treatments: List[TreatmentData]
    final_report: str = ""
    approval_status: str = "pending"

class HealthcareAgentSystem:
    """Main system orchestrator for the healthcare agent hackathon"""
    
    def __init__(self):
        # Initialize AWS Bedrock session
        self.session = boto3.Session(
            aws_access_key_id='ASIAUFJ05VRONEJHNEP7',
            aws_secret_access_key='5FNHUatrDaqx97YKRAVPZ0a2gFgCUW3217RFN9MV',
            aws_session_token='IQ0Jb3JpZ2lux2VjEMn//////////wEaCXVZLWVhc3QtMSJGMEQCIG1TUFYEK5bxNkvX036wTbnjAEJCXOUF1v2X450pBfJYAIA14t61Qitsis4jN1SBPIWNIWZ6NHn6',
            region_name='us-west-2'
        )
        
        # Create Bedrock model
        self.bedrock_model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            boto_session=self.session
        )
        
        # Initialize agents
        self.research_agent = None
        self.documenting_agent = None
        self.risk_assessment_agent = None
        self.revenue_identification_agent = None
        self.emailing_agent = None
        
        # Initialize data storage
        self.processing_results = ProcessingResults(treatments=[])
        
        # Setup output directory
        self.output_dir = Path("./hackathon_output")
        self.output_dir.mkdir(exist_ok=True)
        
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        # Research Agent - data collection
        self.research_agent = Agent(
            model=self.bedrock_model,
            system_prompt="You are a research agent specialized in extracting healthcare treatment information from various sources. Your task is to carefully analyze documents and extract relevant treatment details.",
            tools=[
                self._create_file_reader_tool(),
                self._create_html_parser_tool(),
                self._create_pdf_parser_tool(),
                self._create_docx_parser_tool()
            ]
        )
        
        # Documenting Agent - data organization
        self.documenting_agent = Agent(
            model=self.bedrock_model,
            system_prompt="You are a documenting agent that structures raw treatment data into organized formats. Create clear, standardized documents from extracted information.",
            tools=[
                self._create_document_structuring_tool(),
                self._create_report_generator_tool()
            ]
        )
        
        # Risk Assessment Agent - medical analysis
        self.risk_assessment_agent = Agent(
            model=self.bedrock_model,
            system_prompt="You are a medical risk assessment agent. Analyze treatments for potential risks and provide professional assessments.",
            tools=[
                self._create_risk_analysis_tool(),
                self._create_medical_knowledge_tool()
            ]
        )
        
        # Revenue Identification Agent - business analysis
        self.revenue_identification_agent = Agent(
            model=self.bedrock_model,
            system_prompt="You are a revenue identification agent. Analyze treatment opportunities for business potential and revenue generation.",
            tools=[
                self._create_revenue_analysis_tool(),
                self._create_customer_segmentation_tool()
            ]
        )
        
        # Emailing Agent - final packaging
        self.emailing_agent = Agent(
            model=self.bedrock_model,
            system_prompt="You are an emailing agent that prepares final documents and communications for business stakeholders.",
            tools=[
                self._create_document_aggregation_tool(),
                self._create_word_export_tool()
            ]
        )

    # [Previous tool implementations remain exactly the same...]
    # All the tool definitions (_create_file_reader_tool, _create_html_parser_tool, etc.)
    # should remain exactly as they were in the original code

    # ==================== MAIN PROCESSING METHODS (UPDATED) ====================
    
    async def process_treatments(self, treatment_ids: List[str], source_files: List[str]):
        """
        Main processing pipeline for treatments.
        
        Args:
            treatment_ids: List of treatment IDs to process
            source_files: List of source file paths
        """
        try:
            # Step 1: Research Agent - Extract raw data
            raw_treatment_data = await self._extract_treatment_data(source_files, treatment_ids)
            
            # Step 2: Documenting Agent - Structure data
            structured_treatments = await self._structure_treatment_data(raw_treatment_data, treatment_ids)
            
            # Step 3: Risk Assessment Agent - Analyze risks
            risk_assessments = await self._assess_treatment_risks(structured_treatments)
            
            # Step 4: Revenue Identification Agent - Analyze revenue
            revenue_analyses = await self._analyze_revenue_opportunities(structured_treatments, risk_assessments)
            
            # Step 5: Generate final report
            final_report = await self._generate_final_report(structured_treatments, risk_assessments, revenue_analyses)
            
            # Step 6: Prepare approval package
            approval_package = await self._prepare_approval_package(structured_treatments, risk_assessments, revenue_analyses)
            
            # Step 7: Email results
            await self._email_results(approval_package)
            
            return {
                "status": "success",
                "treatments_processed": len(treatment_ids),
                "final_report_path": str(self.output_dir / "final_report.docx"),
                "approval_package": approval_package
            }
            
        except Exception as e:
            logging.error(f"Error in processing pipeline: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _extract_treatment_data(self, source_files: List[str], treatment_ids: List[str]) -> List[Dict[str, Any]]:
        """Extract raw treatment data from source files"""
        extracted_data = []
        
        for file_path in source_files:
            # Read file content
            file_content = await self.research_agent.chat(
                f"Please read and extract content from {file_path}",
                tool_choice="read_file",
                tool_input={"file_path": file_path}
            )
            
            if isinstance(file_content, dict) and "error" in file_content:
                logging.warning(f"Skipping file {file_path}: {file_content['error']}")
                continue
            
            # Parse content based on file type
            if file_path.endswith(".html"):
                parsed_data = await self.research_agent.chat(
                    f"Parse HTML content from {file_path} for treatments {treatment_ids}",
                    tool_choice="parse_html_content",
                    tool_input={
                        "html_content": file_content.get("content", ""),
                        "target_treatments": treatment_ids
                    }
                )
            elif file_path.endswith(".pdf"):
                parsed_data = await self.research_agent.chat(
                    f"Extract structured data from PDF {file_path}",
                    tool_choice="extract_pdf_structured_data",
                    tool_input={"pdf_content": file_content.get("content", "")}
                )
            elif file_path.endswith(".docx"):
                parsed_data = await self.research_agent.chat(
                    f"Parse DOCX content from {file_path}",
                    tool_choice="parse_docx_content",
                    tool_input={"docx_content": file_content.get("content", "")}
                )
            else:
                parsed_data = {"content": file_content.get("content", "")}
            
            if isinstance(parsed_data, dict) and "error" in parsed_data:
                logging.warning(f"Error parsing {file_path}: {parsed_data['error']}")
                continue
            
            extracted_data.append({
                "file_path": file_path,
                "file_type": Path(file_path).suffix,
                "content": parsed_data,
                "treatments_found": parsed_data.get("treatments_found", [])
            })
        
        return extracted_data
    
    async def _structure_treatment_data(self, raw_data: List[Dict[str, Any]], treatment_ids: List[str]) -> List[Dict[str, Any]]:
        """Structure raw treatment data into organized format"""
        structured_treatments = []
        
        for treatment_id in treatment_ids:
            # Find all raw data mentioning this treatment
            treatment_raw_data = [d for d in raw_data if treatment_id in d.get("treatments_found", [])]
            
            if not treatment_raw_data:
                logging.warning(f"No data found for treatment {treatment_id}")
                continue
            
            # Structure each piece of raw data
            structured_pieces = []
            for raw_piece in treatment_raw_data:
                structured = await self.documenting_agent.chat(
                    f"Structure treatment data for {treatment_id} from {raw_piece['file_path']}",
                    tool_choice="structure_treatment_data",
                    tool_input={
                        "raw_data": raw_piece,
                        "treatment_id": treatment_id
                    }
                )
                
                if not isinstance(structured, dict) or "error" not in structured:
                    structured_pieces.append(structured)
            
            if structured_pieces:
                # Combine structured pieces
                combined_treatment = {
                    "treatment_id": treatment_id,
                    "sources": [s.get("data_sources", []) for s in structured_pieces],
                    "treatment_overview": "\n".join([s.get("treatment_overview", "") for s in structured_pieces]),
                    "clinical_details": {},
                    "effectiveness_data": {}
                }
                
                # Merge clinical details
                clinical_keys = set()
                for piece in structured_pieces:
                    if isinstance(piece, dict):
                        clinical_keys.update(piece.get("clinical_details", {}).keys())
                
                for key in clinical_keys:
                    combined_values = []
                    for piece in structured_pieces:
                        if isinstance(piece, dict):
                            combined_values.extend(piece.get("clinical_details", {}).get(key, []))
                    combined_treatment["clinical_details"][key] = combined_values[:5]
                
                # Merge effectiveness data
                effectiveness_keys = set()
                for piece in structured_pieces:
                    if isinstance(piece, dict):
                        effectiveness_keys.update(piece.get("effectiveness_data", {}).keys())
                
                for key in effectiveness_keys:
                    combined_values = []
                    for piece in structured_pieces:
                        if isinstance(piece, dict):
                            combined_values.extend(piece.get("effectiveness_data", {}).get(key, []))
                    combined_treatment["effectiveness_data"][key] = combined_values[:5]
                
                structured_treatments.append(combined_treatment)
        
        return structured_treatments
    
    async def _assess_treatment_risks(self, structured_treatments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess risks for each structured treatment"""
        risk_assessments = []
        
        for treatment in structured_treatments:
            # Basic risk analysis
            risk_analysis = await self.risk_assessment_agent.chat(
                f"Analyze risks for treatment {treatment['treatment_id']}",
                tool_choice="analyze_treatment_risks",
                tool_input={"treatment_data": treatment}
            )
            
            if isinstance(risk_analysis, dict) and "error" in risk_analysis:
                logging.warning(f"Error assessing risks for {treatment['treatment_id']}: {risk_analysis['error']}")
                continue
            
            # Consult medical knowledge base
            medical_knowledge = await self.risk_assessment_agent.chat(
                f"Provide medical context for {treatment['treatment_id']}",
                tool_choice="consult_medical_knowledge",
                tool_input={
                    "treatment_id": treatment["treatment_id"],
                    "query": "Provide standard medical context for this treatment"
                }
            )
            
            if not isinstance(medical_knowledge, dict) or "error" not in medical_knowledge:
                risk_analysis["medical_context"] = medical_knowledge.get("knowledge_base_info", {})
            
            risk_assessments.append(risk_analysis)
        
        return risk_assessments
    
    async def _analyze_revenue_opportunities(self, structured_treatments: List[Dict[str, Any]], 
                                           risk_assessments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze revenue opportunities for each treatment"""
        revenue_analyses = []
        
        for i, treatment in enumerate(structured_treatments):
            if i >= len(risk_assessments):
                break
                
            # Basic revenue analysis
            revenue_analysis = await self.revenue_identification_agent.chat(
                f"Analyze revenue opportunities for {treatment['treatment_id']}",
                tool_choice="analyze_revenue_opportunities",
                tool_input={
                    "treatment_data": treatment,
                    "risk_data": risk_assessments[i]
                }
            )
            
            if isinstance(revenue_analysis, dict) and "error" in revenue_analysis:
                logging.warning(f"Error analyzing revenue for {treatment['treatment_id']}: {revenue_analysis['error']}")
                continue
            
            # Customer segmentation
            segmentation = await self.revenue_identification_agent.chat(
                f"Segment customers for {treatment['treatment_id']}",
                tool_choice="segment_customers",
                tool_input={
                    "treatment_analysis": {
                        "treatment_id": treatment["treatment_id"],
                        "risk_data": risk_assessments[i],
                        "revenue_data": revenue_analysis
                    }
                }
            )
            
            if not isinstance(segmentation, dict) or "error" not in segmentation:
                revenue_analysis["customer_segmentation"] = segmentation
            
            revenue_analyses.append(revenue_analysis)
        
        return revenue_analyses
    
    async def _generate_final_report(self, structured_treatments: List[Dict[str, Any]], 
                                   risk_assessments: List[Dict[str, Any]], 
                                   revenue_analyses: List[Dict[str, Any]]) -> str:
        """Generate final combined report"""
        combined_data = []
        
        for i, treatment in enumerate(structured_treatments):
            combined = {
                "treatment_id": treatment["treatment_id"],
                "report": treatment,
                "risk_assessment": risk_assessments[i] if i < len(risk_assessments) else {},
                "revenue_analysis": revenue_analyses[i] if i < len(revenue_analyses) else {}
            }
            combined_data.append(combined)
        
        report = await self.documenting_agent.chat(
            "Generate a combined report from the structured treatment data",
            tool_choice="generate_combined_report",
            tool_input={"structured_treatments": combined_data}
        )
        
        # Save report to file
        report_path = self.output_dir / "final_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(str(report))
        
        return str(report_path)
    
    async def _prepare_approval_package(self, structured_treatments: List[Dict[str, Any]], 
                                      risk_assessments: List[Dict[str, Any]], 
                                      revenue_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare complete approval package"""
        approval_package = await self.emailing_agent.chat(
            "Aggregate all documents into an approval package",
            tool_choice="aggregate_documents",
            tool_input={
                "treatment_reports": structured_treatments,
                "risk_assessments": risk_assessments,
                "revenue_analyses": revenue_analyses
            }
        )
        
        if isinstance(approval_package, dict) and "error" in approval_package:
            raise Exception(f"Error aggregating documents: {approval_package['error']}")
        
        # Generate Word document
        doc_path = self.output_dir / "approval_package.docx"
        doc_result = await self.emailing_agent.chat(
            f"Generate Word document at {doc_path}",
            tool_choice="generate_word_document",
            tool_input={
                "aggregated_data": approval_package,
                "output_path": str(doc_path)
            }
        )
        
        if isinstance(doc_result, dict) and "error" in doc_result:
            raise Exception(f"Error generating Word document: {doc_result['error']}")
        
        approval_package["document_path"] = str(doc_path)
        return approval_package
    
    async def _email_results(self, approval_package: Dict[str, Any]):
        """Email results to business stakeholders"""
        # In a real implementation, this would use AWS SES or similar
        # For demo purposes, we'll just log the would-be email
        
        email_content = f"""
        Healthcare Treatment Analysis Results
        
        Treatments Processed: {approval_package.get('metadata', {}).get('total_treatments', 0)}
        Average Risk Score: {approval_package.get('summary', {}).get('average_risk_score', 0):.1f}/10
        Total Projected Revenue: ${approval_package.get('summary', {}).get('total_projected_revenue', 0):,.2f}
        Recommendation: {approval_package.get('summary', {}).get('recommendation', 'REVIEW')}
        
        The complete approval package is attached.
        """
        
        logging.info(f"Would send email with content:\n{email_content}")
        logging.info(f"With attachment at: {approval_package.get('document_path', '')}")

# ==================== MAIN EXECUTION ====================

async def main():
    """Main execution function"""
    try:
        # Initialize the system
        system = HealthcareAgentSystem()
        
        # Define inputs
        treatment_ids = ["treatment_2", "treatment_4", "treatment_7"]
        source_files = [
            "Government Portal.html",
            "Competitor Portal.html"
        ]
        
        # Process treatments
        results = await system.process_treatments(treatment_ids, source_files)
        
        if results["status"] == "success":
            print(f"Successfully processed {results['treatments_processed']} treatments")
            print(f"Final report generated at: {results['final_report_path']}")
        else:
            print(f"Processing failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
