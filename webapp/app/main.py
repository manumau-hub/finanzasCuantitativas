from fastapi import FastAPI, Depends
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from app.Codigo.opcion_europea_bs import opcion_europea_bs
from app.Codigo.opcion_europea_bin import opcion_europea_bin
from app.Codigo.opcion_europea_mc import opcion_europea_mc
from app.Codigo.opcion_europea_fd import opcion_europea_fd

app = FastAPI()

class Model(str, Enum):
    BS = 'BS'
    BIN = 'BIN'
    MC = 'MC'
    FD = 'FD'

class OptionParameters(BaseModel):
    type: str = 'C'
    S: float = 100.0
    K: float = 100.0
    T: float = 1.0
    r: Optional[float] = 0.01
    sigma: Optional[float] = 0.1
    div: Optional[float] = 0.0
    model: Model = Model.BS

class Result(BaseModel):
    price:float
    model: Model

@app.get("/price/options/european", tags=['Europeans'])
async def root(params: OptionParameters = Depends()):

    if params.model == Model.BS:
        price = opcion_europea_bs(tipo=params.type,
                                  S=params.S,
                                  K=params.K,
                                  T=params.T,
                                  r=params.r,
                                  sigma=params.sigma,
                                  div=params.div)
    elif params.model == Model.BIN:
         price = opcion_europea_bin(tipo=params.type,
                                  S=params.S,
                                  K=params.K,
                                  T=params.T,
                                  r=params.r,
                                  sigma=params.sigma,
                                  div=params.div,
                                  pasos=1000)
    elif params.model == Model.MC:
         price = opcion_europea_mc(tipo=params.type,
                                  S=params.S,
                                  K=params.K,
                                  T=params.T,
                                  r=params.r,
                                  sigma=params.sigma,
                                  div=params.div,
                                  pasos=1000000)
    elif params.model == Model.FD:
         price = opcion_europea_fd(tipo=params.type,
                                  S=params.S,
                                  K=params.K,
                                  T=params.T,
                                  r=params.r,
                                  sigma=params.sigma,
                                  div=params.div,
                                  M=200)

    return Result(price=price, model=params.model)
