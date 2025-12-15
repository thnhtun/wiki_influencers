import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import os
import numpy as np
try:
    from streamlit_plotly_events import plotly_events
    _PLOTLY_EVENTS_AVAILABLE = True
except Exception:
    _PLOTLY_EVENTS_AVAILABLE = False

# ================= CẤU HÌNH TRANG WEB =================
st.set_page_config(
    layout="wide", 
    page_title="Social Network Analysis", 
    page_icon="🌐",
    initial_sidebar_state="collapsed"
)
pd.set_option("styler.render.max_elements", 2000000)

# --- CSS: LIGHT THEME (ĐÃ CHUYỂN TỪ DARK) ---
st.markdown("""
    <style>
        /* Main App Background - Light Theme */
        .stApp { 
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%); 
            color: #0f172a; 
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] { display: none; }
        
        /* Custom Header - Light theme with subtle shadow */
        .custom-header { 
            background: rgba(255, 255, 255, 0.98); 
            border-bottom: 1px solid #e5e7eb; 
            padding: 1.5rem 2rem; 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            backdrop-filter: blur(10px); 
            margin-bottom: 0; 
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        /* Modern gradient icon background */
        .header-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 25px;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
        }
        .header-title { 
            font-size: 2rem; 
            font-weight: 700; 
            color: #0f172a; /* Dark Text */
            margin: 0; 
            line-height: 1.2; 
        }
        
        .header-subtitle { 
            font-size: 0.8rem; 
            color: #64748b; /* Gray Text */
            margin: 0; 
        }
        
        .header-right {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #64748b;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .realtime-pulse {
            width: 6px;
            height: 6px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(16, 185, 129, 0.6); }
            50% { opacity: 0.5; box-shadow: 0 0 12px rgba(16, 185, 129, 0.8); }
        }
        
        /* User Profile Card - Light theme with border */
        .user-card { 
            background: rgba(255, 255, 255, 0.95); /* White */
            border: 2px solid #e5e7eb; /* Light Border */
            border-radius: 16px; 
            padding: 2rem; 
            margin: 2rem; 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }
        
        .user-card:hover {
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
            transform: translateY(-2px);
            border-color: #c7d2fe;
        }
        
        .user-left {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        
        /* Modern shield icon with vibrant gradient */
        .user-shield { 
            width: 56px; 
            height: 56px; 
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
            border-radius: 12px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 28px; 
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
        }
        
        .user-name { 
            font-size: 1.75rem; 
            font-weight: 700; 
            color: #0f172a; /* Dark Text */
            margin: 0 0 0.25rem 0; 
        }
        
        .user-subtitle { 
            font-size: 0.85rem; 
            color: #64748b; /* Gray Text */
            margin: 0; 
        }
        
        .user-right {
            text-align: right;
        }
        
        .user-right-label {
            font-size: 0.8rem;
            color: #64748b; /* Gray Text */
            margin: 0 0 0.25rem 0;
        }
        
        .user-right-value {
            font-size: 2rem;
            font-weight: 700;
            color: #0f172a; /* Dark Text */
            margin: 0;
        }
        
        /* Role Badges */
        .role-badge { 
            display: inline-block; 
            padding: 5px 14px; 
            border-radius: 16px; 
            font-weight: 600; 
            font-size: 0.8rem; 
            margin-top: 0.5rem; 
        }
        
        .role-mentor { 
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
            color: white; 
            box-shadow: 0 2px 8px rgba(245, 87, 108, 0.3);
        }
        .role-moderator { 
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
            color: white; 
            box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3);
        }
        .role-both { 
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
            color: white; 
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }
        .role-normal { 
            background: #e5e7eb; /* Light Gray Background */
            color: #64748b; /* Dark Gray Text */
        }
        
        /* Metric Cards - Light theme WITH BORDERS */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.9); /* White Background */
            border: 2px solid #e5e7eb; /* Light Border */
            border-radius: 16px;
            padding: 1.5rem 1.25rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
            border-color: #c7d2fe;
        }
        
        [data-testid="stMetricLabel"] { 
            color: #64748b !important; 
            font-size: 0.85rem !important; 
            font-weight: 600 !important; 
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        [data-testid="stMetricValue"] { 
            color: #0f172a !important; /* Dark Text */
            font-size: 1.8rem !important; 
            font-weight: 700 !important; 
            margin: 0.5rem 0; 
        }
        
        [data-testid="stMetricDelta"] { 
            color: #64748b !important; /* Dark Text */
            font-size: 0.75rem !important; 
            background: rgba(99, 102, 241, 0.1); /* Light Purple Background */
            padding: 3px 8px; 
            border-radius: 6px; 
            font-weight: 600;
        }
        
        [data-testid="stMetricDelta"] svg { 
            display: none; 
        }
        
        /* Network Graph Sections - Light theme with borders */
        .network-section {
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid #e5e7eb;
            border-radius: 16px;
            padding: 1.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
            overflow: hidden;
            width: 100%;
            max-width: 100%;
            box-sizing: border-box;
        }
        
        /* Wrap all content inside network section */
        .network-content-wrapper {
            width: 100%;
            max-width: 100%;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            box-sizing: border-box;
        }
        
        .network-section .stPlotlyChart {
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden !important;
        }
        
        /* Streamlit container within network section */
        .network-section [data-testid="stVerticalBlock"] {
            width: 100% !important;
            max-width: 100% !important;
            gap: 0 !important;
            overflow: hidden !important;
        }
        
        /* Ensure Plotly charts stay within container */
        .network-section .js-plotly-plot {
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }
        
        .network-section .plotly {
            width: 100% !important;
            max-width: 100% !important;
            overflow: hidden !important;
        }
        
        .network-section .main-svg {
            width: 100% !important;
            max-width: 100% !important;
        }
        
        .network-section svg {
            max-width: 100% !important;
            width: 100% !important;
            height: auto !important;
        }
        
        .network-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.2rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.5rem;
            width: 100%;
        }
        
        .network-desc {
            font-size: 0.8rem;
            color: #64748b;
            margin-bottom: 1rem;
            width: 100%;
        }
        
        .neighbor-count {
            display: inline-block;
            background: rgba(99, 102, 241, 0.1);
            color: #6366f1;
            border: 1px solid rgba(99, 102, 241, 0.2);
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        
        /* Input & Selectbox - Light theme */
        .stTextInput > div > div > input,
        .stSelectbox > div > div {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            color: #0f172a;
            padding: 0.5rem 0.8rem;
            font-size: 0.9rem;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus {
            border-color: #7c3aed;
            box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
        }
        
        /* Selectbox label styling */
        .stSelectbox label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #0f172a;
            margin-bottom: 0.5rem;
        }
        
        /* Download Buttons */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            box-shadow: 0 4px 16px rgba(124, 58, 237, 0.25);
            transition: all 0.3s ease;
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%);
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.35);
            transform: translateY(-2px);
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6, p {
            color: #0f172a !important; /* Dark Text */
        }
        
        /* Info/Warning boxes */
        .stAlert {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            color: #1e40af;
        }
        
        /* Search Section */
        .search-section {
            padding: 1.5rem 3rem;
            background: transparent;
            border-bottom: none;
            margin-bottom: 1rem;
        }
        
        /* Navigation + Search Bar Container */
        .nav-search-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 3rem;
            background: white;
            margin-bottom: 1rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .nav-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .nav-right {
            display: flex;
            align-items: center;
            gap: 1rem;
            flex: 1;
            max-width: 600px;
            margin-left: 2rem;
        }
        
        /* Radio buttons styling - Force horizontal layout */
        [role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 0.75rem !important;
            align-items: center !important;
        }
        
        [role="radiogroup"] > label {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 0.5rem !important;
            background: transparent;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            white-space: nowrap;
            margin: 0 !important;
        }
        
        [role="radiogroup"] > label:hover {
            background: rgba(124, 58, 237, 0.1);
        }
        
        [role="radiogroup"] > label > div {
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
        }
        
        /* Hide the default radio circle or make it inline */
        [role="radiogroup"] > label > div:first-child {
            margin: 0 !important;
        }
        
        /* Navigation Buttons Styling - Inactive State */
        .stButton > button {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            color: #64748b;
            padding: 0.6rem 1rem;
            font-weight: 700;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            white-space: nowrap;
        }
        
        .stButton > button:hover {
            border-color: #7c3aed;
            color: #7c3aed;
            background: rgba(124, 58, 237, 0.05);
            transform: translateY(-1px);
        }
        
        /* Navigation Buttons - Active State (Primary type) */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%) !important;
            border: 2px solid #7c3aed !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
            font-weight: 700 !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%) !important;
            box-shadow: 0 6px 16px rgba(124, 58, 237, 0.4) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Search Button Styling - để phân biệt với nav buttons */
        div[data-testid="column"]:last-child .stButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
            font-weight: 700 !important;
            padding: 0.5rem 1.2rem !important;
        }
        
        div[data-testid="column"]:last-child .stButton > button:hover {
            background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Fix Plotly Font/Background */
        .js-plotly-plot .plotly .modebar {
            color: #0f172a !important; /* Dark Modebar Icon */
        }

    </style>
""", unsafe_allow_html=True)

# Tên file dữ liệu gốc và file cache
INPUT_FILE = 'leiden_seed.csv' 
CACHE_FILE = 'analysis_cache.csv' # File cache mới

# ================= 1. HÀM LOAD DỮ LIỆU & TÍNH TOÁN (CÓ CACHE FILE) =================
@st.cache_data
def load_and_process_data():
    # --- 1. Tải đồ thị G (Luôn cần cho việc vẽ) ---
    if not os.path.exists(INPUT_FILE):
        return None, None
    try:
        df = pd.read_csv(INPUT_FILE, header=None, names=['source', 'target'])
        G = nx.from_pandas_edgelist(df, 'source', 'target', create_using=nx.DiGraph())
    except:
        return None, None

    # --- 2. KIỂM TRA FILE CACHE KẾT QUẢ TÍNH TOÁN ---
    if os.path.exists(CACHE_FILE):
        try:
            df_metrics = pd.read_csv(CACHE_FILE)
            return G, df_metrics
        except Exception as e:
            st.warning(f"Lỗi khi đọc file cache: {e}. Đang tính toán lại từ đầu (sẽ mất thêm thời gian).")
            # Tiếp tục xuống phần tính toán nếu cache lỗi

    # --- 3. TÍNH TOÁN LẦN ĐẦU (NẾU CACHE KHÔNG TỒN TẠI) ---
    st.warning("⏳ Lần chạy đầu tiên: Đang tính toán PageRank, HITS và các chỉ số phức tạp...")
    
    degree_dict = dict(G.degree()); in_degree_dict = dict(G.in_degree()); out_degree_dict = dict(G.out_degree())
    try: pagerank_dict = nx.pagerank(G)
    except: pagerank_dict = {n: 0 for n in G.nodes()}
    try: hubs, authorities = nx.hits(G, max_iter=100, tol=1e-06)
    except: hubs = {n: 0 for n in G.nodes()}; authorities = {n: 0 for n in G.nodes()}
        
    reciprocity_dict = nx.reciprocity(G, G.nodes())
    G_undirected = G.to_undirected()
    clustering_dict = nx.clustering(G_undirected)
    triangles_dict = nx.triangles(G_undirected)
    
    # TỔNG HỢP DATAFRAME
    nodes_data = []
    for node in G.nodes():
        nodes_data.append({
            'User': node, 'PageRank': pagerank_dict.get(node, 0), 'Authority': authorities.get(node, 0),
            'HITS Hub': hubs.get(node, 0), 'Reciprocity': reciprocity_dict.get(node, 0),
            'Triangles (Undirected)': triangles_dict.get(node, 0), 'Clustering (Undirected)': clustering_dict.get(node, 0),
            'In-Degree': in_degree_dict.get(node, 0), 'Out-Degree': out_degree_dict.get(node, 0),
            'Degree': degree_dict.get(node, 0)
        })
    df_metrics = pd.DataFrame(nodes_data)
    
    # CHUẨN HÓA & TÍNH ĐIỂM TỔNG HỢP
    cols_to_normalize = ['PageRank', 'Authority', 'HITS Hub', 'Reciprocity', 'Clustering (Undirected)', 'Triangles (Undirected)', 'In-Degree', 'Out-Degree', 'Degree']
    df_norm = df_metrics.copy()
    for col in cols_to_normalize:
        min_val = df_norm[col].min(); max_val = df_norm[col].max()
        df_norm[f'Norm_{col}'] = (df_norm[col] - min_val) / (max_val - min_val) if max_val != min_val else 0
            
    df_metrics['Mentor Score'] = ( 0.4 * df_norm['Norm_Authority'] + 0.3 * df_norm['Norm_In-Degree'] + 0.3 * df_norm['Norm_Clustering (Undirected)'] )
    df_metrics['Moderator Score'] = ( 0.4 * df_norm['Norm_PageRank'] + 0.3 * df_norm['Norm_HITS Hub'] + 0.3 * df_norm['Norm_Out-Degree'] )
    
    # PHÂN LOẠI ROLE
    mentor_threshold = df_metrics['Mentor Score'].quantile(0.95); mod_threshold = df_metrics['Moderator Score'].quantile(0.95)
    def assign_role(row):
        is_mentor = row['Mentor Score'] > mentor_threshold; is_mod = row['Moderator Score'] > mod_threshold
        if is_mentor and is_mod: return "Mentor + Moderator"
        elif is_mentor: return "Mentor"
        elif is_mod: return "Moderator"
        else: return "Normal User"
    df_metrics['Role'] = df_metrics.apply(assign_role, axis=1)
    
    # TÍNH THU HANG (RANK)
    df_metrics['Rank_Degree'] = df_metrics['Degree'].rank(ascending=False, method='min')
    df_metrics['Rank_PR'] = df_metrics['PageRank'].rank(ascending=False, method='min')
    df_metrics['Rank_Auth'] = df_metrics['Authority'].rank(ascending=False, method='min')
    df_metrics['Rank_Hub'] = df_metrics['HITS Hub'].rank(ascending=False, method='min')
    
    df_metrics = df_metrics.sort_values(by='PageRank', ascending=False).reset_index(drop=True)
    
    # --- 4. LƯU KẾT QUẢ VÀO FILE CACHE ---
    try:
        df_metrics.to_csv(CACHE_FILE, index=False)
        st.success(f"💾 Đã hoàn tất tính toán và lưu kết quả vào file cache: '{CACHE_FILE}'.")
    except Exception as e:
        st.error(f"❌ Không thể lưu file cache: {CACHE_FILE}. Lỗi: {e}")
    
    return G, df_metrics

# ================= CÁC HÀM VẼ ĐỒ THỊ (Đã sửa Plotly để khớp Light Theme) =================
def add_arrows_to_graph(fig, G, pos):
    for edge in G.edges():
        if edge[0] in pos and edge[1] in pos:
            start, end = pos[edge[0]], pos[edge[1]]
            fig.add_annotation(x=end[0], y=end[1], ax=start[0], ay=start[1], xref='x', yref='y', axref='x', ayref='y', text="", showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=1.5, arrowcolor="rgba(99, 102, 241, 0.3)", standoff=10, startstandoff=10)
    return fig

def draw_ego_graph_pagerank(G, df_metrics, selected_node):
    try: neighbors = list(G.successors(selected_node)) + list(G.predecessors(selected_node)); neighbors = list(set(neighbors))
    except: neighbors = []
    if not neighbors: return None
    neighbor_df = df_metrics[df_metrics['User'].isin(neighbors)]
    top_neighbors = neighbor_df.sort_values(by='PageRank', ascending=False).head(20)
    nodes_to_draw = [selected_node] + top_neighbors['User'].tolist()
    H = G.subgraph(nodes_to_draw)
    pos = nx.spring_layout(H, seed=42, k=0.5)
    
    node_x, node_y, node_text, node_size, node_color, node_ids = [], [], [], [], [], []
    pr_map = df_metrics.set_index('User')['PageRank'].to_dict()
    max_pr = max(pr_map.values()) if pr_map else 1
    
    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y); node_ids.append(node)
        pr_val = pr_map.get(node, 0)
        # Phân biệt màu: Node chính màu cam/vàng, neighbors màu xanh gradient
        if node == selected_node:
            node_color.append('#f59e0b'); base_size = 40; node_text.append(f"<b>{node} (YOU)</b><br>PR: {pr_val:.5f}")
        else:
            # Gradient xanh dương theo PageRank: từ nhạt (#93c5fd) đến đậm (#1e40af)
            intensity = pr_val / max_pr
            if intensity > 0.7:
                node_color.append('#1e40af')  # Xanh đậm
            elif intensity > 0.4:
                node_color.append('#3b82f6')  # Xanh vừa
            else:
                node_color.append('#93c5fd')  # Xanh nhạt
            base_size = 12 + (pr_val / max_pr * 28)
            node_text.append(f"<b>{node}</b><br>PR: {pr_val:.5f}")
        node_size.append(base_size)

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', text=node_text, customdata=node_ids, marker=dict(color=node_color, size=node_size, line=dict(width=3, color='rgba(255, 255, 255, 0.8)'), opacity=0.95))
    
    fig = go.Figure(data=[node_trace], layout=go.Layout(title=None, showlegend=False, hovermode='closest', margin=dict(b=10, l=10, r=10, t=10), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, zerolinecolor='#aaa'), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, zerolinecolor='#aaa'), width=None, height=400, paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(249,250,251,0.5)', autosize=False))
    fig = add_arrows_to_graph(fig, H, pos)
    return fig

def draw_ego_graph_hits(G, df_metrics, selected_node):
    try: neighbors = list(G.successors(selected_node)) + list(G.predecessors(selected_node)); neighbors = list(set(neighbors))
    except: neighbors = []
    if not neighbors: return None
    neighbor_df = df_metrics[df_metrics['User'].isin(neighbors)]
    top_neighbors = neighbor_df.sort_values(by='Authority', ascending=False).head(20)
    nodes_to_draw = [selected_node] + top_neighbors['User'].tolist()
    H = G.subgraph(nodes_to_draw)
    pos = nx.spring_layout(H, seed=99, k=0.5)
    
    node_x, node_y, node_text, node_size, node_color, node_ids = [], [], [], [], [], []
    auth_map = df_metrics.set_index('User')['Authority'].to_dict()
    max_auth = max(auth_map.values()) if auth_map else 1
    
    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y); node_ids.append(node)
        auth_val = auth_map.get(node, 0)
        # Phân biệt màu: Node chính màu cam/vàng, neighbors màu xanh lục/cyan gradient
        if node == selected_node:
            node_color.append('#f59e0b'); base_size = 40; node_text.append(f"<b>{node} (YOU)</b><br>Auth: {auth_val:.5f}")
        else:
            # Gradient xanh lục/cyan theo Authority: từ nhạt (#67e8f9) đến đậm (#0e7490)
            intensity = auth_val / max_auth
            if intensity > 0.7:
                node_color.append('#0e7490')  # Cyan đậm
            elif intensity > 0.4:
                node_color.append('#06b6d4')  # Cyan vừa
            else:
                node_color.append('#67e8f9')  # Cyan nhạt
            base_size = 12 + (auth_val / max_auth * 28)
            node_text.append(f"<b>{node}</b><br>Auth: {auth_val:.5f}")
        node_size.append(base_size)

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', text=node_text, customdata=node_ids, marker=dict(color=node_color, size=node_size, line=dict(width=3, color='rgba(255, 255, 255, 0.8)'), opacity=0.95))
    fig = go.Figure(data=[node_trace], layout=go.Layout(title=None, showlegend=False, hovermode='closest', margin=dict(b=10, l=10, r=10, t=10), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, zerolinecolor='#aaa'), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, zerolinecolor='#aaa'), width=None, height=400, paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(249,250,251,0.5)', autosize=False))
    fig = add_arrows_to_graph(fig, H, pos)
    return fig

def draw_main_network(G, df_top, selected_node, view_mode):
    """Vẽ đồ thị mạng chính với top 200 nodes, kích thước và màu sắc theo thuật toán được chọn"""
    # Chọn top 200 nodes theo thuật toán
    if view_mode == "PageRank":
        top_nodes = df_top.sort_values(by="PageRank", ascending=False).head(200)['User'].tolist()
        metric_col = 'PageRank'
        title_text = 'Global Network Map - Xếp hạng theo PageRank'
        color_high = '#4f46e5'  # Indigo đậm cho PR cao
        color_low = '#c7d2fe'   # Indigo nhạt cho PR thấp
    else:  # HITS
        top_nodes = df_top.sort_values(by="Authority", ascending=False).head(200)['User'].tolist()
        metric_col = 'Authority'
        title_text = 'Global Network Map - Xếp hạng theo HITS Authority'
        color_high = '#059669'  # Emerald đậm cho Authority cao
        color_low = '#a7f3d0'   # Emerald nhạt cho Authority thấp
    
    # Đảm bảo selected_node luôn có trong graph
    if selected_node and selected_node not in top_nodes: 
        top_nodes.append(selected_node)
    
    H = G.subgraph(top_nodes)
    pos = nx.spring_layout(H, seed=42, k=0.2, iterations=50)
    
    # Vẽ edges
    edge_x, edge_y = [], []
    for edge in H.edges():
        if edge[0] in pos and edge[1] in pos:
            x0, y0 = pos[edge[0]]; x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, 
        line=dict(width=0.5, color='rgba(99, 102, 241, 0.12)'), 
        hoverinfo='none', mode='lines'
    )
    
    # Tính toán metrics
    node_x, node_y, node_text, node_size, node_color, node_ids = [], [], [], [], [], []
    metric_map = df_top.set_index('User').to_dict('index')
    
    # Tính min/max cho normalization
    metric_values = [metric_map.get(n, {}).get(metric_col, 0) for n in top_nodes]
    max_metric = max(metric_values) if metric_values else 1
    min_metric = min(metric_values) if metric_values else 0
    range_metric = max_metric - min_metric if max_metric != min_metric else 1
    
    # Threshold cho influencer (top 5% theo Degree)
    degree_threshold = df_top['Degree'].quantile(0.95)

    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_ids.append(node)
        info = metric_map.get(node, {'Degree': 0, 'PageRank': 0, 'Authority': 0, 'HITS Hub': 0})
        metric_val = info.get(metric_col, 0)
        
        # Normalized value (0-1) cho size và color
        norm_val = (metric_val - min_metric) / range_metric
        
        # Node được chọn - MÀU ĐỎ NỔI BẬT
        if node == selected_node:
            node_color.append('#ff0000')  # Đỏ tươi
            node_size.append(70)  # To nhất
            node_text.append(
                f"<b>🔴 {node} (ĐANG CHỌN)</b><br>"
                f"<b>PageRank:</b> {info['PageRank']:.6f}<br>"
                f"<b>Authority (HITS):</b> {info['Authority']:.6f}<br>"
                f"<b>Hub (HITS):</b> {info.get('HITS Hub', 0):.6f}<br>"
                f"<b>Degree:</b> {info['Degree']}"
            )
        else:
            # Size: 10-45 dựa vào normalized value
            size = 10 + norm_val * 35
            node_size.append(size)
            
            # Color: gradient từ nhạt đến đậm (KHÔNG dùng colorscale)
            if view_mode == "PageRank":
                # Gradient tím: nhạt → đậm
                if norm_val > 0.8:
                    node_color.append('#3730a3')  # Indigo rất đậm
                elif norm_val > 0.6:
                    node_color.append('#4f46e5')  # Indigo đậm
                elif norm_val > 0.4:
                    node_color.append('#6366f1')  # Indigo vừa
                elif norm_val > 0.2:
                    node_color.append('#818cf8')  # Indigo nhạt
                else:
                    node_color.append('#c7d2fe')  # Indigo rất nhạt
            else:  # HITS
                # Gradient xanh lá: nhạt → đậm
                if norm_val > 0.8:
                    node_color.append('#047857')  # Emerald rất đậm
                elif norm_val > 0.6:
                    node_color.append('#059669')  # Emerald đậm
                elif norm_val > 0.4:
                    node_color.append('#10b981')  # Emerald vừa
                elif norm_val > 0.2:
                    node_color.append('#34d399')  # Emerald nhạt
                else:
                    node_color.append('#a7f3d0')  # Emerald rất nhạt
            
            # Hover text
            deg = info.get('Degree', 0)
            is_influencer = "⭐ INFLUENCER" if deg >= degree_threshold else ""
            if view_mode == "PageRank":
                rank_info = f"<b>📊 PageRank:</b> {info['PageRank']:.6f}"
            else:
                rank_info = f"<b>📊 Authority:</b> {info['Authority']:.6f}"
            
            node_text.append(
                f"<b>{node}</b> {is_influencer}<br>"
                f"{rank_info}<br>"
                f"<b>Degree:</b> {info['Degree']}"
            )

    node_trace = go.Scatter(
        x=node_x, y=node_y, 
        mode='markers', 
        hoverinfo='text', 
        text=node_text, 
        customdata=node_ids,
        marker=dict(
            showscale=False,  # Bỏ colorbar vì dùng màu tùy chỉnh
            color=node_color,  # Dùng list màu tùy chỉnh
            size=node_size, 
            line=dict(width=0),  # BỎ VIỀN
            opacity=0.9
        )
    )
    
    # Legend annotation - cập nhật
    legend_text = (
        f"📐 Kích thước = {metric_col}<br>"
        f"🎨 Màu đậm = Giá trị cao<br>"
        f"🔴 Đỏ = Node đang chọn"
    )
    
    fig = go.Figure(
        data=[edge_trace, node_trace], 
        layout=go.Layout(
            title=dict(
                text=title_text, 
                font=dict(size=18, color='#0f172a', family='Arial Black'),
                x=0.02
            ),
            showlegend=False, 
            hovermode='closest', 
            margin=dict(b=20, l=5, r=5, t=60), 
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
            paper_bgcolor='rgba(255,255,255,0)', 
            plot_bgcolor='rgba(249,250,251,0.5)', 
            height=650,
            annotations=[
                dict(
                    text=legend_text,
                    showarrow=False,
                    xref='paper', yref='paper',
                    x=0.02, y=0.98,
                    xanchor='left', yanchor='top',
                    font=dict(size=11, color='#64748b'),
                    bgcolor='rgba(255,255,255,0.85)',
                    bordercolor='#e5e7eb',
                    borderwidth=1,
                    borderpad=6
                )
            ]
        )
    )
    return fig

# ================= GIAO DIỆN: DASHBOARD CÁ NHÂN (Giữ nguyên cấu trúc HTML) =================
def render_dashboard(G, df_metrics, selected_user, total_users, view_mode):
    user_info = df_metrics[df_metrics['User'] == selected_user].iloc[0]

    # User Profile Card với nhiều thông tin hơn
    st.markdown(f"""
    <div class="user-card">
        <div class="user-left">
            <div>
                <div class="user-name">User {selected_user}</div>
                <div class="user-subtitle">Hồ sơ người dùng chi tiết</div>
                {get_role_badge(user_info['Role'])}
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; flex: 1; margin-left: 3rem;">
            <div style="text-align: center;">
                <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; margin-bottom: 0.25rem;">TỔNG NGƯỜI DÙNG</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #0f172a;">{total_users:,}</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; margin-bottom: 0.25rem;">IN-DEGREE</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #3b82f6;">{int(user_info['In-Degree'])}</div>
                <div style="font-size: 0.7rem; color: #64748b;">Người theo dõi</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.75rem; color: #64748b; font-weight: 600; margin-bottom: 0.25rem;">OUT-DEGREE</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #8b5cf6;">{int(user_info['Out-Degree'])}</div>
                <div style="font-size: 0.7rem; color: #64748b;">Đang theo dõi</div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-left: 2rem; padding-left: 2rem; border-left: 2px solid #e5e7eb;">
            <div style="text-align: center;">
                <div style="font-size: 0.7rem; color: #64748b; font-weight: 600; margin-bottom: 0.25rem;">RECIPROCITY</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #10b981;">{user_info['Reciprocity']:.3f}</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 0.7rem; color: #64748b; font-weight: 600; margin-bottom: 0.25rem;">CLUSTERING</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #f59e0b;">{user_info['Clustering (Undirected)']:.3f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==================== METRICS CARDS ====================
    st.markdown('<div style="padding: 0 2rem; margin-top: 1.5rem;">', unsafe_allow_html=True)
    col_metrics = st.columns(4)
    
    with col_metrics[0]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">📊 Degree</div>
            <div data-testid="stMetricValue">{int(user_info['Degree'])}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_Degree'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_metrics[1]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">🔵 PageRank</div>
            <div data-testid="stMetricValue">{user_info['PageRank']:.6f}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_PR'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_metrics[2]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">🟢 Authority</div>
            <div data-testid="stMetricValue">{user_info['Authority']:.6f}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_Auth'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_metrics[3]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">🔶 Hub Score</div>
            <div data-testid="stMetricValue">{user_info['HITS Hub']:.6f}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_Hub'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 2rem; margin-top: 2rem;"><hr style="border: 1px solid #e5e7eb;"/></div>', unsafe_allow_html=True)

    # ==================== EGO GRAPHS ====================
    st.markdown('<div style="padding: 0 2rem;">', unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="medium")
    
    with col_left:
        with st.container():
            st.markdown('''
            <div class="network-section">
                <div class="network-title">PageRank Network</div>
                <div class="network-desc">Mạng lưới uy tín (Có hướng)</div>
            ''', unsafe_allow_html=True)
            
            try:
                neighbors = list(G.successors(selected_user)) + list(G.predecessors(selected_user))
                neighbors = list(set(neighbors))
                st.markdown(f'<div class="neighbor-count">{len(neighbors)} neighbors</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="neighbor-count">0 neighbors</div>', unsafe_allow_html=True)
            
            fig_pr = draw_ego_graph_pagerank(G, df_metrics, selected_user)
            if fig_pr:
                if _PLOTLY_EVENTS_AVAILABLE:
                    events_pr = plotly_events(fig_pr, click_event=True, hover_event=False, select_event=False, override_height=400, override_width="100%")
                    if events_pr:
                        clicked_pr = events_pr[0]
                        new_user_pr = clicked_pr.get('customdata')
                        if new_user_pr:
                            st.session_state['user_selector'] = new_user_pr
                            st.rerun()
                else:
                    st.plotly_chart(fig_pr, use_container_width=False, config={'responsive': True, 'displayModeBar': True})
            else: 
                st.warning("⚠️ User cô lập - không có kết nối")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
    with col_right:
        with st.container():
            st.markdown('''
            <div class="network-section">
                <div class="network-title">HITS Network</div>
                <div class="network-desc">Mạng lưới chuyên gia (Có hướng)</div>
            ''', unsafe_allow_html=True)
            
            try:
                neighbors = list(G.successors(selected_user)) + list(G.predecessors(selected_user))
                neighbors = list(set(neighbors))
                st.markdown(f'<div class="neighbor-count">{len(neighbors)} neighbors</div>', unsafe_allow_html=True)
            except:
                st.markdown('<div class="neighbor-count">0 neighbors</div>', unsafe_allow_html=True)
            
            fig_hits = draw_ego_graph_hits(G, df_metrics, selected_user)
            if fig_hits:
                if _PLOTLY_EVENTS_AVAILABLE:
                    events_hits = plotly_events(fig_hits, click_event=True, hover_event=False, select_event=False, override_height=400, override_width="100%")
                    if events_hits:
                        clicked_hits = events_hits[0]
                        new_user_hits = clicked_hits.get('customdata')
                        if new_user_hits:
                            st.session_state['user_selector'] = new_user_hits
                            st.rerun()
                else:
                    st.plotly_chart(fig_hits, use_container_width=False, config={'responsive': True, 'displayModeBar': True})
            else: 
                st.warning("⚠️ User cô lập - không có kết nối")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== SO SÁNH PAGERANK VS HITS ====================
    st.markdown('<div style="padding: 0 2rem; margin-top: 2rem;"><hr style="border: 1px solid #e5e7eb;"/></div>', unsafe_allow_html=True)
    
    rank_pr = int(user_info['Rank_PR'])
    rank_auth = int(user_info['Rank_Auth'])
    percentile_pr = round((1 - rank_pr / total_users) * 100, 2)
    percentile_auth = round((1 - rank_auth / total_users) * 100, 2)
    
    diff_rank = rank_auth - rank_pr
    if diff_rank > 0:
        comparison_text = f"📈 Node này xếp hạng <b>cao hơn {abs(diff_rank)} bậc</b> theo PageRank so với HITS"
        comparison_color = "#6366f1"
    elif diff_rank < 0:
        comparison_text = f"📈 Node này xếp hạng <b>cao hơn {abs(diff_rank)} bậc</b> theo HITS so với PageRank"
        comparison_color = "#10b981"
    else:
        comparison_text = "⚖️ Node này có xếp hạng <b>tương đương</b> ở cả hai phương pháp"
        comparison_color = "#f59e0b"
    
    st.markdown(f"""
    <div style="padding: 0 2rem; margin-top: 1.5rem;">
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                    border: 2px solid #0ea5e9; border-radius: 16px; padding: 1.5rem;">
            <h3 style="margin: 0 0 1rem 0; color: #0369a1; display: flex; align-items: center; gap: 10px;">
                🔄 So sánh PageRank vs HITS
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1.5fr; gap: 1rem;">
                <div style="background: white; border-radius: 12px; padding: 1.2rem; border-left: 4px solid #6366f1;">
                    <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">🔵 PAGERANK</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #6366f1;">{user_info['PageRank']:.6f}</div>
                    <div style="font-size: 0.85rem; color: #0f172a; margin-top: 0.5rem;">
                        <b>Xếp hạng: #{rank_pr}</b> / {total_users:,}
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b;">Top {percentile_pr}%</div>
                </div>
                <div style="background: white; border-radius: 12px; padding: 1.2rem; border-left: 4px solid #10b981;">
                    <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">🟢 HITS AUTHORITY</div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: #10b981;">{user_info['Authority']:.6f}</div>
                    <div style="font-size: 0.85rem; color: #0f172a; margin-top: 0.5rem;">
                        <b>Xếp hạng: #{rank_auth}</b> / {total_users:,}
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b;">Top {percentile_auth}%</div>
                </div>
                <div style="display: flex; align-items: center; justify-content: center;">
                    <div style="background: {comparison_color}15; border-radius: 8px; padding: 1rem; text-align: center; width: 100%;">
                        <span style="color: {comparison_color}; font-size: 1rem;">{comparison_text}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================= GIAO DIỆN: BẢNG XẾP HẠNG (Giữ nguyên cấu trúc HTML) =================
def render_table_page(df_metrics):
    st.markdown("""
    <div class="custom-header" style="justify-content: start; gap: 20px;">
        <div class="header-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">📋</div>
        <div>
            <div class="header-title">Bảng xếp hạng cộng đồng</div>
            <div class="header-subtitle">Phân tích chuyên sâu tất cả Users trong mạng lưới - Xác định Leaders, Mentors, Moderators</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding: 1rem 2rem;">', unsafe_allow_html=True)
    
    # Thống kê tổng quan theo Role
    mentor_only = len(df_metrics[df_metrics["Role"] == "Mentor"])
    moderator_only = len(df_metrics[df_metrics["Role"] == "Moderator"])
    both_roles = len(df_metrics[df_metrics["Role"] == "Mentor + Moderator"])
    normal_users = len(df_metrics[df_metrics["Role"] == "Normal User"])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1: 
        st.markdown(f'''
        <div data-testid="metric-container" style="padding: 1rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748b;">👥 Tổng Users</div>
            <span style="font-size: 1.8rem; font-weight: 700; color: #0f172a;">{len(df_metrics):,}</span>
        </div>
        ''', unsafe_allow_html=True)
    with col2: 
        st.markdown(f'''
        <div data-testid="metric-container" style="padding: 1rem; text-align: center; border-left: 3px solid #f5576c;">
            <div style="font-size: 0.75rem; color: #64748b;">🎓 Mentors</div>
            <span style="font-size: 1.8rem; font-weight: 700; color: #f5576c;">{mentor_only}</span>
        </div>
        ''', unsafe_allow_html=True)
    with col3: 
        st.markdown(f'''
        <div data-testid="metric-container" style="padding: 1rem; text-align: center; border-left: 3px solid #4facfe;">
            <div style="font-size: 0.75rem; color: #64748b;">🛡️ Moderators</div>
            <span style="font-size: 1.8rem; font-weight: 700; color: #4facfe;">{moderator_only}</span>
        </div>
        ''', unsafe_allow_html=True)
    with col4: 
        st.markdown(f'''
        <div data-testid="metric-container" style="padding: 1rem; text-align: center; border-left: 3px solid #8b5cf6;">
            <div style="font-size: 0.75rem; color: #64748b;">👑 Leaders (Both)</div>
            <span style="font-size: 1.8rem; font-weight: 700; color: #8b5cf6;">{both_roles}</span>
        </div>
        ''', unsafe_allow_html=True)
    with col5: 
        st.markdown(f'''
        <div data-testid="metric-container" style="padding: 1rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #64748b;">👤 Normal Users</div>
            <span style="font-size: 1.8rem; font-weight: 700; color: #64748b;">{normal_users:,}</span>
        </div>
        ''', unsafe_allow_html=True)
    
    st.divider()
    
    # ==================== BỘ LỌC NÂNG CAO ====================
    st.markdown("### 🔍 Bộ lọc nâng cao")
    
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        role_options = ['Tất cả', 'Mentor + Moderator (Leaders)', 'Mentor', 'Moderator', 'Normal User']
        selected_role = st.selectbox('📌 Lọc theo Role', role_options, index=0)
    
    with col_filter2:
        sort_options = ['PageRank (cao → thấp)', 'Authority (cao → thấp)', 'Degree (cao → thấp)', 
                       'Mentor Score (cao → thấp)', 'Moderator Score (cao → thấp)']
        sort_by = st.selectbox('📊 Sắp xếp theo', sort_options, index=0)
    
    with col_filter3:
        top_n = st.slider('🔢 Hiển thị Top N', min_value=10, max_value=500, value=100, step=10)
    
    with col_filter4:
        show_influencers = st.checkbox('⭐ Chỉ hiện Influencers (Degree cao)', value=False)
    
    # Apply filters
    filtered_df = df_metrics.copy()
    
    # Role filter
    if selected_role == 'Mentor + Moderator (Leaders)':
        filtered_df = filtered_df[filtered_df['Role'] == 'Mentor + Moderator']
    elif selected_role != 'Tất cả':
        filtered_df = filtered_df[filtered_df['Role'] == selected_role]
    
    # Influencer filter
    if show_influencers:
        degree_threshold = df_metrics['Degree'].quantile(0.95)
        filtered_df = filtered_df[filtered_df['Degree'] >= degree_threshold]
    
    # Sort
    sort_map = {
        'PageRank (cao → thấp)': ('PageRank', False),
        'Authority (cao → thấp)': ('Authority', False),
        'Degree (cao → thấp)': ('Degree', False),
        'Mentor Score (cao → thấp)': ('Mentor Score', False),
        'Moderator Score (cao → thấp)': ('Moderator Score', False)
    }
    sort_col, sort_asc = sort_map[sort_by]
    filtered_df = filtered_df.sort_values(by=sort_col, ascending=sort_asc).head(top_n)
    
    st.markdown(f"**📋 Hiển thị {len(filtered_df)} / {len(df_metrics)} users**")
    
    # Chuẩn bị các cột để hiển thị
    display_cols = [
        'User', 'Role', 'Mentor Score', 'Moderator Score', 
        'PageRank', 'Authority', 'HITS Hub', 
        'Reciprocity', 'Triangles (Undirected)', 'Clustering (Undirected)', 
        'Degree', 'In-Degree', 'Out-Degree',
        'Rank_PR', 'Rank_Auth', 'Rank_Degree'
    ]
    
    # Hiển thị bảng với highlighting
    def highlight_role(val):
        if val == 'Mentor + Moderator':
            return 'background-color: rgba(139, 92, 246, 0.2); font-weight: bold;'
        elif val == 'Mentor':
            return 'background-color: rgba(245, 87, 108, 0.2);'
        elif val == 'Moderator':
            return 'background-color: rgba(79, 172, 254, 0.2);'
        return ''
    
    styled_df = filtered_df[display_cols].style.applymap(
        highlight_role, subset=['Role']
    ).format({
        'PageRank': '{:.6f}',
        'Authority': '{:.6f}',
        'HITS Hub': '{:.6f}',
        'Mentor Score': '{:.4f}',
        'Moderator Score': '{:.4f}',
        'Reciprocity': '{:.4f}',
        'Clustering (Undirected)': '{:.4f}',
        'Rank_PR': '{:.0f}',
        'Rank_Auth': '{:.0f}',
        'Rank_Degree': '{:.0f}'
    })
    
    st.dataframe(styled_df, use_container_width=True, height=500, hide_index=True)
    
    # ==================== TOP USERS SUMMARY ====================
    st.divider()
    st.markdown("### 🏆 Top Users theo từng tiêu chí")
    
    col_top1, col_top2, col_top3 = st.columns(3)
    
    with col_top1:
        st.markdown("#### 🔵 Top 5 PageRank")
        top_pr = df_metrics.nlargest(5, 'PageRank')[['User', 'PageRank', 'Role']]
        for i, row in top_pr.iterrows():
            medal = "🥇" if top_pr.index.get_loc(i) == 0 else "🥈" if top_pr.index.get_loc(i) == 1 else "🥉" if top_pr.index.get_loc(i) == 2 else "  "
            st.markdown(f"{medal} **{row['User']}** - {row['PageRank']:.6f}")
    
    with col_top2:
        st.markdown("#### 🟢 Top 5 HITS Authority")
        top_auth = df_metrics.nlargest(5, 'Authority')[['User', 'Authority', 'Role']]
        for i, row in top_auth.iterrows():
            medal = "🥇" if top_auth.index.get_loc(i) == 0 else "🥈" if top_auth.index.get_loc(i) == 1 else "🥉" if top_auth.index.get_loc(i) == 2 else "  "
            st.markdown(f"{medal} **{row['User']}** - {row['Authority']:.6f}")
    
    with col_top3:
        st.markdown("#### ⭐ Top 5 Influencers (Degree)")
        top_deg = df_metrics.nlargest(5, 'Degree')[['User', 'Degree', 'Role']]
        for i, row in top_deg.iterrows():
            medal = "🥇" if top_deg.index.get_loc(i) == 0 else "🥈" if top_deg.index.get_loc(i) == 1 else "🥉" if top_deg.index.get_loc(i) == 2 else "  "
            st.markdown(f"{medal} **{row['User']}** - {int(row['Degree'])} connections")
    
    # Download
    st.divider()
    csv = filtered_df[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button("📥 Tải xuống dữ liệu đã lọc (CSV)", csv, "social_network_filtered.csv", "text/csv")
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_role_badge(role):
    role_classes = {"Mentor + Moderator": "role-both", "Mentor": "role-mentor", "Moderator": "role-moderator", "Normal User": "role-normal"}
    role_class = role_classes.get(role, "role-normal")
    return f'<span class="role-badge {role_class}">{role}</span>'

# ================= MAIN APP =================
def main():
    st.markdown("""
    <div class="custom-header">
        <div class="header-left">
            <div class="header-icon">🌐</div>
            <div>
                <div class="header-title">SOCIAL NETWORK ANALYSIS</div>
                <div class="header-subtitle">Phân tích mạng xã hội - PageRank vs HITS Comparison</div>
            </div>
        </div>
        <div class="header-right">
            <div class="realtime-pulse"></div>
            Real-time
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner('⚙️ Đang tải dữ liệu và tính toán...'):
        G, df_metrics = load_and_process_data()

    if G is None:
        st.error(f"❌ Không tìm thấy file '{INPUT_FILE}'. Vui lòng đặt file vào cùng thư mục với script.")
        st.stop()

    # --- Navigation + Mode Selection ---
    st.markdown('<div style="padding: 0 3rem; margin-top: 1rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "📊 Dashboard Cá Nhân"
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "PageRank"
    
    # Navigation buttons
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])
    with nav_col1:
        is_dashboard_active = st.session_state.current_page == "📊 Dashboard Cá Nhân"
        dashboard_selected = st.button(
            "📊 Visualization",
            key="dashboard_btn",
            use_container_width=True,
            type="primary" if is_dashboard_active else "secondary"
        )
    with nav_col2:
        is_ranking_active = st.session_state.current_page == "🏆 Bảng Xếp Hạng"
        ranking_selected = st.button(
            "🏆 Bảng Xếp Hạng",
            key="ranking_btn",
            use_container_width=True,
            type="primary" if is_ranking_active else "secondary"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Xác định trang nào được chọn
    if dashboard_selected:
        st.session_state.current_page = "📊 Dashboard Cá Nhân"
        st.rerun()
    elif ranking_selected:
        st.session_state.current_page = "🏆 Bảng Xếp Hạng"
        st.rerun()
    
    page = st.session_state.current_page
    
    # --- Render content based on selected page ---
    if page == "📊 Dashboard Cá Nhân":
        # ==================== MODE SELECTION ====================
        st.markdown("""
        <div style="padding: 0 3rem; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); 
                        border: 2px solid #e5e7eb; border-radius: 12px; padding: 1rem 1.5rem;">
                <h4 style="margin: 0 0 0.5rem 0; color: #0f172a;">🔄 Chế độ Visualization</h4>
                <p style="margin: 0; color: #64748b; font-size: 0.85rem;">
                    Chọn thuật toán để xếp hạng và hiển thị đồ thị. Node sẽ có kích thước và màu sắc khác nhau dựa theo chỉ số của thuật toán được chọn.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_mode1, col_mode2, col_mode3 = st.columns([1, 1, 2])
        with col_mode1:
            pr_selected = st.button(
                "🔵 PageRank",
                key="pr_mode_btn",
                use_container_width=True,
                type="primary" if st.session_state.view_mode == "PageRank" else "secondary"
            )
        with col_mode2:
            hits_selected = st.button(
                "🟢 HITS Authority",
                key="hits_mode_btn",
                use_container_width=True,
                type="primary" if st.session_state.view_mode == "HITS" else "secondary"
            )
        with col_mode3:
            st.markdown(f"""
            <div style="padding: 0.5rem 1rem; background: {'#eef2ff' if st.session_state.view_mode == 'PageRank' else '#ecfdf5'}; 
                        border-radius: 8px; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2rem;">{'🔵' if st.session_state.view_mode == 'PageRank' else '🟢'}</span>
                <div>
                    <div style="font-weight: 600; color: #0f172a;">Đang xem: {st.session_state.view_mode}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">
                        {'Node có PageRank cao sẽ to và đậm hơn' if st.session_state.view_mode == 'PageRank' else 'Node có Authority cao sẽ to và đậm hơn'}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if pr_selected:
            st.session_state.view_mode = "PageRank"
            st.rerun()
        elif hits_selected:
            st.session_state.view_mode = "HITS"
            st.rerun()
        
        view_mode = st.session_state.view_mode
        
        st.markdown('<div style="padding: 0 3rem;"><hr style="border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0;"/></div>', unsafe_allow_html=True)
        
        # Initialize selected user from session
        selected_user = st.session_state.get('user_selector')

        # ==================== NODE SELECTION (Manual) ====================
        st.markdown('<div style="padding: 0 3rem; margin-bottom: 1rem;">', unsafe_allow_html=True)
        col_search1, col_search2, col_search3 = st.columns([2, 1, 1])
        
        with col_search1:
            # Dropdown để chọn node
            all_users = df_metrics['User'].tolist()
            # Tạo top users để hiển thị đầu tiên
            top_pr = df_metrics.nlargest(20, 'PageRank')['User'].tolist()
            
            search_user = st.selectbox(
                "🔍 Tìm kiếm / Chọn Node để xem chi tiết:",
                options=[None] + all_users,
                index=0 if selected_user is None else (all_users.index(selected_user) + 1 if selected_user in all_users else 0),
                format_func=lambda x: "-- Chọn một node --" if x is None else f"User {x}",
                key="node_search_dropdown"
            )
            
            if search_user and search_user != selected_user:
                st.session_state['user_selector'] = search_user
                st.rerun()
        
        with col_search2:
            # Quick select top PageRank
            st.markdown("**Top PageRank:**")
            top_pr_options = df_metrics.nlargest(5, 'PageRank')['User'].tolist()
            for i, user in enumerate(top_pr_options[:3]):
                if st.button(f"🥇 User {user}" if i == 0 else f"🥈 User {user}" if i == 1 else f"🥉 User {user}", key=f"quick_pr_{user}", use_container_width=True):
                    st.session_state['user_selector'] = user
                    st.rerun()
        
        with col_search3:
            # Quick select top HITS
            st.markdown("**Top HITS:**")
            top_hits_options = df_metrics.nlargest(5, 'Authority')['User'].tolist()
            for i, user in enumerate(top_hits_options[:3]):
                if st.button(f"🥇 User {user}" if i == 0 else f"🥈 User {user}" if i == 1 else f"🥉 User {user}", key=f"quick_hits_{user}", use_container_width=True):
                    st.session_state['user_selector'] = user
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Cập nhật selected_user sau khi search
        selected_user = st.session_state.get('user_selector')

        # ==================== MAIN GRAPH ====================
        st.markdown(f"""
        <div style="padding: 0 3rem;">
            <div class="network-section">
                <div class="network-title">
                    {'🔵' if view_mode == 'PageRank' else '🟢'} Global Network Map - Top 200 Nodes theo {view_mode}
                </div>
                <div class="network-desc">
                    👆 <b>Chọn node từ dropdown hoặc click trực tiếp trên đồ thị.</b> 
                    Node càng to và đậm = {view_mode} càng cao. Viền dày = Influencer (Degree cao).
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Render main graph
        fig_net = draw_main_network(G, df_metrics, selected_user, view_mode)
        
        if _PLOTLY_EVENTS_AVAILABLE:
            events = plotly_events(
                fig_net, 
                click_event=True, 
                hover_event=False, 
                select_event=False, 
                override_height=650, 
                override_width="100%"
            )
            if events:
                clicked = events[0]
                new_user = clicked.get('customdata')
                if new_user:
                    st.session_state['user_selector'] = new_user
                    st.rerun()
        else:
            st.plotly_chart(fig_net, use_container_width=True)

        # ==================== NODE DETAIL (if selected) ====================
        if selected_user:
            if selected_user in df_metrics['User'].values:
                st.markdown(f"""
                <div style="padding: 0 3rem; margin-top: 1rem;">
                    <div style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
                                border: 2px solid #22c55e; border-radius: 12px; padding: 1rem 1.5rem; 
                                display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 2rem;">✅</span>
                            <div>
                                <div style="font-weight: 700; color: #166534; font-size: 1.1rem;">Đã chọn: User {selected_user}</div>
                                <div style="color: #15803d; font-size: 0.85rem;">Xem thông tin chi tiết và so sánh PageRank vs HITS bên dưới</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                render_dashboard(G, df_metrics, selected_user, len(df_metrics), view_mode)
            else:
                st.warning(f"⚠️ User {selected_user} không tồn tại trong dữ liệu.")
                st.session_state['user_selector'] = None
        else:
            st.markdown("""
            <div style="padding: 2rem 3rem; text-align: center;">
                <div style="background: #fef3c7; border: 2px dashed #f59e0b; border-radius: 12px; padding: 2rem;">
                    <span style="font-size: 3rem;">👆</span>
                    <h3 style="color: #b45309; margin: 1rem 0 0.5rem 0;">Chọn một node để xem chi tiết</h3>
                    <p style="color: #92400e; margin: 0;">Sử dụng dropdown bên trên hoặc click trực tiếp vào node trên đồ thị</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        render_table_page(df_metrics)

        

if __name__ == "__main__":
    main()