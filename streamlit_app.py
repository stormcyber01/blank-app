import streamlit as st
import random

# Initialize session state
if "player" not in st.session_state:
    st.session_state.player = {
        "cash": 100_000_000,
        "projects": [],
        "debt": 0,
        "npv_total": 0,
        "equity_projects": 0,
        "vc_risk": False
    }
    st.session_state.round_number = 1
    st.session_state.selected_project = None
    st.session_state.projects = random.sample([
        {"name": "AI Lending Platform", "cost": 30_000_000, "cash_flows": [15_000_000, 20_000_000, 25_000_000], "risk": "high", "sector": "AI"},
        {"name": "Payment Gateway", "cost": 25_000_000, "cash_flows": [10_000_000, 15_000_000, 20_000_000], "risk": "low", "sector": "Fintech"},
        {"name": "Cybersecurity Infrastructure", "cost": 20_000_000, "cash_flows": [8_000_000, 10_000_000, 12_000_000], "risk": "low", "sector": "Security"},
        {"name": "Blockchain Remittance App", "cost": 28_000_000, "cash_flows": [14_000_000, 18_000_000, 22_000_000], "risk": "high", "sector": "Blockchain"},
        {"name": "ESG Compliance Platform", "cost": 18_000_000, "cash_flows": [7_000_000, 9_000_000, 13_000_000], "risk": "low", "sector": "Sustainability"},
        {"name": "Digital Bank Expansion", "cost": 22_000_000, "cash_flows": [11_000_000, 13_000_000, 15_000_000], "risk": "medium", "sector": "Banking"}
    ], 3)

def discount_factor(year):
    return 1 / ((1 + 0.10) ** year)

def calculate_npv(cash_flows):
    return sum(cf * discount_factor(i + 1) for i, cf in enumerate(cash_flows))

def project_outcome(project):
    roll = random.randint(1, 6)
    if project["risk"] == "high":
        roll -= 1
    if roll <= 2:
        modifier = 0.75
    elif roll <= 4:
        modifier = 1.0
    else:
        modifier = 1.25
    return [cf * modifier for cf in project["cash_flows"]]

def invest(financing):
    player = st.session_state.player
    project = st.session_state.selected_project

    if project is None:
        st.warning("Please select a project.")
        return

    player["cash"] -= project["cost"]

    if financing == 'Debt':
        player["debt"] += project["cost"]
    else:
        player["cash"] -= project["cost"]

    if financing == 'Equity':
        player["equity_projects"] += 1
    elif financing == 'VC':
        player["vc_risk"] = True

    player["projects"].append(project)
    cash_flows = project_outcome(project)
    npv_realized = calculate_npv(cash_flows)
    if financing == 'Equity':
        npv_realized *= 0.8

    player["npv_total"] += npv_realized
    player["cash"] += sum(cash_flows)

    st.success(
        f"**Project Complete!**\n\n"
        f"- Realized NPV: ${npv_realized:,.2f}\n"
        f"- Remaining Cash: ${player['cash']:,.2f}\n"
        f"- Total Debt: ${player['debt']:,.2f}"
    )

    if player["vc_risk"]:
        player["cash"] -= 5_000_000
        st.error("VC Risk Penalty: -$5,000,000.00")
        player["vc_risk"] = False

    if player["debt"] > 0:
        interest = player["debt"] * 0.05
        player["cash"] -= interest
        st.error(f"Interest Paid: -${interest:,.2f}")

    st.session_state.selected_project = None
    st.session_state.round_number += 1

    if st.session_state.round_number > 5:
        final_npv = player["npv_total"]
        liquidity = player["cash"] / (player["debt"] if player["debt"] > 0 else 1)
        st.info(
            f"### 🏁 Game Over 🏁\n\n"
            f"- Total NPV: ${final_npv:,.2f}\n"
            f"- Liquidity Ratio: {liquidity:.2f}"
        )
        st.button("Play Again", on_click=reset_game)

def reset_game():
    st.session_state.player = {
        "cash": 100_000_000,
        "projects": [],
        "debt": 0,
        "npv_total": 0,
        "equity_projects": 0,
        "vc_risk": False
    }
    st.session_state.round_number = 1
    st.session_state.selected_project = None
    st.session_state.projects = random.sample(all_projects, 3)

all_projects = [
    {"name": "AI Lending Platform", "cost": 30_000_000, "cash_flows": [15_000_000, 20_000_000, 25_000_000], "risk": "high", "sector": "AI"},
    {"name": "Payment Gateway", "cost": 25_000_000, "cash_flows": [10_000_000, 15_000_000, 20_000_000], "risk": "low", "sector": "Fintech"},
    {"name": "Cybersecurity Infrastructure", "cost": 20_000_000, "cash_flows": [8_000_000, 10_000_000, 12_000_000], "risk": "low", "sector": "Security"},
    {"name": "Blockchain Remittance App", "cost": 28_000_000, "cash_flows": [14_000_000, 18_000_000, 22_000_000], "risk": "high", "sector": "Blockchain"},
    {"name": "ESG Compliance Platform", "cost": 18_000_000, "cash_flows": [7_000_000, 9_000_000, 13_000_000], "risk": "low", "sector": "Sustainability"},
    {"name": "Digital Bank Expansion", "cost": 22_000_000, "cash_flows": [11_000_000, 13_000_000, 15_000_000], "risk": "medium", "sector": "Banking"}
]

st.title("💼 CFO Quest: Capital Budgeting Challenge")
st.header(f"Round {st.session_state.round_number}")
st.markdown(f"**Cash:** ${st.session_state.player['cash']:,.2f}  \n**Debt:** ${st.session_state.player['debt']:,.2f}  \n**Total NPV:** ${st.session_state.player['npv_total']:,.2f}")

for i, proj in enumerate(st.session_state.projects):
    if st.button(f"{proj['name']} (${proj['cost']:,})", key=f"proj{i}"):
        st.session_state.selected_project = proj

if st.session_state.selected_project:
    proj = st.session_state.selected_project
    npv = calculate_npv(proj["cash_flows"])
    st.info(
        f"**Selected Project:** {proj['name']}\n\n"
        f"- Cost: ${proj['cost']:,}\n"
        f"- Estimated NPV: ${npv:,.2f}"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Invest with Debt", on_click=invest, args=("Debt",))
    with col2:
        st.button("Invest with Equity", on_click=invest, args=("Equity",))
    with col3:
        st.button("Invest with VC", on_click=invest, args=("VC",))
