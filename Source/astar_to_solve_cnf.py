import heapq
import time
import tracemalloc
from collections import Counter

from cnf_generator import HashiCNF
from hashiwokakero import PuzzleState


def kiem_tra_clause(clause, gan):
    # kiem tra clause co thoa man voi gan hien tai ko
    for lit in clause:
        v = abs(lit)
        if v in gan:
            gia_tri = gan[v]
            if (lit > 0 and gia_tri) or (lit < 0 and not gia_tri):
                return True
    return False


def dem_chua_thoa(ds_clause, gan):
    # dem so clause chua thoa man
    dem = 0
    for cl in ds_clause:
        if not kiem_tra_clause(cl, gan):
            dem += 1
    return dem


def lan_truyen_don_vi(ds_clause, gan):
    # unit propagation
    gan_moi = gan.copy()
    co_thay_doi = True
    
    while co_thay_doi:
        co_thay_doi = False
        
        for clause in ds_clause:
            if kiem_tra_clause(clause, gan_moi):
                continue
            
            # tim cac bien chua gan
            chua_gan = []
            for lit in clause:
                if abs(lit) not in gan_moi:
                    chua_gan.append(lit)
            
            # clause rong ma chua thoa -> xung dot
            if not chua_gan:
                return None, True
            
            # unit clause -> gan gia tri de thoa man
            if len(chua_gan) == 1:
                lit = chua_gan[0]
                bien = abs(lit)
                can_true = (lit > 0)
                
                if bien in gan_moi and gan_moi[bien] != can_true:
                    return None, True
                
                if bien not in gan_moi:
                    gan_moi[bien] = can_true
                    co_thay_doi = True
                    
    return gan_moi, False


def tao_state_tu_gan(hc, gan, puzzle):
    # chuyen phep gan sang PuzzleState
    state = PuzzleState()
    
    for b in hc.bridges:
        idx = b['idx']
        var1 = hc.var_pool.get((idx, 1))
        var2 = hc.var_pool.get((idx, 2))
        
        so_cau = 0
        if var2 is not None and gan.get(var2, False):
            so_cau = 2
        elif var1 is not None and gan.get(var1, False):
            so_cau = 1

        if so_cau > 0:
            u, v = b['u'], b['v']
            dao_u = puzzle.island_map[(u['r'], u['c'])]
            dao_v = puzzle.island_map[(v['r'], v['c'])]
            state.add_bridge(dao_u, dao_v, so_cau)

    return state


def solve_astar(puzzle, gioi_han_tg=300, gioi_han_node=2000000):
    # giai bang A*
    hc = HashiCNF(puzzle.grid)
    hc.generate_cnf()
    ds_clause, so_bien = hc.get_clause_list()

    tracemalloc.start()
    t0 = time.perf_counter()

    # bat dau voi phep gan rong, chay unit propagation
    gan_dau, xung_dot = lan_truyen_don_vi(ds_clause, {})
    if xung_dot:
        return None, time.perf_counter() - t0, {'status': 'unsat'}

    g0 = len(gan_dau)
    h0 = dem_chua_thoa(ds_clause, gan_dau)
    
    unique_id = 0
    heap = []
    heapq.heappush(heap, (g0 + h0, h0, g0, unique_id, gan_dau))
    
    da_xet = set()
    key_dau = tuple(sorted(gan_dau.items()))
    da_xet.add(key_dau)

    so_node = 0
    max_heap = 1

    while heap:
        # kiem tra gioi han thoi gian
        if (time.perf_counter() - t0) > gioi_han_tg:
            break

        f, h, g, _, gan_ht = heapq.heappop(heap)

        max_heap = max(max_heap, len(heap))
        
        so_node += 1
        if so_node > gioi_han_node:
            break

        # kiem tra da thoa man het clause chua
        if h == 0 and dem_chua_thoa(ds_clause, gan_ht) == 0:
            cur_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            tg_chay = time.perf_counter() - t0
            
            thong_ke = {
                'nodes_expanded': so_node,
                'max_open_size': max_heap,
                'peak_memory_bytes': peak_mem,
                'num_vars': so_bien,
                'algorithm': 'A*'
            }
            
            state = tao_state_tu_gan(hc, gan_ht, puzzle)
            return state, tg_chay, thong_ke

        # tim bien tot nhat de thu
        # chon tu clause ngan nhat chua thoa man
        do_dai_min = float('inf')
        ds_bien_tot = Counter()
        
        co_chua_thoa = False
        for cl in ds_clause:
            if kiem_tra_clause(cl, gan_ht):
                continue
            
            co_chua_thoa = True
            chua_gan = [abs(lit) for lit in cl if abs(lit) not in gan_ht]
            
            if not chua_gan:
                continue
            
            do_dai = len(chua_gan)
            if do_dai < do_dai_min:
                do_dai_min = do_dai
                ds_bien_tot = Counter()
            
            if do_dai == do_dai_min:
                for v in chua_gan:
                    ds_bien_tot[v] += 1
        
        if not co_chua_thoa or not ds_bien_tot:
            continue

        # chon bien xuat hien nhieu nhat
        bien_tiep = ds_bien_tot.most_common(1)[0][0]

        # thu ca 2 gia tri True va False
        for gia_tri in [True, False]:
            gan_moi = gan_ht.copy()
            gan_moi[bien_tiep] = gia_tri
            
            gan_sau, xung_dot = lan_truyen_don_vi(ds_clause, gan_moi)
            
            if xung_dot:
                continue
            
            key_sau = tuple(sorted(gan_sau.items()))
            if key_sau in da_xet:
                continue
            
            da_xet.add(key_sau)
            
            g_moi = len(gan_sau)
            h_moi = dem_chua_thoa(ds_clause, gan_sau)
            
            unique_id += 1
            heapq.heappush(heap, (g_moi + h_moi, h_moi, g_moi, unique_id, gan_sau))

    tracemalloc.stop()
    return None, time.perf_counter() - t0, {
        'nodes_expanded': so_node, 
        'max_open_size': max_heap
    }