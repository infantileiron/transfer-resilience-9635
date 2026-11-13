import math
from src.services.maxflow import edmonds_karp
def enumerate_risk(result,groups,target_throughput):
 # Groups fail together, groups are independent, one arc may belong to several groups.
 # Exact enumeration of all 2**n failure states; states with identical throughput are merged.
 node_ids=[n["node_id"] for n in result["nodes"]]
 arcs=result["arcs"];source=result["source"];sink=result["sink"]
 base_disabled=set(result["disabled_arc_ids"])
 group_arcs=[set(g["arc_ids"]) for g in groups]
 n=len(groups)
 flow_cache={}
 def flow_for(extra_disabled):
  key=frozenset(extra_disabled)
  if key not in flow_cache:
   flow_cache[key]=edmonds_karp(node_ids,arcs,source,sink,tuple(sorted(base_disabled|key)))["value"]
  return flow_cache[key]
 reference=flow_for(set())
 distribution={}
 total_states=2**n
 for state in range(total_states):
  failed=[i for i in range(n) if (state>>i)&1]
  probability=1.0;extra=set()
  for i,g in enumerate(groups):
   if i in failed:probability*=g["probability"];extra|=group_arcs[i]
   else:probability*=1.0-g["probability"]
  throughput=flow_for(extra)
  bucket=distribution.setdefault(throughput,{"throughput":throughput,"probability":0.0,"state_count":0,"states":[]})
  bucket["probability"]+=probability;bucket["state_count"]+=1
  bucket["states"].append({"failed_group_names":[groups[i]["name"] for i in failed],"probability":probability,"throughput":throughput})
 merged=[distribution[k] for k in sorted(distribution,reverse=True)]
 for b in merged:b["states"].sort(key=lambda s:(-s["throughput"],s["failed_group_names"]))
 probability_sum=math.fsum(b["probability"] for b in merged)
 if not math.isclose(probability_sum,1.0,rel_tol=0,abs_tol=1e-10):raise ValueError(f"概率总和应为1，实际为{probability_sum!r}")
 expected_throughput=math.fsum(b["throughput"]*b["probability"] for b in merged)
 target_probability=math.fsum(b["probability"] for b in merged if b["throughput"]>=target_throughput)
 return {"reference_throughput":reference,"target_throughput":target_throughput,"expected_throughput":expected_throughput,"target_probability":target_probability,"probability_sum":probability_sum,"distribution":merged,"group_count":n,"state_count":total_states,"distinct_throughput_count":len(merged),"maxflow_call_count":len(flow_cache),"deterministic_failure_groups":[g["name"] for g in groups if g["probability"]==1.0],"zero_probability_groups":[g["name"] for g in groups if g["probability"]==0.0],"base_disabled_arc_ids":sorted(base_disabled),"checksum":result["checksum"]}
