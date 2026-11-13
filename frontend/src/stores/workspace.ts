import * as datasets from '../api/datasets';import * as arcs from '../api/arcs';import * as scenarios from '../api/scenarios';import * as runs from '../api/runs';import * as reviews from '../api/reviews';import * as reports from '../api/reports';import * as risk from '../api/risk';import * as audit from '../api/audit';
export async function load(){const [d,e,s,r,v,p,k,a]=await Promise.all([datasets.list(),arcs.list(),scenarios.list(),runs.list(),reviews.list(),reports.list(),risk.list(),audit.list()]);return {datasets:d,arcs:e,scenarios:s,runs:r,reviews:v,reports:p,riskAnalyses:k,audit:a}}
export type Workspace=Awaited<ReturnType<typeof load>>;
export const emptyWorkspace=():Workspace=>({datasets:[],arcs:[],scenarios:[],runs:[],reviews:[],reports:[],riskAnalyses:[],audit:[]});
