import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import RiskAnalysis
from src.schemas.risk import MAX_RISK_GROUPS
from src.services.risk_enum import enumerate_risk
from src.services.runs import require_completed
from src.utils.time import now
from src.utils.serialization import serialize
def _validate(run,payload):
 if len(payload.groups)>MAX_RISK_GROUPS:raise HTTPException(422,f"风险组超过{MAX_RISK_GROUPS}组，为防吞吐计算超时，拒绝分析")
 result=run.result
 snapshot_ids={a["arc_id"] for a in result["arcs"]}
 names=[]
 for g in payload.groups:
  unknown=[i for i in g.arc_ids if i not in snapshot_ids]
  if unknown:raise HTTPException(422,"风险组「%s」含未知边ID：%s"%(g.name,"、".join(unknown)))
  if g.name in names:raise HTTPException(422,f"风险组名称重复：{g.name}")
  names.append(g.name)
 return result
def create(db,payload,user):
 run=require_completed(db,payload.run_id)
 result=_validate(run,payload)
 if db.scalar(select(RiskAnalysis).where(RiskAnalysis.run_id==payload.run_id,RiskAnalysis.name==payload.name)):raise HTTPException(409,"本次推演下分析名称已存在")
 groups=[{"name":g.name,"probability":g.probability,"arc_ids":g.arc_ids} for g in payload.groups]
 try:analysis=enumerate_risk(result,groups,payload.target_throughput)
 except HTTPException:raise
 except Exception as e:raise HTTPException(422,f"风险枚举失败：{e}")
 item=RiskAnalysis(id=str(uuid.uuid4()),run_id=payload.run_id,name=payload.name,target_throughput=payload.target_throughput,groups=groups,result=analysis,created_by=user["email"],created_at=now())
 db.add(item);db.commit();return serialize(item)
