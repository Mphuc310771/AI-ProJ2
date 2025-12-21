from pysat.formula import CNF
from pysat.card import CardEnc


class HashiCNF:
    # sinh CNF cho Hashi
    
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.islands = []
        self.bridges = []
        self.var_pool = {}
        self.cnf = CNF()
        
        self._tim_dao()
        self._tim_cau()
        self._gan_bien()

    def _tim_dao(self):
        # duyet grid tim cac o co so > 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] > 0:
                    self.islands.append({
                        'r': r, 'c': c, 
                        'val': self.grid[r][c], 
                        'id': len(self.islands)
                    })

    def _tim_cau(self):
        # tim cac cap dao co the noi cau (ke nhau theo hang/cot)
        for i, u in enumerate(self.islands):
            # tim theo chieu ngang (sang phai)
            for c in range(u['c'] + 1, self.cols):
                val = self.grid[u['r']][c]
                if val > 0:
                    # tim dao tuong ung
                    v = None
                    for dao in self.islands:
                        if dao['r'] == u['r'] and dao['c'] == c:
                            v = dao
                            break
                    
                    self.bridges.append({
                        'u': u, 'v': v,
                        'type': 'horizontal',
                        'idx': len(self.bridges)
                    })
                    break

            # tim theo chieu doc (xuong duoi)
            for r in range(u['r'] + 1, self.rows):
                val = self.grid[r][u['c']]
                if val > 0:
                    v = None
                    for dao in self.islands:
                        if dao['r'] == r and dao['c'] == u['c']:
                            v = dao
                            break
                    
                    self.bridges.append({
                        'u': u, 'v': v,
                        'type': 'vertical',
                        'idx': len(self.bridges)
                    })
                    break

    def _gan_bien(self):
        # moi cau co 2 bien: bien[idx,1] = co 1 cau, bien[idx,2] = co 2 cau
        dem = 1
        for b in self.bridges:
            self.var_pool[(b['idx'], 1)] = dem
            self.var_pool[(b['idx'], 2)] = dem + 1
            dem += 2

    def generate_cnf(self):
        # rang buoc: neu co 2 cau thi phai co 1 cau (var2 -> var1)
        for b in self.bridges:
            idx = b['idx']
            v1 = self.var_pool[(idx, 1)]
            v2 = self.var_pool[(idx, 2)]
            # v2 -> v1 tuong duong voi -v2 OR v1
            self.cnf.append([-v2, v1])

        # rang buoc: cau ngang va cau doc ko duoc cat nhau
        ds_ngang = [b for b in self.bridges if b['type'] == 'horizontal']
        ds_doc = [b for b in self.bridges if b['type'] == 'vertical']

        for h in ds_ngang:
            for v in ds_doc:
                # kiem tra xem 2 cau co giao nhau ko
                h_row = h['u']['r']
                h_c1, h_c2 = h['u']['c'], h['v']['c']
                
                v_col = v['u']['c']
                v_r1, v_r2 = v['u']['r'], v['v']['r']
                
                # giao khi cot cua cau doc nam giua 2 dau cau ngang
                # va hang cua cau ngang nam giua 2 dau cau doc
                if h_c1 < v_col < h_c2 and v_r1 < h_row < v_r2:
                    h_var = self.var_pool[(h['idx'], 1)]
                    v_var = self.var_pool[(v['idx'], 1)]
                    # ko the ca 2 cung co -> -h_var OR -v_var
                    self.cnf.append([-h_var, -v_var])

        # rang buoc: moi dao phai co dung so cau yeu cau
        for dao in self.islands:
            ds_bien = []
            
            for b in self.bridges:
                if b['u'] == dao or b['v'] == dao:
                    ds_bien.append(self.var_pool[(b['idx'], 1)])
                    ds_bien.append(self.var_pool[(b['idx'], 2)])
            
            # dung CardEnc de tao rang buoc tong = val
            clauses = CardEnc.equals(
                lits=ds_bien, 
                bound=dao['val'], 
                top_id=self.cnf.nv
            )
            self.cnf.extend(clauses)

        return self.cnf

    def get_clause_list(self):
        ds = [list(cl) for cl in self.cnf.clauses]
        so_bien = 0
        for cl in ds:
            for lit in cl:
                so_bien = max(so_bien, abs(lit))
        return ds, so_bien
