import streamlit as st
import time
import json
import random
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import random

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI styling
st.markdown("""
<style>
    /* Base theme */
    body, .main, .block-container {
        background-color: #0f172a !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .block-container {
        max-width: 48rem;
        padding: 2rem 1.5rem;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        margin-bottom: 2.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid #1e293b;
        animation: fadeIn 0.5s ease-out;
    }
    
    .header h1 {
        font-size: 2.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.75rem;
        background: linear-gradient(120deg, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header p {
        color: #94a3b8;
        font-size: 1.1rem;
    }
    
    /* Message styling */
    .user-message {
        background: #1e293b;
        color: #f1f5f9;
        padding: 1.25rem 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border: 1px solid #2d3b54;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .assistant-message {
        background: #0f172a;
        color: #f1f5f9;
        padding: 1.25rem 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid #10b981;
        border-radius: 0.5rem;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Status indicators */
    .status-line {
        font-size: 0.95rem;
        color: #94a3b8;
        margin: 0.375rem 0;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        background: #1e293b;
        font-style: normal;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        animation: fadeIn 0.2s ease-out;
    }
    
    .status-running {
        color: #fbbf24;
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.2);
    }
    
    .status-completed {
        color: #34d399;
        background: rgba(52, 211, 153, 0.1);
        border: 1px solid rgba(52, 211, 153, 0.2);
    }
    
    /* Input styling */
    .stTextArea textarea {
        background: #1e293b;
        color: #f1f5f9;
        border-radius: 1rem;
        border: 1px solid #2d3b54;
        padding: 1rem 1.25rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #10b981;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
    }
    
    .stButton > button:hover {
        background-color: #059669;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
    }
    
    .stButton > button:disabled {
        background-color: #475569;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Download button */
    .download-btn {
        background-color: #1e293b;
        border: 1px solid #2d3b54;
        color: #e2e8f0;
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .download-btn:hover {
        background-color: #2d3b54;
        border-color: #3e4d6a;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideIn {
        from { 
            opacity: 0;
            transform: translateY(10px);
        }
        to { 
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        background: #1e293b;
        border-radius: 1rem;
        width: fit-content;
        margin: 1rem 0;
        animation: fadeIn 0.3s ease-out;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: typingBounce 1s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingBounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-4px); }
    }
    
    /* Confidence indicators */
    .confidence-high {
        color: #34d399;
        font-weight: 500;
    }
    
    .confidence-moderate {
        color: #fbbf24;
        font-weight: 500;
    }
    
    .confidence-fair {
        color: #fb923c;
        font-weight: 500;
    }
    
    /* Agent status badges */
    .agent-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.25rem 0.75rem;
        border-radius: 2rem;
        font-size: 0.875rem;
        font-weight: 500;
        background: #1e293b;
        border: 1px solid #2d3b54;
        margin: 0.25rem;
        transition: all 0.2s ease;
    }
    
    .agent-badge.active {
        background: rgba(16, 185, 129, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        color: #10b981;
    }
    
    /* Spin animation for status icon */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Pulse animation for final indicator */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Agent definitions
AGENTS = {
    'governance': {'name': 'Governance Agent', 'icon': '🛡️'},
    'auth': {'name': 'Authorization & Access Agent', 'icon': '🔐'},
    'research': {'name': 'Research Agent', 'icon': '🔍'},
    'legal': {'name': 'Legal Agent', 'icon': '⚖️'},
    'financial': {'name': 'Financial Agent', 'icon': '💰'},
    'risk': {'name': 'Risk Assessment Agent', 'icon': '📊'},
    'marketing': {'name': 'Marketing Analytics Agent', 'icon': '📈'},
    'document': {'name': 'Documenting Agent', 'icon': '📄'}
}

# Orchestration flows
FLOWS = {
    "healthcare_trends": {
        "query": "What are latest trends in the healthcare treatment space?",
        "agents": ['governance', 'auth', 'research', 'document'],
        "response": """**Latest Healthcare Treatment Trends (2025):**\n\n• **Personalized Medicine**: Treatments tailored to individual genetic profiles\n• **AI-Powered Diagnostics**: Machine learning for early disease detection  \n• **Telemedicine Integration**: Hybrid remote and in-person care models\n• **Immunotherapy Advances**: Revolutionary cancer treatments\n• **Digital Therapeutics**: App-based treatments for mental health\n\n*Analysis based on 15+ medical journals and industry reports*"""
    },
    "healthcare_risk": {
        "query": "Is implementing this particular healthcare treatment risky?",
        "agents": ['governance', 'auth', 'risk', 'legal', 'document'],
        "response": """**Risk Assessment Summary:**\n\n**Risk Level: MODERATE ⚠️**\n\n**Key Considerations:**\n• Regulatory compliance (FDA approval: 12-18 months)\n• Clinical trial requirements\n• Insurance coverage uncertainties  \n• Staff training needs\n\n**Recommended Actions:**\n• Phased implementation approach\n• Early regulatory engagement\n• Insurance pre-authorization protocols"""
    },
    "revenue_projection": {
        "query": "What is the revenue and profit projection?",
        "agents": ['governance', 'auth', 'financial', 'document'],
        "response": """**5-Year Revenue & Profit Projection:**\n\n• **Year 1**: $2.5M (Break-even)\n• **Year 2**: $4.8M (15% margin)\n• **Year 3**: $7.2M (22% margin)  \n• **Year 4**: $9.8M (28% margin)\n• **Year 5**: $12.5M (32% margin)\n\n**Key Assumptions:**\n• 15% market penetration by Year 3\n• $8,500 average treatment cost\n• 85% operational efficiency scaling"""
    },
    "marketing_campaigns": {
        "query": "What are the latest marketing campaigns?",
        "agents": ['governance', 'auth', 'research', 'document'],
        "response": """**Latest Marketing Campaigns (Q2 2025):**\n\n**1. "Health Forward" Digital Campaign**\n• Multi-channel approach (Social, Search, Display)\n• Budget: $2.5M | Duration: 6 months\n\n**2. "Wellness Reimagined" Content Series**  \n• Educational content marketing\n• Budget: $800K | Duration: 4 months\n\n**3. "Care Connect" Community Outreach**\n• Local partnerships and events\n• Budget: $1.2M | Duration: 8 months"""
    },
    "campaign_roi": {
        "query": "Give analysis of ROI of these campaigns",
        "agents": ['governance', 'auth', 'marketing', 'document'],
        "response": """**Campaign ROI Analysis:**\n\n**"Health Forward" Digital:**\n• Investment: $2.5M → Revenue: $8.2M\n• **ROI: 228%** (vs 180% benchmark)\n\n**"Wellness Reimagined" Content:**\n• Investment: $800K → Revenue: $2.1M  \n• **ROI: 163%** (vs 140% benchmark)\n\n**"Care Connect" Outreach:**\n• Investment: $1.2M → Revenue: $2.8M\n• **ROI: 133%** (vs 120% benchmark)\n\n**Overall Performance:** Above industry standards across all campaigns"""
    }
}

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'last_flow_key' not in st.session_state:
    st.session_state.last_flow_key = None

def simulate_agent_work(agent_key: str, task_complexity: float = 0.5) -> str:
    """Simulate agent execution with dynamic timing based on task complexity"""
    
    # Base work time 0.5-2.5 seconds based on complexity
    base_time = 0.5 + (task_complexity * 2.0)
    
    # Add some randomness to make it feel more natural
    work_time = base_time + (random.random() * 0.5)
    
    # Simulate thinking/processing
    time.sleep(work_time)
    
    # Agent-specific responses with some variability
    responses = {
        'governance': [
            'Policy compliance validated',
            'Guardrails verified',
            'Governance rules checked',
            'Compliance requirements validated'
        ],
        'auth': [
            'Access validated',
            'Permissions granted',
            'Authorization confirmed',
            'Access level verified'
        ],
        'research': [
            'Research analysis completed',
            'Data gathering finished',
            'Research synthesis completed',
            'Analysis results compiled'
        ],
        'legal': [
            'Legal review completed',
            'Regulatory check finished',
            'Compliance verified',
            'Legal assessment done'
        ],
        'financial': [
            'Financial analysis completed',
            'Cost-benefit analysis done',
            'Revenue projections compiled',
            'Financial assessment finished'
        ],
        'risk': [
            'Risk factors evaluated',
            'Threat assessment completed',
            'Risk analysis finalized',
            'Safety evaluation done'
        ],
        'marketing': [
            'Market analysis completed',
            'Campaign metrics analyzed',
            'Marketing data processed',
            'Analytics review finished'
        ],
        'document': [
            'Documentation processed',
            'Document analysis complete',
            'Content review finished',
            'Documentation synthesis done'
        ]
    }
    
    response_list = responses.get(agent_key, ['Processing completed'])
    return random.choice(response_list)

def get_final_response(flow_key: str) -> str:
    """Get hardcoded responses"""
    responses = {
        "healthcare_trends": """**Latest Healthcare Treatment Trends (2025):**

• **Personalized Medicine**: Treatments tailored to individual genetic profiles
• **AI-Powered Diagnostics**: Machine learning for early disease detection  
• **Telemedicine Integration**: Hybrid remote and in-person care models
• **Immunotherapy Advances**: Revolutionary cancer treatments
• **Digital Therapeutics**: App-based treatments for mental health

*Analysis based on 15+ medical journals and industry reports*""",

        "healthcare_risk": """**Risk Assessment Summary:**

**Risk Level: MODERATE ⚠️**

**Key Considerations:**
• Regulatory compliance (FDA approval: 12-18 months)
• Clinical trial requirements
• Insurance coverage uncertainties  
• Staff training needs

**Recommended Actions:**
• Phased implementation approach
• Early regulatory engagement
• Insurance pre-authorization protocols""",

        "revenue_projection": """**5-Year Revenue & Profit Projection:**

• **Year 1**: $2.5M (Break-even)
• **Year 2**: $4.8M (15% margin)
• **Year 3**: $7.2M (22% margin)  
• **Year 4**: $9.8M (28% margin)
• **Year 5**: $12.5M (32% margin)

**Key Assumptions:**
• 15% market penetration by Year 3
• $8,500 average treatment cost
• 85% operational efficiency scaling""",

        "marketing_campaigns": """**Latest Marketing Campaigns (Q2 2025):**

**1. "Health Forward" Digital Campaign**
• Multi-channel approach (Social, Search, Display)
• Budget: $2.5M | Duration: 6 months

**2. "Wellness Reimagined" Content Series**  
• Educational content marketing
• Budget: $800K | Duration: 4 months

**3. "Care Connect" Community Outreach**
• Local partnerships and events
• Budget: $1.2M | Duration: 8 months""",

        "campaign_roi": """**Campaign ROI Analysis:**

**"Health Forward" Digital:**
• Investment: $2.5M → Revenue: $8.2M
• **ROI: 228%** (vs 180% benchmark)

**"Wellness Reimagined" Content:**
• Investment: $800K → Revenue: $2.1M  
• **ROI: 163%** (vs 140% benchmark)

**"Care Connect" Outreach:**
• Investment: $1.2M → Revenue: $2.8M
• **ROI: 133%** (vs 120% benchmark)

**Overall Performance:** Above industry standards across all campaigns"""
    }
    return responses.get(flow_key, "Analysis completed successfully.")

async def process_agent_results(flow_key: str, query: str, agent_results: List[Dict]) -> str:
    """Process agent results to generate a dynamic response"""
    
    # Get base response template from flow but treat it as a starting point
    base_template = FLOWS.get(flow_key, {}).get("response", "")
    
    # Calculate overall confidence
    overall_confidence = sum(ar["confidence"] for ar in agent_results) / len(agent_results)
    confidence_level = "High" if overall_confidence > 0.95 else "Moderate" if overall_confidence > 0.85 else "Fair"
    
    # Build response based on flow type and agent results
    if "healthcare_trends" in flow_key:
        trends = [
            "Personalized Medicine",
            "AI-Powered Diagnostics",
            "Telemedicine Integration",
            "Immunotherapy Advances",
            "Digital Therapeutics"
        ]
        selected_trends = random.sample(trends, min(len(trends), 3 + int(overall_confidence * 2)))
        
        response = f"**Latest Healthcare Trends Analysis ({datetime.now().year}):**\n\n"
        for trend in selected_trends:
            response += f"• **{trend}**: {get_trend_description(trend)}\n"
        
        response += f"\n*Analysis confidence: {confidence_level} ({overall_confidence:.1%})*"
        
    elif "risk" in flow_key:
        risk_level = "MODERATE" if overall_confidence > 0.9 else "HIGH"
        response = f"""**Risk Assessment Summary:**\n
**Risk Level: {risk_level} {'⚠️' if risk_level == 'MODERATE' else '🚨'}**\n
**Key Considerations:**
{format_risk_considerations(agent_results)}\n
**Confidence Level: {confidence_level}**\n
*Assessment based on {len(agent_results)} agent evaluations*"""
        
    elif "revenue" in flow_key or "roi" in flow_key:
        years = 5
        base_amount = 2.5  # Million
        growth_rate = 0.15 + (random.random() * 0.1)  # 15-25% growth
        
        response = f"**{years}-Year Revenue & Profit Projection:**\n\n"
        
        current_amount = base_amount
        for year in range(1, years + 1):
            margin = 0.15 + (year * 0.03)  # Margins improve over time
            response += f"• **Year {year}**: ${current_amount:.1f}M ({margin:.0%} margin)\n"
            current_amount *= (1 + growth_rate)
            
        response += f"\n*Projection confidence: {confidence_level}*"
        
    else:
        # Default to base template with confidence indicator
        response = base_template + f"\n\n*Analysis confidence: {confidence_level} ({overall_confidence:.1%})*"
    
    return response

def get_trend_description(trend: str) -> str:
    """Generate dynamic trend descriptions"""
    descriptions = {
        "Personalized Medicine": [
            "AI-driven treatment customization",
            "Genetic profile-based therapy",
            "Individual response prediction"
        ],
        "AI-Powered Diagnostics": [
            "Deep learning for early detection",
            "Automated image analysis",
            "Predictive diagnostic models"
        ],
        "Telemedicine Integration": [
            "Remote patient monitoring",
            "Virtual consultations",
            "Digital health platforms"
        ],
        "Immunotherapy Advances": [
            "Targeted immune responses",
            "Cancer treatment breakthroughs",
            "Novel antibody therapies"
        ],
        "Digital Therapeutics": [
            "App-based interventions",
            "Virtual reality therapy",
            "Digital behavior modification"
        ]
    }
    return random.choice(descriptions.get(trend, ["Emerging technology in healthcare"]))

def format_risk_considerations(agent_results: List[Dict]) -> str:
    """Format risk considerations based on agent results"""
    considerations = [
        "• Regulatory compliance requirements",
        "• Implementation timeline impact",
        "• Staff training needs",
        "• Technical integration challenges",
        "• Cost-benefit implications"
    ]
    
    # Select considerations based on confidence
    high_confidence_results = [ar for ar in agent_results if ar["confidence"] > 0.9]
    num_considerations = min(len(considerations), 3 + len(high_confidence_results))
    
    return "\n".join(random.sample(considerations, num_considerations))

async def execute_flow(flow_key: str, user_query: str):
    """Execute orchestration flow with dynamic agent behavior"""
    if flow_key not in FLOWS:
        return
    
    flow = FLOWS[flow_key]
    agents = flow['agents']
    
    # Status container
    status_container = st.empty()
    
    # Show typing indicator while preparing
    with status_container:
        st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.5)
    
    # Calculate task complexity based on query length and flow
    query_complexity = min(1.0, len(user_query) / 200)  # Normalize to 0-1
    flow_complexity = len(agents) / 8.0  # Normalize by max agents
    task_complexity = (query_complexity + flow_complexity) / 2
    
    # Track intermediate results
    agent_results = []
    
    # Execute agents with dynamic timing
    for i, agent_key in enumerate(agents):
        agent = AGENTS[agent_key]
        
        # Calculate agent-specific complexity
        agent_complexity = task_complexity * (1 + (i * 0.1))  # Later agents may be more complex
        
        # Show thinking status with animated icon
        with status_container:
            status_html = f"""
            <div class="status-line status-running">
                <span style="display: inline-block; animation: spin 2s linear infinite;">⚡</span>
                {agent['icon']} {agent['name']} analyzing...
            </div>
            """
            st.markdown(status_html, unsafe_allow_html=True)
        
        # Simulate work with dynamic timing
        result = simulate_agent_work(agent_key, agent_complexity)
        agent_results.append({
            "agent": agent_key,
            "result": result,
            "confidence": random.uniform(0.85, 0.98)
        })
        
        # Show completion with varying confidence levels
        with status_container:
            confidence = agent_results[-1]["confidence"]
            conf_class = "confidence-high" if confidence > 0.95 else "confidence-moderate" if confidence > 0.85 else "confidence-fair"
            conf_indicator = "✓✓" if confidence > 0.95 else "✓"
            
            status_html = f"""
            <div class="status-line status-completed">
                <span class="{conf_class}">{conf_indicator}</span>
                {agent['icon']} {result}
                <span style="margin-left: auto; font-size: 0.9em; opacity: 0.8;">
                    {confidence:.0%}
                </span>
            </div>
            """
            st.markdown(status_html, unsafe_allow_html=True)
        
        # Variable pause between agents
        time.sleep(0.2 + (random.random() * 0.3))
    
    # Show final processing indicator
    with status_container:
        st.markdown("""
        <div class="status-line">
            <span style="display: inline-block; animation: pulse 1s infinite;">🔄</span>
            Synthesizing results...
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.8)
    
    # Clear status
    status_container.empty()
    
    # Generate a dynamic response based on agent results
    response = await process_agent_results(flow_key, user_query, agent_results)
    
    # Add to messages with enhanced metadata
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "timestamp": datetime.now(),
        "flow": flow_key,
        "confidence": sum(ar["confidence"] for ar in agent_results) / len(agent_results),
        "agent_results": agent_results  # Store for potential future reference
    })

def main():
    # Header with gradient effect
    st.markdown("""
    <div class="header">
        <h1>AI Orchestration Agent</h1>
        <p>Unified analysis powered by specialized AI agents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat history with enhanced styling
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <strong>You</strong>
                    <span style="margin-left: auto; font-size: 0.8em; color: #94a3b8;">
                        {message.get("timestamp", datetime.now()).strftime("%H:%M")}
                    </span>
                </div>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            confidence = message.get("confidence", 0.9)
            conf_class = "confidence-high" if confidence > 0.95 else "confidence-moderate" if confidence > 0.85 else "confidence-fair"
            conf_label = "High" if confidence > 0.95 else "Moderate" if confidence > 0.85 else "Fair"
            
            st.markdown(f"""
            <div class="assistant-message">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <strong>Assistant</strong>
                    <span style="margin-left: auto; font-size: 0.8em;">
                        <span class="{conf_class}">● {conf_label} confidence ({confidence:.0%})</span>
                    </span>
                </div>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Add enhanced download button
            if "flow" in message:
                report_data = {
                    "query": message["content"],
                    "timestamp": message["timestamp"].isoformat(),
                    "analysis": message["content"],
                    "confidence": confidence,
                    "agent_results": message.get("agent_results", [])
                }
                report_json = json.dumps(report_data, indent=2)
                st.download_button(
                    label="📥 Download Detailed Report",
                    data=report_json,
                    file_name=f"report_{message['timestamp'].strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"download_{message['timestamp']}"
                )
    
    # Example queries with enhanced styling
    if not st.session_state.messages:
        st.markdown("""
        <p style="color: #94a3b8; margin-bottom: 1rem;">
            <strong>Try asking about:</strong>
        </p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏥 Healthcare Trends Analysis", 
                        key="ex1", 
                        disabled=st.session_state.processing,
                        help="Analyze current healthcare industry trends"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": FLOWS["healthcare_trends"]["query"]
                })
                st.session_state.last_flow_key = "healthcare_trends"
                st.rerun()
        
        with col2:
            if st.button("⚠️ Risk Assessment", 
                        key="ex2",
                        disabled=st.session_state.processing,
                        help="Evaluate implementation risks"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": FLOWS["healthcare_risk"]["query"]
                })
                st.session_state.last_flow_key = "healthcare_risk"
                st.rerun()
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("💰 Financial Projections", 
                        key="ex3",
                        disabled=st.session_state.processing,
                        help="Generate revenue and profit projections"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": FLOWS["revenue_projection"]["query"]
                })
                st.session_state.last_flow_key = "revenue_projection"
                st.rerun()
        
        with col4:
            if st.button("📊 Marketing ROI Analysis", 
                        key="ex4",
                        disabled=st.session_state.processing,
                        help="Analyze marketing campaign performance"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": FLOWS["campaign_roi"]["query"]
                })
                st.session_state.last_flow_key = "campaign_roi"
                st.rerun()
    
    # Input area
    st.markdown("---")
    
    # Text input
    user_input = st.text_area(
        "Message AI Orchestration Agent...",
        height=80,
        placeholder="Ask about healthcare trends, risk assessment, financial projections, or marketing analysis...",
        disabled=st.session_state.processing,
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        send_button = st.button("Send", disabled=st.session_state.processing or not user_input.strip())
    
    with col2:
        if st.button("Clear", disabled=st.session_state.processing):
            st.session_state.messages = []
            st.session_state.last_flow_key = None
            st.rerun()
    
    # Process user input
    if send_button and user_input.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.processing = True
        
        # Determine flow based on keywords
        flow_key = "healthcare_trends"  # default
        
        query_lower = user_input.lower()
        if any(word in query_lower for word in ['risk', 'risky', 'danger', 'safe']):
            flow_key = "healthcare_risk"
        elif any(word in query_lower for word in ['revenue', 'profit', 'money', 'financial']):
            flow_key = "revenue_projection"
        elif any(word in query_lower for word in ['roi', 'return']):
            flow_key = "campaign_roi"
        elif any(word in query_lower for word in ['campaign', 'marketing']):
            flow_key = "marketing_campaigns"
        
        st.session_state.last_flow_key = flow_key
        st.rerun()
    
    # Execute flow if processing
    if st.session_state.processing:
        # Get the last user message to determine flow
        last_user_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        
        if last_user_msg:
            # Determine flow
            query_lower = last_user_msg.lower()
            flow_key = "healthcare_trends"
            
            if any(word in query_lower for word in ['risk', 'risky', 'danger', 'safe']):
                flow_key = "healthcare_risk"
            elif any(word in query_lower for word in ['revenue', 'profit', 'money', 'financial']):
                flow_key = "revenue_projection"
            elif any(word in query_lower for word in ['roi', 'return']):
                flow_key = "campaign_roi"
            elif any(word in query_lower for word in ['campaign', 'marketing']):
                flow_key = "marketing_campaigns"
            
            # Execute flow
            execute_flow(flow_key, last_user_msg)
            st.session_state.processing = False
            st.rerun()

if __name__ == "__main__":
    main()
