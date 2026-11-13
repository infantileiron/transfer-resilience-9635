from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from src.config.database import db_session
from src.controllers.auth import current_user,writer
from src.models import RiskAnalysis
from src.schemas.risk import RiskAnalysisInput
from src.services import risk as service
from src.utils.serialization import rows,serialize
router=APIRouter(prefix="/risk-analyses")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)):return rows(db.scalars(select(RiskAnalysis).order_by(RiskAnalysis.created_at.desc())))
@router.post("")
def create(payload:RiskAnalysisInput,db=Depends(db_session),user=Depends(writer)):return service.create(db,payload,user)
@router.get("/{id}")
def detail(id:str,db=Depends(db_session),user=Depends(current_user)):
 item=db.get(RiskAnalysis,id)
 if not item:raise HTTPException(404,"风险分析不存在")
 return serialize(item)
