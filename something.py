import streamlit as st
import time
import random
from datetime import datetime

# Configure the page
st.set_page_config(
    page_title="Agentic AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .agent-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background: rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    .agent-working {
        border-left: 4px solid #fbbf24;
        background: rgba(251, 191, 36, 0.1);
    }
    .agent-complete {
        border-left: 4px solid #34d399;
        background: rgba(52, 211, 153, 0.1);
        color: #065f46;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }
    .agent-response {
        padding: 1rem;
        border-radius: 0.5rem;
        background: #f8fafc;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        color: #1a1a1a;
    }
    .agent-response h4 {
        color: #1a1a1a;
    }
    .agent-response ul {
        color: #1a1a1a;
    }
    .agent-response li {
        color: #1a1a1a;
    }
    .thinking-animation {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin-left: 0.5rem;
    }
    .dot {
        width: 4px;
        height: 4px;
        background: #60a5fa;
        border-radius: 50%;
        animation: bounce 1s infinite;
    }
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }
</style>
""", unsafe_allow_html=True)

# Agent definitions with hardcoded responses
AGENTS = {
    "orchestrator": {
        "name": "Orchestration Agent",
        "icon": "🎭",
        "description": "Coordinates other agents and manages workflow"
    },
    "auth": {
        "name": "Authentication Agent",
        "icon": "🔐",
        "description": "Validates access and security requirements"
    },
    "research": {
        "name": "Research Agent",
        "icon": "🔍",
        "description": "Analyzes trends and gathers information"
    },
    "document": {
        "name": "Documentation Agent",
        "icon": "📄",
        "description": "Formats and structures information"
    }
}

# Hardcoded responses for different domains
RESPONSES = {
    "healthcare": {
        "trends": [
            "AI-powered diagnostic tools becoming mainstream",
            "Telemedicine adoption increasing by 300%",
            "Personalized medicine through genomic analysis",
            "Mental health apps integration with traditional care",
            "Remote patient monitoring systems"
        ],
        "stats": {
            "market_size": "$12.5T by 2025",
            "growth_rate": "15.4% CAGR",
            "adoption_rate": "78% in developed countries"
        }
    },
    "finance": {
        "trends": [
            "Decentralized Finance (DeFi) integration in traditional banking",
            "AI-driven risk assessment models",
            "Open banking APIs becoming standard",
            "Blockchain-based transaction systems",
            "Automated wealth management solutions"
        ],
        "stats": {
            "market_size": "$26.5T by 2025",
            "growth_rate": "22.4% CAGR",
            "digital_adoption": "85% of transactions"
        }
    },
    "cybersecurity": {
        "trends": [
            "Zero-trust architecture implementation",
            "AI-powered threat detection systems",
            "Quantum-resistant cryptography",
            "Automated security orchestration (SOAR)",
            "Cloud-native security solutions"
        ],
        "stats": {
            "market_size": "$3.5T by 2025",
            "growth_rate": "18.7% CAGR",
            "breach_cost": "$4.5M average"
        }
    }
}

def simulate_agent_work(agent_key: str, context: str) -> str:
    """Simulate agent working with a delay and return a response"""
    time.sleep(random.uniform(0.5, 2.0))
    
    if agent_key == "auth":
        return "Access granted. Security clearance verified."
    elif agent_key == "research":
        domain = context.lower()
        if "health" in domain:
            trends = RESPONSES["healthcare"]["trends"]
        elif "finance" in domain:
            trends = RESPONSES["finance"]["trends"]
        elif "cyber" in domain:
            trends = RESPONSES["cybersecurity"]["trends"]
        else:
            trends = ["No specific trends found for this domain"]
        return f"Research analysis complete. Identified {len(trends)} major trends."
    elif agent_key == "document":
        return "Information structured and formatted for presentation."
    else:
        return "Task completed successfully."

def get_final_response(query: str) -> dict:
    """Generate a final response based on the query"""
    query_lower = query.lower()
    
    if "health" in query_lower:
        domain = "healthcare"
    elif "financ" in query_lower or "bank" in query_lower:
        domain = "finance"
    elif "cyber" in query_lower or "security" in query_lower:
        domain = "cybersecurity"
    else:
        domain = "healthcare"  # default
    
    response_data = RESPONSES[domain]
    return {
        "domain": domain,
        "trends": response_data["trends"],
        "statistics": response_data["stats"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def main():
    # Initialize session state for messages and processing flag
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'processing' not in st.session_state:
        st.session_state.processing = False
        
    # Display header
    st.markdown('<div class="main-header"><h1>🤖 Agentic AI System</h1><p>Ask about trends in Healthcare, Finance, or Cybersecurity</p></div>', unsafe_allow_html=True)

    # Clear chat button in the header area
    _, clear_col = st.columns([6, 1])
    with clear_col:
        if st.button("Clear Chat", key="clear") and len(st.session_state.messages) > 0:
            st.session_state.messages = []
            st.session_state.processing = False
            st.rerun()
    
    # Chat messages container
    with st.container():
        for message in st.session_state.messages:
            if message.get("role") == "user":
                st.chat_message("user").write(f"{message['content']}")
            else:
                with st.chat_message("assistant"):
                    st.markdown(f"""
                    <div class="agent-response">
                        <h4>
                            {message.get('domain', 'Analysis').title()} Trends Analysis 
                            <span style="float: right; font-size: 0.8em; color: #64748b;">
                                {message.get('timestamp', '')}
                            </span>
                        </h4>
                        <p><strong>🎯 Key Trends:</strong></p>
                        <ul>
                            {''.join(f'<li>{trend}</li>' for trend in message.get('trends', []))}
                        </ul>
                        <p><strong>📊 Statistics:</strong></p>
                        <ul>
                            {''.join(f'<li><strong>{k}:</strong> {v}</li>' for k, v in message.get('statistics', {}).items())}
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

    # Input area at the bottom
    with st.container():
        # Query input and submit button
        input_col, submit_col = st.columns([5, 1])
        with input_col:
            query = st.text_input(
                "Ask about current trends:",
                placeholder="e.g., What are the latest trends in healthcare?",
                key="query_input",
                label_visibility="collapsed"
            )
        
        with submit_col:
            submit_button = st.button("Send", type="primary", use_container_width=True)

        # Process input when submitted
        if submit_button and query and not st.session_state.processing:
            st.session_state.processing = True
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Status container for agent progress
            status_container = st.empty()
            
            # Simulate orchestrator
            with status_container:
                st.markdown(f"""
                <div class="agent-status agent-working">
                    {AGENTS['orchestrator']['icon']} {AGENTS['orchestrator']['name']} initializing workflow...
                    <div class="thinking-animation">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            time.sleep(1)
            
            # Simulate other agents
            for agent_key, agent in AGENTS.items():
                if agent_key != "orchestrator":
                    with status_container:
                        st.markdown(f"""
                        <div class="agent-status agent-working">
                            {agent['icon']} {agent['name']} processing...
                            <div class="thinking-animation">
                                <div class="dot"></div>
                                <div class="dot"></div>
                                <div class="dot"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    result = simulate_agent_work(agent_key, query)
                    
                    with status_container:
                        st.markdown(f"""
                        <div class="agent-status agent-complete">
                            {agent['icon']} {agent['name']}: {result}
                        </div>
                        """, unsafe_allow_html=True)
            
            # Generate and add response
            response = get_final_response(query)
            response["role"] = "assistant"
            st.session_state.messages.append(response)
            
            # Clear status and reset state
            status_container.empty()
            st.session_state.processing = False
            
            # Rerun to update the UI
            st.rerun()

if __name__ == "__main__":
    main()
