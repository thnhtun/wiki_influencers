import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import os

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
    
    node_x, node_y, node_text, node_size, node_color = [], [], [], [], []
    pr_map = df_metrics.set_index('User')['PageRank'].to_dict()
    max_pr = max(pr_map.values()) if pr_map else 1
    
    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y)
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

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', text=node_text, marker=dict(color=node_color, size=node_size, line=dict(width=3, color='rgba(255, 255, 255, 0.8)'), opacity=0.95))
    
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
    
    node_x, node_y, node_text, node_size, node_color = [], [], [], [], []
    auth_map = df_metrics.set_index('User')['Authority'].to_dict()
    max_auth = max(auth_map.values()) if auth_map else 1
    
    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y)
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

    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', text=node_text, marker=dict(color=node_color, size=node_size, line=dict(width=3, color='rgba(255, 255, 255, 0.8)'), opacity=0.95))
    fig = go.Figure(data=[node_trace], layout=go.Layout(title=None, showlegend=False, hovermode='closest', margin=dict(b=10, l=10, r=10, t=10), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, zerolinecolor='#aaa'), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, zerolinecolor='#aaa'), width=None, height=400, paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(249,250,251,0.5)', autosize=False))
    fig = add_arrows_to_graph(fig, H, pos)
    return fig

def draw_main_network(G, df_top, selected_node):
    top_nodes = df_top.head(200)['User'].tolist()
    if selected_node not in top_nodes: top_nodes.append(selected_node)
    H = G.subgraph(top_nodes)
    pos = nx.spring_layout(H, seed=42, k=0.2, iterations=50)
    
    edge_x, edge_y = [], []
    for edge in H.edges():
        if edge[0] in pos and edge[1] in pos:
            x0, y0 = pos[edge[0]]; x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None]); edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=0.5, color='rgba(99, 102, 241, 0.15)'), hoverinfo='none', mode='lines')
    
    node_x, node_y, node_text, node_size, node_color = [], [], [], [], []
    metric_map = df_top.set_index('User').to_dict('index')
    max_pr_global = max([info.get('PageRank', 0) for info in metric_map.values()]) if metric_map else 1

    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y)
        info = metric_map.get(node, {'Degree': 0, 'PageRank': 0})
        pr_val = info['PageRank']
        
        # Phân biệt màu: Node chính màu cam, các node khác gradient xanh tím
        if node == selected_node:
            node_color.append('#f59e0b')  # Cam vàng cho node chính
            node_size.append(60)
            node_text.append(f"<b>{node} (YOU)</b><br>PR: {pr_val:.5f}<br>Degree: {info['Degree']}")
        else:
            # Gradient xanh tím theo PageRank
            intensity = pr_val / max_pr_global if max_pr_global > 0 else 0
            if intensity > 0.7:
                node_color.append('#6366f1')  # Tím đậm
            elif intensity > 0.4:
                node_color.append('#8b5cf6')  # Tím vừa
            elif intensity > 0.2:
                node_color.append('#a78bfa')  # Tím nhạt
            else:
                node_color.append('#c7d2fe')  # Tím rất nhạt
            
            size = 12 + (info['Degree'] * 0.08)
            node_size.append(min(size, 35))
            node_text.append(f"<b>{node}</b><br>PR: {pr_val:.5f}<br>Degree: {info['Degree']}")

    node_trace = go.Scatter(
        x=node_x, y=node_y, 
        mode='markers', 
        hoverinfo='text', 
        text=node_text, 
        marker=dict(
            showscale=False,  # Tắt colorbar vì dùng màu rời rạc
            color=node_color, 
            size=node_size, 
            line=dict(width=3, color='rgba(255, 255, 255, 0.8)'),
            opacity=0.9
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(title=dict(text=f'Global Network Map', font=dict(size=18, color='#0f172a', family='Arial Black')), showlegend=False, hovermode='closest', margin=dict(b=20, l=5, r=5, t=50), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), paper_bgcolor='rgba(255,255,255,0)', plot_bgcolor='rgba(249,250,251,0.5)', height=600))
    return fig

# ================= GIAO DIỆN: DASHBOARD CÁ NHÂN (Giữ nguyên cấu trúc HTML) =================
def render_dashboard(G, df_metrics, selected_user, total_users):
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
    
    col_metrics = st.columns(4)
    
    with col_metrics[0]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">Degree</div>
            <div data-testid="stMetricValue">{int(user_info['Degree'])}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_Degree'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_metrics[1]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">PageRank</div>
            <div data-testid="stMetricValue">{user_info['PageRank']:.6f}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_PR'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_metrics[2]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">Authority</div>
            <div data-testid="stMetricValue">{user_info['Authority']:.6f}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_Auth'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_metrics[3]:
        st.markdown(f"""
        <div data-testid="metric-container">
            <div data-testid="stMetricLabel">Hub Score</div>
            <div data-testid="stMetricValue">{user_info['HITS Hub']:.6f}</div>
            <div data-testid="stMetricDelta">Hạng #{int(user_info['Rank_Hub'])} / {total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 2rem; margin-top: 2rem;"><hr style="border: 1px solid #e5e7eb;"/></div>', unsafe_allow_html=True)

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
                st.plotly_chart(fig_hits, use_container_width=False, config={'responsive': True, 'displayModeBar': True})
            else: 
                st.warning("⚠️ User cô lập - không có kết nối")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="padding: 0 2rem; margin-top: 2rem;"><hr style="border: 1px solid #e5e7eb;"/></div>', unsafe_allow_html=True)
    
    with st.container():
        fig_net = draw_main_network(G, df_metrics, selected_user)
        st.plotly_chart(fig_net, use_container_width=True)


# ================= GIAO DIỆN: BẢNG XẾP HẠNG (Giữ nguyên cấu trúc HTML) =================
def render_table_page(df_metrics):
    st.markdown("""
    <div class="custom-header" style="justify-content: start; gap: 20px;">
        <div class="header-icon" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">📋</div>
        <div>
            <div class="header-title">Bảng xếp hạng cộng đồng</div>
            <div class="header-subtitle">Phân tích chuyên sâu tất cả Users trong mạng lưới.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding: 1rem 2rem;">', unsafe_allow_html=True)
    
    # Thống kê tổng quan
    col1, col2, col3 = st.columns(3)
    
    # Đếm riêng biệt từng role (chỉ đếm role đơn lẻ, không bao gồm "Mentor + Moderator")
    mentor_count = len(df_metrics[df_metrics["Role"] == "Mentor"])
    moderator_count = len(df_metrics[df_metrics["Role"] == "Moderator"])
    
    with col1: st.markdown(f'<div data-testid="metric-container" style="padding: 1rem;">Tổng Users: <span style="font-size: 1.5rem; font-weight: 700;">{len(df_metrics)}</span></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div data-testid="metric-container" style="padding: 1rem;">🎓 Mentors: <span style="font-size: 1.5rem; font-weight: 700;">{mentor_count}</span></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div data-testid="metric-container" style="padding: 1rem;">🛡️ Moderators: <span style="font-size: 1.5rem; font-weight: 700;">{moderator_count}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Chuẩn bị các cột để hiển thị
    display_cols = [
        'User', 'Role', 'Mentor Score', 'Moderator Score', 
        'PageRank', 'Authority', 'HITS Hub', 
        'Reciprocity', 'Triangles (Undirected)', 'Clustering (Undirected)', 
        'Degree', 'In-Degree', 'Out-Degree'
    ]
    
    # Lọc và tìm kiếm
    st.markdown("#### DANH SÁCH")
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        st.markdown("*Lọc theo Role:*")
        role_options = ['All'] + list(df_metrics['Role'].unique())
        selected_role = st.selectbox('Chọn role', role_options, index=0, label_visibility="collapsed")
    
    filtered_df = df_metrics.copy()
    if selected_role != 'All': filtered_df = filtered_df[filtered_df['Role'] == selected_role]
    
    st.markdown(f"**Hiển thị {len(filtered_df)} / {len(df_metrics)} users**")
    
    # Hiển thị bảng
    st.dataframe(filtered_df[display_cols], use_container_width=True, height=600, hide_index=True)
    
    # Download
    st.divider()
    csv = filtered_df[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button("### Tải xuống dữ liệu đã lọc (CSV)", csv, "social_network_filtered.csv", "text/csv")
    
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
                <div class="header-subtitle">Phân tích mạng xã hội chuyên nghiệp</div>
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

    # --- Navigation + Search Bar trên cùng 1 hàng ---
    st.markdown('<div style="padding: 0 3rem; margin-top: 1rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    
    # Khởi tạo session state cho current page nếu chưa có
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "📊 Dashboard Cá Nhân"
    
    # Tạo 2 nhóm chính: Navigation bên trái, Search bên phải
    main_col_left, main_col_right = st.columns([2.5, 1])
    
    # NHÓM TRÁI: Navigation Buttons
    with main_col_left:
        nav_col1, nav_col2 = st.columns(2)
        
        with nav_col1:
            # Nút Dashboard - hiển thị primary nếu đang ở trang này
            is_dashboard_active = st.session_state.current_page == "📊 Dashboard Cá Nhân"
            dashboard_selected = st.button(
                "### Dashboard Cá Nhân",
                key="dashboard_btn",
                use_container_width=True,
                type="primary" if is_dashboard_active else "secondary"
            )
        
        with nav_col2:
            # Nút Bảng Xếp Hạng - hiển thị primary nếu đang ở trang này
            is_ranking_active = st.session_state.current_page == "🏆 Bảng Xếp Hạng"
            ranking_selected = st.button(
                "### Bảng Xếp Hạng",
                key="ranking_btn",
                use_container_width=True,
                type="primary" if is_ranking_active else "secondary"
            )
    
    # NHÓM PHẢI: Search Bar
    with main_col_right:
        search_col1, search_col2 = st.columns([2, 1])
        
        with search_col1:
            all_users = df_metrics['User'].tolist()
            selected_user = st.selectbox(
                "Chọn User để xem chi tiết:",
                options=all_users,
                index=0,
                label_visibility="collapsed",
                key="user_selector"
            )
        
        with search_col2:
            search_clicked = st.button(
                "Tìm kiếm",
                key="search_btn",
                use_container_width=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="padding: 0 3rem;"><hr style="border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0;"/></div>', unsafe_allow_html=True)
    
    # Xác định trang nào được chọn dựa trên button clicks
    if dashboard_selected:
        st.session_state.current_page = "📊 Dashboard Cá Nhân"
        st.rerun()
    elif ranking_selected:
        st.session_state.current_page = "🏆 Bảng Xếp Hạng"
        st.rerun()
    
    page = st.session_state.current_page
    
    # --- Render content based on selected page ---
    if page == "📊 Dashboard Cá Nhân":
        render_dashboard(G, df_metrics, selected_user, len(df_metrics))
    else: 
        render_table_page(df_metrics)
        

if __name__ == "__main__":
    main()
