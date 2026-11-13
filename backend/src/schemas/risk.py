import math
from typing import Annotated
from pydantic import BaseModel,Field,field_validator,BeforeValidator
MAX_RISK_GROUPS=12
def _check_probability(v):
 if isinstance(v,bool) or not isinstance(v,(int,float)):raise ValueError("故障概率须为0到1之间的数值")
 if not math.isfinite(v):raise ValueError("故障概率须为有限数值")
 if not 0.0<=v<=1.0:raise ValueError("故障概率须在0到1之间")
 return float(v)
Probability=Annotated[float,BeforeValidator(_check_probability)]
def _check_target(v):
 if isinstance(v,bool) or not isinstance(v,int):raise ValueError("目标箱量须为非负整数")
 if v<0:raise ValueError("目标箱量须为非负整数")
 return v
TargetThroughput=Annotated[int,BeforeValidator(_check_target)]
class RiskGroupInput(BaseModel):
 name:str=Field(min_length=1,max_length=120)
 probability:Probability
 arc_ids:list[str]=Field(min_length=1)
 @field_validator("arc_ids")
 @classmethod
 def arc_ids_known_shape(cls,v):
  if any(not isinstance(i,str) or not i for i in v):raise ValueError("边ID须为非空字符串")
  if len(v)!=len(set(v)):raise ValueError("同一风险组内边ID不得重复")
  return v
 @field_validator("name")
 @classmethod
 def name_not_blank(cls,v):
  if not v.strip():raise ValueError("风险组名称不得为空白")
  return v
class RiskAnalysisInput(BaseModel):
 run_id:str
 name:str=Field(min_length=1,max_length=160)
 target_throughput:TargetThroughput
 groups:list[RiskGroupInput]=Field(min_length=1,max_length=MAX_RISK_GROUPS)
 @field_validator("name")
 @classmethod
 def name_not_blank(cls,v):
  if not v.strip():raise ValueError("分析名称不得为空白")
  return v
