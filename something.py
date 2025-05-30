#!/usr/bin/env python3
"""
AI Agent Hackathon - Healthcare Treatment Analysis System
Streamlit Application Version
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
import streamlit as st
import pandas as pd

# Strands imports
from strands import Agent, tool
from strands.models import BedrockModel

# Additional imports for file handling
import PyPDF2
import docx
from bs4 import BeautifulSoup
import mammoth

# Configure logging
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Page config
st.set_page_config(
    page_title="Healthcare Treatment Analysis",
    page_icon="🏥",
    layout="wide"
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
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            aws_session_token=st.secrets["AWS_SESSION_TOKEN"],
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

    async def process_treatments(self, treatment_ids: List[str], source_files: List[str]):
        """
        Main processing pipeline for treatments.
        
        Args:
            treatment_ids: List of treatment IDs to process
            source_files: List of source file paths
        """
        try:
            with st.status("Processing treatments...", expanded=True) as status:
                # Step 1: Research Agent - Extract raw data
                st.write("🔍 Extracting raw treatment data...")
                raw_treatment_data = await self._extract_treatment_data(source_files, treatment_ids)
                
                # Step 2: Documenting Agent - Structure data
                st.write("📝 Structuring treatment data...")
                structured_treatments = await self._structure_treatment_data(raw_treatment_data, treatment_ids)
                
                # Step 3: Risk Assessment Agent - Analyze risks
                st.write("⚠️ Assessing treatment risks...")
                risk_assessments = await self._assess_treatment_risks(structured_treatments)
                
                # Step 4: Revenue Identification Agent - Analyze revenue
                st.write("💰 Analyzing revenue opportunities...")
                revenue_analyses = await self._analyze_revenue_opportunities(structured_treatments, risk_assessments)
                
                # Step 5: Generate final report
                st.write("📄 Generating final report...")
                final_report = await self._generate_final_report(structured_treatments, risk_assessments, revenue_analyses)
                
                # Step 6: Prepare approval package
                st.write("📦 Preparing approval package...")
                approval_package = await self._prepare_approval_package(structured_treatments, risk_assessments, revenue_analyses)
                
                # Step 7: Email results
                st.write("📧 Preparing email notification...")
                await self._email_results(approval_package)
                
                status.update(label="Processing complete!", state="complete")
            
            return {
                "status": "success",
                "treatments_processed": len(treatment_ids),
                "final_report_path": str(self.output_dir / "final_report.docx"),
                "approval_package": approval_package
            }
            
        except Exception as e:
            logging.error(f"Error in processing pipeline: {str(e)}")
            st.error(f"Processing error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    # [Previous processing methods remain the same but with added Streamlit UI elements...]
    # All the _extract_treatment_data, _structure_treatment_data, etc. methods
    # should remain the same as in the previous implementation but with added st.write() calls
    # to update the UI during processing

    async def _extract_treatment_data(self, source_files: List[str], treatment_ids: List[str]) -> List[Dict[str, Any]]:
        """Extract raw treatment data from source files"""
        extracted_data = []
        
        progress_bar = st.progress(0)
        total_files = len(source_files)
        
        for i, file_path in enumerate(source_files):
            progress_bar.progress((i + 1) / total_files, f"Processing {file_path}...")
            
            # Read file content
            file_content = await self.research_agent.chat(
                f"Please read and extract content from {file_path}",
                tool_choice="read_file",
                tool_input={"file_path": file_path}
            )
            
            if isinstance(file_content, dict) and "error" in file_content:
                st.warning(f"Skipping file {file_path}: {file_content['error']}")
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
                st.warning(f"Error parsing {file_path}: {parsed_data['error']}")
                continue
            
            extracted_data.append({
                "file_path": file_path,
                "file_type": Path(file_path).suffix,
                "content": parsed_data,
                "treatments_found": parsed_data.get("treatments_found", [])
            })
        
        progress_bar.empty()
        return extracted_data
    
    # [Other processing methods with similar Streamlit UI additions...]

def main():
    """Main Streamlit application"""
    st.title("🏥 Healthcare Treatment Analysis System")
    st.markdown("""
    This system analyzes healthcare treatments from various sources, assesses risks, 
    identifies revenue opportunities, and generates comprehensive reports.
    """)
    
    # Initialize session state
    if 'system' not in st.session_state:
        st.session_state.system = HealthcareAgentSystem()
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Input Parameters")
        
        # Treatment selection
        treatment_options = [
            "treatment_1", "treatment_2", "treatment_3", 
            "treatment_4", "treatment_7", "treatment_8"
        ]
        selected_treatments = st.multiselect(
            "Select treatments to analyze:",
            treatment_options,
            default=["treatment_2", "treatment_4", "treatment_7"]
        )
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload source files (HTML, PDF, DOCX):",
            type=["html", "pdf", "docx"],
            accept_multiple_files=True
        )
        
        # Process button
        process_btn = st.button("Analyze Treatments")
    
    # Main content area
    if process_btn and selected_treatments and uploaded_files:
        # Save uploaded files
        source_files = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join("uploaded_files", uploaded_file.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            source_files.append(file_path)
        
        # Process treatments
        st.session_state.results = asyncio.run(
            st.session_state.system.process_treatments(selected_treatments, source_files)
        )
    
    # Display results
    if st.session_state.results:
        if st.session_state.results["status"] == "success":
            st.success("✅ Analysis completed successfully!")
            
            # Show summary
            st.subheader("Analysis Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Treatments Processed", 
                st.session_state.results["treatments_processed"]
            )
            
            avg_risk = st.session_state.results["approval_package"]["summary"].get("average_risk_score", 0)
            col2.metric(
                "Average Risk Score", 
                f"{avg_risk:.1f}/10",
                delta="Low Risk" if avg_risk <= 3 else "Medium Risk" if avg_risk <= 6 else "High Risk",
                delta_color="inverse"
            )
            
            total_revenue = st.session_state.results["approval_package"]["summary"].get("total_projected_revenue", 0)
            col3.metric(
                "Projected Annual Revenue", 
                f"${total_revenue:,.2f}"
            )
            
            # Show detailed results in tabs
            tab1, tab2, tab3 = st.tabs(["Treatments", "Risk Analysis", "Revenue Opportunities"])
            
            with tab1:
                st.subheader("Treatment Details")
                treatments = st.session_state.results["approval_package"]["treatments"]
                for treatment in treatments:
                    with st.expander(f"Treatment {treatment['treatment_id']}"):
                        st.write("**Overview:**", treatment["report"].get("treatment_overview", "No overview available"))
                        
                        st.write("**Clinical Details:**")
                        clinical_details = treatment["report"].get("clinical_details", {})
                        for key, value in clinical_details.items():
                            st.write(f"- **{key.title()}:** {', '.join(value) if isinstance(value, list) else value}")
            
            with tab2:
                st.subheader("Risk Analysis")
                treatments = st.session_state.results["approval_package"]["treatments"]
                for treatment in treatments:
                    with st.expander(f"Treatment {treatment['treatment_id']}"):
                        risk = treatment["risk_assessment"]
                        st.write(f"**Overall Risk Score:** {risk.get('overall_risk_score', 0)}/10")
                        
                        st.write("**Medical Risks:**")
                        for mr in risk.get("medical_risks", [])[:5]:
                            st.write(f"- {mr.get('keyword', '')} ({mr.get('level', '')})")
                        
                        st.write("**Recommendations:**")
                        for rec in risk.get("recommendations", []):
                            st.write(f"- {rec}")
            
            with tab3:
                st.subheader("Revenue Opportunities")
                treatments = st.session_state.results["approval_package"]["treatments"]
                for treatment in treatments:
                    with st.expander(f"Treatment {treatment['treatment_id']}"):
                        revenue = treatment["revenue_analysis"]
                        st.write(f"**Market Potential:** {revenue.get('market_potential', {}).get('level', 'Unknown')}")
                        
                        st.write("**Customer Segments:**")
                        segments = revenue.get("customer_segmentation", {}).get("segments", {})
                        for seg_name, seg_data in segments.items():
                            st.write(f"- **{seg_name.title()}:** {seg_data.get('description', '')}")
                        
                        st.write("**Projected Annual Revenue:**")
                        st.write(f"- New Customers: ${revenue.get('revenue_projections', {}).get('new_customer_revenue', 0):,.2f}")
                        st.write(f"- Existing Customers: ${revenue.get('revenue_projections', {}).get('existing_customer_revenue', 0):,.2f}")
                        st.write(f"- Total: ${revenue.get('revenue_projections', {}).get('total_annual_projection', 0):,.2f}")
            
            # Download button for report
            with open(st.session_state.results["final_report_path"], "rb") as f:
                st.download_button(
                    label="Download Full Report",
                    data=f,
                    file_name="treatment_analysis_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error(f"❌ Error in processing: {st.session_state.results.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
