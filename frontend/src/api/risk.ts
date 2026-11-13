import {request,post} from './client';
import type {RiskAnalysis} from '../types/domain';
export const list=()=>request<RiskAnalysis[]>('/risk-analyses');
export const create=(data:unknown)=>post<RiskAnalysis>('/risk-analyses',data);
