"""Reuse certified component optima for exactly identical finite objectives.

The key contains all domains and every binary/unary factor, including repeated
factors, plus the cost table. Register numbers are immaterial to that objective.
All uncached solves use the unchanged PR1186 component solver. Recount and
primal feasibility are checked independently for every assembled assignment.
"""
import frames as F

CACHE={}

def optimal(w,costs,graph=None,check_literal=False):
    g=graph or F.Graph(w,check_literal=check_literal)
    assign={};total=0;certified=True;hits=0
    costkey=tuple(sorted(costs.c.items()))
    for comp in g.components:
        ids={k:i for i,k in enumerate(comp)};facts=[]
        for (k,r),j in g.prev.items():
            if k in ids and j in ids:facts.append(('b',ids[j],ids[k]))
            elif k in ids:facts.append(('i',ids[k],g.nodes[j][1]))
            elif j in ids:facts.append(('o',ids[j],g.nodes[k][1]))
        key=(costkey,tuple(tuple(g.dom[k]) for k in comp),tuple(sorted(facts)))
        if key in CACHE:
            c,a=CACHE[key];solution={k:a[i] for i,k in enumerate(comp)};ok=True;hits+=1
        else:
            res=F.solve_component_ve(g,costs,comp,max_tuples=5_000_000) if len(comp)<=600 else None
            if res is not None:c,solution=res;ok=True
            else:
                z=F.ChainDD(g,costs,var_subset=comp).solve(max_sweeps=300)
                c=z['primal'];solution=z['assign'];ok=z['certified']
            if ok:CACHE[key]=(c,tuple(solution[k] for k in comp))
        assign.update(solution);total+=c;certified &= ok
    for k in g.var:assert assign[k] in g.dom[k]
    for (k,r),j in g.prev.items():
        a=assign[k] if k in g.varset else g.nodes[k][1]
        b=assign[j] if j in g.varset else g.nodes[j][1]
        assert F.leq(b,a)
        if k not in g.varset and j not in g.varset:total+=costs.c[len(a)-len(b)]
    profile=g.profile(assign)
    assert total==costs.profile_cost(profile)
    return dict(cost=total,profile=profile,assign=assign,certified=certified,cache_hits=hits,components=len(g.components))
