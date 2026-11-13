from sqlalchemy import String,Integer,Double,JSON,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class RiskAnalysis(Base):
 __tablename__="risk_analyses"
 __table_args__=(UniqueConstraint("run_id","name"),)
 id:Mapped[str]=mapped_column(String(80),primary_key=True)
 run_id:Mapped[str]=mapped_column(ForeignKey("network_runs.id"))
 name:Mapped[str]=mapped_column(String(160))
 target_throughput:Mapped[int]=mapped_column(Integer)
 groups:Mapped[list]=mapped_column(JSON)
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 created_by:Mapped[str]=mapped_column(String(160))
 created_at:Mapped[str]=mapped_column(String(64))
