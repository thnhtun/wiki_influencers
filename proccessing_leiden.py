import pandas as pd
import networkx as nx
import igraph as ig
import leidenalg
import sys
import os
import time

# ================= CAU HINH (QUAN TRONG) =================
INPUT_FILE = 'WikiTalk.txt'
OUTPUT_FILE = 'leiden_seed.csv'
RANDOM_STATE = 42  # Dat seed de Leiden on dinh hon

# DIEN SO K BAN DA CHON VAO DAY (Vi du: 2, 5, 10...)
CHON_K = 3  
# =========================================================

def main():
    start_time = time.time()

    # 1. DOC DU LIEU
    if not os.path.exists(INPUT_FILE):
        print(f"Loi: Khong tim thay file '{INPUT_FILE}'!")
        sys.exit()

    print(f"--- 1. Dang doc file '{INPUT_FILE}'... ---")
    try:
        # Thu doc bang Tab
        df = pd.read_csv(INPUT_FILE, sep='\t', comment='#', header=None, names=['source', 'target'])
        if df.empty or len(df.columns) < 2:
            # Neu loi thi doc bang Space
            df = pd.read_csv(INPUT_FILE, sep=' ', comment='#', header=None, names=['source', 'target'])
        
        # Tao do thi CO HUONG de giu lai thong tin huong
        G_directed = nx.from_pandas_edgelist(df, 'source', 'target', create_using=nx.DiGraph())
        print(f"-> Do thi goc (co huong): {G_directed.number_of_nodes()} nodes, {G_directed.number_of_edges()} edges")
        
        # Tao ban sao VO HUONG de chay k-core va Louvain
        G = G_directed.to_undirected()
        print(f"-> Chuyen sang vo huong de xu ly")
    except Exception as e:
        print(f"Loi doc file: {e}")
        sys.exit()

    # 2. AP DUNG K-CORE (LOC RAC)
    print(f"\n--- 2. Dang loc voi K-core = {CHON_K} ---")
    G_core = nx.k_core(G, k=CHON_K)
    print(f"-> So node con lai sau k-core: {G_core.number_of_nodes()}")

    if G_core.number_of_nodes() == 0:
        print("LOI: K qua lon! Khong con node nao. Hay giam K xuong.")
        sys.exit()

    # 3. CHAY THUAT TOAN LEIDEN
    print("\n--- 3. Dang chay thuat toan Leiden (Tim cong dong)... ---")
    print("    (Vui long doi, buoc nay ton thoi gian...)")
    
    try:
        # Chuyen G_core (vo huong) sang igraph
        nodes = list(G_core.nodes())
        node_index = {n: i for i, n in enumerate(nodes)}
        edges_mapped = [(node_index[u], node_index[v]) for u, v in G_core.edges()]

        g_ig = ig.Graph()
        g_ig.add_vertices(len(nodes))
        g_ig.add_edges(edges_mapped)

        # Chay Leiden voi modularity (vo huong)
        leiden_partition = leidenalg.find_partition(
            g_ig,
            leidenalg.ModularityVertexPartition,
            seed=RANDOM_STATE
        )

        # Mapping lai ve node goc
        membership = leiden_partition.membership
        community_counts = {}
        for m in membership:
            community_counts[m] = community_counts.get(m, 0) + 1
    except MemoryError:
        print("LOI: Tran RAM! May tinh khong du bo nho.")
        print("Giai phap: Hay tang so K len (vi du tu 2 len 5 hoac 10) de giam bot du lieu.")
        sys.exit()
    except Exception as e:
        print(f"Loi thuat toan: {e}")
        sys.exit()

    # 4. TIM CONG DONG LON NHAT
    print("\n--- 4. Dang tim cong dong lon nhat... ---")
    
    # Tim ID cua cong dong lon nhat
    largest_comm_id = max(community_counts, key=community_counts.get)
    
    # Lay danh sach node trong cong dong lon nhat
    nodes_in_largest = [nodes[i] for i, m in enumerate(membership) if m == largest_comm_id]
    print(f"-> Cong dong lon nhat co {len(nodes_in_largest)} nodes")
    
    # 5. TAO DO THI CO HUONG TU CONG DONG LON NHAT
    print("\n--- 5. Dang tao do thi co huong tu cong dong lon nhat... ---")
    
    # Lay subgraph CO HUONG tu do thi goc
    G_final = G_directed.subgraph(nodes_in_largest).copy()
    
    # 6. HIEN THI KET QUA VA XUAT FILE
    print("-" * 60)
    print(f"KET QUA CUOI CUNG (K-core = {CHON_K}):")
    print(f" - Cong dong lon nhat co: {G_final.number_of_nodes()} nodes")
    print(f" - So luong canh (co huong): {G_final.number_of_edges()} edges")
    print(f" - File output: {OUTPUT_FILE}")
    print("-" * 60)

    print(f"-> Dang luu vao file '{OUTPUT_FILE}'...")
    
    # Luu file CSV co huong (source,target)
    edges_list = [(u, v) for u, v in G_final.edges()]
    df_output = pd.DataFrame(edges_list, columns=['source', 'target'])
    df_output.to_csv(OUTPUT_FILE, index=False)
    
    duration = round(time.time() - start_time, 2)
    print(f"-> HOAN TAT! Tong thoi gian: {duration} giay.")

if __name__ == "__main__":
    main()


